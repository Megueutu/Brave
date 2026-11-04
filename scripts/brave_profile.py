"""Export and apply the tracked Brave appearance settings (stdlib only)."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "preferences.json"
BACKGROUNDS = ROOT / "assets" / "backgrounds"

# dotted paths inside the profile's Preferences file that are versioned
TRACKED = [
    "bookmark_bar.show_on_all_tabs",
    "brave.new_tab_page.background",
    "brave.new_tab_page.custom_background_image_list",
    "brave.new_tab_page.show_brave_news",
    "brave.new_tab_page.show_brave_vpn",
    "brave.new_tab_page.show_clock",
    "brave.new_tab_page.show_rewards",
    "brave.new_tab_page.show_stats",
    "brave.new_tab_page.show_together",
]


def default_profile():
    if sys.platform == "win32":
        base = Path(os.environ["LOCALAPPDATA"]) / "BraveSoftware/Brave-Browser/User Data"
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser"
    else:
        base = Path.home() / ".config/BraveSoftware/Brave-Browser"
    return base / "Default"


def brave_running():
    if sys.platform == "win32":
        cmd = ["tasklist", "/FI", "IMAGENAME eq brave.exe", "/NH"]
        return "brave.exe" in subprocess.run(cmd, capture_output=True, text=True).stdout
    return subprocess.run(["pgrep", "-x", "brave|Brave Browser"], capture_output=True).returncode == 0


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def get_path(data, dotted):
    for key in dotted.split("."):
        if not isinstance(data, dict) or key not in data:
            return None, False
        data = data[key]
    return data, True


def set_path(data, dotted, value):
    *parents, last = dotted.split(".")
    for key in parents:
        data = data.setdefault(key, {})
    data[last] = value


def merge(target, source):
    for key, value in source.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge(target[key], value)
        else:
            target[key] = value


def export_profile(profile):
    prefs = read_json(profile / "Preferences")
    out = {}
    for dotted in TRACKED:
        value, found = get_path(prefs, dotted)
        if found:
            set_path(out, dotted, value)
    write_json(CONFIG, out)
    images = profile / "sanitized_background_images"
    for name in get_path(out, "brave.new_tab_page.custom_background_image_list")[0] or []:
        if (images / name).is_file():
            BACKGROUNDS.mkdir(parents=True, exist_ok=True)
            shutil.copy2(images / name, BACKGROUNDS / name)
    print(f"exported to {CONFIG}")


def apply_profile(profile):
    if brave_running():
        sys.exit("close brave before applying (it rewrites Preferences on exit)")
    prefs_file = profile / "Preferences"
    prefs = read_json(prefs_file) if prefs_file.exists() else {}
    if prefs_file.exists():
        shutil.copy2(prefs_file, prefs_file.with_name("Preferences.bak"))
    config = read_json(CONFIG)
    merge(prefs, config)
    write_json(prefs_file, prefs)
    names = get_path(config, "brave.new_tab_page.custom_background_image_list")[0] or []
    images = profile / "sanitized_background_images"
    images.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copy2(BACKGROUNDS / name, images / name)
    print(f"applied to {profile}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["export", "apply"])
    parser.add_argument("--profile", type=Path, default=default_profile(), help="Brave profile folder")
    args = parser.parse_args()
    (export_profile if args.action == "export" else apply_profile)(args.profile)


if __name__ == "__main__":
    main()
