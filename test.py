#!/usr/bin/env python
"""Small helper script for debugging stuff."""

from pollbot.db import get_session
from pollbot.helper.plot import get_user_activity


session = get_session()
image = get_user_activity(session)
