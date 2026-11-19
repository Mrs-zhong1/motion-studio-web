import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "generate_r26_local_pilot.py"
SPEC = importlib.util.spec_from_file_location("r26_local_pilot", SCRIPT)
PILOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PILOT)


class LocalPilotTests(unittest.TestCase):
    def test_storyboard_contains_four_representative_scenes(self):
        rows = PILOT.load_scenes(PILOT.DEFAULT_BOARD)
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            [(row["template"], row["chapter"]) for row in rows],
            PILOT.SCENES,
        )

    def test_both_candidates_are_apache_licensed_and_local(self):
        self.assertEqual(PILOT.MODELS["flux2"]["license"], "Apache-2.0")
        self.assertEqual(PILOT.MODELS["zimage"]["license"], "Apache-2.0")
        self.assertTrue(PILOT.MODELS["flux2"]["command"].startswith("mflux-"))
        self.assertTrue(PILOT.MODELS["zimage"]["command"].startswith("mflux-"))

    def test_prompt_is_single_scene_and_preserves_text_safe_zone(self):
        row = PILOT.load_scenes(PILOT.DEFAULT_BOARD)[0]
        prompt = PILOT.build_prompt(row)
        self.assertIn("ONE original", prompt)
        self.assertIn(row["textSafeZone"], prompt)
        self.assertIn("must NOT appear as rendered text", prompt)
        self.assertIn("Do not create a collage", prompt)

    def test_command_profiles_use_native_16_9_and_no_paid_api(self):
        row = PILOT.load_scenes(PILOT.DEFAULT_BOARD)[0]
        with tempfile.TemporaryDirectory() as temp:
            for model_key in ("flux2", "zimage"):
                command = PILOT.command_for(model_key, row, Path(temp), 26000)
                joined = " ".join(command)
                self.assertIn("--width 1792", joined)
                self.assertIn("--height 1008", joined)
                self.assertIn("--low-ram", command)
                self.assertIn("--quantize", command)
                self.assertIn("26000", command)
                self.assertNotIn("generativelanguage.googleapis.com", joined)
                self.assertNotIn("replicate.com", joined)
                self.assertNotIn("fal.ai", joined)
            flux2 = PILOT.command_for("flux2", row, Path(temp), 26000)
            self.assertIn("--small-text-encoder", flux2)
            self.assertIn("4", flux2)
            zimage = PILOT.command_for("zimage", row, Path(temp), 26000)
            self.assertIn("9", zimage)

    def test_default_run_is_dry_run_and_does_not_spawn_processes(self):
        with tempfile.TemporaryDirectory() as temp:
            args = Namespace(
                storyboard=PILOT.DEFAULT_BOARD,
                out=Path(temp) / "pilot",
                models="both",
                run=False,
            )
            original_preflight = PILOT.preflight
            original_run = PILOT.subprocess.run
            calls = []
            try:
                PILOT.preflight = lambda out_dir, models: {"test": "stubbed"}
                PILOT.subprocess.run = lambda *a, **k: calls.append(a)
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    status = PILOT.run(args)
                payload = json.loads(stream.getvalue().split(
                    "DRY RUN ONLY:", 1)[0])
            finally:
                PILOT.preflight = original_preflight
                PILOT.subprocess.run = original_run
            self.assertEqual(status, 0)
            self.assertEqual(payload["mode"], "DRY_RUN_NO_GENERATION")
            self.assertEqual(payload["plannedImages"], 8)
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
