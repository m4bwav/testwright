import json

def save_game(path, state):
    with open(path, "w") as f:
        json.dump({"v": 2, "state": state}, f)

def load_game(path):
    with open(path) as f:
        data = json.load(f)
    if data.get("v") == 1:
        data["state"]["inventory"] = data["state"].pop("items", [])
    return data["state"]
