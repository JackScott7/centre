from pathlib import Path

from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler


class ConfigWatcher(FileSystemEventHandler):
    def __init__(self, centre):
        self.centre = centre
        self.config_path = Path(centre.config_file_path).resolve()

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        if event.is_directory:
            return

        event_path = Path(str(event.src_path)).resolve()

        try:
            if event_path == self.config_path:
                increment_config_version: bool = self.centre.config.cloud.enabled
                self.centre.load_config(increment_version=increment_config_version)
        except SystemExit as ex:
            self.centre.request_shutdown(str(ex) or "Centre stopped because the configuration is invalid.")
