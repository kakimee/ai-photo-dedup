# -*- coding: utf-8 -*-
"""
清理模块 - 安全删除重复照片
"""

import os
import shutil
from pathlib import Path
from typing import List
import json

from .comparator import PhotoGroup


class PhotoCleaner:
    """照片清理器"""
    
    def __init__(self, threshold: float = 90, keep_strategy: str = 'first',
                 interactive: bool = False, dry_run: bool = False,
                 trash_dir: str = './trash'):
        """
        初始化清理器
        
        Args:
            threshold: 相似度阈值
            keep_strategy: 保留策略 (first/best/newest)
            interactive: 交互模式
            dry_run: 预览模式
            trash_dir: 回收站目录
        """
        self.threshold = threshold
        self.keep_strategy = keep_strategy
        self.interactive = interactive
        self.dry_run = dry_run
        self.trash_dir = Path(trash_dir)
        self._deleted_files = []
    
    def clean_directory(self, directory: Path):
        """
        清理目录中的重复照片
        
        Args:
            directory: 要清理的目录
        """
        from .scanner import PhotoScanner
        
        # 先扫描
        scanner = PhotoScanner(threshold=self.threshold)
        groups = scanner.scan_directory(directory)
        
        if not groups:
            print("🎉 未发现重复照片！")
            return
        
        print(f"\n🗑️  准备清理 {len(groups)} 组重复照片")
        print(f"📋 保留策略: {self.keep_strategy}")
        
        if self.dry_run:
            print("🔍 [预览模式] 以下文件将被删除:\n")
        
        total_deleted = 0
        
        for group in groups:
            # 根据策略决定保留哪张
            if self.keep_strategy == 'best':
                keep_photo = group.get_best_quality()
            elif self.keep_strategy == 'newest':
                keep_photo = group.get_newest()
            else:
                keep_photo = group.get_first()
            
            # 要删除的照片
            to_delete = [p for p in group.photos if p.path != keep_photo.path]
            
            for photo in to_delete:
                print(f"  📄 {Path(photo.path).name}")
                print(f"     ← 保留: {Path(keep_photo.path).name}")
                
                if not self.dry_run:
                    self._move_to_trash(Path(photo.path))
                    self._deleted_files.append(photo.path)
                
                total_deleted += 1
        
        if self.dry_run:
            print(f"\n🔍 预览结束，共 {total_deleted} 个文件将被删除")
            print("💡 去掉 --dry-run 参数实际执行删除")
        else:
            print(f"\n✅ 清理完成！共删除 {total_deleted} 个文件")
            print(f"🗑️  文件已移动到: {self.trash_dir.absolute()}")
            
            # 保存删除记录
            self._save_delete_log()
    
    def _move_to_trash(self, file_path: Path):
        """
        将文件移动到回收站
        
        Args:
            file_path: 要删除的文件路径
        """
        # 创建回收站目录
        self.trash_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        dest = self.trash_dir / file_path.name
        counter = 1
        while dest.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            dest = self.trash_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # 移动文件
        shutil.move(str(file_path), str(dest))
        print(f"     ✓ 已移到回收站: {dest.name}")
    
    def _save_delete_log(self):
        """保存删除日志"""
        log_file = self.trash_dir / 'delete_log.json'
        
        log_data = {
            'deleted_at': str(Path.cwd()),
            'files': self._deleted_files
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def restore_from_trash(self, trash_path: Path):
        """
        从回收站恢复文件
        
        Args:
            trash_path: 回收站目录路径
        """
        log_file = trash_path / 'delete_log.json'
        
        if not log_file.exists():
            print("❌ 未找到删除日志，无法恢复")
            return
        
        with open(log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        print(f"📋 删除记录: {len(log_data['files'])} 个文件\n")
        
        for file_path in log_data['files']:
            src = trash_path / Path(file_path).name
            
            if src.exists():
                # 恢复到原位置
                original_dir = Path(file_path).parent
                original_dir.mkdir(parents=True, exist_ok=True)
                
                dest = original_dir / src.name
                shutil.move(str(src), str(dest))
                print(f"✓ 已恢复: {dest}")
        
        print(f"\n✅ 恢复完成！")
        
        # 删除日志
        log_file.unlink()
