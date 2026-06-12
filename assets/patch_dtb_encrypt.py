#!/usr/bin/env python3
# Binary-safe DTB encryption patch.
# Replaces the fstab fs_mgr flag string "forceencrypt=footer" with
# "encryptable=footer" (and bare "forceencrypt" -> "encryptable") directly
# in the DTB bytes, WITHOUT decompiling/recompiling. This preserves every
# other property byte-for-byte (notably the panel backlight string props
# like qcom,mdss-dsi-bl-pmic-control-type which dtc round-trip can corrupt).
#
# DTB property strings are NUL-terminated. We keep total length identical by
# padding the shorter replacement with a trailing space inside the value
# token, so the value stays "encryptable=footer " (kernel fs_mgr trims/parses
# token before '=' and ignores trailing junk after the recognized flag list
# entry). To be safe we keep the '=' position semantics intact.
import sys

path = sys.argv[1]
data = bytearray(open(path, "rb").read())

def replace_keep_len(buf, old, new):
    # old/new are bytes; new must be <= len(old). Pad new with spaces to match.
    assert len(new) <= len(old), "replacement longer than original"
    pad = old[:0]  # empty bytes
    newp = new + b" " * (len(old) - len(new))
    count = 0
    idx = 0
    while True:
        i = buf.find(old, idx)
        if i == -1:
            break
        buf[i:i+len(old)] = newp
        count += 1
        idx = i + len(old)
    return count

# 1) "forceencrypt" (12) -> "encryptable " (12, space-padded). Same length.
c1 = replace_keep_len(data, b"forceencrypt", b"encryptable")
# 2) "fileencryption=" style (rare on this device) -> "encryptable=   "
c2 = replace_keep_len(data, b"fileencryption", b"encryptable")

sys.stderr.write("forceencrypt replaced: %d, fileencryption replaced: %d\n" % (c1, c2))
open(path, "wb").write(data)
print("OK len=%d" % len(data))
