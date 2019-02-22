# Logmatic

This is a simple logger for Python 3.6+ apps. It wraps the Python logging library with some default configs, and has optional integration for 3rd party logging systems.

## Quick Start Guide

```python
from logmatic import log

# Log some normal information.
log.info("Hello World")

# Add some arbitrary data.
log.info("Hello World", {"greeting_count": 1})

# WARNING: For things that aren't breaking, but should be avoided.
log.warning("Be careful!")

# ERROR: Things that are breaking and need to be fixed.
log.error("This is an error.")

# CRITICAL: This is for something major that will cause a system failure.
log.critical("We are on fire.")
```

```python
# Metric Logging: DataDog integration.
log.increment("my_app.my_metric_name", 1)
log.gauge("my_app.another_metric", 0.786)
```

## ENV Setup

```bash
# In logmatic.env
JSON_LOGGER__ACTIVE=1
JSON_LOGGER__PATH=./logs/output.json.log

FILE_LOGGER__ACTIVE=1
FILE_LOGGER__PATH=./logs/output.logUpdate

ROTATION__INTERVAL_UNIT=d
ROTATION__INTERVAL_VALUE=1
ROTATION__BACKUP_COUNT=30

# For DD integration. 
DATADOG__ACTIVE=0  # 0 | 1
DATADOG__API_KEY=REDACTED
DATADOG__APP_KEY=REDACTED
DATADOG__HTTP_LOG_ACTIVE=0 # 0 | 1
DATADOG__HOST=logmatic-tests
DATADOG__SERVICE=logmatic-tests

PRINT_GAP=1
```