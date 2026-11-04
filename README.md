# Brave

Backup of my Brave appearance and navigation settings, plus the scripts to export and re-apply them.

## Structure

```
.
├── assets/backgrounds/   new tab page background images
├── config/preferences.json   tracked subset of the profile's Preferences
├── scripts/brave_profile.py  export and apply (python 3, stdlib only)
└── LICENSE               the unlicense
```

## Usage

Export the current profile into this repo (brave can stay open):

```bash
python scripts/brave_profile.py export
```

Apply the repo to a profile (close brave first, a `Preferences.bak` is created):

```bash
python scripts/brave_profile.py apply
```

Use `--profile <folder>` to target a profile other than `Default`.

## What is versioned

- new tab page: custom background and which widgets are shown
- bookmarks bar visibility

The tracked keys live in `TRACKED` inside `scripts/brave_profile.py`. Passwords, cookies, history and sync data are never versioned.
