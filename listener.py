import os
import logging

import click
from spotframework.listener.cmd import ListenCmd
from spotframework.net.network import Network, NetworkUser

logger = logging.getLogger('spotframework')

if not os.path.exists('.spot'):
    os.mkdir('.spot')

log_format = '%(asctime)s %(levelname)s %(name)s:%(funcName)s - %(message)s'

file_handler = logging.FileHandler(".spot/listener.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

stream_log_format = '%(levelname)s %(name)s:%(funcName)s - %(message)s'
stream_formatter = logging.Formatter(stream_log_format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


@click.command()
@click.option('-v', '--verbose', is_flag=True)
@click.option('--client-id', prompt=True, default=lambda: os.environ.get('SPOT_CLIENT', ''))
@click.option('--client-secret', prompt=True, default=lambda: os.environ.get('SPOT_SECRET', ''))
@click.option('--refresh-token', prompt=True, default=lambda: os.environ.get('SPOT_REFRESH', ''))
def listen(verbose, client_id, client_secret, refresh_token):
    if verbose:
        stream_handler.setLevel('DEBUG')
    else:
        stream_handler.setLevel('WARNING')

    net = Network(NetworkUser(client_id=client_id,
                              client_secret=client_secret,
                              refresh_token=refresh_token)).refresh_access_token()
    cmd = ListenCmd(net, stream_handler)
    cmd.cmdloop()


if __name__ == '__main__':
    listen()
