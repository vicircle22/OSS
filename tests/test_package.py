import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.ci.package import ARCHIVE, MANIFEST, ROOT_FILES, build, digest, verify


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.root.mkdir()
        for name in ROOT_FILES:
            (self.root / name).write_text('fixture\n', encoding='utf-8')
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/hello.py').write_text('print("hello")\n', encoding='utf-8')
        self.out = Path(self.temp.name) / 'dist'
        self.unpacked = Path(self.temp.name) / 'unpacked'
        self.revision = 'a' * 40

    def test_same_archive_is_verified_and_extracted_reproducibly(self):
        first = build(self.root, self.out, self.revision)
        self.assertEqual(build(self.root, self.out, self.revision), first)
        self.assertEqual(verify(self.out, self.unpacked, self.revision), first)
        self.assertEqual((self.unpacked / 'ai-summit/scripts/hello.py').read_text(), 'print("hello")\n')
        with self.assertRaises(ValueError):
            verify(self.out, self.unpacked, self.revision)

    def test_secrets_caches_and_unlisted_root_files_are_excluded(self):
        for name in ('.env', 'private.key', 'token.pem', 'unlisted.txt'):
            (self.root / name).write_text('DO NOT PACKAGE', encoding='utf-8')
        (self.root / 'scripts/.env').write_text('DO NOT PACKAGE', encoding='utf-8')
        (self.root / 'scripts/cache.pyc').write_bytes(b'cache')
        build(self.root, self.out, self.revision)
        with zipfile.ZipFile(self.out / ARCHIVE) as archive:
            self.assertFalse(any(b'DO NOT PACKAGE' in archive.read(n) for n in archive.namelist()))
            self.assertFalse(any(n.endswith('.pyc') for n in archive.namelist()))

    def test_tampered_archive_and_wrong_revision_are_rejected(self):
        build(self.root, self.out, self.revision)
        with self.assertRaises(ValueError):
            verify(self.out, self.unpacked, 'b' * 40)
        with (self.out / ARCHIVE).open('ab') as stream:
            stream.write(b'corruption')
        with self.assertRaises(ValueError):
            verify(self.out, self.unpacked, self.revision)

    def test_traversal_is_rejected_even_if_checksum_matches(self):
        manifest = build(self.root, self.out, self.revision)
        with zipfile.ZipFile(self.out / ARCHIVE, 'w') as archive:
            archive.writestr('../escaped.txt', 'unsafe')
        manifest.update(sha256=digest(self.out / ARCHIVE), file_count=1)
        (self.out / MANIFEST).write_text(json.dumps(manifest), encoding='utf-8')
        with self.assertRaises(ValueError):
            verify(self.out, self.unpacked, self.revision)
        self.assertFalse((Path(self.temp.name) / 'escaped.txt').exists())
