# 多类型图片抓取工具

这是一个本地命令行工具，用于按预设类型批量抓取图片素材。当前内置 8 个类型：

- `home_cooking`：家常炒菜
- `beverage`：酒水饮料
- `takeout_box`：打包盒
- `staple_food`：主食
- `dessert`：甜品
- `noodle`：面食
- `milk_tea`：奶茶
- `coffee`：咖啡

## 环境要求

- Python 3.9 及以上
- `Pillow`

## 安装依赖

```bash
python3 -m pip install -r requirements-dev.txt
```

## 运行方式

按类型执行：

```bash
python3 -m src.main --type beverage
```

如果不传 `--type`，默认使用 `home_cooking`。

## 数据文件

每个类型都有独立词表，位于 `data/categories/`：

```text
data/
└── categories/
    ├── home_cooking.txt
    ├── beverage.txt
    ├── takeout_box.txt
    ├── staple_food.txt
    ├── dessert.txt
    ├── noodle.txt
    ├── milk_tea.txt
    └── coffee.txt
```

你可以直接修改对应 txt 文件里的词条，一行一个。

## 输出结果

```text
output/
├── images/
│   └── beverage/
│       └── 可乐/
│           ├── 001.jpg
│           ├── 002.jpg
│           └── 003.jpg
└── manifest.csv
```

`manifest.csv` 包含以下字段：

- `image_id`
- `category_type`
- `item_name`
- `file_path`
- `width`
- `height`
- `source_url`
- `status`

## 搜索词规则

程序会根据类型自动拼接搜索后缀。当前逻辑位于 [src/search.py](/Users/qintao/develop/projects/foods/src/search.py)。

例如：

```python
build_query("可乐", "饮料 酒水 实拍 产品图")
```

会生成：

```text
可乐 饮料 酒水 实拍 产品图
```

各类型的默认搜索后缀和词表路径定义在 [src/categories.py](/Users/qintao/develop/projects/foods/src/categories.py)。

## 可选官方图片 API

为了提升稳定性，程序会优先使用官方图库 API，然后再回退到网页搜索源。当前顺序是：

1. `Pixabay`
2. `Pexels`
3. `DuckDuckGo`
4. `Wikimedia Commons`

配置方式：

```bash
export PIXABAY_API_KEY="your_pixabay_key"
export PEXELS_API_KEY="your_pexels_key"
python3 -m src.main --type beverage
```

说明：

- 没有配置 API key 时，程序仍然可运行，只是会直接回退到现有网页搜索源。
- 配置一个 key 也可以，程序只会启用对应的官方 provider。
- 如果当前运行环境没有网络权限，程序会在启动阶段直接报错退出，而不是误导性地输出 0 张图片。

## 说明

- 已配置 API key 时，默认搜索源顺序为：`Pixabay -> Pexels -> DuckDuckGo -> Wikimedia Commons`。
- 未配置 API key 时，默认搜索源顺序为：`DuckDuckGo -> Wikimedia Commons`。
- 每个词条默认保留 3 张图片。
- 如果搜索结果较差或下载失败，部分词条最终可能不足 3 张有效图片。
- 在正式商用前，请自行确认图片版权和来源合规性。
