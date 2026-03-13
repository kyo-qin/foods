from pathlib import Path


def load_dishes(path: str) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    dishes: list[str] = []
    seen: set[str] = set()
    for raw in lines:
        name = raw.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        dishes.append(name)
    return dishes
