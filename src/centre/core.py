import json
import logging
import os
import keyboard
from .utilities import Utilities


class Centre:
    """
    Base class for Centre

    This is where config and log handling are initialized.
    """
    def __init__(self):
        config_dir = os.path.join(os.path.expanduser("~"), ".centre")
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)

        self.__config_file_path = os.path.join(config_dir, "config.json")

        if not os.path.isfile(self.__config_file_path):
            with open(self.__config_file_path, 'w') as f:
                self.__config = {
                    "presets": {
                        f"{Utilities.get_display_resolution()}": {}
                    },

                    "predefined_keybindings": {
                        "enabled": True,
                        "bindings": {
                            "refresh": "ctrl+alt+r",
                            "center": "ctrl+alt+d",
                            "minimize": "ctrl+alt+m",
                        }
                    },
                    "logging": False
                }
                json.dump(self.__config, f, indent=4)
                return
        self.load_config()

        self.__logging = self.__config.get("logging", False)
        if self.__logging:
            logging.basicConfig(level=logging.INFO, filename=Utilities.get_log_file_path())

    @property
    def get_config(self) -> str:
        """
        Get the loaded config upon initialization

        :return: loaded config
        """
        return json.dumps(self.__config, indent=4)

    def load_config(self) -> None:
        """
        Load the `config.json`

        This method is used to refresh/reload the config without restarting the background process.

        Config will be accessible through Centre.get_config

        :return: None
        """
        try:
            with open(self.__config_file_path, "r") as f:
                self.__config = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Config file not found at '{self.__config_file_path}'\nPlease run centre again.")
        except json.decoder.JSONDecodeError as parse_error:
            print(f"Syntax error in {self.__config_file_path}\nError: {parse_error.msg} on line {parse_error.lineno}")
            exit(1)

    def __get_keybindings(self) -> dict:
        bindings = self.__config.get("predefined_keybindings").get("bindings", {})
        return bindings

    def __assign_keyboard_bindings(self, bindings: dict) -> None:
        if not bindings:
            raise ValueError("Your config seems to have an issue that's causing centre to exit.")

        if not self.__config.get("predefined_keybindings").get("enabled", False):
            raise ValueError("Please enable the predefined keybindings in config so centre can assign keybindings.")

        for k,v in bindings.items():
            if k == "refresh":
                keyboard.add_hotkey(v, Utilities.refresh_hotkey, (self,))
            elif k == "center":
                args = (self.__config.get("presets"), Utilities.get_display_resolution())
                keyboard.add_hotkey(v, Utilities.center_hotkey, args)
            elif k == "minimize":
                keyboard.add_hotkey(v, Utilities.minimize_window_hotkey)
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
            keyboard.wait()
        except KeyboardInterrupt or Exception:
            exit(0)
