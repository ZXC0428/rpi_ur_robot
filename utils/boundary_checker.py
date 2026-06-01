import json

def load_boundaries(config_path="config/parameters.json"):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config["boundaries"]

def is_within_boundaries(target_tcp, boundaries=None):
    """
    檢查目標 TCP (至少包含 [x, y, ...]) 是否在設定的邊界範圍內
    """
    if boundaries is None:
        boundaries = load_boundaries()
    x, y = target_tcp[0], target_tcp[1]

    # 當 x 超出邊界時拒絕
    if x < boundaries["x_min"] or x > boundaries["x_max"]:
        print(x, boundaries["x_min"], boundaries["x_max"])
        return False
    # 當 y 超出邊界時拒絕
    if y < boundaries["y_min"] or y > boundaries["y_max"]:
        print(y, boundaries["y_min"], boundaries["y_max"])
        return False
    return True
