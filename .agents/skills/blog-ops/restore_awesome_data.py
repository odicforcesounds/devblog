#!/usr/bin/env python3
"""Restore the Awesome Index shelf files that are no longer JSON.

Commit 3e2792d left docs/awesome/data/ either empty or holding `git show`
output instead of the shelf JSON, so awesomeIndex.html cannot paint a single
tool. For every file under docs/awesome/data/ (index.json excepted) that does
not parse, take the newest revision in git history that does parse and write
that blob back.

    python3 .agents/skills/blog-ops/restore_awesome_data.py            # report only
    python3 .agents/skills/blog-ops/restore_awesome_data.py --apply    # write the files
"""

import glob
import json
import os
import subprocess
import sys

DATA = "docs/awesome/data"


def git(*args):
    return subprocess.run(("git",) + args, capture_output=True, text=True).stdout


def main(argv):
    apply_changes = "--apply" in argv
    paths = sorted(glob.glob(os.path.join(DATA, "*.json")))
    broken, healed, unrecoverable = [], [], []
    for path in paths:
        if path.endswith("index.json"):
            continue
        raw = open(path, encoding="utf-8", errors="replace").read()
        try:
            json.loads(raw)
            continue
        except Exception:
            broken.append(path)
        revisions = [line.split()[0] for line in
                     git("log", "--format=%h", "--date=short", "--", path).strip().splitlines()]
        for revision in revisions:
            blob = git("show", "%s:%s" % (revision, path))
            try:
                json.loads(blob)
            except Exception:
                continue
            healed.append((path, revision, len(blob)))
            if apply_changes:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(blob)
            break
        else:
            unrecoverable.append(path)
    print("shelf files: %d | broken: %d | recovered: %d"
          % (len(paths), len(broken), len(healed)))
    for path, revision, size in healed:
        print("  %-72s <- %s (%d bytes)" % (path, revision, size))
    for path in unrecoverable:
        print("  ! no good revision for", path)
    if not apply_changes:
        print("report only — rerun with --apply to write")
    return 1 if unrecoverable else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
