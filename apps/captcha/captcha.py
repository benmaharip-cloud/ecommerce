import random, math, base64, json
from io import BytesIO

EMOJI_SETS = [
    {"items": ["🦁", "🐻", "🦊", "🐼", "🐨", "🐯"], "name": "animaux"},
    {"items": ["🍎", "🍓", "🍋", "🍇", "🍊", "🍉"], "name": "fruits"},
    {"items": ["🚗", "✈️", "🚀", "🚢", "🚂", "🚁"], "name": "véhicules"},
]

def generate_captcha(type_=None):
    """Génère un captcha et retourne (data_for_template, correct_answer)."""
    if type_ is None:
        type_ = random.choice(["checkbox", "math", "image_click", "image_count"])

    if type_ == "checkbox":
        token = base64.b64encode(str(random.randint(100000, 999999)).encode()).decode()
        return {"type": "checkbox", "token": token}, token

    elif type_ == "math":
        ops = [("+", lambda a,b: a+b), ("-", lambda a,b: a-b), ("×", lambda a,b: a*b)]
        op_sym, op_fn = random.choice(ops)
        a = random.randint(1, 9)
        b = random.randint(1, 9) if op_sym != "×" else random.randint(1, 5)
        answer = op_fn(a, b)
        return {"type": "math", "question": f"{a} {op_sym} {b} = ?", "a": a, "b": b, "op": op_sym}, str(answer)

    elif type_ == "image_click":
        eset = random.choice(EMOJI_SETS)
        items = eset["items"][:]
        random.shuffle(items)
        target = items[0]
        grid = items[:6]
        random.shuffle(grid)
        positions = [i for i, x in enumerate(grid) if x == target]
        return {"type": "image_click", "target": target, "grid": grid, "category": eset["name"]}, json.dumps(positions)

    else:  # image_count
        eset = random.choice(EMOJI_SETS)
        target = random.choice(eset["items"])
        count = random.randint(1, 4)
        others = [x for x in eset["items"] if x != target]
        grid = [target] * count + random.choices(others, k=9-count)
        random.shuffle(grid)
        return {"type": "image_count", "target": target, "grid": grid, "count": count}, str(count)
