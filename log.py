"""Logging created for FAB cards program.

Functions:

	log(str, str) -> str

__version__
format_version
compatible_formats
"""

from datetime import datetime


def log(level: str, message: str) -> str:
    """Writes log to file log.txt.

    Args:
        level: the log level ['Debug', 'Info', 'Warn', 'Error']
        message: the log message to be printed

    Returns:
        the entire log message in case of printing
    """

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    log_string: str = f'{current_time} - {level}: {message}\n'

    with open('log.txt', 'a') as file:
        file.write(log_string)

    return log_string
