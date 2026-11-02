#!/usr/bin/env bash
# Commit only the files you approve, with the message you write.
#
# Unlike pushit.sh this never stages everything and never pushes. It lists every
# changed file and asks about them one by one, then asks for the commit message,
# shows what will be committed, and commits that. The commit is authored by you
# (your git identity). No tool is credited as an author or co-author: the message
# you type is the message that is recorded.

set -u

cd "$(dirname "$0")" || exit 1

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "not a git repository: $(pwd)"
    exit 1
fi

git status --short

# Changed paths, one per line, with renames reduced to their new name.
changed=()
while IFS= read -r -d '' entry; do
    if [ "${entry:0:2}" = "R " ] || [ "${entry:0:2}" = "C " ]; then
        changed+=("${entry:3}")
        IFS= read -r -d '' _original || true      # rename/copy records carry the old path too
    else
        changed+=("${entry:3}")
    fi
done < <(git status --porcelain=v1 -z)

if [ "${#changed[@]}" -eq 0 ]; then
    echo "No changes to commit."
    exit 1
fi

files=()
total=${#changed[@]}
index=0
echo
echo "Answer for each changed file, one at a time."

for path in "${changed[@]}"; do
    index=$((index + 1))
    printf '[%d/%d] git add "%s"? [y/N] ' "$index" "$total" "$path"
    IFS= read -r answer || answer=""
    case "$answer" in
        y|Y|yes|YES) files+=("$path") ;;
        *) echo "  skipped" ;;
    esac
done

if [ "${#files[@]}" -eq 0 ]; then
    echo "No files chosen. Nothing committed."
    exit 1
fi

for path in "${files[@]}"; do
    git add -- "$path" || { echo "git add failed for $path"; exit 1; }
done

if git diff --cached --quiet; then
    echo "Those files have no changes to commit. Nothing to do."
    exit 1
fi

echo
echo "Staged:"
git diff --cached --stat

echo
echo "Write the commit message. One line per line, empty line to finish."

message=""
while :; do
    printf '> '
    IFS= read -r line || break
    [ -z "$line" ] && break
    message="${message}${line}"$'\n'
done
message="${message%$'\n'}"

if [ -z "$message" ]; then
    echo "No commit message. Unstaging the files you chose."
    git restore --staged -- "${files[@]}" 2>/dev/null || git reset -q -- "${files[@]}" 2>/dev/null
    exit 1
fi

echo
echo "About to commit ${#files[@]} file(s):"
printf '  %s\n' "${files[@]}"
echo "Message:"
printf '%s\n' "$message" | sed 's/^/  /'
echo
printf 'Continue? [y/N] '
IFS= read -r answer || answer=""
case "$answer" in
    y|Y|yes|YES) ;;
    *)
        echo "Aborted. Unstaging the files you chose."
        git restore --staged -- "${files[@]}" 2>/dev/null || git reset -q -- "${files[@]}" 2>/dev/null
        exit 1
        ;;
esac

if ! git commit -m "$message"; then
    echo "git commit failed. The files are still staged."
    exit 1
fi

echo
git --no-pager log -1 --format='committed %h by %an <%ae>'
echo "message:"
git --no-pager log -1 --format='%B' | sed 's/^/  /'
