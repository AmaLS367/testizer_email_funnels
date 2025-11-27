import logging
import logging.handlers
import os
from typing import Optional


def configure_logging(log_level: str, logs_directory: Optional[str] = None) -> None:
    """
    Configure application logging to console and rotating file.
    """
    if logs_directory is None:
        logs_directory = os.path.join(os.getcwd(), "logs")

    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)

    log_file_path = os.path.join(logs_directory, "app.log")

    log_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
