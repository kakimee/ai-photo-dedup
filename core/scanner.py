# -*- coding: utf-8 -*-
"""
目录扫描模块 - 扫描目录中的照片并分组
"""

import os
from pathlib import Path
from typing import List, Set, Generator
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .hasher import ImageHasher
from .comparator import PhotoInfo, PhotoGroup, PhotoComparator


class PhotoScanner:
    """照片扫描器"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'}
    
    def __init__(self, threshold: float = 90, exclude_dirs: Set[str] = None):
        """
        初始化扫描器
        
        Args:
            threshold: 相似度阈值
            exclude_dirs: 排除的目录名
        """
        self.threshold = threshold
        self.exclude_dirs = exclude_dirs or {'.git', '__pycache__', '.DS_Store', 'trash'}
        self.hasher = ImageHasher()
        self.comparator = PhotoComparator(threshold)
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> List[PhotoGroup]:
        """
        扫描目录并返回相似照片组
        
        Args:
            directory: 要扫描的目录
            recursive: 是否递归扫描
            
        Returns:
            相似照片组列表
        """
        print(f"🔍 正在扫描 {directory}...")
        
        # 收集所有照片文件
        photo_files = list(self._collect_photos(directory, recursive))
        print(f"📸 发现 {len(photo_files)} 张照片")
        
        if not photo_files:
            return []
        
        # 计算所有照片的哈希值
        photo_infos = self._compute_hashes(photo_files)
        print(f"✅ 哈希计算完成")
        
        # 分组相似照片
        groups = self._group_similar_photos(photo_infos)
        
        return groups
    
    def _collect_photos(self, directory: Path, recursive: bool) -> Generator[Path, None, None]:
        """收集目录中的所有照片文件"""
        if recursive:
            for root, dirs, files in os.walk(directory):
                # 排除特定目录
                dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
                
                for file in files:
                    path = Path(root) / file
                    if path.suffix.lower() in self.SUPPORTED_FORMATS:
                        yield path
        else:
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in self.SUPPORTED_FORMATS:
                    yield file
    
    def _compute_hashes(self, photo_files: List[Path]) -> List[PhotoInfo]:
        """并行计算所有照片的哈希值"""
        photo_infos = []
        
        def process_photo(path: Path) -> PhotoInfo:
            info = PhotoInfo(
                path=str(path),
                phash=self.hasher.compute_phash(str(path)),
                md5=self.hasher.compute_md5(str(path)),
                size=path.stat().st_size if path.exists() else None,
                mtime=path.stat().st_mtime if path.exists() else None
            )
            
            # 获取图像尺寸
            try:
                from PIL import Image
                with Image.open(path) as img:
                    info.width, info.height = img.size
            except:
                pass
            
            return info
        
        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(process_photo, p): p for p in photo_files}
            
            for future in as_completed(futures):
                try:
                    info = future.result()
                    if info.phash:  # 只保留成功计算哈希的照片
                        photo_infos.append(info)
                except Exception as e:
                    print(f"处理照片失败: {e}")
        
        return photo_infos
    
    def _group_similar_photos(self, photo_infos: List[PhotoInfo]) -> List[PhotoGroup]:
        """将相似照片分组"""
        groups = []
        assigned = set()
        
        # 首先按 MD5 分组完全相同的文件
        md5_groups = {}
        for info in photo_infos:
            if info.md5:
                if info.md5 not in md5_groups:
                    md5_groups[info.md5] = []
                md5_groups[info.md5].append(info)
        
        # 将完全相同的文件作为一组
        for md5, photos in md5_groups.items():
            if len(photos) > 1:
                groups.append(PhotoGroup(photos=photos, similarity=100.0))
                for p in photos:
                    assigned.add(p.path)
        
        # 按 pHash 分组相似照片
        remaining = [p for p in photo_infos if p.path not in assigned]
        
        for i, photo1 in enumerate(remaining):
            if photo1.path in assigned:
                continue
            
            similar = [photo1]
            
            for photo2 in remaining[i+1:]:
                if photo2.path in assigned:
                    continue
                
                similarity = self.comparator.compare(photo1.phash, photo2.phash)
                
                if similarity >= self.threshold:
                    similar.append(photo2)
                    assigned.add(photo2.path)
            
            if len(similar) > 1:
                avg_similarity = sum(
                    self.comparator.compare(photo1.phash, p.phash)
                    for p in similar
                ) / len(similar)
                
                groups.append(PhotoGroup(photos=similar, similarity=round(avg_similarity, 1)))
                assigned.add(photo1.path)
        
        return groups
