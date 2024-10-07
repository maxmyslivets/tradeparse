from loguru import logger as _logger

log = _logger
log.add(f"data/errors.log", level='ERROR', rotation="5 seconds")
