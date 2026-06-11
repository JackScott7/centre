import os.path
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class Config(FileSystemEventHandler):
    def __init__(self, centre):
        self.centre = centre

    def on_any_event(self, event: FileSystemEvent):
        path = getattr(event, "dest_path", None) or event.src_path

        if os.path.abspath(path) == os.path.abspath(self.centre.config_file_path):
            self.centre.load_config()
