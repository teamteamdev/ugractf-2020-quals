#!/usr/bin/env python3

import construct
import hmac
import json
import os
import pymp4.parser
import shutil
import sys
import subprocess
import tempfile

PREFIX = "ugra_like_and_subscribe_"
SECRET = b"immense-drain-bench-longevity-spontaneously"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + (hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]
                     .translate("".maketrans("0123456789", "abacadaeaf")))


def find_box(c, t):
    for b in c:
        if b.type == t:
            return b
    return None


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]

    flag = get_flag()

    with tempfile.TemporaryDirectory() as temp_dir:
        open(os.path.join(temp_dir, "flag-frame.svg"), "w").write(
            open(os.path.join("private", "flag-frame.svg")).read().replace("+++flag+++", flag.upper()))

        subprocess.check_call(["inkscape", "-z", "-e",
                               os.path.join(temp_dir, "flag-frame.png"), os.path.join(temp_dir, "flag-frame.svg")],
                              stdout=sys.stderr,
                              env={**os.environ,
                                   "FONTCONFIG_FILE": os.path.abspath(os.path.join("private", "fonts.conf"))})
        
        subprocess.check_call(["ffmpeg",
                               "-loop", "1", "-i", os.path.join(temp_dir, "flag-frame.png"),
                               "-c:v", "libx264", "-r", "25",
                               "-video_track_timescale", "12800", "-b:v", "256k", "-t", "0.04",
                               os.path.join(temp_dir, "flag-frame.mp4")])

        shutil.copy(os.path.join("private", "black.mp4"), os.path.join(temp_dir, "black.mp4"))
        open(os.path.join(temp_dir, "concat1.txt"), "w").write("file flag-frame.mp4\nfile black.mp4")
        subprocess.check_call(["ffmpeg",
                               "-skip_estimate_duration_from_pts", "1",
                               "-f", "concat", "-i", "concat1.txt",
                               "-vsync", "0", "-fflags", "+igndts+genpts", "-b:v", "256k",
                               os.path.join(temp_dir, "flag-tail-muted.mp4")],
                              cwd=temp_dir)

        subprocess.check_call(["ffmpeg",
                               "-skip_estimate_duration_from_pts", "1",
                               "-i", os.path.join(temp_dir, "flag-tail-muted.mp4"),
                               "-i", os.path.join("private", "directed-audio.aac"),
                               "-c:v", "copy", "-c:a", "copy",
                               os.path.join(temp_dir, "flag-tail.mp4")])

        shutil.copy(os.path.join("private", "directed-cut.mp4"), os.path.join(temp_dir, "directed-cut.mp4"))
        open(os.path.join(temp_dir, "concat2.txt"), "w").write("file directed-cut.mp4\nfile flag-tail.mp4")
        subprocess.check_call(["ffmpeg",
                               "-skip_estimate_duration_from_pts", "1",
                               "-f", "concat", "-i", "concat2.txt",
                               "-vsync", "0", "-fflags", "+igndts+genpts", "-b:v", "256k", "-c:a", "copy",
                               os.path.join(temp_dir, "anthem-clean.mp4")],
                              cwd=temp_dir)

        data = open(os.path.join(temp_dir, "anthem-clean.mp4"), "rb").read()
        boxes = []
        while data:
            box = pymp4.parser.Box.parse(data)
            boxes.append(box)
            data = data[box.end:]

        b = find_box(boxes, b"moov")
        b = find_box(b.children, b"trak")
        b = find_box(b.children, b"mdia")
        b = find_box(b.children, b"minf")
        b = find_box(b.children, b"stbl")
        b = find_box(b.children, b"stts")
        
        b.entries = [construct.Container(sample_count=599)(sample_delta=512),
                     construct.Container(sample_count=1)(sample_delta=1000000000),
                     construct.Container(sample_count=2)(sample_delta=1),
                     construct.Container(sample_count=25)(sample_delta=512),
                     construct.Container(sample_count=48)(sample_delta=20000000)]

        with open(os.path.join(target_dir, "anthem2.mp4"), "wb") as f:
            for b in boxes:
                f.write(pymp4.parser.Box.build(b))

    json.dump({"flags": [flag], "substitutions": {}, "urls": []}, sys.stdout)


if __name__ == "__main__":
    generate()
