"""Conservative changed-file classification for CI and release selection."""
import json
import os
from pathlib import Path
import re
import subprocess


def classify(paths, manual=False):
    def documentation(path):
        if path in {'README.md', 'CONTRIBUTING.md'}:
            return True
        return (path.startswith('docs/')
                and not path.startswith(('docs/wireframes/', 'docs/dora/example/'))
                and Path(path).suffix.lower() in {'.md', '.txt', '.png', '.jpg', '.svg'})
    required = manual or any(not documentation(p) for p in paths)
    return {'ci_required': required, 'deploy_required': required, 'changed_count': len(paths)}


def main():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    kind = os.environ['GITHUB_EVENT_NAME']
    if kind == 'pull_request':
        base, head = event['pull_request']['base']['sha'], event['pull_request']['head']['sha']
        operator = '...'
    else:
        base, head = event.get('before', ''), os.environ['GITHUB_SHA']
        operator = '..'
    manual = kind == 'workflow_dispatch'
    paths, reason = [], 'manual' if manual else 'changed-files'
    if not manual:
        try:
            if not all(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', sha) and set(sha) != {'0'}
                       for sha in (base, head)):
                raise ValueError('Missing comparison base')
            raw = subprocess.run(['git', 'diff', '--name-only', '--no-renames', '-z',
                                  base + operator + head], check=True, capture_output=True).stdout
            paths = [p.decode('utf-8') for p in raw.split(b'\0') if p]
        except (ValueError, UnicodeDecodeError, subprocess.CalledProcessError):
            manual, reason = True, 'comparison-unavailable-run-conservatively'
    result = dict(classify(paths, manual), reason=reason, paths=paths)
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
        for key in ('ci_required', 'deploy_required', 'changed_count'):
            stream.write(f'{key}={str(result[key]).lower()}\n')
    report = '# Changed-file decision\n\n```json\n' + json.dumps(result, indent=2, ensure_ascii=False) + '\n```\n'
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
        stream.write(report)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
