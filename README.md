# This is Centre
___
Centre is your Window Position Manager.


So what's a `Window Position Manager`?

Take control of your windows by choosing where they appear, how they’re arranged, and what size they should be.

Consistency is `Centre`'s goal.

## What Centre's tries to achieve
___
I myself have a very deep OCD, 
where even apps not being aligned on my desktop will make me ache.

So I tried to make centre as easy as
having a single config file on each desktop device you have, will
make your life super easy to have everything setup.

# Install
___
```bash
pip install centre
```

## Make the process persistent
___
We are going to the following to make `centr` persistent when booting the machine or restarting it.
- Windows Task Scheduler

...

# Usage

This is the script's main starting point. when you got everything setup (window configuration is done) and ready to start the listener.
Start as a background process.
___
```bash
$ centre -s
```

# The CLI
___
You can use `centre` CLI to find out window's titles, sizes and screen positions.
The CLI will help you to accurately find your window's title to set the exact position you want on the screen with your desired size.

Examples:
```bash
# List all active windows titles
$ centre -l
```

## Refresh your config without restarting
___
You can use the predefined shortcut `ctrl+alt+r` to reload/refresh your config without restarting the background process.
This is useful when trying to edit your config.

# Window Configuration (centre.json)
___
Default config comes like the following example:

- The Resolution below will be based on your display resolution
```json
{
    "1920x1080": {},
    "predefined_bindings": {
        "enabled": true,
        "bindings": {
            "refresh": "ctrl+alt+r"
        }
    }
}
```
___
A Window example be like:
```json
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
```
Default_Position: ...


# Caveats
___

So when you try out `centre` you WILL find that some windows even while having the same exact Position and Size will on screen, will overlap each other.

This is due to some apps having a bigger actual Window than the rendered UI.
