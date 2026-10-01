#!/bin/sh
# Pathspec exclusion test on a throwaway repository with harmless files.
# Every file contains the word "needle". A pattern is safe only if no path
# containing "holdout" or "nestor_secrets" (any case) comes back.
set -u
D="${1:?usage: pathspec_exclusion_test.sh <scratch directory OUTSIDE any repository>}/pathspec_repo"
rm -rf "$D"
mkdir -p "$D" && cd "$D" || exit 1
git init -q .
git config user.email t@example.invalid
git config user.name t
mkdir -p a b/c3_HOLDOUT_D c/c3_holdout_E holdout_dir a/nestor_secrets nestor_secrets NESTOR_SECRETS_UP
for f in normal.txt a/normal2.txt a/holdout_x.txt HOLDOUT_TOP.txt holdout_low.txt \
         b/c3_HOLDOUT_D/file.txt c/c3_holdout_E/file.txt holdout_dir/file.txt \
         a/nestor_secrets/k.txt nestor_secrets/k.txt NESTOR_SECRETS_UP/k.txt b/plain.txt; do
  echo needle > "$f"
done
git add -A . && git commit -q -m init
git --version
echo "tracked files: $(git ls-files | wc -l); risky by name: $(git ls-files | grep -i -c -E 'holdout|nestor_secrets')"

run() {
  label="$1"; shift
  out="$("$@" 2>&1)"
  total=$(printf '%s\n' "$out" | grep -c .)
  risky=$(printf '%s\n' "$out" | grep -i -c -E 'holdout|nestor_secrets')
  echo "[$label] returned=$total risky=$risky"
  printf '%s\n' "$out" | grep -i -E 'holdout|nestor_secrets' | sed 's/^/      LEAKS: /'
}

echo "--- git grep, repo-wide"
run "P0 brief       " git grep -l needle -- ':!**/*holdout*/**' ':!**/nestor_secrets/**'
run "P1 correction  " git grep -l needle -- ':!**/*holdout*/**' ':!**/*holdout*' ':!**/nestor_secrets/**'
run "P2 bare        " git grep -l needle -- ':!*holdout*' ':!*nestor_secrets*'
run "P3 icase       " git grep -l needle -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'
run "P4 icase+glob  " git grep -l needle -- ':(exclude,icase,glob)**/*holdout*/**' ':(exclude,icase,glob)**/*holdout*' ':(exclude,icase,glob)**/*nestor_secrets*/**'
echo "--- git grep, one positive path (a) plus exclusions"
run "P0 a           " git grep -l needle -- a ':!**/*holdout*/**' ':!**/nestor_secrets/**'
run "P3 a           " git grep -l needle -- a ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'
echo "--- git ls-files, repo-wide"
run "P0 brief       " git ls-files -- ':!**/*holdout*/**' ':!**/nestor_secrets/**'
run "P3 icase       " git ls-files -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'
echo "--- git ls-files, one positive path (a) plus exclusions (expect 1 file: a/normal2.txt)"
run "P0 a           " git ls-files -- a ':!**/*holdout*/**' ':!**/nestor_secrets/**'
run "P3 a           " git ls-files -- a ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'
run "P3 a + dummy   " git ls-files -- a zz_no_such_path ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*'
echo "--- git ls-files, one positive path (b) plus exclusions (expect 1 file: b/plain.txt)"
run "P1 b           " git ls-files -- b ':!**/*holdout*/**' ':!**/*holdout*'
run "P3 b           " git ls-files -- b ':(exclude,icase)*holdout*'
echo "--- repo-wide exclusion, then prefix filter (expect a/normal2.txt only)"
run "P3 then grep ^a/" sh -c "git ls-files -- ':(exclude,icase)*holdout*' ':(exclude,icase)*nestor_secrets*' | grep '^a/'"
