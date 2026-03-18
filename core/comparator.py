# -*- coding: utf-8 -*-
"""
相似度比较模块
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from PIL import Image


@dataclass
class PhotoInfo:
    """照片信息"""
    path: str
    phash: Optional[str] = None
    md5: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mtime: Optional[float] = None


@dataclass
class PhotoGroup:
    """相似照片组"""
    photos: List[PhotoInfo]
    similarity: float
    
    def get_best_quality(self) -> PhotoInfo:
        """获取质量最好的照片（分辨率最高）"""
        return max(self.photos, key=lambda p: (p.width or 0) * (p.height or 0))
    
    def get_newest(self) -> PhotoInfo:
        """获取最新的照片"""
        return max(self.photos, key=lambda p: p.mtime or 0)
    
    def get_first(self) -> PhotoInfo:
        """获取第一张"""
        return self.photos[0]


class PhotoComparator:
    """照片相似度比较器"""
    
    def __init__(self, threshold: float = 90):
        """
        初始化比较器
        
        Args:
            threshold: 相似度阈值 (0-100)
        """
        self.threshold = threshold
        self._hash_cache = {}
    
    def compare(self, hash1: str, hash2: str) -> float:
        """比较两个哈希值的相似度"""
        if not hash1 or not hash2:
            return 0.0
        
        try:
            # 转换为二进制
            bin1 = bin(int(hash1, 16))[2:].zfill(64)
            bin2 = bin(int(hash2, 16))[2:].zfill(64)
            
            # 计算汉明距离
            distance = sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
            
            # 转换为相似度
            return (1 - distance / 64) * 100
        except:
            return 0.0
    
    def compute_mse(self, image1_path: str, image2_path: str) -> float:
        """
        计算两幅图像的均方误差 (MSE)
        
        Args:
            image1_path: 第一张图像路径
            image2_path: 第二张图像路径
            
        Returns:
            MSE 值（越小越相似）
        """
        try:
            # 打开图像并转换为相同尺寸
            img1 = Image.open(image1_path).convert('RGB')
            img2 = Image.open(image2_path).convert('RGB')
            
            # 调整为相同尺寸
            size = (min(img1.width, img2.width), min(img1.height, img2.height))
            img1 = img1.resize(size, Image.Resampling.LANCZOS)
            img2 = img2.resize(size, Image.Resampling.LANCZOS)
            
            # 转换为数组
            arr1 = np.array(img1, dtype=np.float32)
            arr2 = np.array(img2, dtype=np.float32)
            
            # 计算 MSE
            mse = np.mean((arr1 - arr2) ** 2)
            
            return float(mse)
        except Exception as e:
            print(f"计算 MSE 失败: {e}")
            return float('inf')
    
    def is_similar(self, hash1: str, hash2: str) -> bool:
        """判断两张照片是否相似"""
        return self.compare(hash1, hash2) >= self.threshold
