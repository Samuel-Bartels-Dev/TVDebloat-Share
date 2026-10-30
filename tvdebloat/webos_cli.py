"""Platform dispatch kept separate from the Android engine."""
from __future__ import annotations

import json
from pathlib import Path

from .webos import SSHClient, WebOSError, discover, preflight
from .webos_profile import initialize, load
from .webos_plan import preview, apply, restore_preview, restore, write_json


SUPPORTED = {'preflight', 'probe', 'discover', 'profile-init', 'preview', 'provision',
             'restore', 'verify', 'drift'}


def _json(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError()
        return data
    except (OSError, ValueError):
        raise WebOSError('Cannot read webOS JSON artifact') from None


def run(args):
    if args.command not in SUPPORTED:
        raise WebOSError(f'{args.command} is not supported for webOS')
    if args.command == 'profile-init':
        path = initialize(args.from_file, args.vendor, args.model, args.name)
        return {'profile': str(path), 'platform': 'webos', 'status': 'candidate'}
    if getattr(args, 'profile', None) and args.command != 'restore':
        load(args.profile)  # Schema errors fail before constructing transport.
    if args.command == 'restore':
        journal = _json(args.profile)
        if journal.get('platform') != 'webos':
            raise WebOSError('Recovery journal platform is not webOS')
    plan = None
    if args.command == 'provision' and args.apply:
        if not args.plan or not args.approve_plan or not args.state_dir:
            raise WebOSError('webOS --apply requires --plan, --approve-plan and --state-dir')
        plan = _json(args.plan)
    if not args.host:
        raise WebOSError('--host is required for webOS discovery')
    client = SSHClient(args.host, args.ssh_port, args.ssh_user, args.ssh_key)
    if args.command == 'preflight':
        return preflight(client)
    if args.command == 'probe':
        data = discover(client)
        return {'platform': 'webos', 'device': data['device'],
                'capabilities': data['capabilities'], 'warnings': data['warnings']}
    if args.command == 'discover':
        data = discover(client)
        write_json(args.out, data)
        return {'discovery': str(Path(args.out)), 'platform': 'webos',
                'apps': len(data['apps']), 'launch_points': len(data['launch_points']),
                'warnings': data['warnings']}
    if args.command in {'preview', 'provision', 'drift'}:
        if plan is not None:
            return apply(client, args.profile, plan, args.approve_plan, args.state_dir, args.pilot)
        result = preview(client, args.profile)
        if args.plan:
            write_json(args.plan, result)
        return result
    if args.command == 'restore':
        if args.apply:
            if not args.approve_plan or not args.state_dir:
                raise WebOSError('Restore requires approval of the recovery preview and --state-dir')
            return restore(client, args.profile, args.approve_plan, args.state_dir)
        return restore_preview(client, args.profile)
    data = discover(client)
    return {'platform': 'webos', 'readable': True, 'device': data['device'],
            'capabilities': data['capabilities'], 'validation': 'physical checks pending',
            'warnings': data['warnings']}
