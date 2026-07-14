import json
import logging
import os
import keyboard
from watchdog.observers import Observer
from pydantic import ValidationError
from .configwatcher import ConfigWatcher
from .utilities import Utilities
from .schemas import Config


class Centre:
    """
    Base class for Centre

    This is where config and log handling are initialized.
    """

    def __init__(self):
        config_dir = os.path.join(os.path.expanduser("~"), ".centre")
        os.makedirs(config_dir, exist_ok=True)

        self.config_file_path = os.path.join(config_dir, "config.json")

        if os.path.isfile(self.config_file_path):
            self.load_config()
        else:
            with open(self.config_file_path, 'w') as f:
                self.__config: Config = Config(
                    presets={
                        Utilities.get_display_resolution(): {}
                    }
                )
                json.dump(self.__config.model_dump(), f, indent=4)

        self.__config_observer = Observer()
        self.__config_observer.schedule(
            ConfigWatcher(self),
            path=os.path.dirname(self.config_file_path),
            recursive=False
        )

        self.__logging = self.__config.logging
        if self.__logging:
            logging.basicConfig(level=logging.INFO, filename=Utilities.get_log_file_path())

    @property
    def config(self) -> Config:
        """
        Get the loaded config upon initialization

        :return: loaded config
        """
        return self.__config

    def load_config(self) -> None:
        """
        Load the `config.json`

        This method is used to refresh/reload the config without restarting the background process.

        ConfigWatcher will be accessible through Centre.config

        :return: None
        """
        try:
            with open(self.config_file_path, "r") as f:
                raw_config = json.load(f)

            self.__config: Config = Config.model_validate(raw_config)
            migrated_config = self.__config.model_dump()

            if migrated_config != raw_config:
                Utilities.update_config(self.__config)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"ConfigWatcher file not found at '{self.config_file_path}'\nPlease run centre again.")
        except json.decoder.JSONDecodeError as parse_error:
            print(f"Syntax error in {self.config_file_path}\nError: {parse_error.msg} on line {parse_error.lineno}")
            raise SystemExit
        except ValidationError as ve:
            print(ve.args)
            raise SystemExit

    def __get_keybindings(self) -> dict[str, str]:
        bindings = self.config.predefined_keybindings.bindings
        return bindings.model_dump()

    def __assign_keyboard_bindings(self, bindings: dict) -> None:
        if not bindings:
            raise ValueError(
                "Your config seems to have an issue that's causing centre to exit.\n"
                "You can fix the issue by checking any syntax or invalid characters in config.json, or"
                " Simply removing the config file and starting Centre again will fix the issue."
                " However you presets will not be saved"
            )

        if not self.__config.predefined_keybindings.enabled:
            raise ValueError(
                "Please enable the predefined keybindings in config so centre can assign keybindings.\n"
                "Fix the following key in config.json like this:\n"
                '"enabled": true'
            )

        hotkey_args = (self,)
        for k, v in bindings.items():
            match k:
                case "center":
                    keyboard.add_hotkey(v, Utilities.center_hotkey, hotkey_args)
                case "minimize":
                    keyboard.add_hotkey(v, Utilities.minimize_window_hotkey)
                case "capture":
                    keyboard.add_hotkey(v, Utilities.capture_hotkey, hotkey_args)
                case "ignore_preset":
                    keyboard.add_hotkey(v, Utilities.ignore_window_hotkey, hotkey_args)
                case "center_all":
                    keyboard.add_hotkey(v, Utilities.center_all_hotkey, hotkey_args)
                case _:
                    pass

    def listen(self) -> None:
        """
        Main entry point for centre, will run in the background when called.

        Keyboard shortcuts in config will be processed.
        :return: None
        """
        try:
            bindings = self.__get_keybindings()
            self.__assign_keyboard_bindings(bindings)

            self.__config_observer.start()
            print("[+] Centre running in background")

            keyboard.wait()
        except KeyboardInterrupt:
            raise SystemExit
        finally:
            keyboard.unhook_all()
            if self.__config_observer.is_alive():
                self.__config_observer.stop()
                self.__config_observer.join()
