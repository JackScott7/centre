from pydantic import BaseModel, ConfigDict, Field
from typing import TypedDict
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


class Config(BaseModel):
    """
    Base Centre configuration Model
    """
    model_config = ConfigDict(extra="forbid")

    presets: dict[str, dict[str, WindowPreset]]= Field(default_factory=dict)
    predefined_keybindings: KeyBinding = Field(default_factory=KeyBinding)
    logging: bool = False
    ignored_presets: list[str] = Field(default_factory=list)
