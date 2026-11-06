"""缓存整理回归检查：活跃链接保留，未使用文件归档后移出，不一致时中止。"""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
import singdo_mirror as mirror


class CacheMigrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='oldbridge-mirror-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'oldbridge'
        self.cache = self.root / '文保名录/杭州市/云端档案'
        self.cache.joinpath('图片').mkdir(parents=True)
        self.archive = Path(self.temp.name) / 'singdo_云端档案'
        self.archive.mkdir()
        town = self.root / '杭州市/西湖区/三墩镇'
        town.mkdir(parents=True)
        town.joinpath('三墩镇古桥.md').write_text('[常用桥](../../../文保名录/杭州市/云端档案/1_常用桥.html)')
        self.cache.joinpath('1_常用桥.html').write_text('<img src="图片/1_keep.jpg">')
        self.cache.joinpath('图片/1_keep.jpg').write_bytes(b'used image')
        self.cache.joinpath('历保2_未使用桥.html').write_text('<img src="图片/历保2_unused.jpg">')
        # 既有缓存中可能包含空资源，也应原样归档后清理。
        self.cache.joinpath('图片/历保2_unused.jpg').write_bytes(b'')
        self.root.joinpath('文保名录/杭州市/云端档案_桥梁.md').write_text(
            '[常用桥](云端档案/1_常用桥.html)\n[未使用桥](云端档案/历保2_未使用桥.html)\n')
        for name, value in [('ROOT', self.root), ('CACHE', self.cache), ('MIRROR', self.archive)]:
            p = patch.object(mirror, name, value)
            p.start()
            self.addCleanup(p.stop)

    def run_prune(self):
        with contextlib.redirect_stdout(io.StringIO()):
            mirror.prune_cache()

    def test_unused_files_are_archived_and_active_links_survive(self):
        self.run_prune()
        self.assertTrue(self.cache.joinpath('1_常用桥.html').is_file())
        self.assertTrue(self.cache.joinpath('图片/1_keep.jpg').is_file())
        self.assertFalse(self.cache.joinpath('历保2_未使用桥.html').exists())
        backup = self.archive / '历史建筑/项目缓存'
        self.assertEqual(backup.joinpath('历保2_未使用桥.html').read_text(), '<img src="图片/历保2_unused.jpg">')
        self.assertEqual(backup.joinpath('图片/历保2_unused.jpg').read_bytes(), b'')
        index = self.root.joinpath('文保名录/杭州市/云端档案_桥梁.md').read_text()
        self.assertIn('[常用桥](云端档案/1_常用桥.html)', index)
        self.assertNotIn('云端档案/历保2_未使用桥.html', index)
        # 再次运行不应损坏常用文件。
        self.run_prune()
        self.assertTrue(self.cache.joinpath('1_常用桥.html').is_file())

    def test_failed_image_address_uses_official_alternative(self):
        archive = mirror.Archive('libao', 1)
        url = 'http://z1.singdo.org/libao/upfile/test.png'
        target = archive.folder / '资源/test.png'
        image = b'\x89PNG\r\n\x1a\nimage data'
        with patch.object(mirror, 'urlopen', side_effect=[
            HTTPError(url, 404, 'Not Found', {}, None), io.BytesIO(image)
        ]) as request:
            self.assertEqual(archive.fetch(url, target), image)
        self.assertEqual(request.call_count, 2)
        self.assertEqual(target.read_bytes(), image)
        self.assertEqual(archive.alternatives[url], 'http://www.singdo.org/libao/upfile/test.png')
        self.assertFalse(archive.failures)

    def test_mismatched_backup_prevents_all_removals(self):
        backup = self.archive / '历史建筑/项目缓存'
        backup.mkdir(parents=True)
        backup.joinpath('历保2_未使用桥.html').write_text('different content')
        with self.assertRaises(RuntimeError):
            self.run_prune()
        self.assertTrue(self.cache.joinpath('历保2_未使用桥.html').is_file())
        self.assertTrue(self.cache.joinpath('图片/历保2_unused.jpg').is_file())
        self.assertTrue(self.cache.joinpath('1_常用桥.html').is_file())


if __name__ == '__main__':
    unittest.main()
