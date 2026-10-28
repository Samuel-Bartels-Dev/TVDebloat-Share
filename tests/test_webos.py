import json
import subprocess
import unittest
from unittest.mock import patch

from tvdebloat import webos

HOST_KEY_LOG = b'debug1: Server host key: ssh-ed25519 SHA256:TestServerKey123\n'


class FakeTV:
    target_id = 'test-host-key-bound-target'
    move_verified = False

    def __init__(self):
        self.calls = []
        self.order = ['netflix_default', 'hdmi_one', 'browser_bookmark']
        self.responses = {
            webos.SYSTEM: {'returnValue': True, 'modelName': 'SyntheticPanel',
                           'firmwareVersion': '01.02.03', 'serialNumber': 'PRIVATE'},
            webos.OS: {'returnValue': True, 'platformVersion': '4.9.0'},
            webos.APPS: {'returnValue': True, 'apps': [
                {'id': 'netflix', 'version': '1', 'removable': True, 'title': 'PRIVATE'},
                {'id': 'com.webos.app.hdmi1', 'systemApp': True},
                {'id': 'com.webos.app.browser', 'systemApp': True}]},
        }

    def read(self, uri, payload=None):
        self.calls.append((uri, payload))
        if uri == webos.POINTS:
            apps = dict(zip(['netflix_default', 'hdmi_one', 'browser_bookmark'],
                            ['netflix', 'com.webos.app.hdmi1', 'com.webos.app.browser']))
            return {'returnValue': True, 'launchPoints': [
                {'launchPointId': p, 'id': apps.get(p, 'netflix'), 'params': {'token': 'PRIVATE'}}
                for p in self.order]}
        return self.responses[uri]


class DiscoveryTests(unittest.TestCase):
    def test_identity_versions_are_separate_and_private_fields_discarded(self):
        tv = FakeTV()
        result = webos.discover(tv)
        self.assertEqual(result['device']['webos'], '4.9.0')
        self.assertEqual(result['device']['firmware'], '01.02.03')
        self.assertEqual(len(result['launch_points']), 3)
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertFalse(result['capabilities']['move_launch_point'])
        self.assertEqual({x[0] for x in tv.calls}, webos.READ_URIS)

    def test_failed_or_missing_inventory_is_not_an_empty_success(self):
        for response in ({'returnValue': False}, {'returnValue': True},
                         {'returnValue': True, 'apps': 'bad'}):
            tv = FakeTV()
            tv.responses[webos.APPS] = response
            with self.assertRaises(webos.WebOSError):
                webos.discover(tv)

    def test_missing_platform_version_is_not_inferred_from_firmware(self):
        tv = FakeTV()
        tv.responses[webos.OS] = {'returnValue': False}
        result = webos.discover(tv)
        self.assertEqual(result['device']['webos'], '')
        self.assertFalse(result['ready_for_write'])

    def test_transport_identity_error_during_platform_read_is_not_swallowed(self):
        tv = FakeTV()
        read = tv.read
        def changed_key(uri, payload=None):
            if uri == webos.OS:
                raise webos.WebOSError('SSH server host key changed')
            return read(uri, payload)
        tv.read = changed_key
        with self.assertRaisesRegex(webos.WebOSError, 'host key'):
            webos.discover(tv)

    def test_duplicate_launch_point_ids_rejected_but_duplicate_apps_allowed(self):
        tv = FakeTV()
        tv.order += ['second_netflix']
        self.assertEqual(len(webos.discover(tv)['launch_points']), 4)
        tv.order += ['hdmi_one']
        with self.assertRaises(webos.WebOSError):
            webos.discover(tv)


