#!/usr/bin/env python3
# Patch lavender-base.dtsi fstab to NON-DYNAMIC (legacy) layout.
# Device lavender (crDroid 7.61) uses direct system/vendor partitions (no super/dynamic).
# Uses brace-counting to robustly find the fstab { ... }; block (handles nested + metadata sibling).
import sys, re

path = sys.argv[1]
with open(path) as f:
    content = f.read()

# Also fix vbmeta 'parts' to drop system_ext/product/odm (device only has system+vendor)
# parts = "vbmeta,boot,system,system_ext,product,vendor,odm,dtbo,recovery";
# -> parts = "vbmeta,boot,system,vendor,dtbo,recovery";
def fix_vbmeta_parts(text):
    m = re.search(r'parts\s*=\s*"([^"]*)"', text)
    if m:
        old = m.group(1)
        keep = [p for p in old.split(',') if p.strip() not in ('system_ext', 'product', 'odm')]
        newparts = ','.join(keep)
        text = text[:m.start(1)] + newparts + text[m.end(1):]
        print("Fixed vbmeta parts: " + old + " -> " + newparts)
    return text

content = fix_vbmeta_parts(content)

new_fstab = (
    'fstab {\n'
    '\t\t\tcompatible = "android,fstab";\n'
    '\t\t\tsystem {\n'
    '\t\t\t\tcompatible = "android,system";\n'
    '\t\t\t\tdev = "/dev/block/bootdevice/by-name/system";\n'
    '\t\t\t\ttype = "ext4";\n'
    '\t\t\t\tmnt_flags = "ro,barrier=1,discard";\n'
    '\t\t\t\tfsmgr_flags = "wait,avb";\n'
    '\t\t\t\tstatus = "ok";\n'
    '\t\t\t};\n'
    '\t\t\tvendor {\n'
    '\t\t\t\tcompatible = "android,vendor";\n'
    '\t\t\t\tdev = "/dev/block/bootdevice/by-name/vendor";\n'
    '\t\t\t\ttype = "ext4";\n'
    '\t\t\t\tmnt_flags = "ro,barrier=1,discard";\n'
    '\t\t\t\tfsmgr_flags = "wait,avb";\n'
    '\t\t\t\tstatus = "ok";\n'
    '\t\t\t};\n'
    '\t\t}'
)

# Find start of 'fstab {' (with any leading whitespace)
m = re.search(r'fstab\s*\{', content)
if not m:
    # No fstab block -> inject after vbmeta { ... };  using brace counting
    vm = re.search(r'vbmeta\s*\{', content)
    if not vm:
        print("ERROR: no fstab or vbmeta node found")
        sys.exit(1)
    # brace-count from vbmeta open to its close
    i = vm.end()
    depth = 1
    while i < len(content) and depth > 0:
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        i += 1
    # skip trailing ';'
    while i < len(content) and content[i] in ' \t\n': i += 1
    if i < len(content) and content[i] == ';': i += 1
    inject = "\n\n\t\t" + new_fstab + ";"
    content = content[:i] + inject + content[i:]
    print("Injected non-dynamic fstab block after vbmeta")
else:
    start = m.start()
    # brace-count to find matching close of fstab block
    i = m.end()
    depth = 1
    while i < len(content) and depth > 0:
        if content[i] == '{': depth += 1
        elif content[i] == '}': depth -= 1
        i += 1
    # i now points just after the closing '}' of fstab; include trailing ';'
    end = i
    while end < len(content) and content[end] in ' \t': end += 1
    if end < len(content) and content[end] == ';': end += 1
    # Replace [start:end] with new_fstab + ';'
    content = content[:start] + new_fstab + ";" + content[end:]
    print("Replaced existing fstab block (brace-counted) with non-dynamic version")

with open(path, 'w') as f:
    f.write(content)
print("DTS fstab patch done (non-dynamic)")
