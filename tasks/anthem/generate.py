#!/usr/bin/env python3

import hmac
import json
import os
import sys
import subprocess
import tempfile

PREFIX = "ugra_do_the_guys_a_favor_"
SECRET = b"rotten-disproportional-gas-script-olive"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]

    flag = get_flag()

    with tempfile.TemporaryDirectory() as temp_dir:
        open(os.path.join(temp_dir, "hun.vtt"), "w").write(
            open(os.path.join("private", "hun.vtt")).read().replace("+++flag+++", '\u2009'.join(flag))
        )
        subprocess.check_call(["ffmpeg",
                               "-i", os.path.join("private", "directed-cut.webm"),
                               "-i", os.path.join("private", "eng.vtt"),
                               "-i", os.path.join("private", "fre.vtt"),
                               "-i", os.path.join("private", "ger.vtt"),
                               "-i", os.path.join(temp_dir,  "hun.vtt"),
                               "-i", os.path.join("private", "ita.vtt"),
                               "-i", os.path.join("private", "rus.vtt"),
                               "-i", os.path.join("private", "spa.vtt"),
                               "-i", os.path.join("private", "swe.vtt"),
                               "-i", os.path.join("private", "ukr.vtt"),
                               "-map", "0:v", "-map", "0:a",
                               "-map", "1", "-map", "2", "-map", "3",
                               "-map", "4", "-map", "5", "-map", "6",
                               "-map", "7", "-map", "8", "-map", "9",
                               "-c:v", "copy", "-c:a", "copy", "-c:s", "webvtt",
                               "-metadata:s:s:0", "language=eng",
                               "-metadata:s:s:1", "language=fre",
                               "-metadata:s:s:2", "language=ger",
                               "-metadata:s:s:3", "language=hun",
                               "-metadata:s:s:4", "language=ita",
                               "-metadata:s:s:5", "language=rus",
                               "-metadata:s:s:6", "language=spa",
                               "-metadata:s:s:7", "language=swe",
                               "-metadata:s:s:8", "language=ukr",
                               os.path.join(target_dir, "anthem.webm")])

    json.dump({"flags": [flag], "substitutions": {}, "urls": []}, sys.stdout)


if __name__ == "__main__":
    generate()
