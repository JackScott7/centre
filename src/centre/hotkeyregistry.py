import logging

import keyboard

from .schemas import Config

log = logging.getLogger("centre")


class HotkeyRegistry:
    def __init__(self, config: Config, log_errors: bool = True):
        self.config = config
        self.log_errors = log_errors

    def validate(self) -> bool:
        presets = self.config.wm.presets
        original_keys = [preset.hotkey for preset in presets]

        seen: set[tuple] = set()

        for hotkey in original_keys:
            identity = self.hotkey_identity(hotkey)
            if identity not in seen:
                seen.add(identity)
                continue

            if self.log_errors:
                log.error("Duplicate hotkey for '%s' detected in WM.", hotkey)

        wm_hk_validation = len(original_keys) == len(seen)

        duplicate_core_binding: bool = False
        bindings = self.config.predefined_keybindings.bindings.model_dump().values()

        for binding in bindings:
            identity = self.hotkey_identity(binding)
            if identity in seen:
                duplicate_core_binding = True
                if self.log_errors:
                    log.error(
                        "Duplicate hotkey of '%s' from WM is found in default core bindings.\n"
                        "Please select a different hotkey for this preset", binding)

        return wm_hk_validation and not duplicate_core_binding

    @staticmethod
    def hotkey_identity(hotkey: str) -> tuple:
        steps = keyboard.parse_hotkey_combinations(hotkey)
        return tuple(tuple(sorted(step)) for step in steps)
