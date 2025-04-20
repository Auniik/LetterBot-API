import logging
import os

from pythonjsonlogger.json import JsonFormatter


def dev_debug(logger, message, *args, **kwargs):
    if os.getenv('APP_ENV') in ['local', 'development', 'staging']:
        logger.debug(f"{os.getenv('APP_ENV')}: {message}", *args, **kwargs)

class CustomJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['severity'] = record.levelname
        log_record['logger'] = record.name


def setup_logging():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:\t  %(message)s')
    info_handler = logging.StreamHandler()
    info_handler.setFormatter(formatter)

    debug_handler = logging.StreamHandler()
    debug_handler.setFormatter(formatter)
    debug_handler.setLevel(logging.DEBUG)
    _logger.addHandler(debug_handler)

    error_handler = logging.StreamHandler()
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    _logger.addHandler(error_handler)

    _logger.propagate = False
    return _logger

logger = setup_logging()
logger.dev_debug = lambda message, *args, **kwargs: dev_debug(logger, message, *args, **kwargs)


def log(severity, **kwargs):
    log_data = {
        **kwargs
    }
    getattr(logger, severity.lower())(log_data)
