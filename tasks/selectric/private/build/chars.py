#!/usr/bin/env python3

import json
import subprocess
import tqdm

for c in tqdm.tqdm([i for i in open("chars.txt").read().strip()]):
    fn = f"u{ord(c):04X}.stl"
    subprocess.check_call(["openscad", "-o", fn, "-D", "char=" + json.dumps(c), "char.scad"])
    data = open(fn).read()
    open(fn, "w").write(data.replace("OpenSCAD_Model", fn.split(".")[0]))
