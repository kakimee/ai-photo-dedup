# -*- coding: utf-8 -*-
"""
测试模块
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from core.hasher import ImageHasher
from core.comparator import PhotoComparator, PhotoInfo
from core.scanner import PhotoScanner


class TestImageHasher(unittest.TestCase):
    """测试图像哈希计算"""
    
    def setUp(self):
        self.hasher = ImageHasher()
    
    def test_hamming_distance(self):
        """测试汉明距离计算"""
        hash1 = "a" * 16  # 64位二进制
        hash2 = "a" * 16
        self.assertEqual(self.hasher.hamming_distance(hash1, hash2), 0)
        
        hash3 = "0" * 16
        self.assertEqual(self.hasher.hamming_distance(hash1, hash3), 64)
    
    def test_similarity(self):
        """测试相似度计算"""
        hash1 = "a" * 16
        hash2 = "a" * 16
        self.assertEqual(self.hasher.similarity(hash1, hash2), 100.0)


class TestPhotoComparator(unittest.TestCase):
    """测试照片比较器"""
    
    def setUp(self):
        self.comparator = PhotoComparator(threshold=90)
    
    def test_compare_identical(self):
        """测试完全相同哈希"""
        hash1 = "a" * 16
        hash2 = "a" * 16
        similarity = self.comparator.compare(hash1, hash2)
        self.assertEqual(similarity, 100.0)
    
    def test_is_similar(self):
        """测试相似判断"""
        hash1 = "a" * 16
        hash2 = "a" * 16
        self.assertTrue(self.comparator.is_similar(hash1, hash2))


class TestPhotoScanner(unittest.TestCase):
    """测试照片扫描器"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.scanner = PhotoScanner(threshold=90)
    
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_supported_formats(self):
        """测试支持的格式"""
        formats = self.scanner.SUPPORTED_FORMATS
        self.assertIn('.jpg', formats)
        self.assertIn('.png', formats)


if __name__ == '__main__':
    unittest.main()
