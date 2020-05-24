#!/usr/bin/env python3

import hmac
import json
import os
import sys

PREFIX = "ugra_my_main_backup_is_my_last_will_"
SECRET = b"elderly-grandpa-soviet-dated-straightforward"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


MORSE = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.", "g": "--.", "h": "....", "i": "..",
         "j": ".---", "k": "-.-", "l": ".-..", "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.",
         "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-", "y": "-.--", "z": "--..", "0": "-----",
         "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..",
         "9": "----.", "_": "..--.-"}


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]

    flag = get_flag()

    
    bits = "000".join(["0".join(("111" if p == "-" else "1") for p in MORSE[c]) for c in flag])
    bits += "0" * ((8 - len(bits) % 8) % 8)

    open(os.path.join(target_dir, "Новый документ"), "wb").write(int(bits, 2).to_bytes(len(bits) // 8, "big"))

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
