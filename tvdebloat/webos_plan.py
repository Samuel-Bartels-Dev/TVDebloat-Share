"""Exact launcher plans and recovery. Native SSH remains read-only until validated."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import uuid

from .webos import WebOSError, discover
from .webos_profile import load


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=True).encode()).hexdigest()


def seal(value):
    return dict(value, digest=digest(value))


def _approved(plan, approval):
    body = {key: value for key, value in plan.items() if key != 'digest'}
    if not approval or approval != plan.get('digest') or approval != digest(body):
        raise WebOSError('Explicit approval of the exact untampered plan digest is required')


def _snapshot(data):
    return {key: data[key] for key in ('target_id', 'device', 'apps', 'launch_points', 'capabilities')}


def _order(snapshot):
    return [point['id'] for point in snapshot['launch_points']]


def _moves(before, after):
    if len(before) != len(after) or set(before) != set(after) or len(set(after)) != len(after):
        raise WebOSError('Launcher order must preserve every unique launch point exactly once')
    working, actions = before[:], []
    for index, point in enumerate(after):
        if working[index] != point:
            actions.append({'type': 'move_launch_point', 'id': point, 'position': index})
            working.remove(point)
            working.insert(index, point)
    return actions


def _protected(app):
    return (app.startswith(('com.webos.app.hdmi', 'com.webos.app.input'))
            or app in {'com.webos.app.home', 'com.palm.app.settings', 'com.webos.app.settings',
                       'com.webos.app.livetv', 'com.webos.app.firstuse', 'firstuse',
                       'com.webos.app.eula', 'eula', 'com.webos.app.browser',
                       'com.webos.app.container', 'container', 'com.webos.app.webapphost',
                       'webapphost', 'org.webosbrew.hbchannel', 'com.tvweb.dashboard', 'com.tvweb.home'})


def preview(client, profile_path):
    profile = load(profile_path)  # Validate before transport.
    if profile['status'] == 'deprecated':
        raise WebOSError('Deprecated webOS profile cannot be used')
    snapshot = _snapshot(discover(client))
    if profile['device'] != snapshot['device']:
        raise WebOSError('Exact webOS model, firmware and platform match required')
    before = _order(snapshot)
    after = profile['launcher']['order'] or before[:]
    actions = _moves(before, after)
    installed = {app['id'] for app in snapshot['apps']}
    for app in profile['apps']['hide']:
        if app not in installed or _protected(app):
            raise WebOSError('Cannot hide unknown or protected webOS app')
    blocked = []
    if profile['apps']['hide']:
        blocked.append('App hiding is not implemented; a verified visibility/recovery contract is required')
    if profile['services']['disable']:
        blocked.append('Service disabling is not implemented; service evidence and recovery are required')
    if actions and not snapshot['capabilities']['move_launch_point']:
        blocked.append('No verified native firmware contract for launcher writes')
    return seal({'schema_version': 1, 'platform': 'webos', 'kind': 'launcher_order',
                 'profile_sha256': hashlib.sha256(Path(profile_path).read_bytes()).hexdigest(),
                 'snapshot': snapshot, 'before_order': before, 'after_order': after,
                 'actions': actions, 'inverse': _moves(after, before), 'blocked': blocked,
                 'pending': {'hide_apps': profile['apps']['hide'], 'disable_services': profile['services']['disable']},
                 'ready': bool(actions) and not blocked,
                 'warnings': ['TV-visible Home refresh and physical tests remain unverified; no automatic restart']})


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8') as output:
            json.dump(value, output, sort_keys=True, indent=2)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _execute(client, plan, state_dir):
    if not plan['ready'] or not plan['snapshot']['capabilities']['move_launch_point']:
        raise WebOSError('Plan is blocked or has no executable changes')
    if not state_dir:
        raise WebOSError('Choose an explicit private local state directory')
    journal_path = Path(state_dir) / ('webos-' + uuid.uuid4().hex + '.json')
    journal = {'schema_version': 1, 'platform': 'webos', 'plan': plan,
               'created_at': datetime.now(timezone.utc).isoformat(), 'status': 'applying',
               'completed': [], 'pending': None, 'current_order': plan['before_order'][:]}
    write_json(journal_path, journal)
    for action in plan['actions']:
        current = _snapshot(discover(client))
        expected = dict(plan['snapshot'])
        by_id = {point['id']: point for point in expected['launch_points']}
        expected['launch_points'] = [by_id[p] for p in journal['current_order']]
        if current != expected:
            journal['status'] = 'drift'
            write_json(journal_path, journal)
            raise WebOSError('Live state drifted; stop and create a new preview')
        journal['pending'] = action
        write_json(journal_path, journal)  # Durable before sending a mutation.
        try:
            client.move_launch_point(action['id'], action['position'])
            order = journal['current_order'][:]
            order.remove(action['id'])
            order.insert(action['position'], action['id'])
            observed = _snapshot(discover(client))
            expected['launch_points'] = [by_id[p] for p in order]
            if observed != expected:
                raise WebOSError('Launcher readback did not match')
        except Exception:
            journal['status'] = 'uncertain'
            write_json(journal_path, journal)
            raise WebOSError('Write outcome uncertain; preserve journal and inspect before recovery') from None
        journal['completed'].append(action)
        journal['pending'] = None
        journal['current_order'] = order
        write_json(journal_path, journal)
    journal['status'] = 'complete'
    write_json(journal_path, journal)
    return {'journal': str(journal_path), 'changed': journal['completed'],
            'physical_validation': 'pending; no automatic restart or promotion'}


def apply(client, profile_path, plan, approval, state_dir, pilot=False):
    _approved(plan, approval)
    profile = load(profile_path)
    if profile['status'] == 'candidate' and not pilot:
        raise WebOSError('Candidate profile requires explicit pilot acknowledgement')
    fresh = preview(client, profile_path)
    if fresh != plan:
        raise WebOSError('Profile, target or state drifted; preview and approve again')
    return _execute(client, plan, state_dir)


def restore_preview(client, journal_path):
    try:
        journal = json.loads(Path(journal_path).read_text(encoding='utf-8'))
        plan = journal['plan']
        _approved(plan, plan['digest'])
        if journal['status'] not in {'complete', 'applying', 'drift'} or journal['pending'] is not None:
            raise WebOSError('Uncertain journal requires manual evidence before recovery')
        completed = journal['completed']
        if not isinstance(completed, list) or not completed or completed != plan['actions'][:len(completed)]:
            raise WebOSError('Journal does not contain a verified completed action prefix')
        current_order = plan['before_order'][:]
        for action in completed:
            current_order.remove(action['id'])
            current_order.insert(action['position'], action['id'])
        if journal['current_order'] != current_order:
            raise WebOSError('Journal completion evidence does not match plan')
        snapshot = _snapshot(discover(client))
        expected = dict(plan['snapshot'])
        by_id = {point['id']: point for point in expected['launch_points']}
        expected['launch_points'] = [by_id[p] for p in current_order]
        if snapshot != expected:
            raise WebOSError('Recovery target or launcher state drifted; manual investigation required')
        before, after = current_order, plan['before_order']
        return seal({'schema_version': 1, 'platform': 'webos', 'kind': 'restore_launcher_order',
                     'source_plan': plan['digest'], 'snapshot': snapshot,
                     'before_order': before, 'after_order': after,
                     'actions': _moves(before, after), 'ready': bool(before != after)
                     and snapshot['capabilities']['move_launch_point']})
    except (OSError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, WebOSError):
            raise
        raise WebOSError('Invalid webOS recovery journal') from None


def restore(client, journal_path, approval, state_dir):
    plan = restore_preview(client, journal_path)
    _approved(plan, approval)
    return _execute(client, plan, state_dir)
