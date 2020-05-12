#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import Crypto.Util.number  # pip install pycryptodome
import decimal

n = 639220509535296589964722099841808137521575230900899091649965100587075175857259231594546961107966791622273064144950814916211091808622505711135193998063508129778049789266786521665403311664305857674952505833188180586900118536492211781
e = 65537

ciphertext = 407158859532325243993765492115502989164731634900920150579598753597272891377437854991788691814831245835212273428123717560706892014567496879777016162054730984131413328476813501445023571617705633305036954468083929102935287132262687794


def get_p(n):
    # naive factorization
    i = 3
    while True:
        if n % i == 0:
            return i
        i += 1


def get_qr(n):
    # fermat method
    with decimal.localcontext() as ctx:
        ctx.prec = 1000
        a = int(decimal.Decimal(n).sqrt())

        while True:
            a += 1
            b2 = a ** 2 - n
            
            b = int(decimal.Decimal(b2).sqrt())

            if b * b == b2:
                return a + b, a - b

def decrypt():
    p = get_p(n)
    q, r = get_qr(n // p)

    phi = (p - 1) * (q - 1) * (r - 1)
    d = Crypto.Util.number.inverse(e, phi)

    m = pow(ciphertext, d, n)

    print(Crypto.Util.number.long_to_bytes(m))


if __name__ == "__main__":
    decrypt()
