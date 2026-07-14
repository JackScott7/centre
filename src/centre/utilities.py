import json
import win32process
import psutil
import os
import pygetwindow as gw
from pyautogui import size as resolution_size
from importlib.metadata import version, PackageNotFoundError
from pygetwindow import Win32Window
from .schemas import Config, WindowPreset, ActiveWindow


class Utilities:
    @staticmethod
    def entry_path(file: str) -> str:
        return os.path.dirname(os.path.abspath(file))

    @staticmethod
    def get_display_resolution() -> str:
        width, height = resolution_size()
        return f"{width}x{height}"

    @staticmethod
    def get_log_file_path() -> str:
        config_dir = os.path.join(os.path.expanduser("~"), '.centre')
        return os.path.join(config_dir, 'centre.log')

    @staticmethod
    def get_config_file_path() -> str:
        config_dir = os.path.join(os.path.expanduser("~"), '.centre')
        return os.path.join(config_dir, 'config.json')

    @staticmethod
    def minimize_window_hotkey() -> None:
        window = gw.getActiveWindow()
        if window:
            window.minimize()

    @staticmethod
    def center_hotkey(centre) -> None:
        config: Config = centre.config

        window, window_name = Utilities.get_window()
        if not window or not window_name:
            return

        ignore_list = config.ignored_presets
        if ignore_list and window_name in ignore_list:
            return

        app_poses = config.presets[Utilities.get_display_resolution()]

        if window_name in app_poses.keys():
            window.resizeTo(app_poses[window_name].SIZE_X, app_poses[window_name].SIZE_Y)
            window.moveTo(app_poses[window_name].LEFT, app_poses[window_name].TOP)
            return

        if not app_poses.get('Default_Position'):
            return

        window.resizeTo(app_poses['Default_Position'].SIZE_X, app_poses['Default_Position'].SIZE_Y)
        window.moveTo(app_poses['Default_Position'].LEFT, app_poses['Default_Position'].TOP)

    @staticmethod
    def refresh_hotkey(centre) -> None:
        centre.load_config()

    @staticmethod
    def list_window_titles() -> str:
        """
        Gets a list of all window titles.

        :return: list of window titles
        """
        return json.dumps([
            {
                "title": x.title,
                "size": {
                    "width": x.size.width,
                    "height": x.size.height
                },
                "top": x.top,
                "left": x.left,
                "bottom": x.bottom,
                "right": x.right,
            } for x in gw.getAllWindows() if x.title
        ], indent=4)

    @staticmethod
    def update_config(config: Config) -> None:
        with open(Utilities.get_config_file_path(), 'w') as file:
            json.dump(config.model_dump(), file, indent=4)

    @staticmethod
    def capture_hotkey(centre) -> None:
        window, window_name = Utilities.get_window()
        if not window or not window_name:
            return

        preset: WindowPreset = WindowPreset(
            LEFT=window.left,
            TOP=window.top,
            SIZE_X=window.size.width,
            SIZE_Y=window.size.height
        )

        Utilities.add_update_preset(window_name, preset, centre)

    @staticmethod
    def add_update_preset(window_name: str, preset: WindowPreset, centre) -> None:
        current_config: Config = centre.config
        # update the preset with new window
        current_config.presets.setdefault(Utilities.get_display_resolution(), {})[window_name] = preset
        # update the actual config file content
        Utilities.update_config(current_config)

    @staticmethod
    def ignore_window_hotkey(centre) -> None:
        window, window_name = Utilities.get_window()
        if not window or not window_name:
            return

        config: Config = centre.config

        ignored_presets = config.ignored_presets

        if window_name not in ignored_presets:
            ignored_presets.append(window_name)
            Utilities.update_config(config)

    @staticmethod
    def get_package_version() -> str:
        try:
            return version("centre")
        except PackageNotFoundError:
            return "unknown"

    @staticmethod
    def center_all_hotkey(centre) -> None:
        windows: list[ActiveWindow] = []

        for window in gw.getAllWindows():
            _, window_name = Utilities.get_window(window)
            if not window_name:
                continue

            windows.append({
                "win": window,
                "name": window_name,
            })

        presets = centre.config.presets[Utilities.get_display_resolution()]
        if not presets:
            return

        all_active = [window for window in windows if window["name"] in presets.keys()]

        if not all_active:
            return

        for window in all_active:
            win = window["win"]
            name = window["name"]

            win.resizeTo(presets[name].SIZE_X, presets[name].SIZE_Y)
            win.moveTo(presets[name].LEFT, presets[name].TOP)

    @staticmethod
    def get_window(window: Win32Window | None = None) -> tuple[Win32Window | None, str | None]:
        """
        This will get the window's object and process name.

        Pass a window object to get its process name.

        Passing None as window will return the ActiveWindow's window object and process name

        :param window: Your specific window or None (to get the active window)
        """
        if not window:
            window = gw.getActiveWindow()

        try:
            _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
            process_name = os.path.splitext(psutil.Process(pid).name())[0].upper()
            return window, process_name
        except (IndexError, Exception):
            return None, None
