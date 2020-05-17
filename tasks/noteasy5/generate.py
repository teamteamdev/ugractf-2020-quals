#!/usr/bin/env python3

import hmac
import json
import os
import sys

PREFIX = "ugra_rituals_may_vary_and_so_do_quirks_"
SECRET = b"mundane-exhibition-wavelength-thick-pinroll"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + (hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]
                     .translate(''.maketrans('0123456789', 'bcdeffedcb')))


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]

    flag = get_flag()
    flag_enc = flag.translate(''.maketrans('abcdepqrsfoxytgnwvuhmlkji', 'aponmbqxwlcryvkdstujefghi'))

    open(os.path.join(target_dir, "noteasy5.txt"), "w").write(flag_enc)

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
