from __future__ import annotations
from spotframework.model.user import PublicUser
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class NetworkUser:
    client_id: str
    client_secret: str

    access_token: str = None
    refresh_token: str = None

    user: PublicUser = field(default=None, init=False)

    last_refreshed: datetime = field(default=None, init=False)
    token_expiry: datetime = field(default=None, init=False)

    on_refresh: List = field(default_factory=list, init=False)

    refresh_counter: int = field(default=0, init=False)
