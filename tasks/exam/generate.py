#!/usr/bin/env python3

import hmac
import json
import os
import os.path
import random
import sys
import subprocess
import tempfile

PREFIX = "ugra_teacher_is_so_proud_of_you_"
SECRET = b"which-pagan-woodlands-scream-victoria"
SALT_SIZE = 12

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]

    random.seed(hmac.new(SECRET, str(user_id).encode(), "sha256").digest())

    flag = get_flag()

    flag_packed = ""
    for c in flag:
        t = 0
        while t < ord(c):
            t0 = min(random.randint(1, 15), ord(c) - t)
            flag_packed += f"\\x{t0:0x}"
            t += t0
        flag_packed += "\\x7f"

    with tempfile.TemporaryDirectory() as temp_dir:
        open(os.path.join(temp_dir, "history.cpp"), "w").write(
            open(os.path.join("private", "history.cpp")).read().replace("+++flag+++", flag_packed)
        )
        subprocess.check_call(["docker", "build", "-f", "Dockerfile", temp_dir])
        image_name = subprocess.run(["docker", "build", "-q", "-f", "Dockerfile", temp_dir], capture_output=True, check=True).stdout.decode("utf-8").strip()
        container_name = subprocess.run(["docker", "create", image_name], capture_output=True, check=True).stdout.decode("utf-8").strip()
        subprocess.check_call(["docker", "cp", f"{container_name}:/root/history", os.path.join(target_dir, "history")], stdout=subprocess.DEVNULL)
        subprocess.check_call(["docker", "rm", container_name], stdout=subprocess.DEVNULL)

    json.dump({"flags": [flag], "substitutions": {}, "urls": []}, sys.stdout)


if __name__ == "__main__":
    generate()
