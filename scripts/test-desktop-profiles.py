#!/usr/bin/env python3
"""Run profile installation and backup primitives only in temporary homes."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DesktopProfileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='hypr-profile-test-')
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.config = self.home / '.config'
        self.profile = self.config / 'desktop-profiles/hyprland-ii/hypr'
        self.profile.mkdir(parents=True)
        (self.profile / 'hyprland.lua').write_text('-- previous desktop\n')
        (self.profile / 'custom').mkdir()
        (self.profile / 'custom/remote.lua').write_text('-- personal remote policy\n')
        (self.config / 'hypr').symlink_to('desktop-profiles/hyprland-ii/hypr')
        (self.config / 'desktop-profiles/profiles.json').write_text('{}')
        for name in ('inir', 'nyxuri'):
            other = self.config / 'desktop-profiles' / name / 'niri'
            other.mkdir(parents=True)
            (other / 'remote-panel__custom__.kdl').write_text(name + ' sentinel\n')
        manager = self.home / '.local/bin/desktop-profile'
        manager.parent.mkdir(parents=True)
        manager.write_text('''#!/bin/sh
[ "$1" = guard ] && [ "$2" = hyprland-ii ] || exit 2
[ "$(realpath "$HOME/.config/hypr")" = "$HOME/.config/desktop-profiles/hyprland-ii/hypr" ]
''')
        manager.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.config),
                        XDG_DATA_HOME=str(self.home / '.local/share'),
                        XDG_STATE_HOME=str(self.home / '.local/state'))

    def bash(self, code):
        return subprocess.run(['bash', '-euc', code], env=self.env, capture_output=True, text=True, cwd=self.home)

    def test_plain_update_uses_the_shared_personal_pipeline(self):
        helper = self.home / ".local/bin/desktop-update"
        helper.write_text('#!/bin/sh\nprintf "%s\\n" "$*"\n')
        helper.chmod(0o755)
        result = subprocess.run(['bash', str(ROOT / 'setup-ii-p3drovfx.sh'), 'update'], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'update hyprland-ii')

    def legacy_backup(self):
        code = (ROOT / 'sdata/lib/functions.sh').read_text()
        return code[code.index('function backup_clashing_targets(){'):code.index('function install_cmds(){')]

    def test_entrypoints_reject_another_profile_before_work(self):
        (self.config / 'hypr').unlink()
        (self.config / 'hypr').symlink_to('desktop-profiles/nyxuri/niri')
        for entry, arguments in (('setup', ['install']), ('setup-ii-p3drovfx.sh', ['update', '--yes'])):
            with self.subTest(entry=entry):
                result = subprocess.run(['bash', str(ROOT / entry), *arguments], env=self.env, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / '.local/share').exists())

    def test_legacy_snapshot_has_profile_contents_and_preserves_other_links(self):
        source = self.home / 'source'
        (source / 'hypr').mkdir(parents=True)
        (source / 'other-app').mkdir()
        outside = self.home / 'outside'
        outside.mkdir()
        (outside / 'settings').write_text('keep external settings\n')
        (self.config / 'other-app').symlink_to(outside)
        code = 'x(){ "$@"; }\n' + self.legacy_backup() + '\nbackup_clashing_targets "$HOME/source" "$XDG_CONFIG_HOME" "$HOME/backup"\n'
        result = self.bash(code)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.home / 'backup/hypr').is_symlink())
        self.assertEqual((self.home / 'backup/hypr/custom/remote.lua').read_bytes(), (self.profile / 'custom/remote.lua').read_bytes())
        self.assertTrue((self.home / 'backup/other-app').is_symlink())
        self.assertTrue((self.config / 'hypr').is_symlink())

    def test_legacy_wrong_profile_stops_before_snapshot(self):
        (self.home / 'source/hypr').mkdir(parents=True)
        (self.config / 'hypr').unlink()
        (self.config / 'hypr').symlink_to('desktop-profiles/nyxuri/niri')
        result = self.bash('x(){ "$@"; }\n' + self.legacy_backup() + '\nbackup_clashing_targets "$HOME/source" "$XDG_CONFIG_HOME" "$HOME/backup"\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / 'backup').exists())

    def modern_install(self, backup_failure=False):
        code = (ROOT / 'setup-ii-p3drovfx.sh').read_text()
        functions = code[code.index('backup_hyprland_config() {'):code.index('# apply_config <url>')]
        policy = '\n'.join(line for line in code.splitlines() if line.startswith(('HYPR_EXCLUDE_DIRS=(', 'HYPR_SEED_ONLY=(')))
        source = self.home / 'source/dots/.config/hypr'
        (source / 'custom').mkdir(parents=True)
        (source / 'hyprland.lua').write_text('-- new desktop\n')
        (source / 'custom/remote.lua').write_text('-- must not overwrite personal policy\n')
        if backup_failure:
            (self.home / 'backups').write_text('unwritable directory sentinel')
        harness = '''OPT_HYPR=true
OPT_BACKUP=true
OPT_RESTART=true
G_SEP=';'
G_ARROW='->'
ui_step(){ :; }
ui_ok(){ :; }
ui_note(){ :; }
ui_warn(){ :; }
ui_verbose(){ :; }
prune_backups(){ :; }
next_backup_dir(){ printf '%s' "$HOME/backups/${1}test"; }
'''+policy+'\n'+functions+'\ninstall_hypr_config "$HOME/source"\n'
        return self.bash(harness)

    def test_modern_install_snapshots_entity_and_keeps_personal_remote_policy(self):
        result = self.modern_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / 'backups/hyprland_test/hyprland.lua').read_text(), '-- previous desktop\n')
        self.assertEqual((self.profile / 'hyprland.lua').read_text(), '-- new desktop\n')
        self.assertEqual((self.profile / 'custom/remote.lua').read_text(), '-- personal remote policy\n')
        self.assertTrue((self.config / 'hypr').is_symlink())
        for name in ('inir', 'nyxuri'):
            self.assertEqual((self.config / 'desktop-profiles' / name / 'niri/remote-panel__custom__.kdl').read_text(), name + ' sentinel\n')

    def test_modern_backup_failure_stops_before_install(self):
        result = self.modern_install(backup_failure=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.profile / 'hyprland.lua').read_text(), '-- previous desktop\n')


if __name__ == '__main__':
    unittest.main()
