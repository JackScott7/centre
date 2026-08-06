from typing import TypedDict

import keyboard
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pygetwindow import Win32Window


class ActiveWindow(TypedDict):
    win: Win32Window
    name: str


class WindowPreset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    LEFT: float | int
    TOP: float | int
    SIZE_X: float | int
    SIZE_Y: float | int


class Bindings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center: str = "ctrl+alt+d"
    minimize: str = "ctrl+alt+m"
    capture: str = "ctrl+alt+p"
    ignore_preset: str = "ctrl+alt+i"
    center_all: str = "ctrl+alt+a"


class KeyBinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    bindings: Bindings = Field(default_factory=Bindings)


class SoundActions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center: bool = False
    capture: bool = False
    ignore: bool = False

class FocusPreset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    center_on_focus: bool = False

    executable: str = Field(min_length=1)
    hotkey: str = Field(min_length=1)
    title_contains: str | None = None

    @field_validator('hotkey')
    @classmethod
    def validate_hotkey(cls, value: str) -> str:
        try:
            keyboard.parse_hotkey(value)
        except (ValueError, TypeError) as error:
            raise (
                ValueError(f"'{value}' is not a valid hotkey")
            ) from error

        return value


class FocusManager(BaseModel):
    model_config = ConfigDict(extra='forbid')

    enabled: bool = False
    target_preset: str = Field(default_factory=str)
    presets: list[FocusPreset] = Field(default_factory=list)


class Config(BaseModel):
    """
    Base Centre configuration Model
    """
    model_config = ConfigDict(extra="forbid")

    logging: bool = False
    play_sound: SoundActions = Field(default_factory=SoundActions)
    predefined_keybindings: KeyBinding = Field(default_factory=KeyBinding)
    wm: FocusManager = Field(default_factory=FocusManager)
    presets: dict[str, dict[str, WindowPreset]]= Field(default_factory=dict)
    ignored_presets: list[str] = Field(default_factory=list)
