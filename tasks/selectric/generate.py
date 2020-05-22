#!/usr/bin/env python3

import gzip
import hmac
import json
import os
import random
import subprocess
import sys
import tempfile

PREFIX = "ugra_does_one_like_new_3d_episodes_"
SECRET = b"orchestra-violation-brotherhood-tape-film"
SALT_SIZE = 9

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + (hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]
                     .translate(''.maketrans('a', random.choice('0123456789bcdef'))))

LETTERS = ('ÀÁÃÄÅĀĂĄÆÇĆĈĊČÐĎÈÉÊËĒĔĖĘĚĜĞĠĢĤĦÌÍÎÏĨĪĮİĬĴĶŁĿĽĹÑŃŇŅŊÒÓÔÕÖØŌŎŐŒŔŘŖŠŚŜŞȘŤȚŦŢÙÚÛÜŨŪŬŮŰŲŴẀẂ'
           'ẄŸÝŶŽŹŻàáâãäåāăąæçćĉċčđďèéêëēĕėęěĝğġģĥħıìíîïĩīįĭĵȷķłŀļĺľñńňņŉŋòóôõöøōŏőœŕřŗšśŝşșțŧţťùúû'
           'üũūŭůűųŵẁẃẅýÿŷžźżÞþßƒðſ∏∫Ω∆∑π√∞∂≈◊ℓ℮≤≥~‹›«»−±×÷¦<≠>*^€‘’“”‚„•–—¯¬™®©¤¢£¥ƒ…·¡¿°ªº¹²³⁄¼½¾'
           '‰µ¶§†‡≠,;:!?@#$&%`~^*()[]=-+<>|"АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯЁЂЃҐЄЇЉЊЋЌЎЏбвджзийкл'
           'мнптфцчшщъыьэюяёђѓґєїљњћќўџDFGJLNQRSUVWYZ')


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]
    random.seed(hmac.new(SECRET, str(user_id).encode(), "sha256").digest())

    flag = get_flag()

    letters = list(LETTERS)
    random.shuffle(letters)
    letters = letters[:200]
    fib = [5, 8]
    while len(fib) < len(flag) + 1:
        fib.append(fib[-1] + fib[-2])
    shift = random.randint(0, 199)
    fib = [i + shift for i in fib]

    for n, c in enumerate(flag + "."):
        idx = fib[n] % 200
        letters[(idx // 40) + (idx % 40) * 5] = c

    with tempfile.TemporaryDirectory() as temp_dir:
        for n, c in enumerate(letters):
            c_file = os.path.join(temp_dir, "char.stl")
            open(c_file, "wb").write(gzip.open(os.path.join("private", f"u{ord(c):04X}.stl.gz")).read())
            subprocess.check_call(["openscad", "-o", os.path.join(temp_dir, f"{n}.stl"),
                                   "-D", f"pos={n}", "-D", f"char={json.dumps(c_file)}",
                                   os.path.join("private", "char-import.scad")])
       
        with gzip.open(os.path.join(target_dir, "typewriter-ball.stl.gz"), "wb", compresslevel=9) as f:
            f.write(gzip.open(os.path.join("private", "ball.stl.gz")).read())
            for n in range(len(letters)):
                f.write(open(os.path.join(temp_dir, f"{n}.stl"), "rb").read().replace(b"OpenSCAD_Model", f"char{n}".encode()))

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
