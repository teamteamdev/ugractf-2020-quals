#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hmac
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PREFIX1 = "ugra_nullptr_is_a_zero_"
PREFIX2 = "ugra_zerobyte_does_not_count_"
SECRET1 = b"snap-rubbish-fail-block-technique"
SALT1_SIZE = 16
SECRET2 = b"rough-limited-talented-software-snatch"
SALT2_SIZE = 12
SECRET3 = b"marathon-version-account-bottom-deer"
SALT3_SIZE = 12


def verify_token(token):
    left_token, right_token = token[:SALT1_SIZE], token[SALT1_SIZE:]

    signature = hmac.new(SECRET1, left_token.encode(), 'sha256').hexdigest()[:SALT1_SIZE]

    return signature == right_token


def get_flags(token):
    flag1 = PREFIX1 + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]
    flag2 = PREFIX2 + hmac.new(SECRET3, token.encode(), 'sha256').hexdigest()[:SALT3_SIZE]
    return flag1, flag2



def create_folder(token):
    directory = os.path.join(sys.argv[1], token)
    os.mkdir(directory)

    flag1, flag2 = get_flags(token)

    with open(os.path.join(directory, "flag1.txt"), "w") as f:
        f.write(flag1)
    with open(os.path.join(directory, "flag2.txt"), "w") as f:
        f.write(flag2)


def main():
    print("Your token: ", end="", flush=True)
    token = input()

    if not verify_token(token):
        print("Try again with a token in the problem statement.")
        return
    
    directory = os.path.join(sys.argv[1], token)

    if not os.path.exists(directory):
        create_folder(token)
    
    os.chdir(directory)

    print(BASE_DIR)

    binary = os.path.join(BASE_DIR, "melodrama")
    os.execve(binary, [binary], {})


if __name__ == "__main__":
    main()
