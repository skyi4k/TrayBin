import ctypes
from ctypes import wintypes

ERROR_ALREADY_EXISTS = 183

class SingleInstance:
    def __init__(self, app_id="MiniBinKT_Application_Mutex"):
        self.app_id = f"Global\\{app_id}"
        self.mutex = None
        self.already_running = False

        self._create_mutex()

    def _create_mutex(self):
        kernel32 = ctypes.windll.kernel32
        # Create named mutex
        self.mutex = kernel32.CreateMutexW(None, False, self.app_id)
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            self.already_running = True

    def is_running(self):
        return self.already_running

    def release(self):
        if self.mutex:
            ctypes.windll.kernel32.CloseHandle(self.mutex)
            self.mutex = None

    def __del__(self):
        self.release()
