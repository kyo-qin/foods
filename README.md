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

## 如何修改搜索词

默认情况下，程序会读取 [data/dishes.txt](/Users/qintao/develop/projects/foods/data/dishes.txt) 里的词条，并在 [src/search.py](/Users/qintao/develop/projects/foods/src/search.py) 的 `build_query()` 中自动拼接搜索关键词。

如果你想改搜索内容，可以用下面两种方式：

- 修改 [data/dishes.txt](/Users/qintao/develop/projects/foods/data/dishes.txt)：把每一行替换成你想抓取的主题词。它不一定必须是菜品，也可以是水果、饮品、甜点、门店环境、餐具、促销海报，或者任何你想搜索的图片主题。
- 修改 [src/search.py](/Users/qintao/develop/projects/foods/src/search.py) 里的 `build_query()`：当前默认会在词条后面追加“中餐 菜品图 实拍”之类的限定词。如果你要搜索其他内容，可以改成更适合的关键词组合。

例如，当前默认逻辑类似：

```python
def build_query(dish_name: str) -> str:
    return f"{dish_name} 中餐 菜品图 实拍"
```

如果你想搜索饮品图片，可以改成：

```python
def build_query(dish_name: str) -> str:
    return f"{dish_name} 饮品 实拍 高清"
```

如果你只想按原词直接搜索，也可以改成：

```python
def build_query(dish_name: str) -> str:
    return dish_name
```

## 说明

- 默认搜索源顺序为：先使用 `DuckDuckGo` 图片搜索，失败时自动回退到 `Wikimedia Commons`。
- 默认搜索源使用公开网络图片搜索结果，不同菜品的图片质量可能不一致。
- 如果搜索结果较差或下载失败，部分菜品最终可能不足 3 张有效图片。
- 在正式商用前，请自行确认图片版权和来源合规性。
