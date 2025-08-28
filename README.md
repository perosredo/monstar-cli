# Monstar CLI 🖥️

**GNOME Display Layout Manager CLI** - Save, manage, and quickly switch between multiple monitor configurations with integrated Tiling Shell support.

## Features

- 🖥️ **Save/Load Display Layouts** - Capture your current monitor setup, including on/off states, and switch between them instantly
- 🎨 **Tiling Shell Integration** - Saves and restores Tiling Shell window layouts with each display profile
- ⚡ **Numbered Shortcuts** - Quick access with `monstar 1`, `monstar 2`, etc.
- 🚀 **Boot Persistence** - Auto-restore your preferred layout on login with `--autostart` toggle
- 🔧 **Monitor Name Fix** - Automatically refreshes monitor names after configuration changes
- 💻 **Pure CLI** - Lightweight command-line only tool

## Installation

```bash
pip install monstar-cli
```

Or install with pipx for isolated environment:
```bash
pipx install monstar-cli
```

## Usage

### Command Line
```bash
# Save current display configuration (including Tiling Shell layouts)
monstar save work

# Load a saved layout
monstar load work

# Remove a layout
monstar remove old-layout

# List saved layouts
monstar list

# Set up numbered shortcuts
monstar shortcut work 1
monstar shortcut play 2

# Quick switch using shortcuts
monstar 1  # Loads 'work' layout
monstar 2  # Loads 'play' layout

# List all shortcuts
monstar shortcuts

# Enable auto-restore on login (toggles on/off)
monstar --autostart

# Show help
monstar --help
```

## Requirements

- **Linux** with GNOME desktop environment
- **Python 3.6+**
- **PyGObject** (for DBus access)

On Fedora:
```bash
sudo dnf install python3-gobject
```

## Configuration

Layouts are stored in `~/.config/monstar/` as JSON files.

### Layout Files Include:
- Display configuration (monitor positions, scales, resolutions, on/off states, rotations)
- Tiling Shell window layouts (if Tiling Shell extension is installed)
- Custom shortcuts mapping

### Auto-Restore on Login
When `--autostart` is enabled, Monstar creates `~/.config/autostart/monstar-restore.desktop` that automatically restores your last used layout when you log in. The desktop file updates every time you switch layouts, so it always restores your most recent configuration.

### Tiling Shell Integration
If you have Tiling Shell extension installed, Monstar will:
- Save your Tiling Shell layouts with each display profile
- Restore the correct window tiling when switching displays
- Automatically reload Tiling Shell to fix monitor names

## Uninstall

```bash
pip3 uninstall monstar-cli
rm -rf ~/.config/monstar/
```

## How It Works

Monstar uses GNOME's `org.gnome.Mutter.DisplayConfig` DBus interface to:
1. **Capture** current monitor positions, scales, rotations, and modes
2. **Store** configurations as JSON files with human-readable names  
3. **Apply** saved layouts by reconstructing the exact display setup
4. **Backup** Tiling Shell window layouts from dconf settings
5. **Restore** complete workspace configurations including window tiling

## Known Issues & Fixes

### Monitor Names Reset
When switching display configurations, GNOME sometimes resets monitor names to generic "Monitor 1", "Monitor 2", etc. Monstar automatically reloads the Tiling Shell extension after each layout change to restore proper monitor names.


## Quick Start Guide

1. **Set up your displays** the way you like for work
2. **Save the layout**: `monstar save work`
3. **Create a shortcut**: `monstar shortcut work 1`
4. **Enable autostart**: `monstar --autostart`
5. **Switch displays** for gaming/relaxing
6. **Save another layout**: `monstar save play`
7. **Create another shortcut**: `monstar shortcut play 2`
8. **Quick switch** anytime: `monstar 1` for work, `monstar 2` for play
9. **Your layouts persist** across reboots automatically!

## Contributing

Contributions welcome! This started as a simple script to manage multi-monitor setups and grew into a proper application.

### Development

```bash
# Install in development mode
pip3 install -e .

# Run from source
python3 -m monstar.cli list

# Test basic functionality
monstar list
```

### Recent Updates
- Added `--autostart` toggle for boot persistence - no more manual layout restoration!
- Added Tiling Shell integration for complete workspace management
- Implemented numbered shortcuts for quick access
- Fixed monitor name reset issue with automatic extension reload
- Added remove command for layout management

## License

MIT License

## Why "Monstar"?

Because it manages your **mon**itor setup like a **star** ⭐ - and it sounds way cooler than "display-manager-thing".

---

*Built for people who are tired of manually repositioning windows every time they dock/undock their laptop.*

**Note:** This project was 100% developed by Claude Code with micromanagement from ps.
