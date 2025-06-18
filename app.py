from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Emojis
FULL_YELLOW = "<:ystar:1214063559076749312>"
FULL_GRAY = "<:sstar:1214063700886036532>"
HALF_YELLOW = "<:mystar:1214063655646138408>"
HALF_GRAY = "<:msstar:1216072572924596276>"

EMOJI_TO_VALUE = {
    FULL_YELLOW: 1.0,
    HALF_YELLOW: 0.5,
    FULL_GRAY: 1.0,
    HALF_GRAY: 0.5
}

def value_to_emojis(yellow: float, gray: float) -> str:
    result = []
    while yellow >= 1.0:
        result.append(FULL_YELLOW)
        yellow -= 1.0
    if yellow >= 0.5:
        result.append(HALF_YELLOW)
    while gray >= 1.0:
        result.append(FULL_GRAY)
        gray -= 1.0
    if gray >= 0.5:
        result.append(HALF_GRAY)
    return ''.join(result)

@app.route("/skill-up", methods=["POST"])
def skill_up():
    data = request.json
    stars = data.get("stars")  # Lista de emojis

    yellow = 0.0
    gray = 0.0

    for e in stars:
        val = EMOJI_TO_VALUE.get(e, 0)
        if e in [FULL_YELLOW, HALF_YELLOW]:
            yellow += val
        else:
            gray += val

    if yellow >= 5.0:
        return jsonify({
            "error": "Este jogador já atingiu o limite máximo de estrelas amarelas (5.0)"
        })

    outcome = random.choices(
        population=[1.5, 0.5, 0],
        weights=[25, 50, 25],
        k=1
    )[0]

    evolved = 0.0
    while outcome >= 1.0 and gray >= 1.0 and yellow < 5.0:
        yellow += 1.0
        gray -= 1.0
        evolved += 1.0
        outcome -= 1.0
    if outcome >= 0.5 and gray >= 0.5 and yellow < 5.0:
        yellow += 0.5
        gray -= 0.5
        evolved += 0.5

    return jsonify({
        "updated_stars": value_to_emojis(yellow, gray),
        "evolved": evolved
    })

@app.route("/")
def home():
    return "Skill Up API Online"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
