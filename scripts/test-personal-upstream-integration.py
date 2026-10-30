#!/usr/bin/env python3
"""Keep upstream additions wired through the personal lazy-loading split."""
from pathlib import Path
import re
import unittest

SHELL = Path(__file__).resolve().parents[1] / "dots/.config/quickshell/ii"


class PersonalUpstreamIntegrationTests(unittest.TestCase):
    def test_upstream_services_keep_event_loop_scheduling(self):
        shell = (SHELL / "shell.qml").read_text()
        queue = shell.split("deferredServiceSteps = [", 1)[1].split("\n        ];", 1)[0]
        self.assertIn("perfAutoWire.running = true", queue)
        self.assertIn("gamesAutoWired", queue)
        self.assertIn("IiIconPack.busy", queue)
        self.assertEqual(shell.count("id: perfAutoWire"), 1)
        self.assertIn("step();", shell)

    def test_timer_alert_moves_to_the_deferred_family(self):
        first = (SHELL / "panelFamilies/IllogicalImpulseFamily.qml").read_text()
        deferred = (SHELL / "panelFamilies/IllogicalImpulseDeferredFamily.qml").read_text()
        self.assertNotIn("timerAlertPopup/TimerAlertPopup.qml", first)
        self.assertIn("timerAlertPopup/TimerAlertPopup.qml", deferred)
        self.assertIn("TimerService.alert !== null", deferred)
        self.assertIn("IllogicalImpulseDeferredFamily.qml", first)

    def test_sidebar_hosts_keep_upstream_float_geometry(self):
        top = (SHELL / "modules/ii/topLayer/TopLayerPanel.qml").read_text()
        for side, edge in (("left", "right"), ("right", "left")):
            block = top.split(f"id: {side}SidebarContentLoader", 1)[1].split("onLoaded:", 1)[0]
            self.assertIn('Qt.resolvedUrl("SidebarContentHost.qml")', block)
            self.assertIn("wantedContentKind", block)
            self.assertIn(f"{edge}: parent.{edge}", block)
            self.assertIn(f"topPanel.{side}ContentWidth", block)
            self.assertIn(f"GlobalStates.{side}SidebarAnimating && topPanel.floatSidebarCards", block)
            self.assertNotRegex(block, re.compile(r"^(?:<{7}|={7}|>{7}|\|{7})", re.M))


if __name__ == "__main__":
    unittest.main()
