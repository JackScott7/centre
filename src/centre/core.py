import json
import logging
import os
from threading import Event

import keyboard
from pydantic import ValidationError
from watchdog.observers import Observer

from .configwatcher import ConfigWatcher
from .hotkeyregistry import HotkeyRegistry
from .schemas import Config, FocusPreset
from .utilities import Utilities

log = logging.getLogger("centre")


class Centre:
    """
    Base class for Centre

    This is where config and log handling are initialized.
    """

    def __init__(self):
        self.__exit_reason: str | None = None
        self.__shutdown_event: Event = Event()

        self.log_file_path = Utilities.get_log_file_path()
        self.config_file_path = Utilities.get_config_file_path()

        config_dir = os.path.dirname(self.config_file_path)
        os.makedirs(config_dir, exist_ok=True)

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

                self.__configure_logging()

        self.__config_observer = Observer()
        self.__config_observer.schedule(
            ConfigWatcher(self),
            path=os.path.dirname(self.config_file_path),
            recursive=False
        )

    @property
    def config(self) -> Config:
        """
        Get the loaded config upon initialization

        :return: loaded config
        """
        return self.__config

    def __configure_logging(self) -> None:
        logger = logging.getLogger("centre")
        logger.setLevel(logging.INFO)
        logger.propagate = False

        # Remove the previous handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()

        if not self.__config.logging:
            return

        handler = logging.FileHandler(
            self.log_file_path,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(handler)

    def __get_core_keybindings(self) -> dict[str, str]:
        bindings = self.config.predefined_keybindings.bindings
        return bindings.model_dump()

    def __get_wm_keybindings(self) -> list[FocusPreset] | None:
        bindings = self.config.wm.presets
        if not bindings:
            return None

        shortcuts = []

        for preset in bindings:
            try:
                keyboard.parse_hotkey(preset.hotkey)
                shortcuts.append(preset)
            except ValueError as error:
                message = (
                    f"Invalid WM hotkey '{preset.hotkey}' for '{preset.executable}'"
                )
                log.error(message)
                raise SystemExit(message) from error

        return shortcuts

    def __assign_core_bindings(self, bindings: dict) -> None:
        if not bindings:
            log.error(
                "Your config seems to have an issue that's causing centre to exit.\n"
                "You can fix the issue by checking any syntax or invalid characters in config.json, or"
                " Simply removing the config file and starting Centre again will fix the issue."
                " However you presets will not be saved"
            )
            raise SystemExit

        if not self.__config.predefined_keybindings.enabled:
            log.error(
                "Please enable the predefined keybindings in config so centre can assign keybindings.\n"
                "Fix the following key in config.json like this:\n"
                '"enabled": true'
            )
            raise SystemExit

        hotkey_args = (self,)
        for k, v in bindings.items():
            match k:
                case "center":
                    keyboard.add_hotkey(v, Utilities.center_hotkey, hotkey_args, suppress=True)
                case "minimize":
                    keyboard.add_hotkey(v, Utilities.minimize_window_hotkey, suppress=True)
                case "capture":
                    keyboard.add_hotkey(v, Utilities.capture_hotkey, hotkey_args, suppress=True)
                case "ignore_preset":
                    keyboard.add_hotkey(v, Utilities.ignore_window_hotkey, hotkey_args, suppress=True)
                case "center_all":
                    keyboard.add_hotkey(v, Utilities.center_all_hotkey, hotkey_args, suppress=True)
                case _:
                    pass

    def __assign_wm_bindings(self, wm_presets: list[FocusPreset]) -> None:
        if not self.config.wm.target_preset:
            if len(self.config.presets) > 1:
                log.warning(
                    "You have more than 1 presets, please configure wm.target_preset to your desired one\n"
                    "target_preset is the one that you want all the FocusWindow or wm bindings to be bound to."
                )
                return

            if len(self.config.presets) < 1:
                return

            tp = self.config.presets.copy().popitem()[0] # grab the target_preset
            self.config.wm.target_preset = tp

            log.info("Using %s as the target_preset as it's the only one available.", tp)

            # Update the config with tp (target_preset) as WM's target preset
            Utilities.update_config(self.config)

        hk_registry = HotkeyRegistry(self.config)
        valid_registry = hk_registry.validate()
        if not valid_registry:
            log.warning("Duplicate WM hotkeys detected, please remove any duplications from WM presets and try again.")
            return

        if self.config.wm.target_preset not in self.config.presets:
            log.error("Selected 'target_preset' in WM is not valid and does not exist in Presets")
            return

        for preset in wm_presets:
            target_presets = self.config.presets.get(self.config.wm.target_preset)
            if not target_presets:
                break

            if preset.executable not in target_presets:
                log.error("No WindowPreset was found for '%s' from '%s'", preset.executable, preset)
                continue

            keyboard.add_hotkey(preset.hotkey, Utilities.focus_window, (preset, self), suppress=True)
            log.info(f"FocusWindow Hotkey '{preset.hotkey}' assigned for '{preset.executable}'")

    def request_shutdown(self, reason: str) -> None:
        self.__exit_reason = reason
        self.__shutdown_event.set()

    def load_config(self) -> None:
        """
        Load the `config.json`

        This method is used to refresh/reload the config without restarting the background process.

        Config will be accessible through Centre.config

        :return: None
        """
        try:
            with open(self.config_file_path, "r") as f:
                raw_config = json.load(f)

            self.__config: Config = Config.model_validate(raw_config)
            migrated_config = self.__config.model_dump()

            if migrated_config != raw_config:
                Utilities.update_config(self.__config)

            self.__configure_logging()

        except FileNotFoundError:
            message = f"Config file not found at '{self.config_file_path}'\nPlease run centre again."

            log.error(message)
            raise SystemExit(message)
        except json.decoder.JSONDecodeError as parse_error:
            message = (
                f"Syntax error in {self.config_file_path}\n"
                f"Error: {parse_error.msg}, "
                f"line {parse_error.lineno}, column {parse_error.colno}"
            )
            log.error(message)
            raise SystemExit(message)
        except ValidationError as ve:
            log.error(ve.args)
            raise SystemExit(ve)

    def listen(self) -> None:
        """
        Main entry point for centre, will run in the background when called.

        Keyboard shortcuts in config will be processed.
        :return: None
        """
        try:
            core_bindings = self.__get_core_keybindings()
            self.__assign_core_bindings(core_bindings)

            if self.config.wm.enabled:
                wm_bindings = self.__get_wm_keybindings()
                if wm_bindings:
                    self.__assign_wm_bindings(wm_bindings)
            else:
                log.warning("WM is not enabled in config, skipping...")

            self.__config_observer.start()
            print("[+] Centre running in background")

            while not self.__shutdown_event.wait(0.25):
                pass

            if self.__exit_reason:
                raise SystemExit(self.__exit_reason)
        except KeyboardInterrupt:
            raise SystemExit("KeyboardInterrupt")

        finally:
            keyboard.unhook_all()

            if self.__config_observer.is_alive():
                self.__config_observer.stop()
                self.__config_observer.join()
