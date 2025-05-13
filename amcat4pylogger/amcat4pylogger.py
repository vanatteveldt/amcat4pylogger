import logging
import sys
from traceback import format_tb
from typing import Optional

from amcat4py import AmcatClient

LOGGING_FIELDS = dict(
    date="date",
    level="keyword",
    logger="keyword",
    origin="keyword",
    title="text",
    error_type="keyword",
    error_message="text",
    error_trace="text",
)


class AmCATLogFormatter(logging.Formatter):
    def __init__(self, *, extra_fields=None, extra_values=None, **kargs):
        self.extra_fields = extra_fields
        self.extra_values = extra_values
        super().__init__(**kargs)

    def format_to_amcat(self, record: logging.LogRecord):
        date = f'{self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S")}.{int(record.msecs):03d}Z'
        doc = {
            "date": date,
            "level": record.levelname,
            "logger": record.name,
            "origin": f"{record.filename}:{record.lineno}",
            "title": record.getMessage(),
        }
        for field in self.extra_fields:
            if hasattr(record, field):
                doc[field] = getattr(record, field)
        for field, value in self.extra_values.items():
            doc[field] = value

        if record.exc_info:
            exc_info = sys.exc_info if isinstance(record.exc_info, bool) else record.exc_info
            doc["error_type"] = exc_info[0].__name__
            doc["error_message"] = str(exc_info[1])
            doc["error_trace"] = "".join(format_tb(record.exc_info[2]))

        return doc


class AmCATLogHandler(logging.Handler):
    def __init__(
        self, client: AmcatClient, index: str, extra_fields: Optional[list], extra_values: Optional[dict[str, str]]
    ):
        self.client = client
        self.index = index
        super().__init__()
        self.setFormatter(AmCATLogFormatter(extra_fields=extra_fields, extra_values=extra_values))

    def emit(self, record):
        global RECORD
        RECORD = record
        doc = self.formatter.format_to_amcat(record)
        self.client.upload_documents(index=self.index, articles=[doc], allow_unknown_fields=True)


def setup_amcat4pylogger(
    name: str,
    client: AmcatClient,
    index: str,
    level=logging.INFO,
    copy_console=True,
    extra_fields: Optional[list[str]] = None,
    **extra_values: dict[str, str],
):
    """Convenience function to configure logging with an AmCAT4 backend

    Args:
        name (str): Name of the logger
        client (AmcatClient): Backend to log to
        index (str): Index name to log to. Will be created if it doesn't exist
        level (_type_, optional): Minimum log level. Defaults to logging.INFO.
        copy_console (bool, optional): Also log to stdout? Defaults to True.
        extra_fields: Optional list of extra fields that should be included in logging. Their values can be specified in the log entries with the `extra=dict` argument .
        extra_values: Optional dict of extra field:value pairs that should be included. The fields will be included as extra fields, and the values will be automatically included with every log entry.

    Returns:
        a Logger object. If extra_values are specified, it will return a LogAdapter that includes the extra values.
    """
    # Set up basic logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Set up console / stream handler
    if copy_console:
        console_handler = logging.StreamHandler()
        format_string = f"[%(asctime)s-%(levelname)s-%(name)s] - %(message)s"
        console_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(console_handler)

    # Set up AmCAT index
    logger.info("Setting up AmCAT logger")
    if not client.check_index(index):
        logger.info("Creating index")
        client.create_index(index)
    fields = LOGGING_FIELDS
    if extra_fields:
        fields.update({f: "keyword" for f in extra_fields})
    if extra_values:
        fields.update({f: "keyword" for f in extra_values.keys()})

    client.set_fields(index, fields)

    handler = AmCATLogHandler(client, index, extra_fields=extra_fields, extra_values=extra_values)
    logger.addHandler(handler)
    return logger
