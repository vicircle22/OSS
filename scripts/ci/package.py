"""Build one portable project archive and verify it before testing or releasing."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile


ROOT_FILES = ('README.md', 'CONTRIBUTING.md', 'pyproject.toml', 'requirements-ci.txt')
SOURCE_DIRS = ('scripts', 'tests', 'docs')
ARCHIVE = 'ai-summit.zip'
MANIFEST = 'bundle-manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def allowed(path):
    return (not any(part.startswith('.') or part == '__pycache__' for part in path.parts)
            and path.suffix.lower() not in {'.pyc', '.pyo', '.pem', '.key'})


def build(root, out, revision):
    if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', revision):
        raise ValueError('A full Git commit SHA is required')
    root, out = Path(root).resolve(), Path(out).resolve()
    files = [root / name for name in ROOT_FILES]
    if not all(p.is_file() and not p.is_symlink() for p in files):
        raise ValueError('Required root files are missing or symbolic links')
    for directory in SOURCE_DIRS:
        files.extend(p for p in (root / directory).rglob('*')
                     if p.is_file() and not p.is_symlink()
                     and allowed(p.relative_to(root)) and not p.is_relative_to(out))
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out / ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            name = 'ai-summit/' + path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    manifest = {'schema_version': 1, 'archive': ARCHIVE, 'revision': revision,
                'sha256': digest(out / ARCHIVE), 'file_count': len(files)}
    (out / MANIFEST).write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def verify(artifact_dir, out, revision):
    artifact_dir, out = Path(artifact_dir), Path(out)
    manifest = json.loads((artifact_dir / MANIFEST).read_text(encoding='utf-8'))
    if manifest.get('archive') != ARCHIVE or manifest.get('revision') != revision:
        raise ValueError('Unexpected archive name or source revision')
    if manifest.get('sha256') != digest(artifact_dir / ARCHIVE):
        raise ValueError('Archive SHA-256 mismatch')
    with zipfile.ZipFile(artifact_dir / ARCHIVE) as archive:
        names = archive.namelist()
        if len(names) != manifest.get('file_count') or len(set(names)) != len(names):
            raise ValueError('Unexpected or duplicate archive members')
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            if (path.is_absolute() or '..' in path.parts or '\\' in entry.filename
                    or not path.parts or path.parts[0] != 'ai-summit'
                    or stat.S_ISLNK(entry.external_attr >> 16)):
                raise ValueError('Unsafe archive member')
        if out.exists() and any(out.iterdir()):
            raise ValueError('Extraction destination must be empty')
        archive.extractall(out)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    pack = commands.add_parser('build')
    pack.add_argument('--root', type=Path, default=Path('.'))
    pack.add_argument('--out', type=Path, required=True)
    pack.add_argument('--revision', required=True)
    check = commands.add_parser('verify')
    check.add_argument('--artifact-dir', type=Path, required=True)
    check.add_argument('--out', type=Path, required=True)
    check.add_argument('--revision', required=True)
    args = parser.parse_args()
    if args.command == 'build':
        result = build(args.root, args.out, args.revision)
    else:
        result = verify(args.artifact_dir, args.out, args.revision)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
