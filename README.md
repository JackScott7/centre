# Centre

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/centre.svg)](https://badge.fury.io/py/centre)
[![Python Versions](https://img.shields.io/pypi/pyversions/centre.svg)](https://pypi.org/project/centre/)
---

Centre is your window position manager.

Take control of your windows by choosing where they appear, how they’re arranged, and what size they should be.

Consistency is `centre`'s goal.


## Preview
https://github.com/user-attachments/assets/d088a951-8c6b-4731-8228-80b063f1a6e5

## What Centre Tries to Achieve

Centre was built for users who want consistent window placement across desktop sessions.

## Requirements

- Windows
- Python 3.10 or newer

# Install

```PowerShell
pip install centre
```

# Update

```PowerShell
pip install -U centre
```

## Start Centre Automatically

To do that, create a Windows Task Scheduler task.

Run the following command as Administrator in PowerShell/cmd to create a Task in Windows Task Scheduler.
```PowerShell
schtasks /Create /TN "centre" /SC ONLOGON /TR "centre -s" /RL LIMITED /F
```

# Usage

After your window configuration is ready, start the listener:

```PowerShell
centre -s
```

## Single-Instance Listener

Centre allows one `centre --start` listener per Windows login session. If a
listener is already running, another start attempt prints
`Centre already running` and exits.

The other CLI commands remain available while the listener is running.

## Stopping Centre

When Centre is running interactively in a terminal, press `Ctrl+C` to stop it.
Centre will remove its keyboard hooks and stop its configuration observer
before exiting.

# The CLI

The action flags are mutually exclusive, so use one action per invocation.

| Command                      | Description                                                 |
|------------------------------|-------------------------------------------------------------|
| `centre -s`, `--start`       | Start the listener.                                         |
| `centre -l`, `--list`        | Print window titles, sizes, and positions as formatted JSON. |
| `centre -c`, `--read-config` | Print the loaded and validated configuration.               |
| `centre -v`, `--version`     | Print the installed Centre version.                         |
| `centre -h`, `--help`        | Show the available CLI options.                             |

## Automatic Configuration Reload

While Centre is running, it watches `config.json` for changes. Saving a valid
change reloads presets, ignored applications, and logging settings without
restarting the process.

Keyboard shortcuts are registered when the listener starts. Changing a shortcut
in `bindings` requires you to stop and restart Centre before the new shortcut is
used.

If `config.json` is invalid at startup, Centre reports the problem and exits
without starting the listener. If a saved configuration becomes invalid while
Centre is running, Centre performs an orderly shutdown. Correct `config.json`,
then run `centre --start` again.

# Window Configuration (config.json)

Your config will be created at the first startup in:

CMD

```cmd
%USERPROFILE%\.centre\config.json
```

PowerShell

```PowerShell
$env:USERPROFILE\.centre\config.json
```

The default config includes these values:

- The resolution key is based on your display resolution.

```json
{
    "presets": {
        "1920x1080": {}
    },
    "predefined_keybindings": {
        "enabled": true,
        "bindings": {
            "center": "ctrl+alt+d",
            "minimize": "ctrl+alt+m",
            "capture": "ctrl+alt+p",
            "ignore_preset": "ctrl+alt+i",
            "center_all": "ctrl+alt+a"
        }
    },
    "logging": false,
    "ignored_presets": []
}
```

## Configuration Validation and Migration

Centre validates the complete configuration, including window presets and
predefined keyboard shortcuts. Unknown configuration fields, shortcut names,
and preset properties are rejected.

When a valid configuration is missing fields that have defaults, Centre adds
those defaults and writes the migrated configuration back to `config.json`.

The listener requires `predefined_keybindings.enabled` to be `true`. If it is
`false`, `centre --start` exits instead of continuing without keyboard
shortcuts.

## Logging

File logging is disabled by default. To enable it, set `logging` to `true` in
`config.json`:

```json
{
  "logging": true
}
```

When logging is enabled, Centre creates or appends to:

```text
%USERPROFILE%\.centre\centre.log
```

While Centre is running, saving a valid configuration change applies the new
logging setting without requiring a restart. Changing `logging` to `false`
closes the file handler and stops new log entries from being written.

Log entries include a timestamp, severity level, and message:

```text
[2026-07-27 12:34:56,789] INFO - Centering NOTEPAD
```

Centre logs window-management activity and errors. Entries may contain
normalized executable names and captured preset details. The log file is
append-only and is not automatically rotated or deleted.

___

Window presets should be placed inside the "presets" object in `config.json`.

## Capture a Window

Focus the window you want to capture and press `ctrl+alt+p`. Centre stores its
current position and size under the current display resolution.

Captured windows are identified by their executable name without the `.exe`
extension. The name is normalized to uppercase, for example:

- `notepad++.exe` becomes `NOTEPAD++`
- `WindowsTerminal.exe` becomes `WINDOWSTERMINAL`

Executable names remain stable when an application changes its window title,
such as when switching tabs in Notepad++.

Capturing the same application again updates its existing preset.

## Ignore a Window Preset

Focus the window you want Centre to ignore and press `ctrl+alt+i`. Centre adds
the active application's executable name to `ignored_presets`.

Ignored applications are skipped when you press the center shortcut. Centre will
not apply the application's custom preset or `Default_Position`.

To allow Centre to manage the application again, remove its executable name from
`ignored_presets` in `config.json`.

## Center All Configured Windows

Press `ctrl+alt+a` to apply presets to all currently open windows that have a
matching entry under the current display resolution.

Centre skips open windows that do not have a named preset. `Default_Position` is
only used by the regular center shortcut for the active window.

___

A window preset should look like this:

```json
{
    "NOTEPAD++": {
        "LEFT": 224,
        "TOP": 168,
        "SIZE_X": 1473,
        "SIZE_Y": 697
    },
    "Default_Position": {
        "LEFT": 25,
        "TOP": 34,
        "SIZE_X": 1860,
        "SIZE_Y": 980
    }
}

```

- Be sure to add `Default_Position` in your presets under the generated default resolution.
  When Centre does not find the active window in your presets, it uses `Default_Position` as the fallback size and position.

- `Default_Position` is useful when you have a list of apps that you have set a custom position for,
  but intend to keep all other apps in one specific location.

## Default Shortcuts

| Action     | Shortcut     | Description                                                  |
|------------|--------------|--------------------------------------------------------------|
| Center     | `ctrl+alt+d` | Apply the active application's preset or `Default_Position`. |
| Minimize   | `ctrl+alt+m` | Minimize the active window.                                  |
| Capture    | `ctrl+alt+p` | Save or update the active application's position and size.   |
| Ignore     | `ctrl+alt+i` | Add the active application to `ignored_presets`.             |
| Center All | `ctrl+alt+a` | Apply presets to all matching open windows.                  |

Your final config should look something like this:

```json
{
    "presets": {
        "1920x1080": {
            "WINDOWSTERMINAL": {
                "LEFT": 224,
                "TOP": 168,
                "SIZE_X": 1473,
                "SIZE_Y": 697
            },
            "Default_Position": {
                "LEFT": 25,
                "TOP": 34,
                "SIZE_X": 1860,
                "SIZE_Y": 980
            }
        }
    },
    "predefined_keybindings": {
        "enabled": true,
        "bindings": {
            "center": "ctrl+alt+d",
            "minimize": "ctrl+alt+m",
            "capture": "ctrl+alt+p",
            "ignore_preset": "ctrl+alt+i",
            "center_all": "ctrl+alt+a"
        }
    },
    "logging": false,
    "ignored_presets": [
        "NOTEPAD++"
    ]
}
```

# Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.


# License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