class TransportTests(unittest.TestCase):
    def test_fixed_reads_strict_host_keys_and_no_forwarding(self):
        result = subprocess.CompletedProcess([], 0, b'{"returnValue":true}', HOST_KEY_LOG)
        with patch('tvdebloat.webos.subprocess.run', return_value=result) as run:
            client = webos.SSHClient('192.0.2.4')
            client.read(webos.APPS)
        command = run.call_args.args[0]
        self.assertIn('StrictHostKeyChecking=yes', command)
        self.assertIn('BatchMode=yes', command)
        self.assertIn('ForwardAgent=no', command)
        self.assertIn('ClearAllForwardings=yes', command)
        self.assertIn('timeout', run.call_args.kwargs)
        self.assertFalse(run.call_args.kwargs.get('shell', False))
        with self.assertRaises(webos.WebOSError):
            client.read('com.webos.applicationManager/removeLaunchPoint', {})
        with self.assertRaises(webos.WebOSError):
            client.read(webos.APPS, {'subscribe': True})

    def test_rejects_option_and_shell_injection(self):
        for host in ('-oProxyCommand=evil', 'host;reboot', 'user@host', 'host\nreboot'):
            with self.assertRaises(ValueError):
                webos.SSHClient(host)

    def test_errors_do_not_expose_remote_private_output(self):
        result = subprocess.CompletedProcess([], 1, b'', b'PRIVATE key path and serial')
        with patch('tvdebloat.webos.subprocess.run', return_value=result):
            with self.assertRaisesRegex(webos.WebOSError, 'SSH read failed') as error:
                webos.SSHClient('tv.example').read(webos.APPS)
        self.assertNotIn('PRIVATE', str(error.exception))

    def test_malformed_and_oversized_json_rejected(self):
        for output in (b'not json', b'[]', b'{}' * 600000):
            result = subprocess.CompletedProcess([], 0, output, HOST_KEY_LOG)
            with patch('tvdebloat.webos.subprocess.run', return_value=result):
                with self.assertRaises(webos.WebOSError):
                    webos.SSHClient('tv.example').read(webos.APPS)

    def test_discovery_from_actual_transport_response_shapes(self):
        outputs = [
            b'{"returnValue":true,"modelName":"SyntheticPanel","firmwareVersion":"01.02.03","serialNumber":"PRIVATE"}',
            b'webOS TV 4.9.0\nPRIVATE unrelated text\n',
            b'{"returnValue":true,"apps":[{"id":"netflix","removable":true}]}',
            b'{"returnValue":true,"launchPoints":[{"id":"netflix","launchPointId":"netflix_default","params":{"url":"PRIVATE"}}]}',
        ]
        responses = [subprocess.CompletedProcess([], 0, raw, HOST_KEY_LOG) for raw in outputs]
        with patch('tvdebloat.webos.subprocess.run', side_effect=responses):
            data = webos.discover(webos.SSHClient('tv.example'))
        self.assertEqual(data['device']['webos'], '4.9.0')
        self.assertEqual(data['launch_points'][0]['id'], 'netflix_default')
        self.assertNotIn('PRIVATE', json.dumps(data))

    def test_target_is_bound_to_observed_host_key_and_rotation_stops_reads(self):
        client = webos.SSHClient('tv.example')
        before = client.target_id
        first = subprocess.CompletedProcess([], 0, b'{"returnValue":true}', HOST_KEY_LOG)
        second = subprocess.CompletedProcess([], 0, b'{"returnValue":true}',
                                             HOST_KEY_LOG.replace(b'TestServerKey123', b'ReplacementKey456'))
        with patch('tvdebloat.webos.subprocess.run', side_effect=[first, second]):
            client.read(webos.APPS)
            self.assertNotEqual(before, client.target_id)
            with self.assertRaisesRegex(webos.WebOSError, 'host key'):
                client.read(webos.POINTS)

    def test_missing_host_key_evidence_fails_closed(self):
        result = subprocess.CompletedProcess([], 0, b'{"returnValue":true}', b'')
        with patch('tvdebloat.webos.subprocess.run', return_value=result):
            with self.assertRaisesRegex(webos.WebOSError, 'host key'):
                webos.SSHClient('tv.example').read(webos.APPS)


if __name__ == '__main__':
    unittest.main()
