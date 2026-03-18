# -*- coding: utf-8 -*-
"""
图像哈希计算模块 - 基于感知哈希 (pHash) 算法
"""

import numpy as np
from PIL import Image
from typing import Optional
import hashlib


class ImageHasher:
    """感知哈希计算器"""
    
    def __init__(self, hash_size: int = 8):
        """
        初始化哈希器
        
        Args:
            hash_size: 哈希尺寸，默认 8x8 = 64 位指纹
        """
        self.hash_size = hash_size
        self.highfreq_factor = 4  # DCT 高频因子
    
    def compute_phash(self, image_path: str) -> Optional[str]:
        """
        计算图像的感知哈希值
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            64位十六进制哈希字符串，失败返回 None
        """
        try:
            # 打开图像并转换为灰度
            img = Image.open(image_path).convert('L')
            
            # 缩放为 (hash_size * highfreq_factor) x (hash_size * highfreq_factor)
            size = self.hash_size * self.highfreq_factor
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # 转换为 numpy 数组
            pixels = np.array(img, dtype=np.float32)
            
            # 2D DCT 变换
            dct = self._dct2d(pixels)
            
            # 取低频区域 (左上角 hash_size x hash_size)
            dct_low = dct[:self.hash_size, :self.hash_size]
            
            # 计算平均值（排除 DC 分量）
            avg = (dct_low.sum() - dct_low[0, 0]) / (self.hash_size ** 2 - 1)
            
            # 生成哈希：大于平均值为1，否则为0
            diff = dct_low > avg
            
            # 转换为二进制字符串
            hash_bits = diff.flatten().tolist()
            
            # 转换为十六进制
            hash_hex = ''.join(
                format(int(''.join('1' if b else '0' for b in hash_bits[i:i+4]), 2), 'x')
                for i in range(0, len(hash_bits), 4)
            )
            
            return hash_hex
            
        except Exception as e:
            print(f"计算哈希失败 {image_path}: {e}")
            return None
    
    def compute_md5(self, image_path: str) -> Optional[str]:
        """
        计算文件的 MD5 哈希（用于检测完全相同的文件）
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            MD5 哈希字符串
        """
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"计算 MD5 失败 {image_path}: {e}")
            return None
    
    def _dct2d(self, matrix: np.ndarray) -> np.ndarray:
        """
        2D DCT 变换
        
        Args:
            matrix: 输入矩阵
            
        Returns:
            DCT 变换后的矩阵
        """
        from scipy.fftpack import dct
        
        # 行 DCT
        dct_rows = dct(matrix, type=2, norm='ortho', axis=0)
        # 列 DCT
        dct_cols = dct(dct_rows, type=2, norm='ortho', axis=1)
        
        return dct_cols
    
    @staticmethod
    def hamming_distance(hash1: str, hash2: str) -> int:
        """
        计算两个哈希值的汉明距离
        
        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值
            
        Returns:
            汉明距离（0-64）
        """
        if len(hash1) != len(hash2):
            raise ValueError("哈希值长度不匹配")
        
        # 将十六进制转换为二进制
        bin1 = bin(int(hash1, 16))[2:].zfill(64)
        bin2 = bin(int(hash2, 16))[2:].zfill(64)
        
        # 计算不同位数
        return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
    
    def similarity(self, hash1: str, hash2: str) -> float:
        """
        计算两个哈希值的相似度
        
        Args:
            hash1: 第一个哈希值
            hash2: 第二个哈希值
            
        Returns:
            相似度百分比 (0-100)
        """
        distance = self.hamming_distance(hash1, hash2)
        return (1 - distance / 64) * 100
