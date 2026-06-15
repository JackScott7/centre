import json
import win32process
import psutil
import os
import pygetwindow as gw
from pyautogui import size as resolution_size
from importlib.metadata import version, PackageNotFoundError


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
    def center_hotkey(centre, current_preset) -> None:
        presets = centre.config.get("presets")
        if not presets:
            return

        window, window_name = Utilities.get_active_window()
        if not window:
            return

        app_poses = presets.get(current_preset)
        if not app_poses:
            return

        if window_name in app_poses.keys():
            window.resizeTo(app_poses[window_name]['SIZE_X'], app_poses[window_name]['SIZE_Y'])
            window.moveTo(app_poses[window_name]['LEFT'], app_poses[window_name]['TOP'])
            return

        if not app_poses.get('Default_Position'):
            return

        window.resizeTo(app_poses['Default_Position']['SIZE_X'], app_poses['Default_Position']['SIZE_Y'])
        window.moveTo(app_poses['Default_Position']['LEFT'], app_poses['Default_Position']['TOP'])

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
    def update_config(new_config_json) -> None:
        with open(Utilities.get_config_file_path(), 'w') as file:
            json.dump(new_config_json, file, indent=4)

    @staticmethod
    def capture_hotkey(centre) -> None:
        window, window_name = Utilities.get_active_window()
        if not window:
            return

        preset = {
            "LEFT": window.left,
            "TOP": window.top,
            "SIZE_X": window.size.width,
            "SIZE_Y": window.size.height
        }

        Utilities.add_update_preset(window_name, preset, centre)

    @staticmethod
    def get_active_window() -> tuple:
        active = gw.getActiveWindow()
        if not active:
            return None, None
        _, pid = win32process.GetWindowThreadProcessId(active._hWnd)
        process_name = os.path.splitext(psutil.Process(pid).name())[0].upper()
        return active, process_name

    @staticmethod
    def add_update_preset(window_name, preset, centre) -> None:
        current_config = centre.config
        # update the preset with new window
        current_config["presets"][Utilities.get_display_resolution()][window_name] = preset
        # update the actual config file content
        Utilities.update_config(current_config)

    @staticmethod
    def get_package_version() -> str:
        try:
            return version("centre")
        except PackageNotFoundError:
            return "unknown"
