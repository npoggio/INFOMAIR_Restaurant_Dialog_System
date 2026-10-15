from datetime import datetime
import time
from enum import StrEnum, auto

NOW = lambda: datetime.now().strftime('%d/%m/%Y %H:%M:%S')
NOW_FILE = NOW().replace('/', '').replace(':', '').replace(' ', '_')
LOG_FILE = f'logs/{NOW_FILE}.log' 


class _LogTypes(StrEnum):
    PARAMS = auto()
    SYSMSG = auto()
    USRMSG = auto()
    

class Logger:
    def __init__(self, log_file: str = LOG_FILE):
        self.writer = open(log_file, 'a')
        self.write_parameters = lambda msg: self.__write(_LogTypes.PARAMS, msg)
        self.write_sys_msg    = lambda msg: self.__write(_LogTypes.SYSMSG, msg)
        self.write_user_msg   = lambda msg: self.__write(_LogTypes.USRMSG, msg)

    def __write(self, cause: str, msg: str):
        formatted_msg = f'[{NOW()}] <{str(cause).upper()}> {msg}\n'
        self.writer.write(formatted_msg)


if __name__ == '__main__':
    l = Logger()
    l.write_parameters('Hello')
    l.write_sys_msg('Test')
    l.write_user_msg('Test')