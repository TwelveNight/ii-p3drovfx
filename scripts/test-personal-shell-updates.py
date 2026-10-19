#!/usr/bin/env python3
"""Execute the real QML consumer with private-branch update reports."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent

class UpdateConsumerTests(unittest.TestCase):
    def test_personal_ahead_is_current_and_upstream_behind_is_an_update(self):
        text = (ROOT / 'dots/.config/quickshell/ii/services/ShellUpdates.qml').read_text()
        text = text[text.index('id: remoteHeadProc'):]
        start = text.index('onStreamFinished: {') + len('onStreamFinished: {')
        depth, end = 1, start
        while depth:
            depth += (text[end] == '{') - (text[end] == '}')
            end += 1
        callback = text[start:end-1]
        script = '''
const assert = require('node:assert/strict');
const consume = new Function('root', 'text', 'compareProc', process.argv[1]);
for (const [response, behind, remote] of [
    [JSON.stringify({status:'current', behind:0, remote_commit:'upstream-sha'}), 0, 'private-commit'],
    [JSON.stringify({status:'behind', behind:7, remote_commit:'new-upstream'}), 7, 'new-upstream'],
    ['', 0, '']]) {
    let finished = 0;
    const root = {personalOverlay:true, activeCommit:'private-commit', commits:[],
                  _finishCheck: () => finished++};
    const githubCompare = {running:false};
    consume(root, response, githubCompare);
    assert.equal(root.commitsBehind, behind);
    assert.equal(root.remoteCommit, remote);
    assert.equal(root.probed, true);
    assert.equal(finished, 1);
    assert.equal(githubCompare.running, false, 'private commits must not be queried via GitHub compare');
}
'''
        subprocess.run(['node', '-e', script, callback], check=True, text=True, capture_output=True)

if __name__ == '__main__':
    unittest.main()
