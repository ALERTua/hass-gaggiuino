"""The manifest and the project pin the same version of the library."""

import json
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).parents[1]
LIBRARY = canonicalize_name("gaggiuino_api")


def _pin(requirements: list[str]) -> str:
    """Return the version specifier of the library in a list of requirements."""
    pins = [Requirement(r) for r in requirements]
    return next(str(p.specifier) for p in pins if canonicalize_name(p.name) == LIBRARY)


def test_manifest_and_pyproject_pin_one_version() -> None:
    """Home Assistant installs the version of the manifest; the tests use the pyproject one."""
    manifest = json.loads(
        (ROOT / "custom_components/gaggiuino/manifest.json").read_text(encoding="utf-8")
    )
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    manifest_pin = _pin(manifest["requirements"])

    assert manifest_pin.startswith("==")
    assert manifest_pin == _pin(pyproject["project"]["dependencies"])
