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

# Install

```PowerShell
pip install centre
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

# The CLI

You can use the `centre` CLI to inspect open windows and read the active
configuration.

Examples:

```PowerShell
# List active windows, including their titles, sizes, and positions
centre -l

# Print the loaded configuration
centre -c
```

## Automatic Configuration Reload

While Centre is running, it watches `config.json` for changes. Saving the file
causes Centre to read the configuration again without restarting the process.

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
            "ignore_preset": "ctrl+alt+i"
        }
    },
    "logging": false,
    "ignored_presets": []
}
```

You can change any predefined keyboard shortcut in the `bindings` object.

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

| Action   | Shortcut     | Description                                                  |
|----------|--------------|--------------------------------------------------------------|
| Center   | `ctrl+alt+d` | Apply the active application's preset or `Default_Position`. |
| Minimize | `ctrl+alt+m` | Minimize the active window.                                  |
| Capture  | `ctrl+alt+p` | Save or update the active application's position and size.   |
| Ignore   | `ctrl+alt+i` | Add the active application to `ignored_presets`.             |

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
            "ignore_preset": "ctrl+alt+i"
        }
    },
    "logging": false,
    "ignored_presets": [
        "NOTEPAD++"
    ]
}
```

# Caveats

Some windows may overlap even when they use the same configured position and size.

This is due to some apps having a bigger actual window than the rendered UI.

# License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
