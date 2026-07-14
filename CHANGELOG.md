# Changelog

All notable changes to Centre are documented in this file.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses package versions from `pyproject.toml`.

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
