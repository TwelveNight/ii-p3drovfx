#!/usr/bin/env python3
"""Check the combined upstream update probe and personal session boundary."""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PersonalUpdateMergeTests(unittest.TestCase):
    def test_update_probe_keeps_personal_route_and_stable_cwd(self):
        text = (ROOT / 'dots/.config/quickshell/ii/services/ShellUpdates.qml').read_text()
        probe = text.split('id: remoteHeadProc', 1)[1].split('stdout: StdioCollector', 1)[0]
        self.assertIn('workingDirectory: root.stateDir', probe)
        self.assertIn('command: root.personalOverlay', probe)
        self.assertIn('"check", "hyprland-ii", "--json"', probe)

    def test_idle_dedup_preserves_personal_session_ownership(self):
        text = (ROOT / 'dots/.config/hypr/hyprland/execs.lua').read_text()
        commands = re.findall(r'hl\.exec_cmd\("(systemctl[^"\n]+hypridle)"\)', text)
        self.assertEqual(len(commands), 1)
        self.assertNotIn('dbus-update-activation-environment --all', text)
        self.assertNotIn('systemctl --user import-environment', text)
        self.assertNotIn('__restore_video_wallpaper.sh', text)
        personal = (ROOT / 'dots/.config/hypr/custom/execs.lua').read_text()
        self.assertIn('require("custom.inir-session")', personal)
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            log = directory / 'idle.log'
            for tool, body in {
                'systemctl': '#!/bin/sh\nexit "$SERVICE_ENABLED"\n',
                'hypridle': '#!/bin/sh\nprintf "idle\\n" >> "$IDLE_LOG"\n',
            }.items():
                path = directory / tool
                path.write_text(body)
                path.chmod(0o700)
            env = dict(os.environ, PATH=str(directory), IDLE_LOG=str(log))
            subprocess.run(['/bin/sh', '-c', commands[0]], env=dict(env, SERVICE_ENABLED='0'), check=True)
            self.assertFalse(log.exists())
            subprocess.run(['/bin/sh', '-c', commands[0]], env=dict(env, SERVICE_ENABLED='1'), check=True)
            self.assertEqual(log.read_text(), 'idle\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
