"""Write Deepwick.itermcolors from the Deepwick palette.

Run from this directory: PYTHONPATH=../spec python3 generate.py
"""
import plistlib
from pathlib import Path

from deepwick_spec.palette import ANSI_SLOTS, Palette, load_palette

OUT = Path(__file__).with_name("Deepwick.itermcolors")
ROLES = {
    "Background Color": "background", "Foreground Color": "foreground", "Bold Color": "foreground",
    "Cursor Color": "foreground", "Cursor Text Color": "background", "Selection Color": "selection",
    "Selected Text Color": "foreground", "Link Color": "orange", "Underline Color": "blue",
    "Match Background Color": "gold", "Tab Color": "surface", "Cursor Guide Color": "surface", "Badge Color": "blue",
}
ALPHA = {"Cursor Guide Color": 0.25, "Badge Color": 0.5}


def entry(hex_color: str, alpha: float = 1.0) -> dict:
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return {"Alpha Component": alpha, "Blue Component": b, "Color Space": "sRGB", "Green Component": g, "Red Component": r}


def presets(palette: Palette) -> dict:
    result = {}
    for i, slot in enumerate(ANSI_SLOTS):
        result[f"Ansi {i} Color"] = entry(palette.ansi[slot])
        result[f"Ansi {i + 8} Color"] = entry(palette.ansi["bright" + slot.capitalize()])
    for key, name in ROLES.items():
        result[key] = entry(palette.colors[name], ALPHA.get(key, 1.0))
    return result


if __name__ == "__main__":
    OUT.write_bytes(plistlib.dumps(presets(load_palette()), sort_keys=True))
    print(f"wrote {OUT.name}")
