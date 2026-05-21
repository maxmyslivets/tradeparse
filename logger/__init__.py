from loguru import logger as _logger
import sys

log = _logger
log.remove()
log.add(sys.stderr, level='INFO', format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>")
log.add(f"data/errors.log", level='ERROR', rotation="1 week")
