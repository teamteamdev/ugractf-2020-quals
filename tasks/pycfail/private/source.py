import codecs
import sys

def get(a, b):
    if a >= b:
        arg1 = a - b
        arg2 = b
        return get(arg1, arg2)
    
    if a == 0:
        return b
    
    arg1 = b
    arg2 = a
    return get(arg1, arg2)


def main():
    p = 111
    q = 222

    print("Calculating result, wait....", end="\r", flush=True)

    scientific_result = get(p, q)

    print("Result is calculated!       ", flush=True)

    hexad = hex(scientific_result)[2:]

    print("Got:", codecs.decode(hexad, "hex"), flush=True)


if __name__ == "__main__":
    main()
