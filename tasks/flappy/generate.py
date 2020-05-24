#!/usr/bin/env python3

import hmac
import json
import hashlib
import os
import sys

PREFIX = "ugra_moore_is_flapping_in_his_dreams_"
SECRET = b"2mZ3nGKCdz5aLKqc"
SALT_SIZE = 63 - len(SECRET)


def encode_flag(flag):
    prefix = flag[:48]
    suffix = flag[48:64]

    xor_value = 17

    encoded_prefix = bytearray()
    for c in prefix:
        encoded_prefix.append(ord(c) ^ xor_value)
        xor_value = (xor_value + 13) % 256
    encoded_prefix.append(ord('%') ^ xor_value)

    encoded_suffix = bytearray()
    for c in suffix:
        encoded_suffix.append(ord(c) ^ xor_value)
        xor_value = (xor_value + 13) % 256
    encoded_suffix.append(ord('%') ^ xor_value)

    return (bytes(encoded_prefix), bytes(encoded_suffix))


def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    target_dir = sys.argv[2]

    flag = get_flag()
    prefix, suffix = encode_flag(flag)

    data = open(os.path.join("private", "flappy.exe"), "rb").read()
    data = data.replace(b"PREFIX__________________________________________\0", prefix)
    data = data.replace(b"SUFFIX__________\0", suffix)
    open(os.path.join(target_dir, "flappy.exe"), "wb").write(data)

    decoded_suffix = flag[48:64]
    for i in range(43):
        m = hashlib.md5()
        m.update(decoded_suffix.encode("utf-8"))
        decoded_suffix = m.hexdigest()[:len(decoded_suffix)]

    new_flag = flag[:48] + decoded_suffix

    json.dump({
        "flags": [new_flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
