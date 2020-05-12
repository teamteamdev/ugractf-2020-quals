#!/usr/bin/env python3

import codecs
import hmac
import json
import math
import os
import random
import sys
import tempfile

PREFIX = "ugra_3rsa_is_secure_unless_you_get_bad_primes_"
SECRET = b"architech-treaty-loot-infection-thesis"
SALT_SIZE = 16


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    _, x, _ = egcd(a, m)
    return x % m


def is_prime(n):  
    # Base check
    
    prime_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    
    for prime in prime_list:
        if n % prime == 0:
            return False
    
    # Miller-Rabin primality test
    
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    
    for _ in range(64):
        a = random.randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    
    return True


def generate_prime_number(length):
    found_prime = False
    
    while not found_prime:
        p = random.getrandbits(length)
        p |= (1 << length - 1) | 1
        
        found_prime = is_prime(p)
    
    return p


def bytes_to_int(data):
    return int(codecs.encode(data, "hex"), 16)


def get_flag():
    user_id = sys.argv[1]
    random.seed(hmac.new(SECRET, str(user_id).encode(), "sha256").digest())
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) != 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    flag = get_flag()

    while True:
        p = generate_prime_number(16)
        q = generate_prime_number(376)

        print("p, q")
        
        r = q + generate_prime_number(42) + 1
        while not is_prime(r):
            r += 2
            print(".", end='')
        print("\rr")
        phi = (p - 1) * (q - 1) * (r - 1)
        e = 65537

        if math.gcd(e, phi) == 1:
            break
            
        print("fail")

    n = p * q * r
    d = modinv(e, phi)

    m = bytes_to_int(flag.encode())
    c = pow(m, e, n)

    json.dump({
        "flags": [flag],
        "substitutions": {
            "n": n,
            "p": p,
            "q": q,
            "r": r,
            "phi": phi,
            "e": e,
            "d": d,
            "m": m,
            "ciphertext": c
        },
        "urls": []
    }, sys.stdout)


if __name__ == "__main__":
    generate()
