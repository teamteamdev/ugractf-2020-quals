#!/usr/bin/env python3

import sys
import zlib

from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP
from scapy.utils import rdpcap, wrpcap

# See https://github.com/yarrick/iodine/blob/master/src/base128.c for details
ALPHABET = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\274\275\276\277\300\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317\320\321\322\323\324\325\326\327\330\331\332\333\334\335\336\337\340\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357\360\361\362\363\364\365\366\367\370\371\372\373\374\375"

# useful shorthand
code = ALPHABET.index


def b128decode(data):
    if type(data) == str:
        data = data.encode()
    
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("str or bytes should be passed into function")

    index = 0
    result = bytearray()

    while True:
        if index + 1 >= len(data):
            break
        
        coefs = [
            2 ** (7 - index % 8) - 1,       # data[i]     &
            2 ** 7 - 2 ** (6 - index % 8)   # data[i + 1] & 
        ]

        shifts = [
            index % 8 + 1,  # <<
            6 - index % 8   # >>
        ]

        result.append(
            ((code(data[index])     & coefs[0]) << shifts[0])
            |
            ((code(data[index + 1]) & coefs[1]) >> shifts[1])
        )

        index += 1
        if index % 8 == 7:
            index += 1
    
    return bytes(result)


def get_base16_code(c):
    if c in range(65, 71):
        return c - 55
    if c in range(97, 103):
        return c - 87
    if c in range(48, 58):
        return c - 48
    raise ValueError("Invalid base16 character")


def get_base32_code(c):
    if c in range(65, 91): # uppercase
        return c - 65
    if c in range(97, 123): # lowercase
        return c - 97
    if c in range(48, 54):
        return c - 22
    raise ValueError("Invalid base32 character")


def b32decode_int(c):
    result = 0
    for i in c:
        result <<= 5
        result |= get_base32_code(i)
    return result


class ClientHeader:
    def __init__(self, pkt):
        self.uid      = get_base16_code(pkt[0])
        data = b32decode_int(pkt[1:4])
        # SSS FFFF DDD GGGG L
        self.useq     = (data >> 12) & 0b111
        self.ufrag    = (data >> 8)  & 0b1111
        self.dseq     = (data >> 5) & 0b111
        self.dfrag    = (data >> 1) & 0b1111
        self.last     = data & 1


class ServerHeader:
    def __init__(self, pkt):
        # C SSS FFFF DDD GGGG L
        data = pkt[0] << 8 | pkt[1]
        self.compress = (data >> 15) & 1
        self.useq     = (data >> 12) & 0b111
        self.ufrag    = (data >> 8)  & 0b1111
        self.dseq     = (data >> 5)  & 0b1111
        self.dfrag    = (data >> 1)  & 0b1111
        self.last     =  data & 1


def extract_iodine(root, source, destination):
    dns_packets = rdpcap(source)

    downstream = b''
    upstream = b''

    is_transfer = False
    real_packets = []

    for packet in dns_packets:
        if not packet.haslayer(DNS):
            continue
            
        if DNSRR in packet and len(packet[DNSRR].rdata) > 0:
            # downstream
            data = packet[DNSRR].rdata
            if isinstance(data, str):
                # should be some bug in scapy?
                data = data.encode()
            
            if not is_transfer:
                continue

            downstream += data[2:]

            headers = ServerHeader(data)
            if headers.last and len(downstream) > 0:
                try:
                    raw_data = zlib.decompress(downstream)
                    real_packets.append(IP(raw_data[4:]))
                except zlib.error:
                    pass

                downstream = b''
        elif DNSQR in packet:
            # client
            hostname = packet[DNSQR].qname
            if hostname[0] not in b"0123456789abcdefABCDEF":
                continue
                
            is_transfer = True
            
            if not hostname.endswith(root):
                print("Warning: skipped upstream packet:", hostname, file=sys.stderr)
                continue
            
            upstream += hostname[5:-len(root)].replace(b".", b"")

            headers = ClientHeader(hostname)
            if headers.last and len(upstream) > 0:
                try:
                    raw_data = zlib.decompress(b128decode(upstream))
                    real_packets.append(IP(raw_data[4:]))
                except zlib.error:
                    pass

                upstream = b''

    wrpcap(destination, real_packets)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: ./get_underlying_pcap.py .domain.tld. dump.pcap output.pcap", file=sys.stderr)
        sys.exit(1)
    
    root = sys.argv[1].encode()
    if not root.startswith(b".") or not root.endswith(b"."):
        print("Warning: TLD should start and end with dot.", file=sys.stderr)
    
    source = sys.argv[2]
    destination = sys.argv[3]

    extract_iodine(root, source, destination)
