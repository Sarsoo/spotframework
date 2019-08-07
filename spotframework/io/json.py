import json
import os
import logging

logger = logging.getLogger(__name__)


def load_json(path):

    logger.info(f"{path}")

    if os.path.exists(path):
        with open(path, 'r') as fileobj:

            data = json.load(fileobj)
            return data

    else:
        logger.error("file doesn't exist")

    return None
