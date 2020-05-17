#!/usr/bin/env python3

import hmac
import json
import io
import math
import os
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import random
import re
import sys
import subprocess
import tempfile
import xml.etree.ElementTree

PREFIX = "ugra_apply_now_for_senior_ai_researcher_"
SECRET = b"town-ludicrous-christian-promotion-rinse"
SALT_SIZE = 10

def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)
    user_id = sys.argv[1]
    target_dir = sys.argv[2]
    random.seed(hmac.new(SECRET, str(user_id).encode(), "sha256").digest())

    flag = get_flag()

    etalons_xml = xml.etree.ElementTree.parse(open(os.path.join("private", "etalons.svg")))
    etalons = {}
    for n, c in enumerate(etalons_xml.getroot().findall("{http://www.w3.org/2000/svg}path")):
        if n % 4 == 0:
            etalons[n // 4] = []
        etalons[n // 4].append(c.attrib["d"])
    
    font = PIL.ImageFont.load(os.path.join("private", "ter-u14b_iso-8859-1.pil"))

    image = PIL.Image.new("RGB", (len(flag) * 8 + 1, 14))
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            image.putpixel((x, y), tuple(int(127 + c * 127) for c in [math.sin(30 + 0.03 * (2 * x + 3 * y)),
                                                                      math.sin(40 + 0.04 * (4 * x - 1 * y)),
                                                                      math.sin(50 + 0.02 * (5 * x - 8 * y))]))

    text_image = PIL.Image.new("RGB", (len(flag) * 8 + 1, 14))
    draw = PIL.ImageDraw.ImageDraw(text_image)
    draw.text((1, -1), flag, font=font, fill=(255, 255, 255))

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if text_image.getpixel((x, y)) == (255, 255, 255):
                image.putpixel((x, y), tuple(255 - c for c in image.getpixel((x, y))))
    
    image = image.convert("P", palette=PIL.Image.WEB)
    image_io = io.BytesIO()
    image.save(image_io, format="BMP")

    data = image_io.getvalue()

    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, "1.svg"), "w") as svg:
            R = re.compile("-?\d+\.\d+")
            LINE_LENGTH = 74  # BMP size is known to be divisible by this number
            svg.write(f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                          <svg xmlns="http://www.w3.org/2000/svg" width="{28 * 3 * LINE_LENGTH}"
                                                                  height="{28 * len(data) // LINE_LENGTH}">\n"""
                       """<style>svg { fill: black; }
                                 .p { stroke: white; fill: none; stroke-linecap: round; stroke-linejoin: round } </style>
                          <rect width="100%" height="100%" fill="black"/>\n""")
            for n, ch in enumerate(data):
                for dn, digit in enumerate(f"{ch:03d}"):
                    svg.write(f"""<g transform="translate({28 * 3 * (n % LINE_LENGTH)} {28 * (n // LINE_LENGTH)})
                                                translate({28 * dn} 0) scale(0.8 0.8) translate(3 3)">""")
                    d = random.choice(etalons[int(digit)])
                    d = R.sub(lambda m: "%.6f" % (float(m.group(0)) + random.random() * 3 - 1.5), d)
                    svg.write(f'<path d="{d}" class="p" style="stroke-width:{random.randint(20, 45) * 0.1}px" />')
                    svg.write("</g>\n")
            svg.write("</svg>")
        # or probably: dbus-run-session inkscape -z -e ...
        subprocess.check_call(["inkscape", "-z", "-e", os.path.join(target_dir, "mnistry-data.png"), os.path.join(temp_dir, "1.svg")])

    json.dump({"flags": [flag], "substitutions": {}, "urls": []}, sys.stdout)


if __name__ == "__main__":
    generate()
