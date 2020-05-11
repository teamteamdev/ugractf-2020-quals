#!/usr/bin/env python3

import codecs
import hmac
import json
import os
import random
import sys

PREFIX = "ugra_i_love_emoji_"
SECRET = b"throne-teenager-arrow-touch-straw"
SALT_SIZE = 12

ALPHABET = "👍🤔"

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    flag = get_flag()

    binary = "".join([bin(ord(c))[2:].zfill(8) for c in flag])

    table = str.maketrans("01", ALPHABET)
    
    emoji = binary.translate(table)

    json.dump({
        "flags": [flag],
        "substitutions": {
            "review": emoji
        },
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
