from pathlib import Path

import pytest

from src.categories import get_category_config, list_category_types


def test_get_category_config_returns_beverage_settings():
    config = get_category_config("beverage")
    assert config.type_key == "beverage"
    assert config.label == "酒水饮料"
    assert config.items_file == Path("data/categories/beverage.txt")
    assert config.query_suffixes == (
        "饮料 酒水 实拍 产品图",
        "饮料 实拍",
        "饮料",
        "",
    )


def test_list_category_types_contains_all_presets():
    assert list_category_types() == [
        "beverage",
        "coffee",
        "dessert",
        "home_cooking",
        "milk_tea",
        "noodle",
        "staple_food",
        "takeout_box",
    ]


def test_get_category_config_rejects_unknown_type():
    with pytest.raises(ValueError) as exc_info:
        get_category_config("unknown")
    assert "unknown" in str(exc_info.value)


def test_home_cooking_category_keeps_more_conservative_fallbacks():
    config = get_category_config("home_cooking")
    assert config.query_suffixes[-1] == "中餐 实拍"
