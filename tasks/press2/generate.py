#!/usr/bin/env python3

import codecs
import hmac
import json
import math
import os
import random
import sys
import tempfile

PREFIX = "ugra_zerobyte_does_not_count_"
SECRET1 = b"snap-rubbish-fail-block-technique"
SALT1_SIZE = 16
SECRET2 = b"marathon-version-account-bottom-deer"
SALT2_SIZE = 12


def get_user_tokens():
    user_id = sys.argv[1]

    token1 = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:SALT1_SIZE]
    token2 = hmac.new(SECRET1, token1.encode(), "sha256").hexdigest()[:SALT1_SIZE]
    token = token1 + token2

    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]

    return token, flag


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    token, flag = get_user_tokens()

    json.dump({
        "flags": [flag],
        "substitutions": {"token": token},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
