from flask import Flask, request, jsonify
import random
import re

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

# Regex para identificar os emojis da NLEDF
EMOJI_PATTERN = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

# Mensagens possíveis de treino
TRAINING_MESSAGES = [
    "Um treino espetacular, chamou atenção de todos os olheiros presentes.",
    "Treino sólido, os fundamentos foram reforçados com sucesso.",
    "Dedicado e concentrado, evoluiu bem em aspectos táticos.",
    "Mostrou evolução clara na leitura de jogo.",
    "Teve um desempenho excelente no treino de finalizações.",
    "Trabalho mental exemplar durante o treino.",
    "Impressionou os treinadores com visão de jogo.",
    "Se destacou entre os colegas com intensidade e foco.",
    "Treino físico de altíssimo nível, evolução clara.",
    "Grande progresso na tomada de decisão.",
    "Mostrou raça, vontade e aprendeu rápido.",
    "Dificuldades no início, mas terminou com bons resultados.",
    "Superou as expectativas em fundamentos defensivos.",
    "Chute calibrado e força física melhorada.",
    "Visão de jogo mais afiada após o treino tático.",
    "Trabalho em grupo excelente, entrosamento subiu.",
    "Teve paciência e absorveu bem o que foi passado.",
    "Cresceu muito no 1 contra 1.",
    "Mostrou que tem potencial para liderar em campo.",
    "Dominou o treino e saiu ovacionado pelos colegas."
]

@app.route("/skill-up", methods=["POST"])
def skill_up():
    data = request.form

    stars_raw = data.get("stars", "")
    print("RAW stars string:", stars_raw)  # Debug print

    # Extrai todos os emojis válidos, mesmo se grudados
    stars = EMOJI_PATTERN.findall(stars_raw)
    print("Parsed emojis:", stars)  # Debug print

    yellow = 0.0
    gray = 0.0

    for e in stars:
        val = EMOJI_TO_VALUE.get(e, 0)
        if e in [FULL_YELLOW, HALF_YELLOW]:
            yellow += val
        elif e in [FULL_GRAY, HALF_GRAY]:
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

    if evolved == 0.0:
        message = "Apesar do esforço, o jogador apenas ganhou experiência e não conseguiu converter estrelas."
    else:
        message = random.choice(TRAINING_MESSAGES)

    return jsonify({
        "updated_stars": value_to_emojis(yellow, gray),
        "evolved": evolved,
        "message": message
    })

@app.route("/")
def home():
    return "Skill Up API Online"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
