import json
import os

import spotframework.log.log as log


def load_json(path):

    log.log("load json", path)

    if os.path.exists(path):
        with open(path, 'r') as fileobj:

            data = json.load(fileobj)
            return data

    else:
        log.log("load json", "file doesn't exist")

    return None
