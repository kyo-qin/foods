from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CategoryConfig:
    type_key: str
    label: str
    items_file: Path
    query_suffixes: tuple[str, ...]
    per_item_limit: int = 3
    search_candidate_limit: int = 12


CATEGORY_CONFIGS = {
    "home_cooking": CategoryConfig(
        type_key="home_cooking",
        label="家常炒菜",
        items_file=Path("data/categories/home_cooking.txt"),
        query_suffixes=("家常菜 实拍 菜品图", "菜品图 实拍", "中餐 实拍"),
    ),
    "beverage": CategoryConfig(
        type_key="beverage",
        label="酒水饮料",
        items_file=Path("data/categories/beverage.txt"),
        query_suffixes=("饮料 酒水 实拍 产品图", "饮料 实拍", "饮料", ""),
    ),
    "takeout_box": CategoryConfig(
        type_key="takeout_box",
        label="打包盒",
        items_file=Path("data/categories/takeout_box.txt"),
        query_suffixes=("打包盒 外卖餐盒 实拍", "外卖餐盒 实拍", "餐盒"),
    ),
    "staple_food": CategoryConfig(
        type_key="staple_food",
        label="主食",
        items_file=Path("data/categories/staple_food.txt"),
        query_suffixes=("主食 实拍 菜品图", "主食 实拍", ""),
    ),
    "dessert": CategoryConfig(
        type_key="dessert",
        label="甜品",
        items_file=Path("data/categories/dessert.txt"),
        query_suffixes=("甜品 实拍 高清", "甜品 实拍", "甜品"),
    ),
    "noodle": CategoryConfig(
        type_key="noodle",
        label="面食",
        items_file=Path("data/categories/noodle.txt"),
        query_suffixes=("面食 实拍 菜品图", "面食 实拍", ""),
    ),
    "milk_tea": CategoryConfig(
        type_key="milk_tea",
        label="奶茶",
        items_file=Path("data/categories/milk_tea.txt"),
        query_suffixes=("奶茶 饮品 实拍", "奶茶 实拍", "奶茶 饮品", ""),
    ),
    "coffee": CategoryConfig(
        type_key="coffee",
        label="咖啡",
        items_file=Path("data/categories/coffee.txt"),
        query_suffixes=("咖啡 饮品 实拍", "咖啡 实拍", "咖啡", ""),
    ),
}


def get_category_config(type_key: str) -> CategoryConfig:
    try:
        return CATEGORY_CONFIGS[type_key]
    except KeyError as exc:
        supported = ", ".join(sorted(CATEGORY_CONFIGS))
        raise ValueError(
            f"unknown category type '{type_key}'. supported types: {supported}"
        ) from exc


def list_category_types() -> list[str]:
    return sorted(CATEGORY_CONFIGS)
