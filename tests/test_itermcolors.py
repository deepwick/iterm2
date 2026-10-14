import plistlib
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

from deepwick_spec.check_port import check_port
from deepwick_spec.palette import ANSI_SLOTS, load_palette

REPO = Path(__file__).resolve().parents[1]
PALETTE = load_palette()
C = PALETTE.colors
sys.path.insert(0, str(REPO))
FILE = REPO / "Deepwick.itermcolors"
KEYS = {f"Ansi {i} Color" for i in range(16)} | {
    "Foreground Color", "Background Color", "Bold Color", "Link Color", "Match Background Color",
    "Selection Color", "Selected Text Color", "Cursor Color", "Cursor Text Color", "Tab Color",
    "Underline Color", "Cursor Guide Color", "Badge Color",
}
COMPONENTS = {"Red Component", "Green Component", "Blue Component", "Alpha Component", "Color Space"}
ROLES = {
    "Background Color": "background", "Foreground Color": "foreground", "Bold Color": "foreground",
    "Cursor Color": "foreground", "Cursor Text Color": "background", "Selection Color": "selection",
    "Selected Text Color": "foreground", "Link Color": "orange", "Underline Color": "blue",
    "Match Background Color": "gold", "Tab Color": "surface", "Cursor Guide Color": "surface", "Badge Color": "blue",
}


def presets():
    assert FILE.is_file(), "Deepwick.itermcolors missing"
    with FILE.open("rb") as f:
        return plistlib.load(f)


def float32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def as_hex(entry, rounding):
    channels = (entry[f"{c} Component"] for c in ("Red", "Green", "Blue"))
    return "#" + "".join(f"{rounding(float32(v) * 255):02x}" for v in channels)


def expected_hex():
    result = {key: C[name] for key, name in ROLES.items()}
    for i, slot in enumerate(ANSI_SLOTS):
        result[f"Ansi {i} Color"] = PALETTE.ansi[slot]
        result[f"Ansi {i + 8} Color"] = PALETTE.ansi["bright" + slot.capitalize()]
    return result


def test_exact_key_set():
    assert set(presets()) == KEYS


def test_entries_are_srgb_with_alpha():
    for key, entry in presets().items():
        assert set(entry) == COMPONENTS, key
        assert entry["Color Space"] == "sRGB", key


def test_colors_round_trip_to_palette():
    p = presets()
    for key, hex_color in expected_hex().items():
        # iTerm2 reads components as 32-bit floats and truncates when converting to hex.
        assert as_hex(p[key], int) == hex_color.lower(), key
        assert as_hex(p[key], round) == hex_color.lower(), key


def test_alphas():
    p = presets()
    assert p["Cursor Guide Color"]["Alpha Component"] == 0.25
    assert p["Badge Color"]["Alpha Component"] == 0.5
    others = KEYS - {"Cursor Guide Color", "Badge Color"}
    assert all(p[key]["Alpha Component"] == 1.0 for key in others)


def test_committed_file_matches_generator():
    import generate

    assert presets() == generate.presets(PALETTE)


@pytest.mark.skipif(shutil.which("xmllint") is None, reason="requires xmllint")
def test_well_formed_xml():
    subprocess.run(["xmllint", "--noout", "--nonet", str(FILE)], check=True)


def test_port_conventions():
    assert check_port(REPO, PALETTE.allowed_hex()) == []
