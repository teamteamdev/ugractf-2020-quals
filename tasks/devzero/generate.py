#!/usr/bin/env python3

import codecs
import hmac
import json
import os
import random
import sys
import tempfile

PREFIX = "ugra_did_you_ever_feel_that_clean_"
SECRET1 = b"splash-trouble-chemistry-mansion-hen"
SALT1_SIZE = 16
SECRET2 = b"metal-chimney-fork-unleash-vertigo"
SALT2_SIZE = 12


def get_user_tokens():
    user_id = sys.argv[1]

    token = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:SALT1_SIZE]
    flag = PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]

    return token, flag


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    token, flag = get_user_tokens()

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": [f"https://devzero.{{hostname}}/{token}/dev/zero"]
    }, sys.stdout)


if __name__ == "__main__":
    generate()
