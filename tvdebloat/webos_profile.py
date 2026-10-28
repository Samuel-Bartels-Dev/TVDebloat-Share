"""webOS profiles deliberately do not use Android package semantics."""
from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib

from .webos import WebOSError, identifier


def _keys(data, allowed):
    if not isinstance(data, dict) or set(data) - set(allowed):
        raise WebOSError('Unknown or invalid webOS profile fields')


def load(path):
    try:
        data = tomllib.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise WebOSError('Cannot read webOS TOML profile') from None
    _keys(data, {'schema_version', 'platform', 'name', 'status', 'device', 'apps', 'launcher', 'services'})
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1 or data.get('platform') != 'webos':
        raise WebOSError('Expected webOS profile schema 1')
    if data.get('status') not in {'candidate', 'validated', 'deprecated'}:
        raise WebOSError('Invalid webOS profile status')
    device = data.get('device')
    _keys(device, {'manufacturer', 'model', 'firmware', 'webos'})
    if set(device) != {'manufacturer', 'model', 'firmware', 'webos'} or device['manufacturer'] != 'LG':
        raise WebOSError('webOS profile needs exact LG model, firmware and platform fields')
    identifier(device['model'])
    for field in ('firmware', 'webos'):
        value = device[field]
        if not isinstance(value, str) or (value and not re.fullmatch(r'\d+(?:\.\d+)+', value)):
            raise WebOSError('Invalid version in webOS profile')
    for section, fields in {'apps': ['hide', 'keep', 'review'], 'launcher': ['order'],
                            'services': ['disable', 'review']}.items():
        block = data.setdefault(section, {})
        _keys(block, fields)
        for field in fields:
            values = block.setdefault(field, [])
            if not isinstance(values, list):
                raise WebOSError('webOS decisions must be lists of identifiers')
            for value in values:
                identifier(value)
            if len(values) != len(set(values)):
                raise WebOSError('Duplicate webOS profile identifiers')
    if set(data['apps']['hide']) & set(data['apps']['keep']):
        raise WebOSError('An app cannot be both hidden and kept')
    return data


def initialize(discovery_path, vendor, model, name, root='profiles'):
    try:
        data = json.loads(Path(discovery_path).read_text(encoding='utf-8'))
        device = data['device']
        if data.get('platform') != 'webos' or vendor.lower() != 'lg' or device['model'] != model:
            raise WebOSError('Profile vendor/model must match webOS discovery')
        review = sorted({identifier(app['id']) for app in data['apps']})
        values = {key: device[key] for key in ('manufacturer', 'model', 'firmware', 'webos')}
    except (OSError, KeyError, TypeError, ValueError):
        raise WebOSError('Invalid webOS discovery for profile initialization') from None
    folder = Path(root) / 'lg' / re.sub(r'[^a-z0-9._-]', '-', identifier(model).lower())
    text = '\n'.join([
        'schema_version = 1', 'platform = "webos"', f'name = {json.dumps(name)}',
        'status = "candidate"', '', '[device]',
        *(f'{key} = {json.dumps(value)}' for key, value in values.items()),
        '', '[apps]', 'hide = []', 'keep = []', f'review = {json.dumps(review)}',
        '', '[launcher]', 'order = []', '', '[services]', 'disable = []', 'review = []', ''])
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'profile.toml'
    # Exclusive creation prevents overwriting an existing researched profile.
    with path.open('x', encoding='utf-8') as output:
        output.write(text)
    notes = folder / 'NOTES.md'
    if not notes.exists():
        notes.write_text('# webOS evidence\n\nCandidate from read-only discovery. No TV validation yet.\n'
                         'Record access, identity, launcher contracts, operator tests, recovery and reboot results here.\n',
                         encoding='utf-8')
    return path
