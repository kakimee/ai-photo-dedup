# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


DEFAULT_CONFIG = {
    'threshold': 90,
    'trash_dir': './trash',
    'exclude_dirs': ['.git', '__pycache__', '.DS_Store', 'trash', 'node_modules'],
    'image_formats': ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'],
    'keep_strategy': 'first',
    'max_workers': 8,
    'hash_size': 8
}


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    config = DEFAULT_CONFIG.copy()
    
    # 查找配置文件
    if config_path:
        path = Path(config_path)
    else:
        # 默认查找顺序
        search_paths = [
            Path.cwd() / 'config.yaml',
            Path.cwd() / '.photo-dedup.yaml',
            Path.home() / '.photo-dedup' / 'config.yaml'
        ]
        path = next((p for p in search_paths if p.exists()), None)
    
    if path and path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
                config.update(user_config)
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}，使用默认配置")
    
    return config


def save_config(config: Dict[str, Any], config_path: str = 'config.yaml'):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def get_env_config() -> Dict[str, Any]:
    """
    从环境变量获取配置
    
    Returns:
        配置字典
    """
    config = {}
    
    env_mappings = {
        'PHOTO_DEDUP_THRESHOLD': ('threshold', int),
        'PHOTO_DEDUP_TRASH_DIR': ('trash_dir', str),
        'PHOTO_DEDUP_KEEP_STRATEGY': ('keep_strategy', str),
        'PHOTO_DEDUP_MAX_WORKERS': ('max_workers', int),
    }
    
    for env_key, (config_key, converter) in env_mappings.items():
        value = os.environ.get(env_key)
        if value:
            try:
                config[config_key] = converter(value)
            except ValueError:
                pass
    
    return config
