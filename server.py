"""Main Module"""

import argparse
import json
import logging

from flask import Flask
from flask_cors import CORS

from settings import Configurations

from src.api_v1 import v1

HOST = Configurations.HOST
PORT = Configurations.PORT
ORIGINS = Configurations.ORIGINS

app = Flask(__name__)

CORS(app, origins=json.loads(ORIGINS), supports_credentials=True)

app.register_blueprint(v1, name="v1", url_prefix="/v1")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", help="Set log level")
    args = parser.parse_args()

    log_level = args.logs or "debug"
    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"[!] Invalid Log Level '{log_level}'")

    logging.basicConfig(level=numeric_level)

    app.run(host=HOST, port=PORT)
