#!/usr/bin/env python3

import codecs
import hmac
import json
import os
import py_compile
import random
import sys
import tempfile

PREFIX = "ugra_weird_gcd_calculation_"
SECRET = b"truth-corruption-spare-recovery-drive"
SALT_SIZE = 12


def bytes_to_int(data):
    return int(codecs.encode(data, "hex"), 16)


def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    target_dir = sys.argv[2]

    flag = get_flag()

    gcd = bytes_to_int(flag.encode())

    with tempfile.TemporaryDirectory() as temp_dir:
        with open("private/source.py") as f:
            source = f.read()

        source = source.replace("111", str(37 * gcd)).replace("222", str(512345 * gcd))
        
        with open(os.path.join(temp_dir, "file.py"), "w") as f:
            f.write(source)
        
        py_compile.compile(
            os.path.join(temp_dir, "file.py"),
            os.path.join(target_dir, "recovered-001.pyc"),
            "s3cr3t_5c13nc3_j0b.py",
            optimize=2
        )

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
