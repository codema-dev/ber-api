import json
from pathlib import Path

_DIRPATH = Path(__file__).parent.resolve()

with open(_DIRPATH / "defaults.json", "r") as json_file:
    DEFAULTS = json.load(json_file)

from .api import request_public_ber_db