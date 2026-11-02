#!/usr/bin/env python3
"""Check commit/PR headers only; bodies, footers and SemVer meaning are not validated."""
import argparse
import re
import subprocess
import sys


# This type allowlist is a team policy, not a restriction of the specification.
SUBJECT = re.compile(
    r'(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)'
    r'(?:\([A-Za-z0-9][A-Za-z0-9._/-]*\))?!?: \S[^\r\n]*'
)


def valid_subject(subject):
    return bool(SUBJECT.fullmatch(subject))


def git(*args):
    return subprocess.run(
        ['git', *args], check=True, capture_output=True, text=True,
        encoding='utf-8',
    ).stdout.strip()


def new_commits(base, head):
    # Resolve arguments before constructing a revision range; do not run a shell.
    base_sha = git('rev-parse', '--verify', '--end-of-options', base + '^{commit}')
    head_sha = git('rev-parse', '--verify', '--end-of-options', head + '^{commit}')
    output = git('log', '--no-merges', '--format=%H%x00%s', base_sha + '..' + head_sha)
    return [tuple(line.split('\0', 1)) for line in output.splitlines()]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='Base commit/ref; needs full Git history')
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--title', help='Also validate this PR title')
    args = parser.parse_args(argv)
    try:
        commits = new_commits(args.base, args.head)
    except subprocess.CalledProcessError:
        print('ERROR: cannot read the revision range; fetch the base/head history.', file=sys.stderr)
        return 2
    errors = [f'{sha[:12]}: {subject!r}' for sha, subject in commits
              if not valid_subject(subject)]
    if args.title is not None and not valid_subject(args.title):
        errors.append(f'PR title: {args.title!r}')
    if not commits:
        errors.append('No new non-merge commits in the selected range.')
    if errors:
        for error in errors:
            print('ERROR: ' + error, file=sys.stderr)
        print('Expected: type(scope optional)! optional: description; e.g. feat: add search', file=sys.stderr)
        return 1
    print(f'PASS: {len(commits)} non-merge commit(s)' + (' and PR title' if args.title is not None else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
