#!/usr/bin/env python3

import codecs
import hmac
import hashlib
import json
import os
import py_compile
import random
import sys
import tempfile

PREFIX = "ugra_shrunk_the_shrink_"
SECRET = b"truth-corruption-spare-recovery-drive"
SALT_SIZE = 12
MAX_TRIES = 17

def bytes_to_int(data):
    return int(codecs.encode(data, "hex"), 16)


def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def encrypt_flag(flag):
    hashed = hashlib.sha256(chr(MAX_TRIES).encode()).hexdigest()
    return [str(ord(a) ^ ord(b)) for a,b in zip(flag, hashed)]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    target_dir = sys.argv[2]

    flag = get_flag()
    hashed_flag = ' '.join(encrypt_flag(flag))

    with tempfile.TemporaryDirectory() as temp_dir:
        with open("private/shrink.el") as f:
            source = f.read()

        source = source.replace("FLAGFLAGFLAG", hashed_flag)
        
        with open(os.path.join(target_dir, "shrink.el"), "w") as f:
            f.write(source)
        
    json.dump({
        "flags": [flag]
    }, sys.stdout)


if __name__ == "__main__":
    generate()
