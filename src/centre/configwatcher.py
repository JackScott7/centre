from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class ConfigWatcher(FileSystemEventHandler):
    def __init__(self, centre):
        self.centre = centre
        self.config_path = Path(centre.config_file_path).resolve()

    def on_modified(self, event: FileModifiedEvent):
        event_path = Path(str(event.src_path)).resolve()

        try:
            if event_path == self.config_path:
                self.centre.load_config()
        except SystemExit as ex:
            self.centre.request_shutdown(str(ex) or "Centre stopped because the configuration is invalid.")
