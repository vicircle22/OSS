"""Prepare or validate an exact-key cached environment and report measured time."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time


def interpreter(folder):
    folder = Path(folder).absolute()
    return folder / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--started', type=float, required=True)
    parser.add_argument('--cache-hit', choices=['true', 'false'], default='false')
    args = parser.parse_args()
    folder = Path('.ci-venv')
    python = interpreter(folder)
    if args.cache_hit == 'true':
        if not python.is_file():
            raise ValueError('Cache hit has no usable interpreter')
    else:
        subprocess.run(['python', '-m', 'venv', str(folder)], check=True)
        subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
                        '-r', 'requirements-ci.txt'], check=True)
    subprocess.run([str(python), '-m', 'ruff', '--version'], check=True)
    elapsed = time.perf_counter() - args.started
    result = {'python_path': python.as_posix(), 'dependency_seconds': round(elapsed, 6),
              'cache_hit': args.cache_hit}
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as stream:
        for key, value in result.items():
            stream.write(f'{key}={value}\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
