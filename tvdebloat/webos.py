"""Independent, read-only webOS discovery over existing trusted SSH access."""
from __future__ import annotations

import hashlib
import json
import re
import shlex
import subprocess


SYSTEM = 'com.webos.service.tv.systemproperty/getSystemProperties'
OS = 'os-release'
APPS = 'com.webos.applicationManager/listApps'
POINTS = 'com.webos.applicationManager/listLaunchPoints'
READ_URIS = {SYSTEM, OS, APPS, POINTS}
LIMIT = 1024 * 1024
ID = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.+-]{0,255}$')


class WebOSError(ValueError):
    pass


def identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise WebOSError('Invalid webOS identifier')
    return value


class SSHClient:
    # No native firmware write contract has yet been validated. Profiles cannot
    # override this. A future adapter needs exact firmware evidence and tests.
    move_verified = False

    def __init__(self, host, port=22, user='root', key=None):
        if not isinstance(host, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', host):
            raise ValueError('Use a plain IPv4 address or DNS hostname for SSH')
        if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*', user):
            raise ValueError('Invalid SSH user')
        if not 1 <= port <= 65535:
            raise ValueError('Invalid SSH port')
        self._endpoint = f'{user}@{host.lower()}:{port}'
        self._server_key = None
        self.target_id = hashlib.sha256(self._endpoint.encode()).hexdigest()
        self.command = ['ssh', '-v', '-T', '-o', 'FingerprintHash=sha256',
                        '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                        '-o', 'ForwardAgent=no', '-o', 'ClearAllForwardings=yes',
                        '-o', 'ConnectTimeout=5', '-o', 'ConnectionAttempts=1', '-p', str(port)]
        if key:
            self.command += ['-o', 'IdentitiesOnly=yes', '-i', str(key)]
        self.command += [f'{user}@{host}']

    def read(self, uri, payload=None):
        if uri not in READ_URIS or payload not in (None, {}):
            raise WebOSError('Operation is not an allowlisted webOS read')
        if uri == OS:
            remote = 'cat /etc/issue /etc/issue.net /etc/starfish-release 2>/dev/null | head -c 4096'
        else:
            args = {'keys': ['modelName', 'firmwareVersion', 'boardType', 'sdkVersion']} if uri == SYSTEM else {}
            remote = shlex.join(['/usr/bin/luna-send', '-n', '1', '-f', 'luna://' + uri,
                                 json.dumps(args, separators=(',', ':'))])
            remote += f' 2>/dev/null | head -c {LIMIT + 1}'
        try:
            proc = subprocess.run(self.command + [remote], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, timeout=12)
        except (OSError, subprocess.TimeoutExpired):
            raise WebOSError('SSH read failed; check trusted host key, access and reachability') from None
        if proc.returncode:
            raise WebOSError('SSH read failed; check trusted host key, access and reachability')
        # Retain only a digest bound to the negotiated server key. Never emit
        # SSH's verbose log: it can contain local paths and account details.
        if len(proc.stderr) > 65536:
            raise WebOSError('SSH host key evidence exceeded size limit')
        match = re.search(rb'debug1: Server host key: [^\s]+ (SHA256:[A-Za-z0-9+/=]+)', proc.stderr)
        if not match:
            raise WebOSError('SSH server host key evidence unavailable')
        server_key = match[1].decode('ascii')
        if self._server_key and server_key != self._server_key:
            raise WebOSError('SSH server host key changed; stop and verify identity')
        self._server_key = server_key
        self.target_id = hashlib.sha256((self._endpoint + '|' + server_key).encode()).hexdigest()
        if len(proc.stdout) > LIMIT:
            raise WebOSError('webOS response exceeds size limit')
        try:
            raw = proc.stdout.decode('utf-8')
            if uri == OS:
                match = re.search(r'(?:webOS(?:\s+TV)?\s+|release\s+)(\d+(?:\.\d+)+)', raw, re.I)
                return {'returnValue': bool(match), 'platformVersion': match[1] if match else ''}
            result = json.loads(raw)
        except (UnicodeError, ValueError):
            raise WebOSError('Invalid webOS response') from None
        if not isinstance(result, dict):
            raise WebOSError('Invalid webOS response object')
        return result

    def move_launch_point(self, launch_point_id, position):
        raise WebOSError('No verified native firmware contract for launcher writes; read-only')


def _success(response, operation):
    if not isinstance(response, dict) or response.get('returnValue') is not True:
        raise WebOSError(f'webOS {operation} failed or permission unavailable')
    return response


def _version(value):
    return value if isinstance(value, str) and re.fullmatch(r'\d+(?:\.\d+)+', value) else ''


def discover(client):
    system = _success(client.read(SYSTEM), 'identity read')
    model = identifier(system.get('modelName'))
    firmware = _version(system.get('firmwareVersion'))
    if not firmware:
        raise WebOSError('TV firmware could not be established')
    os_info = client.read(OS)  # Transport/host identity failures must stop discovery.
    platform = (_version(os_info.get('platformVersion'))
                if isinstance(os_info, dict) and os_info.get('returnValue') is True else '')
    apps_raw = _success(client.read(APPS), 'app inventory').get('apps')
    points_raw = _success(client.read(POINTS), 'launcher inventory').get('launchPoints')
    if not isinstance(apps_raw, list) or not isinstance(points_raw, list):
        raise WebOSError('Incomplete webOS inventory')
    apps, points, seen = [], [], set()
    for item in apps_raw:
        if not isinstance(item, dict):
            raise WebOSError('Malformed app inventory')
        app_id = identifier(item.get('id'))
        if app_id in seen:
            raise WebOSError('Duplicate app identifier')
        seen.add(app_id)
        apps.append({'id': app_id, 'system': item.get('systemApp') is True,
                     'removable': item.get('removable') is True})
    seen = set()
    for item in points_raw:
        if not isinstance(item, dict):
            raise WebOSError('Malformed launcher inventory')
        point_id, app_id = identifier(item.get('launchPointId')), identifier(item.get('id'))
        if point_id in seen:
            raise WebOSError('Duplicate launch-point identifier')
        seen.add(point_id)
        points.append({'id': point_id, 'app': app_id})
    verified = bool(platform and getattr(client, 'move_verified', False))
    return {'schema_version': 1, 'platform': 'webos', 'target_id': client.target_id,
            'device': {'manufacturer': 'LG', 'model': model, 'firmware': firmware, 'webos': platform},
            'apps': apps, 'launch_points': points, 'services': [],
            'capabilities': {'move_launch_point': verified, 'hide_app': False,
                             'disable_service': False, 'replace_home': False},
            'ready_for_write': verified,
            'warnings': ([] if platform else ['webOS platform version unavailable; firmware is not an OS version'])
                        + ([] if verified else ['No verified launcher write contract; discovery and preview only']),
            'services_evidence': 'not collected; no service decisions established'}


def preflight(client):
    try:
        snapshot = discover(client)
    except WebOSError as exc:
        return {'ready': False, 'ready_for_write': False,
                'checks': [{'id': 'webos_discovery', 'status': 'fail', 'summary': str(exc)}]}
    return {'ready': True, 'ready_for_write': snapshot['ready_for_write'],
            'device': snapshot['device'], 'checks': [
                {'id': 'webos_discovery', 'status': 'ok', 'summary': 'Identity and inventories readable'},
                {'id': 'write_contract', 'status': 'ok' if snapshot['ready_for_write'] else 'warn',
                 'summary': 'Verified launcher adapter' if snapshot['ready_for_write'] else 'Read-only native adapter'}]}
