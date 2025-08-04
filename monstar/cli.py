#!/usr/bin/env python3

import gi
from gi.repository import Gio, GLib

import sys
import json
import os
import subprocess
import time

CONFIG_DIR = os.path.expanduser("~/.config/monstar/")

class DisplayManager:
    def __init__(self):
        self.proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION,
            Gio.DBusProxyFlags.NONE,
            None,
            'org.gnome.Mutter.DisplayConfig',
            '/org/gnome/Mutter/DisplayConfig',
            'org.gnome.Mutter.DisplayConfig',
            None)
        
    def get_current_modes(self):
        # Get available modes for monitors
        try:
            serial, monitors, logical_monitors, properties = self.proxy.GetCurrentState()
            print("Physical monitors and their modes:")
            for monitor in monitors:
                print(f"Monitor: {monitor}")
                if len(monitor) > 2:
                    modes = monitor[2]  # modes are typically the 3rd element
                    print(f"  Available modes: {modes}")
        except Exception as e:
            print(f"Error getting modes: {e}")
    
    def set_shortcut(self, layout_name, shortcut_num):
        """Set a numbered shortcut for a layout"""
        if not layout_name or not shortcut_num:
            print("Error: Please provide both layout name and shortcut number.")
            return
            
        # Verify the layout exists
        filepath = os.path.join(CONFIG_DIR, f"{layout_name}.json")
        if not os.path.exists(filepath):
            print(f"Error: Layout '{layout_name}' not found.")
            self.list_layouts()
            return
        
        # Load or create shortcuts file
        shortcuts_file = os.path.join(CONFIG_DIR, "shortcuts.json")
        shortcuts = {}
        if os.path.exists(shortcuts_file):
            try:
                with open(shortcuts_file, 'r') as f:
                    shortcuts = json.load(f)
            except:
                shortcuts = {}
        
        # Set the shortcut
        shortcuts[str(shortcut_num)] = layout_name
        
        # Save shortcuts
        try:
            with open(shortcuts_file, 'w') as f:
                json.dump(shortcuts, f, indent=2)
            print(f"Shortcut '{shortcut_num}' set to layout '{layout_name}'")
        except Exception as e:
            print(f"Error saving shortcut: {e}")
    
    def get_shortcut_layout(self, shortcut_num):
        """Get the layout name for a shortcut number"""
        shortcuts_file = os.path.join(CONFIG_DIR, "shortcuts.json")
        if not os.path.exists(shortcuts_file):
            return None
            
        try:
            with open(shortcuts_file, 'r') as f:
                shortcuts = json.load(f)
            return shortcuts.get(str(shortcut_num))
        except:
            return None
    
    def list_shortcuts(self):
        """List all shortcuts"""
        shortcuts_file = os.path.join(CONFIG_DIR, "shortcuts.json")
        if not os.path.exists(shortcuts_file):
            print("No shortcuts defined.")
            return
            
        try:
            with open(shortcuts_file, 'r') as f:
                shortcuts = json.load(f)
            
            if not shortcuts:
                print("No shortcuts defined.")
                return
                
            print("Shortcuts:")
            for num, layout in sorted(shortcuts.items()):
                print(f"  {num} -> {layout}")
        except Exception as e:
            print(f"Error reading shortcuts: {e}")
    
    def remove_layout(self, name):
        """Remove a saved layout"""
        if not name:
            print("Error: Please provide a layout name to remove.")
            return
        
        filepath = os.path.join(CONFIG_DIR, f"{name}.json")
        if not os.path.exists(filepath):
            print(f"Error: Layout '{name}' not found.")
            self.list_layouts()
            return
        
        try:
            os.remove(filepath)
            print(f"Layout '{name}' removed successfully.")
        except Exception as e:
            print(f"Error removing layout: {e}")
    
    def reload_tiling_shell(self):
        """Reload Tiling Shell extension to refresh monitor names"""
        try:
            # Check if Tiling Shell is installed and enabled
            result = subprocess.run(['gnome-extensions', 'info', 'tilingshell@ferrarodomenico.com'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # Extension not found
                return False
            
            if 'Enabled: Yes' not in result.stdout:
                # Extension not enabled
                return False
            
            print("Reloading Tiling Shell to refresh monitor names...")
            
            # Disable the extension
            subprocess.run(['gnome-extensions', 'disable', 'tilingshell@ferrarodomenico.com'], 
                         capture_output=True)
            
            # Small delay to ensure it's fully disabled
            time.sleep(0.5)
            
            # Re-enable the extension
            subprocess.run(['gnome-extensions', 'enable', 'tilingshell@ferrarodomenico.com'], 
                         capture_output=True)
            
            print("Tiling Shell reloaded.")
            return True
            
        except Exception as e:
            print(f"Warning: Could not reload Tiling Shell: {e}")
            return False

    def get_current_state(self):
        # FIX: The proxy call returns a tuple directly, no .unpack() needed.
        serial, physical_monitors, logical_monitors, properties = self.proxy.GetCurrentState()
        return logical_monitors

    def list_layouts(self):
        print("Available layouts:")
        if not os.path.exists(CONFIG_DIR):
            print("  (No layouts saved)")
            return
        for f in sorted(os.listdir(CONFIG_DIR)):
            if f.endswith(".json"):
                print(f"  - {f[:-5]}")

    def get_tiling_shell_config(self):
        """Get Tiling Shell configuration from dconf"""
        try:
            # Get layouts JSON
            result = subprocess.run(['dconf', 'read', '/org/gnome/shell/extensions/tilingshell/layouts-json'], 
                                  capture_output=True, text=True)
            layouts_json = result.stdout.strip() if result.returncode == 0 else None
            
            # Get selected layouts
            result = subprocess.run(['dconf', 'read', '/org/gnome/shell/extensions/tilingshell/selected-layouts'], 
                                  capture_output=True, text=True)
            selected_layouts = result.stdout.strip() if result.returncode == 0 else None
            
            return {
                'layouts_json': layouts_json,
                'selected_layouts': selected_layouts
            }
        except Exception as e:
            print(f"Warning: Could not backup Tiling Shell config: {e}")
            return None
    
    def restore_tiling_shell_config(self, config):
        """Restore Tiling Shell configuration to dconf"""
        try:
            if not config:
                return False
                
            # Restore layouts JSON
            if config.get('layouts_json'):
                subprocess.run(['dconf', 'write', '/org/gnome/shell/extensions/tilingshell/layouts-json', 
                              config['layouts_json']], capture_output=True)
            
            # Restore selected layouts
            if config.get('selected_layouts'):
                subprocess.run(['dconf', 'write', '/org/gnome/shell/extensions/tilingshell/selected-layouts', 
                              config['selected_layouts']], capture_output=True)
            
            return True
        except Exception as e:
            print(f"Warning: Could not restore Tiling Shell config: {e}")
            return False

    def save_layout(self, name):
        if not name:
            print("Error: Please provide a name for the layout.")
            return

        # FIX: The proxy call returns a tuple directly, no .unpack() needed.
        serial, physical_monitors, logical_monitors, properties = self.proxy.GetCurrentState()
        
        layout_to_save = []
        for monitor in logical_monitors:
            # Handle variable structure - GNOME version has 7 elements including properties dict
            if len(monitor) >= 7:
                x, y, scale, transform, primary, physical_spec, properties = monitor
            elif len(monitor) >= 6:
                x, y, scale, transform, primary, physical_spec = monitor[:6]
                properties = {}
            else:
                # Fallback for older GNOME versions
                x, y, scale, transform, primary = monitor[:5]
                physical_spec = []
                properties = {}
                
            # Extract monitor serial for reliable identification
            monitor_serial = None
            monitor_info = {}
            if physical_spec:
                # physical_spec is [connector, vendor, product, serial]
                connector, vendor, product, serial = physical_spec[0]
                monitor_serial = serial
                monitor_info = {
                    'vendor': vendor,
                    'product': product,
                    'serial': serial,
                    'connector': connector  # Keep for reference/UI
                }
            
            layout_to_save.append({
                'x': x,
                'y': y,
                'scale': scale,
                'transform': transform,
                'primary': primary,
                'monitor_serial': monitor_serial,
                'monitor_info': monitor_info,
                'properties': properties if 'properties' in locals() else {}
            })

        # Get Tiling Shell configuration
        tiling_shell_config = self.get_tiling_shell_config()
        
        # Combine display layout and Tiling Shell config
        complete_config = {
            'display_layout': layout_to_save,
            'tiling_shell': tiling_shell_config
        }

        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        filepath = os.path.join(CONFIG_DIR, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(complete_config, f, indent=2)
        print(f"Layout '{name}' saved.")
        if tiling_shell_config:
            print("  - Display configuration saved")
            print("  - Tiling Shell layouts saved")

    def load_layout(self, name):
        if not name:
            print("Error: Please provide a layout name to load.")
            self.list_layouts()
            return
        
        filepath = os.path.join(CONFIG_DIR, f"{name}.json")
        if not os.path.exists(filepath):
            print(f"Error: Layout '{name}' not found.")
            self.list_layouts()
            return

        with open(filepath, 'r') as f:
            saved_config = json.load(f)

        # Handle both old format (direct array) and new format (with tiling_shell)
        if isinstance(saved_config, list):
            # Old format - just display layout
            saved_layout_props = saved_config
            tiling_shell_config = None
        else:
            # New format - extract both
            saved_layout_props = saved_config.get('display_layout', [])
            tiling_shell_config = saved_config.get('tiling_shell', None)

        new_logical_monitors = []
        for props in saved_layout_props:
            # Reconstruct the variant structure for the method call
            # The variant signature for a logical monitor is (iiduba(ssa{sv}))
            # This includes x, y, scale, transform, primary, monitors (array with connector and props), properties
            # Convert our saved monitor format to the expected format
            # We need to look up the actual current mode for each monitor
            serial, physical_monitors, current_logical_monitors, properties = self.proxy.GetCurrentState()
            
            monitor_specs = []
            
            # Handle both old format (monitors array) and new format (monitor_serial)
            if 'monitor_serial' in props:
                # New serial-based format
                target_serial = props['monitor_serial']
                if not target_serial:
                    print(f"Warning: No serial found for monitor, skipping")
                    continue
                
                # Find current connector and mode for this serial
                current_connector = None
                current_mode = None
                
                for phys_mon in physical_monitors:
                    # phys_mon[0] is (connector, vendor, product, serial)
                    if len(phys_mon[0]) >= 4 and phys_mon[0][3] == target_serial:
                        current_connector = phys_mon[0][0]
                        
                        # Find the preferred or current mode
                        for mode in phys_mon[1]:  # modes list
                            mode_props = mode[5] if len(mode) > 5 else {}
                            if isinstance(mode_props, dict):
                                if mode_props.get('is-current') or mode_props.get('is-preferred'):
                                    current_mode = mode[0]
                                    break
                        if not current_mode and phys_mon[1]:
                            current_mode = phys_mon[1][0][0]  # fallback to first mode
                        break
                
                if not current_connector or not current_mode:
                    monitor_info = props.get('monitor_info', {})
                    display_name = f"{monitor_info.get('vendor', 'Unknown')} {monitor_info.get('product', 'Monitor')}"
                    print(f"Warning: Could not find monitor {display_name} (serial: {target_serial}), skipping")
                    continue
                
                # Use monitor_info if available, fallback to old format
                monitor_info = props.get('monitor_info', {})
                vendor = monitor_info.get('vendor', 'Unknown')
                product = monitor_info.get('product', 'Monitor')
                
                monitor_specs.append((
                    current_connector,
                    current_mode,
                    {
                        'vendor': GLib.Variant('s', vendor),
                        'product': GLib.Variant('s', product),
                        'serial': GLib.Variant('s', target_serial)
                    }
                ))
                
            else:
                # Legacy format - old layouts with connector-based matching
                for monitor in props['monitors']:
                    # Each monitor is [connector, vendor, product, serial]
                    connector = monitor[0]
                    
                    # Find the current mode for this connector from physical_monitors
                    current_mode = None
                    for phys_mon in physical_monitors:
                        if phys_mon[0][0] == connector:  # Match connector name
                            # Find the preferred or current mode
                            for mode in phys_mon[1]:  # modes list
                                mode_props = mode[5] if len(mode) > 5 else {}
                                if isinstance(mode_props, dict):
                                    if mode_props.get('is-current') or mode_props.get('is-preferred'):
                                        current_mode = mode[0]  # mode string like '2560x1600@60.000'
                                        break
                            if not current_mode and phys_mon[1]:
                                current_mode = phys_mon[1][0][0]  # fallback to first mode
                            break
                    
                    if not current_mode:
                        print(f"Warning: Could not find mode for {connector}, skipping")
                        continue
                        
                    monitor_specs.append((
                        connector,
                        current_mode,
                        {
                            'vendor': GLib.Variant('s', monitor[1]),
                            'product': GLib.Variant('s', monitor[2]), 
                            'serial': GLib.Variant('s', monitor[3])
                        }
                    ))
            
            monitor_variant = (
                props['x'],
                props['y'],
                props['scale'],
                props['transform'],
                props['primary'],
                monitor_specs
            )
            new_logical_monitors.append(monitor_variant)

        try:
            # The ApplyMonitorsConfig method signature is (uua(iiduba(ssa{sv}))a{sv})
            # where u=serial, u=method, a(...)=array of logical monitors, a{sv}=properties
            serial, _, _, _ = self.proxy.GetCurrentState()
            
            # Use call_sync for proper method invocation with signature
            result = self.proxy.call_sync(
                'ApplyMonitorsConfig',
                GLib.Variant('(uua(iiduba(ssa{sv}))a{sv})', (
                    serial,
                    1,  # Method: Apply persistent (1) - auto-accepts changes
                    new_logical_monitors,
                    {}  # Properties (empty)
                )),
                Gio.DBusCallFlags.NONE,
                -1,  # timeout
                None
            )
            print(f"Layout '{name}' applied successfully.")
            
            # Restore Tiling Shell configuration if available
            if tiling_shell_config:
                time.sleep(0.5)  # Give the display config a moment to settle
                if self.restore_tiling_shell_config(tiling_shell_config):
                    print("  - Tiling Shell layouts restored")
            
            # Reload Tiling Shell to refresh monitor names and apply restored config
            time.sleep(0.5)
            self.reload_tiling_shell()
            
        except Exception as e:
            print(f"Error applying layout: {e}")

def print_help():
    """Print help message"""
    print("Monstar - GNOME Display Layout Manager")
    print()
    print("Usage: monstar <command> [args]")
    print()
    print("Commands:")
    print("  list                     - List all saved layouts")
    print("  save <name>              - Save current display and Tiling Shell layout")
    print("  load <name>              - Load saved display and Tiling Shell layout")
    print("  remove <name>            - Remove a saved layout")
    print("  shortcut <layout> <num>  - Set a numbered shortcut for a layout")
    print("  shortcuts                - List all shortcuts")
    print("  <number>                 - Load layout using shortcut number")
    print("  help, --help, -h         - Show this help message")
    print()
    print("Examples:")
    print("  monstar save work")
    print("  monstar load home")
    print("  monstar shortcut work 1   # Set shortcut: 'monstar 1' loads 'work'")
    print("  monstar 1                 # Quick load using shortcut")
    print("  monstar remove old-layout")
    print()
    print("Notes:")
    print("  - Layouts are saved with both display configuration and Tiling Shell layouts")
    print("  - Tiling Shell is automatically reloaded to refresh monitor names")
    print("  - Layouts are stored in ~/.config/monstar/")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['help', '--help', '-h']:
        print_help()
        sys.exit(0)
    
    dm = DisplayManager()
    command = sys.argv[1]
    
    # Check if command is a number (shortcut)
    if command.isdigit():
        layout_name = dm.get_shortcut_layout(command)
        if layout_name:
            print(f"Loading layout '{layout_name}' via shortcut {command}")
            dm.load_layout(layout_name)
        else:
            print(f"No shortcut defined for '{command}'")
            dm.list_shortcuts()
        sys.exit(0)
    
    if command == "list":
        dm.list_layouts()
    elif command == "shortcuts":
        dm.list_shortcuts()
    elif command == "shortcut":
        if len(sys.argv) < 4:
            print("Error: Please provide layout name and shortcut number.")
            print("Usage: monstar shortcut <layout> <number>")
            sys.exit(1)
        dm.set_shortcut(sys.argv[2], sys.argv[3])
    elif command == "save":
        if len(sys.argv) < 3:
            print("Error: Please provide a name for the layout.")
            sys.exit(1)
        dm.save_layout(sys.argv[2])
    elif command == "load":
        if len(sys.argv) < 3:
            print("Error: Please provide a layout name to load.")
            dm.list_layouts()
            sys.exit(1)
        dm.load_layout(sys.argv[2])
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Please provide a layout name to remove.")
            dm.list_layouts()
            sys.exit(1)
        dm.remove_layout(sys.argv[2])
    elif command == "debug":
        dm.get_current_modes()
    else:
        print(f"Unknown command: {command}")
        print()
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
