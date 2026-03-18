# AI Photo Deduplicator 🤖📸

基于图像感知哈希算法（Perceptual Hashing）的智能重复照片检测与清理工具。

[English](README_EN.md) | 中文

## ✨ 功能特性

- **智能检测**：采用 pHash + MSE 双算法，精准识别重复/相似照片
- **批量处理**：支持文件夹批量扫描，自动归组相似照片
- **预览对比**：提供相似照片并排预览，直观判断删除对象
- **安全删除**：删除前自动备份到 `trash/` 目录，可恢复
- **灵活配置**：支持自定义相似度阈值、排除目录、文件类型过滤

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

```bash
# 扫描照片目录并查看重复组
python main.py scan /path/to/photos

# 自动清理（保留每组最清晰的
python main.py clean /path/to/photos --keep best

# 交互式选择删除
python main.py clean /path/to/photos --interactive
```

## 📁 项目结构

```
ai-photo-dedup/
├── main.py              # 主入口
├── core/
│   ├── __init__.py
│   ├── hasher.py        # 图像哈希计算
│   ├── comparator.py    # 相似度比较
│   ├── scanner.py       # 目录扫描
│   └── cleaner.py      # 清理逻辑
├── utils/
│   ├── __init__.py
│   ├── logger.py       # 日志工具
│   └── config.py       # 配置管理
├── tests/
│   └── test_*.py
├── requirements.txt
├── README.md
└── LICENSE
```

## ⚙️ 配置说明

编辑 `config.yaml` 或通过命令行参数配置：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `threshold` | 相似度阈值 (0-100) | 90 |
| `trash_dir` | 回收站目录 | `./trash` |
| `exclude_dirs` | 排除的目录 | `['.git', '__pycache__']` |
| `image_formats` | 支持的图片格式 | `['.jpg', '.jpeg', '.png', '.webp']` |

## 🔧 算法原理

1. **pHash（感知哈希）**：将图像缩放→灰度→DCT变换，提取低频特征
2. **MSE（均方误差）**：逐像素计算两图差异
3. **汉明距离**：比较 pHash 指纹的位数差异

```
相似度 = 100 - (汉明距离 / 64) * 100
```

## 📊 使用示例

```
$ python main.py scan ./photos

🔍 扫描中...
✅ 完成！发现 3 组重复照片

📁 组 1 (3 张, 相似度 98%)
   - photos/vacation_001.jpg
   - photos/vacation_002.jpg
   - photos/vacation_003.jpg

📁 组 2 (2 张, 相似度 95%)
   - photos/portrait_duo.jpg
   - photos/portrait_duo_copy.png
```

## 🛡️ 安全机制

- ✅ 删除前自动备份到 `./trash/`
- ✅ 支持 `--dry-run` 预览模式
- ✅ 删除前确认提示
- ✅ 可通过 `restore` 命令恢复

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 自由使用，商用免责

---

Made with ❤️ by AI Assistant
