# 中餐菜品图片抓取工具

这是一个本地命令行工具，用于为餐饮点餐系统批量抓取中餐菜品图片。

## 环境要求

- Python 3.9 及以上
- `Pillow`

## 安装依赖

```bash
python3 -m pip install -r requirements-dev.txt
```

## 运行方式

```bash
python -m src.main
```

## 输出结果

```text
output/
├── images/
│   └── 鱼香肉丝/
│       ├── 001.jpg
│       ├── 002.jpg
│       └── 003.jpg
└── manifest.csv
```

`manifest.csv` 包含以下字段：

- `image_id`
- `dish_name`
- `file_path`
- `width`
- `height`
- `source_url`
- `status`

## 说明

- 默认搜索源顺序为：先使用 `DuckDuckGo` 图片搜索，失败时自动回退到 `Wikimedia Commons`。
- 默认搜索源使用公开网络图片搜索结果，不同菜品的图片质量可能不一致。
- 如果搜索结果较差或下载失败，部分菜品最终可能不足 3 张有效图片。
- 在正式商用前，请自行确认图片版权和来源合规性。
