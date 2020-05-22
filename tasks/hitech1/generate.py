#!/usr/bin/env python3

import codecs
import hmac
import json
import math
import os
import random
import sys
import tempfile

PREFIX = "ugra_vim_saves_the_world_"
SECRET = b"ostensible-unimodal-pole-spike-herself"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]

    return hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    flag = get_flag()
    target_dir = sys.argv[2]

    with open(os.path.join(target_dir, "data.img"), "w") as f:
        f.write("Kek")
    
    
    json.dump({"flags": [flag]}, sys.stdout)


if __name__ == "__main__":
    generate()
