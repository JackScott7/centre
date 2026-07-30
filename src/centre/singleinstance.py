import win32api
import win32event
import winerror


class CentreAlreadyRunning(RuntimeError):
    pass


class SingleInstanceMutex:
    MUTEX_NAME = r"Local\JackScott7.Centre.SingleInstance"

    def __init__(self, name: str) -> None:
        self._name = name
        self._handle = None

    def __enter__(self) -> "SingleInstanceMutex":
        self._handle = win32event.CreateMutex(
            None,
            False,
            self._name,
        )

        # This must be checked immediately after CreateMutex.
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            win32api.CloseHandle(self._handle)
            self._handle = None
            raise CentreAlreadyRunning

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._handle is not None:
            win32api.CloseHandle(self._handle)
            self._handle = None
