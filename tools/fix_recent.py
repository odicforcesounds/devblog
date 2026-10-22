#!/usr/bin/env python3
from pathlib import Path

path = Path('tools/debug_recent.js')
text = path.read_text(encoding='utf-8')
lines = text.splitlines(True)
out = []
for line in lines:
    if "html.match(/<script>(" in line and "</script>/);" in line:
        line = line.replace(
            "html.match(/<script>([\\\\s\\\\S]*?)<\\\\/script>/);",
            "html.match(/<script>([\\s\\S]*?)<\\/script>/);"
        )
    out.append(line)
path.write_text(''.join(out), encoding='utf-8')
print('rewrote:', path)
