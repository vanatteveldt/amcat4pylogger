# AmCAT4pylogger

Simple Python Logger facility with AmCAT backend

# Installation

```
pip install amcat4pylogger
```

# Usage

You can use the `AmCATLogHandler` directly, but it's more convenient to use the `setup_amcat4pylogger` helper function.
This function checks the AmCAT index and fields and configures the log handler.

Example:

```{py}
import amcat4py
from amcat4pylogger.amcat4pylogger import setup_amcat4pylogger

client = amcat4py.AmcatClient("http://localhost:5000")
logger = setup_amcat4pylogger("testapp", client, index="log_index")
logger.info("A message")
```

If desired, you can add `**extra_values` which will be added to each log entry for this handler.
You can also add `extra_fields`, which allows for additional information to be passed with each log entry.
By default these fields will be added as `keyword` fields, you can create the fields before setting up the logging
to change this.

```
logger = setup_amcat4pylogger("testapp", client, index="log_index", extra_fields=["status"], project="Paperclip")

logger.info("Feeling blue today", extra={"status": "blue"})
```
