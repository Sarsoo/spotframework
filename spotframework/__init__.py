import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
formatter = logging.Formatter(log_format)

if os.environ.get('CLOUD', None):
    from google.cloud import logging as glogging
    from google.cloud.logging.handlers import CloudLoggingHandler

    client = glogging.Client()

    # handler = client.get_default_handler()
    handler = CloudLoggingHandler(client)

    handler.setFormatter(formatter)

    logger.addHandler(handler)
else:

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
