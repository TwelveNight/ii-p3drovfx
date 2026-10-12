#!/usr/bin/env python3
"""Exercise both file installers against disposable sibling shell directories."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

parser = argparse.ArgumentParser()
parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
args, remaining = parser.parse_known_args()
REPO = args.repo.resolve()

class QuickshellInstallBoundary(unittest.TestCase):
    def exercise(self, experimental):
        with tempfile.TemporaryDirectory(prefix='ii-install-boundary-') as tmp:
            root = Path(tmp)
            source = root / 'dots/.config/quickshell/ii'
            target = root / 'config/quickshell'
            source.mkdir(parents=True)
            (source / 'shell.qml').write_text('new II shell\n')
            (target / 'ii').mkdir(parents=True)
            (target / 'ii/shell.qml').write_text('previous II shell configuration\n')
            (target / 'ii/obsolete.qml').write_text('obsolete\n')
            for name in ('inir', 'another-shell'):
                (target / name / 'scripts').mkdir(parents=True)
                (target / name / 'shell.qml').write_text(name + '\n')
                (target / name / 'scripts/helper.sh').write_text('preserve me\n')
            (target / 'shell-link').symlink_to('another-shell', target_is_directory=True)
            (target / 'shared.txt').write_text('shared metadata\n')
            before = self.siblings(target)
            # Use the installer's real destructive-sync primitive, without
            # running its package, backup, font or compositor reload stages.
            code = (REPO / 'sdata/subcmd-install/3.files.sh').read_text()
            start = code.index('rsync_dir__sync(){')
            end = code.index('rsync_dir__sync_exclude(){', start)
            primitive = code[start:end]
            harness = '''set -euo pipefail
x(){ "$@"; }
v(){ "$@"; }
warning_overwrite(){ :; }
install_file(){ :; }
install_dir__sync(){ rsync_dir__sync "$@"; }
SKIP_MISCCONF=true
SKIP_QUICKSHELL=false
SKIP_FISH=true
SKIP_FONTCONFIG=true
SKIP_HYPRLAND=true
ask=false
FONTSET_DIR_NAME=
'''+primitive+'\nsource "$1"\n'
            suffix = 'exp' if experimental else 'legacy'
            script = REPO / f'sdata/subcmd-install/3.files-{suffix}.sh'
            if experimental:
                directory = root / 'sdata/subcmd-install'
                directory.mkdir(parents=True)
                shutil.copyfile(REPO / 'sdata/subcmd-install/3.files-exp.yaml', directory / '3.files-exp.yaml')
            env = dict(os.environ, XDG_CONFIG_HOME=str(root / 'config'),
                       XDG_DATA_HOME=str(root / 'data'), INSTALLED_LISTFILE=str(root / 'installed'))
            for _ in range(2):
                result = subprocess.run(['bash', '-c', harness, 'test', str(script)],
                                        cwd=root, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.siblings(target), before, 'Installer deleted or changed a sibling shell')
                self.assertEqual((target / 'ii/shell.qml').read_text(), 'new II shell\n')
                self.assertFalse((target / 'ii/obsolete.qml').exists(), 'Obsolete II files must still be removed')

    @staticmethod
    def siblings(target):
        return {p.relative_to(target).as_posix(): ('link', os.readlink(p)) if p.is_symlink()
                else ('file', p.read_bytes()) if p.is_file() else ('directory',)
                for p in target.rglob('*') if p.relative_to(target).parts[0] != 'ii'}

    def test_legacy_preserves_siblings(self):
        self.exercise(False)

    def test_experimental_preserves_siblings(self):
        self.exercise(True)

if __name__ == '__main__':
    unittest.main(argv=[__file__, *remaining])
