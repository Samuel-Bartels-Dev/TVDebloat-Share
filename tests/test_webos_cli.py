import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_webos import FakeTV
from tvdebloat.cli import main
from tvdebloat.profile import load, ProfileError
from tvdebloat import webos


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def call(self, args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            status = main(args)
        return status, output.getvalue()

    def test_webos_preflight_never_constructs_adb_client(self):
        with patch('tvdebloat.cli.Client') as adb, patch('tvdebloat.webos_cli.SSHClient', return_value=FakeTV()):
            status, output = self.call(['--platform', 'webos', '--host', 'tv.example', 'preflight'])
        adb.assert_not_called()
        self.assertEqual(status, 0)
        self.assertFalse(json.loads(output)['ready_for_write'])

    def test_cross_platform_profile_rejected_before_either_transport(self):
        for requested, file_platform in [('android', 'webos'), ('webos', 'android')]:
            profile = self.root / 'profile.toml'
            profile.write_text(f'platform = "{file_platform}"\n', encoding='utf-8')
            with patch('tvdebloat.cli.Client') as adb, patch('tvdebloat.webos_cli.SSHClient') as ssh:
                status, output = self.call(['--platform', requested, '--host', 'tv.example', 'preflight', str(profile)])
            self.assertEqual(status, 1)
            adb.assert_not_called()
            ssh.assert_not_called()
            self.assertIn('platform', output.lower())

    def test_android_profile_loader_rejects_webos_profile(self):
        profile = self.root / 'profile.toml'
        profile.write_text('platform = "webos"\n', encoding='utf-8')
        with self.assertRaises(ProfileError):
            load(profile)

    def test_unsupported_command_rejected_before_connecting(self):
        with patch('tvdebloat.webos_cli.SSHClient') as ssh:
            status, output = self.call(['--platform', 'webos', '--host', 'tv.example', 'privacy'])
        self.assertEqual(status, 1)
        ssh.assert_not_called()
        self.assertIn('not supported', output)

    def test_ssh_failure_preflight_nonzero_without_traceback(self):
        with patch('tvdebloat.webos_cli.SSHClient') as ssh:
            ssh.return_value.read.side_effect = webos.WebOSError('SSH read failed')
            status, output = self.call(['--platform', 'webos', '--host', 'tv.example', 'preflight'])
        self.assertEqual(status, 1)
        self.assertFalse(json.loads(output)['ready'])
        self.assertNotIn('Traceback', output)

    def test_discovery_out_and_local_profile_init_without_host(self):
        source = self.root / 'discovery.json'
        with patch('tvdebloat.webos_cli.SSHClient', return_value=FakeTV()):
            status, _ = self.call(['--platform', 'webos', '--host', 'tv.example', 'discover', '--out', str(source)])
        self.assertEqual(status, 0)
        with patch('tvdebloat.webos_cli.initialize', return_value=self.root / 'profile.toml') as initialize, patch('tvdebloat.webos_cli.SSHClient') as ssh:
            status, _ = self.call(['--platform', 'webos', 'profile-init', '--name', 'Test', '--vendor', 'lg',
                                  '--model', 'SyntheticPanel', '--from', str(source)])
        self.assertEqual(status, 0)
        initialize.assert_called_once()
        ssh.assert_not_called()

    def test_android_profile_init_refuses_webos_discovery(self):
        source = self.root / 'webos.json'
        source.write_text(json.dumps(webos.discover(FakeTV())), encoding='utf-8')
        status, output = self.call(['profile-init', '--name', 'Test', '--vendor', 'lg', '--model', 'SyntheticPanel', '--from', str(source)])
        self.assertEqual(status, 1)
        self.assertIn('platform', output.lower())

    def test_non_object_discovery_is_a_clean_cli_error(self):
        source = self.root / 'bad.json'
        source.write_text('[]', encoding='utf-8')
        status, output = self.call(['--platform', 'webos', 'profile-init', '--name', 'Test',
                                   '--vendor', 'lg', '--model', 'SyntheticPanel', '--from', str(source)])
        self.assertEqual(status, 1)
        self.assertNotIn('Traceback', output)

    def test_existing_profile_is_a_clean_cli_error(self):
        source = self.root / 'discovery.json'
        source.write_text(json.dumps(webos.discover(FakeTV())), encoding='utf-8')
        with patch('tvdebloat.webos_cli.initialize', side_effect=FileExistsError('PRIVATE path')):
            status, output = self.call(['--platform', 'webos', 'profile-init', '--name', 'Test',
                                       '--vendor', 'lg', '--model', 'SyntheticPanel', '--from', str(source)])
        self.assertEqual(status, 1)
        self.assertNotIn('PRIVATE', output)

    def test_android_missing_profile_remains_a_clean_error(self):
        status, output = self.call(['preview', str(self.root / 'missing.toml')])
        self.assertEqual(status, 1)
        self.assertIn('error:', output)


if __name__ == '__main__':
    unittest.main()
