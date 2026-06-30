"""Select the settings module based on the ``DJANGO_ENV`` environment variable.

``DJANGO_ENV=prod`` (or ``production``) loads production settings; anything else
(including unset) loads development settings.
"""

import os

_env = os.environ.get("DJANGO_ENV", "dev").lower()

if _env.startswith("prod"):
    from .prod import *  # noqa: F401,F403
else:
    from .dev import *  # noqa: F401,F403
