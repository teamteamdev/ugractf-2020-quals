#!/usr/bin/env python3

import hmac
import io
import json
import os
import PIL.Image
import qrcode
import sys

PREFIX = "ugra_no_firewood_required_for_now_"
SECRET = b"ostensible-unimodal-pole-spike-herself"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83,
          89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179,
          181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251]   

def ensure_prime(n):
    if n <= 2:
        return 2
    return max(i for i in PRIMES if i <= n)

def ensure_odd_nonprime(n):
    if n == 2:
        return 1
    if n in PRIMES or n % 2 == 0:
        for k in range(0, 256 - n, 2):
            if n + k + (1 - n % 2) not in PRIMES:
                return n + k + (1 - n % 2)
        else:
            return 255
    return n

def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]

    flag = get_flag()

    image = PIL.Image.open(os.path.join("private", "himself.png"))

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=4)
    qr.add_data(flag)
    qr.make(fit=True)
    code = qr.make_image(fill_color="black", back_color="white")

    pixels = image.load()
    code_pixels = code.get_image().load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pixels[x, y] = (ensure_prime if code_pixels[x, y] == 0 else ensure_odd_nonprime)(pixels[x, y])

    data = io.BytesIO()
    image.save(data, format="PNG")
    arr = bytearray(data.getvalue())

    with open(os.path.join(target_dir, "ancient-person.png"), "wb") as f:
        f.write(bytes(arr))

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
