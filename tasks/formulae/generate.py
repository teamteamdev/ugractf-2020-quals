#!/usr/bin/env python3

import hmac
import json
import os
import random
import sys
import xlsxwriter

PREFIX = "ugra_school_informatics_isnt_that_useless_"
SECRET = b"carbon-menace-corollary-union-wool"
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

    workbook = xlsxwriter.Workbook(os.path.join(target_dir, "Formulæ.xlsx"))
    for real in [True, False]:
        worksheet = workbook.add_worksheet("Лист1" if real else "Лист2")
        data = ("x" * len(flag)) if real else "helloabc"
        real_data = flag if real else data

        permutation = list(range(len(data)))
        random.shuffle(permutation)
        permutation = {k: next_k for k, next_k in zip(permutation, permutation[1:] + [None])}

        for n, (c0, c1) in enumerate(zip(real_data[0] + real_data[:-1], real_data)):
            n0 = max(n - 1, 0)
            x0, x1 = ord(c0), ord(c1)
            b = -(x0 + x1)
            c = x0 * x1
            a = random.randint(1, 30)
            if a > 20:
                a = 1
            if random.random() < 0.5:
                a *= -1
            b, c = b * a, c * a

            a_ = "" if a == 1 else ("-" if a == -1 else f"{a}*")
            b_ = f"- {-b}" if b < 0 else f"+ {b}"
            c_ = f"- {-c}" if c < 0 else f"+ {c}"
            guard = f"EE{permutation[n] + 1}=1" if permutation[n] is not None else "2 + 2 = 4"
            worksheet.write_formula(n, 134, f"=IF(({guard}) AND ({a_}(CODE(A{n0+1})^2) {b_}*CODE(A{n0+1}) {c_} = 0) AND "
                                            f"({a_}(CODE(A{n+1})^2) {b_}*CODE(A{n+1}) {c_} = 0), 1, 0)",
                                    None, 0 if real else 1)

        for n, c in enumerate(data):
            worksheet.write(n, 0, c)

        worksheet.write_formula(len(data) + 1, 0, "=IF(PRODUCT(EE1:EE%d)=1, \"ПРАВИЛЬНО\", \"НЕПРАВИЛЬНО\")" % len(data),
                                None, "НЕПРАВИЛЬНО" if real else "ПРАВИЛЬНО")

        f1 = workbook.add_format({"bg_color": "#22BB00", "font_color": "#FFFFFF"})
        f2 = workbook.add_format({"bg_color": "#FF0011", "font_color": "#FFFFFF"})
        for f in [{"type": "text", "criteria": "begins with", "value": "ПРАВИЛЬНО", "format": f1},
                  {"type": "text", "criteria": "begins with", "value": "НЕПРАВИЛЬНО", "format": f2}]:
            worksheet.conditional_format(len(data) + 1, 0, len(data) + 1, 0, f)

        ff = workbook.add_format()
        ff.set_align("center")
        worksheet.set_column(0, 0, 20, ff)

    workbook.add_worksheet("Лист3")
    workbook.close()

    json.dump({
        "flags": [flag],
        "substitutions": {},
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
