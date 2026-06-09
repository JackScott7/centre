import os
import pygetwindow as gw
from pyautogui import size as resolution_size


class Utilities:
    @staticmethod
    def entry_path(file: str):
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
    def minimize_window_hotkey() -> None:
        window = gw.getActiveWindow()
        if window:
            window.minimize()

    @staticmethod
    def center_hotkey(presets, current_preset) -> None:
        window = gw.getActiveWindow()
        if not window:
            return
        app_poses = presets[current_preset]

        if not app_poses.get('Default_Position', None):
            return

        for key in app_poses.keys():
            if key in window.title:
                window.resizeTo(app_poses[key]['SIZE_X'], app_poses[key]['SIZE_Y'])
                window.moveTo(app_poses[key]['LEFT'], app_poses[key]['TOP'])
                return
        else:
            if window:
                window.resizeTo(app_poses['Default_Position']['SIZE_X'], app_poses['Default_Position']['SIZE_Y'])
                window.moveTo(app_poses['Default_Position']['LEFT'], app_poses['Default_Position']['TOP'])

    @staticmethod
    def refresh_hotkey(centre) -> None:
        centre.load_config()

    @staticmethod
    def list_window_titles() -> list[str]:
        """
        Gets a list of all window titles.

        :return: list of window titles
        """
        return [x.title for x in gw.getAllWindows() if x.title]
