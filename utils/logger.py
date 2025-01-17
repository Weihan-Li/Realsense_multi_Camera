import logging
import os
from datetime import datetime
from functools import wraps
from typing import Callable, Any


class Logger:
    """Custom logger implementation for the RealSense camera system."""

    def __init__(self, name: str, log_dir: str = "logs") -> None:
        """
        Initialize logger with custom formatting and handlers.

        Args:
            name: Logger name
            log_dir: Directory for log files
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # File handler
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_function_call(self, func: Callable) -> Callable:
        """
        Decorator to log function calls with parameters and return values.

        Args:
            func: Function to be decorated
        Returns:
            Wrapped function with logging
        """

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            self.logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise

        return wrapper

    def debug(self, msg: str) -> None:
        self.logger.debug(msg)

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def warning(self, msg: str) -> None:
        self.logger.warning(msg)

    def error(self, msg: str) -> None:
        self.logger.error(msg)