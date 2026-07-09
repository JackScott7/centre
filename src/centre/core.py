import json
import logging
import os
import keyboard
from .config import Config
from .utilities import Utilities
from watchdog.observers import Observer


class Centre:
    """
    Base class for Centre

    This is where config and log handling are initialized.
    """
    def __init__(self):
        config_dir = os.path.join(os.path.expanduser("~"), ".centre")
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)

        self.config_file_path = os.path.join(config_dir, "config.json")
        self.__config: dict = {}

        if not os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'w') as f:
                self.__config = {
                    "presets": {
                        f"{Utilities.get_display_resolution()}": {}
                    },

                    "predefined_keybindings": {
                        "enabled": True,
                        "bindings": {
                            "center": "ctrl+alt+d",
                            "minimize": "ctrl+alt+m",
                            "capture": "ctrl+alt+p",
                            "ignore_preset": "ctrl+alt+i",
                            "center_all": "ctrl+alt+a",
                        }
                    },
                    "logging": False,
                    "ignored_presets": []
                }
                json.dump(self.__config, f, indent=4)

        if not self.__config:
            self.load_config()

        self.__config_observer = Observer()
        self.__config_observer.schedule(
            Config(self),
            path=os.path.dirname(self.config_file_path),
            recursive=False
        )

        self.__logging = self.__config.get("logging", False)
        if self.__logging:
            logging.basicConfig(level=logging.INFO, filename=Utilities.get_log_file_path())

    @property
    def config(self) -> dict:
        """
        Get the loaded config upon initialization

        :return: loaded config
        """
        return self.__config

    def load_config(self) -> None:
        """
        Load the `config.json`

        This method is used to refresh/reload the config without restarting the background process.

        Config will be accessible through Centre.config

        :return: None
        """
        try:
            with open(self.config_file_path, "r") as f:
                self.__config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at '{self.config_file_path}'\nPlease run centre again.")
        except json.decoder.JSONDecodeError as parse_error:
            print(f"Syntax error in {self.config_file_path}\nError: {parse_error.msg} on line {parse_error.lineno}")
            raise SystemExit

    def __get_keybindings(self) -> dict[str, str]:
        bindings = self.__config.get("predefined_keybindings", {}).get("bindings", {})
        if not bindings:
            return {}

        return bindings

    def __assign_keyboard_bindings(self, bindings: dict) -> None:
        if not bindings:
            raise ValueError("Your config seems to have an issue that's causing centre to exit.")

        if not self.__config.get("predefined_keybindings", {}).get("enabled", False):
            raise ValueError("Please enable the predefined keybindings in config so centre can assign keybindings.")

        for k, v in bindings.items():
            if k == "center":
                args = (self, Utilities.get_display_resolution())
                keyboard.add_hotkey(v, Utilities.center_hotkey, args)
            elif k == "minimize":
                keyboard.add_hotkey(v, Utilities.minimize_window_hotkey)
            elif k == "capture":
                keyboard.add_hotkey(v, Utilities.capture_hotkey, (self,))
            elif k == "ignore_preset":
                keyboard.add_hotkey(v, Utilities.ignore_window_hotkey, (self,))
            elif k == "center_all":
                keyboard.add_hotkey(v, Utilities.center_all_hotkey, (self, Utilities.get_display_resolution()))
            else:
                pass

    def listen(self) -> None:
        """
        Main entry point for centre, will run in the background when called.

        Keyboard shortcuts in config will be processed.
        :return: None
        """
        bindings = self.__get_keybindings()
        self.__assign_keyboard_bindings(bindings)
        try:
            print("[+] Centre running in background")
            self.__config_observer.start()
            keyboard.wait()
        except (KeyboardInterrupt, Exception):
            raise SystemExit
