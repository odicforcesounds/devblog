#!/usr/bin/env bash
# Commit each file you approve on its own, with its own message.
#
# Lives in .agents/skills/blog-ops/ and can be run from any directory inside the
# repository: it resolves the root first, so the paths you type are the paths git
# shows you.
#
# Unlike pushit.sh this never stages everything and never pushes. It lists every
# changed file and asks about them one by one; for each accepted file it prints
# what changed in it — the diffstat and the first changed lines, or the size of a
# new file — and then asks for that file's message, so the message can say what
# actually changed there and why. It commits the files one commit at a time. The
# commits are authored by you (your git identity). No tool is credited as an
# author or co-author: the messages you type are the messages that are recorded.

set -u

here="$(cd "$(dirname "$0")" && pwd)"
root="$(git -C "$here" rev-parse --show-toplevel 2>/dev/null)" || {
    echo "not a git repository: $here"
    exit 1
}
cd "$root" || exit 1

git status --short

# Changed paths, one per line, with renames reduced to their new name.
# Only files that exist in the working tree can be committed, so drop
# deletions and any path whose leaf does not exist locally.
changed=()
while IFS= read -r -d '' entry; do
    if [ "${entry:0:2}" = "R " ] || [ "${entry:0:2}" = "C " ]; then
        changed+=("${entry:3}")
        IFS= read -r -d '' _original || true
    else
        changed+=("${entry:3}")
    fi
done < <(git status --porcelain=v1 -z)

if [ "${#changed[@]}" -eq 0 ]; then
    echo "No changes to commit."
    exit 1
fi

kept=()
for path in "${changed[@]}"; do
    if git ls-files --error-unmatch -- "$path" >/dev/null 2>&1 || [ -e "$path" ]; then
        kept+=("$path")
    else
        echo "skip (not in the index and no local file): $path"
    fi
done
changed=("${kept[@]}")

# Untracked files that exist on disk are commitable too, even when git index
# does not know them yet (e.g. a brand-new script). Their ls-files above
# reported an error, but they are real files, so keep them.
for path in "${changed[@]}"; do
    if ! git ls-files --error-unmatch -- "$path" >/dev/null 2>&1 && [ -e "$path" ]; then
        git add -- "$path" >/dev/null 2>&1
    fi
done
changed=("${kept[@]}")
if [ "${#changed[@]}" -eq 0 ]; then
    echo "Nothing can be committed."
    exit 1
fi

files=()
messages=()
total=${#changed[@]}
index=0
echo
echo "Answer for each changed file, one at a time."

for path in "${changed[@]}"; do
    index=$((index + 1))
    printf '[%d/%d] git add "%s"? [y/N] ' "$index" "$total" "$path"
    IFS= read -r answer || answer=""
    case "$answer" in
        y|Y|yes|YES) ;;
        *)
            echo "  skipped"
            continue
            ;;
    esac
    echo "  what changed in \"$path\":"
    if git ls-files --error-unmatch -- "$path" >/dev/null 2>&1; then
        git --no-pager diff --stat -- "$path" | sed 's/^/    /'
        git --no-pager diff --unified=0 -- "$path" \
            | grep -E '^[-+][^-+]' | head -n 6 | sed 's/^/    /'
    else
        echo "    new file, $(wc -l < "$path") lines"
    fi
    printf '  message for "%s", saying what changed here and why (empty to skip): ' "$path"
    IFS= read -r message || message=""
    if [ -z "$message" ]; then
        echo "  no message, skipped"
        continue
    fi
    files+=("$path")
    messages+=("$message")
done

if [ "${#files[@]}" -eq 0 ]; then
    echo "No files chosen. Nothing committed."
    exit 1
fi

echo
echo "About to make ${#files[@]} commit(s):"
for i in "${!files[@]}"; do
    printf '  "%s"  ->  %s\n' "${files[$i]}" "${messages[$i]}"
done
echo
printf 'Continue? [y/N] '
IFS= read -r answer || answer=""
case "$answer" in
    y|Y|yes|YES) ;;
    *)
        echo "Aborted. Nothing was committed."
        exit 1
        ;;
esac

failed=""
for i in "${!files[@]}"; do
    path="${files[$i]}"
    message="${messages[$i]}"
    if ! git add -- "$path"; then
        echo "git add failed for $path"
        failed="$path"
        break
    fi
    if ! git commit -m "$message"; then
        echo "git commit failed for $path; it is left staged."
        failed="$path"
        break
    fi
    echo "committed $path: $message"
done

echo
echo "Commits made in this run:"
git --no-pager log --format='  %h %s' -n "${#files[@]}"

if [ -n "$failed" ]; then
    echo
    echo "Stopped at: $failed"
    exit 1
fi
