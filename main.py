#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Photo Deduplicator - 智能重复照片清理工具
基于感知哈希算法检测相似图片
"""

import argparse
import sys
from pathlib import Path
from core.scanner import PhotoScanner
from core.cleaner import PhotoCleaner
from utils.logger import setup_logger
from utils.config import load_config


def main():
    parser = argparse.ArgumentParser(
        description='AI 智能清理重复照片工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  %(prog)s scan ./photos              # 扫描并显示重复组
  %(prog)s clean ./photos --keep best # 自动清理，保留最清晰的
  %(prog)s clean ./photos -i          # 交互式选择删除
  %(prog)s restore ./trash            # 从回收站恢复
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # scan 命令
    scan_parser = subparsers.add_parser('scan', help='扫描目录中的重复照片')
    scan_parser.add_argument('path', help='要扫描的目录路径')
    scan_parser.add_argument('-t', '--threshold', type=int, default=90,
                            help='相似度阈值 (0-100)，默认 90')
    scan_parser.add_argument('-r', '--recursive', action='store_true',
                            help='递归扫描子目录')
    
    # clean 命令
    clean_parser = subparsers.add_parser('clean', help='清理重复照片')
    clean_parser.add_argument('path', help='要清理的目录路径')
    clean_parser.add_argument('-t', '--threshold', type=int, default=90,
                             help='相似度阈值 (0-100)，默认 90')
    clean_parser.add_argument('--keep', choices=['first', 'best', 'newest'],
                             default='first',
                             help='保留策略：first(第一张), best(最清晰), newest(最新)')
    clean_parser.add_argument('-i', '--interactive', action='store_true',
                             help='交互式选择删除')
    clean_parser.add_argument('--dry-run', action='store_true',
                             help='预览模式，不实际删除')
    
    # restore 命令
    restore_parser = subparsers.add_parser('restore', help='从回收站恢复照片')
    restore_parser.add_argument('path', help='回收站目录路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 设置日志
    logger = setup_logger()
    
    # 加载配置
    config = load_config()
    
    # 执行命令
    if args.command == 'scan':
        scanner = PhotoScanner(threshold=args.threshold)
        groups = scanner.scan_directory(Path(args.path), recursive=args.recursive)
        
        if not groups:
            logger.info('🎉 未发现重复照片！')
            return
        
        logger.info(f'🔍 扫描完成！发现 {len(groups)} 组重复照片\n')
        for i, group in enumerate(groups, 1):
            logger.info(f'📁 组 {i} ({len(group)} 张, 相似度 {group.similarity}%)')
            for photo in group.photos:
                logger.info(f'   - {photo.path}')
            print()
    
    elif args.command == 'clean':
        cleaner = PhotoCleaner(
            threshold=args.threshold,
            keep_strategy=args.keep,
            interactive=args.interactive,
            dry_run=args.dry_run
        )
        cleaner.clean_directory(Path(args.path))
    
    elif args.command == 'restore':
        cleaner = PhotoCleaner()
        cleaner.restore_from_trash(Path(args.path))


if __name__ == '__main__':
    main()
