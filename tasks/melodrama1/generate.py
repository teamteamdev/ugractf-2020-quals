#!/usr/bin/env python3

import codecs
import hmac
import json
import math
import os
import random
import sys
import tempfile

PREFIX = [
    "ugra_nullptr_is_a_zero_",
    "ugra_zerobyte_does_not_count_"
]

TOKEN_SECRET = b"snap-rubbish-fail-block-technique"
TOKEN_SALT_SIZE = 16

FLAG_SECRET = [
    b"rough-limited-talented-software-snatch",
    b"marathon-version-account-bottom-deer"
]
FLAG_SALT_SIZE = 12


def get_token():
    user_id = sys.argv[1]

    token1 = hmac.new(TOKEN_SECRET, str(user_id).encode(), "sha256").hexdigest()[:TOKEN_SALT_SIZE]
    token2 = hmac.new(TOKEN_SECRET, token1.encode(), "sha256").hexdigest()[:TOKEN_SALT_SIZE]
    
    return token1 + token2


def get_flag(i, token):
    return PREFIX[i] + hmac.new(FLAG_SECRET[i], token.encode(), "sha256").hexdigest()[:FLAG_SALT_SIZE]


def generate():
    if len(sys.argv) != 4:
        print("Usage: generate.py user_id target_dir tasks", file=sys.stderr)
        sys.exit(1)

    token = get_token()
    
    
    json.dump({
        f"melodrama{i + 1}": {
            "flags": [get_flag(i, token)],
            "substitutions": {},
            "urls": [],
            "bullets": [
                "<code>nc melodrama.q.2020.ugractf.ru 17493</code>",
                f"Токен: <code>{token}</code>"
            ]
        }
        for i in range(2)
    }, sys.stdout)


if __name__ == "__main__":
    generate()
