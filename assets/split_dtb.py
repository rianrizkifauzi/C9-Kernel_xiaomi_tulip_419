#!/usr/bin/env python3
# Split a possibly-concatenated DTB blob into individual FDTs.
# Writes /tmp/dtb_NN.dtb and prints the list (one path per line) to stdout.
import sys, struct

data = open(sys.argv[1], 'rb').read()
MAGIC = b'\xd0\x0d\xfe\xed'
offs = [i for i in range(len(data) - 4) if data[i:i+4] == MAGIC]
sys.stderr.write("Found %d FDT blob(s)\n" % len(offs))
parts = []
for k, o in enumerate(offs):
    total = struct.unpack('>I', data[o+4:o+8])[0]
    if total <= 0 or o + total > len(data):
        continue
    blob = data[o:o+total]
    p = "/tmp/dtb_%02d.dtb" % k
    open(p, 'wb').write(blob)
    parts.append(p)
print("\n".join(parts))
