#!/usr/bin/env python3

import base64
import gzip
import hmac
import json
import os
import sys

PREFIX = "ugra_vim_saves_the_world_"
SECRET = b"ostensible-unimodal-pole-spike-herself"
SALT_SIZE = 14

def get_flag():
    user_id = sys.argv[1]

    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    flag = get_flag()
    target_dir = sys.argv[2]

    with gzip.open("private/fs.gz") as f:
        data = f.read()
        data = data.replace(
            b'dWdyYV92aW1fc2F2ZXNfdGhlX3dvcmxkXzAxMjM0NTY3ODlhYmNk',
            base64.b64encode(flag.encode())
        )

        with gzip.open(os.path.join(target_dir, "data.img.gz"), "w") as fo:
            fo.write(data)

    
    json.dump({"flags": [flag]}, sys.stdout)


if __name__ == "__main__":
    generate()
