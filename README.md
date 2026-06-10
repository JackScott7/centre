# Centre

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
---

Centre is your window position manager.

Take control of your windows by choosing where they appear, how they’re arranged, and what size they should be.

Consistency is `centre`'s goal.

## What Centre Tries to Achieve

---
Centre was built for users who want consistent window placement across desktop sessions.

# Install

---

```PowerShell
pip install centre
```

## Start Centre Automatically

---
To do that, create a Windows Task Scheduler task.

Run the following command as Administrator in PowerShell/cmd to create a Task in Windows Task Scheduler.
```PowerShell
schtasks /Create /TN "centre" /SC ONLOGON /TR "centre -s" /RL LIMITED /F
```

# Usage

After your window configuration is ready, start the listener:
---

```bash
$ centre -s
```

# The CLI

---
You can use `centre` CLI to find out window titles, sizes and screen positions.
The CLI will help you to accurately find your window title to set the exact position you want on the screen with your
desired size.

Examples:

```PowerShell
# List all active window titles
centre -l
```

## Refresh your config without restarting

---
You can use the predefined shortcut `ctrl+alt+r` to reload/refresh your config without restarting the background
process.
This is useful when trying to edit your config.

# Window Configuration (config.json)

---
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
            "refresh": "ctrl+alt+r",
            "center": "ctrl+alt+d",
            "minimize": "ctrl+alt+m"
        }
    },
    "logging": false
}
```

**_You can change any predefined keyboard shortcut, for example setting refresh to ctrl+shift+f10._**

---
Window presets should be placed inside the "presets" object in `config.json`.

A window preset should look like this:

```json
{
    "PS7": {
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

Your final config should look something like this:

```json
{
    "presets": {
        "1920x1080": {
            "PS7": {
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
            "refresh": "ctrl+alt+r",
            "center": "ctrl+alt+d",
            "minimize": "ctrl+alt+m"
        }
    },
    "logging": false
}
```

# Caveats

---

Some windows may overlap even when they use the same configured position and size.

This is due to some apps having a bigger actual window than the rendered UI.

# License

---

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
