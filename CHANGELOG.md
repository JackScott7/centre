# Changelog

All notable changes to Centre are documented in this file.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses package versions from `pyproject.toml`.

## [0.10.3] - 2026-08-09

### Fixed

- HotkeyRegistry will now respect `centre.config.logging` (simply `logging` in `config.json`)

## [0.10.2] - 2026-08-09

### Fixed

- focus_window will now respect the general rule that ignored presets should not be processed.

## [0.10.1] - 2026-08-09

### Fixed

- an unwanted behavior where pressing a shortcut (e.g. ctrl+alt+d) would cause the literal character 'd' in the shortcut to be typed/inserted.

## [0.10.0] - 2026-08-06

### Added

- Added opt-in Focus Window shortcuts through the new `wm` configuration section.
- Added `FocusPreset` support for matching an open window by its executable preset key and an optional case-insensitive title substring.
- Added `center_on_focus` so a focused window can optionally be resized and moved to its configured WindowPreset.
- Added reliable Windows foreground activation that restores minimized windows, retries foreground activation, and temporarily attaches input queues when Windows rejects the initial request.
- Added `HotkeyRegistry` validation for duplicate Focus Window shortcuts and conflicts with Centre's predefined shortcuts.
- Added Pydantic validation for Focus Window hotkey syntax during startup and live configuration reloads.

### Changed

- Split predefined and Focus Window shortcut discovery and registration into separate listener paths.
- Added `FocusManager` and `FocusPreset` to the strict configuration schema, with Focus Window disabled by default.
- Automatically selects and saves the only available layout as `wm.target_preset` when no target is configured.
- Updated the package version and lockfile metadata to `0.10.0`.

### Fixed

- Prevented duplicate or conflicting Focus Window shortcuts from being registered.
- Prevented invalid Focus Window hotkeys from starting or remaining in a running Centre configuration.
- Prevented stale Focus Window callbacks from acting after Window Manager is disabled or the matching WindowPreset is removed.
- Prevented centering after foreground activation fails.
- Handled windows that close between discovery and activation without allowing expected Win32 errors to escape the hotkey callback.
- Added explicit handling for missing target layouts, missing executable presets, inaccessible processes, and absent matching windows.

## [0.9.1] - 2026-08-01

### Changed

- Removed the PyAutoGUI dependency and used the existing PyWin32 dependency to determine the primary display resolution.
- Improved import organization, logging calls, type annotations, and handling of expected process and Win32 errors.

## [0.9.0] - 2026-07-31

### Added

- Added optional confirmation sounds for successful Center, Center All, Capture, and Ignore actions.
- Added `play_sound.center`, `play_sound.capture`, and `play_sound.ignore` configuration options, disabled by default.
- Packaged the Center, Capture, and Ignore WAV resources with the application.

### Changed

- Updated the package version to `0.9.0`.

## [0.8.4] - 2026-07-30

### Fixed
- Ensured `center_all_hotkey` skips executables listed in `ignored_presets`.

## [0.8.3] - 2026-07-30

### Changed

- Made `--start` mutually exclusive with the other CLI action flags.
- Added a clear message when a Centre listener is already running.
- Updated the package version to `0.8.3`.

### Fixed

- Prevented multiple `centre --start` listeners from running in the same Windows login session by using a named mutex.
- Ensured duplicate startup is detected before Centre initializes its configuration, logging, and filesystem observer.

## [0.8.2] - 2026-07-27

### Added

- Added configurable file logging through the `logging` configuration option.
- Added operational and error logging for window-management actions.
- Added an event-based graceful shutdown mechanism.

### Changed

- Applied logging configuration during startup and live configuration reloads.
- Changed invalid configuration reloads to request an orderly shutdown.
- Centralized configuration and log-file path resolution.
- Updated the package version to `0.8.2`.

### Fixed

- Fixed logging handlers not being closed when file logging is disabled.
- Prevented duplicate logging handlers after configuration reloads.
- Improved cleanup of keyboard hooks and the filesystem observer during shutdown.
- Improved handling of unavailable windows and inaccessible processes.


## [0.7.1] - 2026-07-14

### Fixed

- Fixed `ignore_window_hotkey` so the first ignored window can be added when `ignored_presets` is empty.

## [0.7.0] - 2026-07-14

### Added

- Added Pydantic models to validate `config.json`.
- Added automatic migration for newly introduced predefined keyboard shortcuts.
- Added stricter validation for unknown config keys and unknown predefined shortcut names.

### Changed

- Renamed the file watcher implementation to `ConfigWatcher`.
- Limited config reload handling to file modification events.
- Refactored config loading, validation, and predefined keybinding handling.
- Updated README documentation for the current config format and shortcut behavior.
- Updated package version to `0.7.0`.

### Fixed

- Fixed minor config and keybinding edge cases around new predefined shortcut releases.

## [0.4.1] - 2026-07-09

### Added

- Added `center_all` predefined shortcut support with the default shortcut `ctrl+alt+a`.
- Added `center_all_hotkey` to apply matching presets to all currently open windows.

### Changed

- Updated README documentation for the `center_all` feature.
- Updated package version to `0.4.1`.

## [0.3.0] - 2026-06-21

### Added

- Added ignored preset support through `ignored_presets`.
- Added the default ignore shortcut `ctrl+alt+i`.
- Added hotkey handling for ignoring the active application's preset.

### Changed

- Updated README documentation for the ignore preset feature.
- Updated package version to `0.3.0`.

## [0.2.1] - 2026-06-15

### Added

- Added `centre -v` / `centre --version` to print the installed package version.

### Changed

- Improved README preview and formatting.
- Updated package version to `0.2.1`.

## [0.2.0] - 2026-06-11

### Added

- Added window capture with the `ctrl+alt+p` hotkey.
- Added executable-based preset matching so saved presets are tied to application process names.
- Added automatic config reload while Centre is running.

### Changed

- Updated README documentation for window capture and config reload behavior.
- Updated project dependencies.
- Updated package version to `0.2.0`.

### Fixed

- Fixed predefined keybindings being reloaded incorrectly when config file changes are detected.
- Fixed dependency metadata for packaging.

## [0.1.0] - 2026-06-10

### Added

- Added the initial `centre` CLI package.
- Added the `centre -s` listener command.
- Added active-window centering from configured presets.
- Added active-window minimization through a predefined shortcut.
- Added `centre -l` to list open window titles, sizes, and positions.
- Added `centre -c` to print the loaded configuration.
- Added default config creation under the user's `.centre` directory.
- Added PyPI packaging with a console script entry point.

### Changed

- Refactored the early CLI and core API structure before the first public release.
- Updated README and project dependency documentation for the first PyPI release.

### Fixed

- Added a guard clause to avoid crashing when no active window is available for centering.
