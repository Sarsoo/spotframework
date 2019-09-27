from spotframework.net.user import NetworkUser
from spotframework.net.network import Network

import os
import logging

logger = logging.getLogger('spotframework')
stream_log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
stream_formatter = logging.Formatter(stream_log_format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

logger.addHandler(stream_handler)

if __name__ == '__main__':

    network = Network(NetworkUser(os.environ['SPOTCLIENT'],
                                  os.environ['SPOTSECRET'],
                                  os.environ['SPOTREFRESH']))
    network.user.refresh_token()

    print(network.user.access_token)
