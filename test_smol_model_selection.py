import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_SPEC = importlib.util.spec_from_file_location("smol", Path(__file__).with_name("smol.py"))
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
smol = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(smol)


class ModelSelectionTests(unittest.TestCase):
    def test_numeric_model_id_is_not_treated_as_menu_position(self):
        with tempfile.TemporaryDirectory() as directory:
            smol.CFG = str(Path(directory) / "smol.json")
            with (
                patch.object(smol, "conf", return_value={"base": "", "key": "", "model": ""}),
                patch.object(smol, "models", return_value=["model-a", "model-b", "2"]),
                patch.object(smol, "getpass", return_value=""),
                patch("builtins.input", side_effect=["https://example.test/v1", "2"]),
            ):
                smol.login()

            with Path(smol.CFG).open() as config_file:
                saved = json.load(config_file)
            self.assertEqual(saved["model"], "2")


if __name__ == "__main__":
    unittest.main()
