from src.dishes import load_dishes


def test_load_dishes_returns_at_least_50_unique_names():
    dishes = load_dishes("data/dishes.txt")
    assert len(dishes) >= 50
    assert len(dishes) == len(set(dishes))


def test_load_dishes_strips_blank_lines():
    dishes = load_dishes("tests/fixtures/dishes_sample.txt")
    assert dishes == ["鱼香肉丝", "宫保鸡丁"]
