#!/usr/bin/env python3
"""
Fix backlight on lavender (A11 / S0NiX stock DTB) by retargeting the WLED node
to the WLED driver that actually exists in this kernel.

Root cause (verified):
  - Stock kernel_dtb is a multi-DTB blob. The board revision this device matches
    declares /soc/.../qcom,leds@d800 with compatible "qcom,qpnp-wled" (downstream
    QPNP WLED driver). That driver (drivers/leds/leds-qpnp-wled.c) is ABSENT in
    this 4.19 source tree.
  - The tree only ships drivers/video/backlight/qcom-spmi-wled.c (mainline WLED)
    which matches compatible "qcom,pm660l-spmi-wled".
  - With CONFIG_BACKLIGHT_QCOM_SPMI_WLED=y, mdss_dsi_panel routes BL_WLED through
    backlight_device_set_brightness(raw_bd). raw_bd is resolved via
    backlight_device_get_by_type(BACKLIGHT_RAW), which only exists if the WLED
    driver probed. Since the qpnp-wled node never binds, raw_bd is NULL and
    brightness never reaches the WLED hardware -> screen stuck bright.

Fix:
  Rewrite the qcom,leds@d800 "compatible" from "qcom,qpnp-wled" to
  "qcom,pm660l-spmi-wled" in every DTB blob that uses the downstream string.
  The reg layout (0xd800/0x100 ctrl + 0xd900/0x100 sink) is IDENTICAL across
  variants and the mainline driver reads reg by index (of_get_address 0/1), not
  by reg-names, so no further structural change is required. Downstream-only
  tuning props are ignored by the mainline driver (sane defaults applied).

Usage: python3 patch_dtb_wled.py <kernel_dtb>
Requires: pip install fdt
"""
import sys, struct

try:
    import fdt
except ImportError:
    sys.stderr.write("ERROR: python 'fdt' module required (pip install fdt)\n")
    sys.exit(2)

OLD = "qcom,qpnp-wled"
NEW = "qcom,pm660l-spmi-wled"
NODE = "qcom,leds@d800"
MAGIC = b"\xd0\x0d\xfe\xed"

def main():
    path = sys.argv[1]
    data = open(path, "rb").read()

    # locate each FDT blob
    offs = []
    i = 0
    while True:
        j = data.find(MAGIC, i)
        if j == -1:
            break
        offs.append(j)
        i = j + 4
    if not offs:
        sys.stderr.write("ERROR: no FDT magic found in %s\n" % path)
        sys.exit(3)

    sys.stderr.write("Found %d DTB blob(s)\n" % len(offs))

    out = bytearray()
    cursor = 0
    patched_total = 0

    for idx, off in enumerate(offs):
        # copy any bytes between previous blob end and this magic verbatim
        if off > cursor:
            out += data[cursor:off]
        total = struct.unpack(">I", data[off+4:off+8])[0]
        blob = data[off:off+total]

        changed = False
        try:
            dt = fdt.parse_dtb(blob)
            # find target node(s)
            def walk(node):
                nonlocal changed
                if node.name == NODE:
                    prop = node.get_property("compatible")
                    if prop is not None:
                        # fdt PropStrings: .value may be str or list
                        val = None
                        try:
                            val = prop.value
                        except Exception:
                            val = None
                        cur = val if isinstance(val, str) else (val[0] if val else None)
                        if cur == OLD:
                            node.set_property("compatible", NEW)
                            changed = True
                for ch in node.nodes:
                    walk(ch)
            walk(dt.root if hasattr(dt, "root") else dt.get_node("/"))

            if changed:
                newblob = dt.to_dtb(version=17)
                # ensure new blob keeps a valid totalsize header (fdt does this)
                out += newblob
                patched_total += 1
                sys.stderr.write("DTB[%d]: compatible %s -> %s (rebuilt, %d->%d bytes)\n"
                                 % (idx, OLD, NEW, total, len(newblob)))
            else:
                out += blob
                sys.stderr.write("DTB[%d]: no qpnp-wled target, kept as-is\n" % idx)
        except Exception as e:
            sys.stderr.write("DTB[%d]: parse/build failed (%s), kept as-is\n" % (idx, e))
            out += blob

        cursor = off + total

    # copy any trailing bytes after the last blob
    if cursor < len(data):
        out += data[cursor:]

    open(path, "wb").write(out)
    sys.stderr.write("Patched %d/%d DTB blob(s). New file size: %d (was %d)\n"
                     % (patched_total, len(offs), len(out), len(data)))
    print("OK wled_patch patched=%d total=%d size=%d" % (patched_total, len(offs), len(out)))

if __name__ == "__main__":
    main()
