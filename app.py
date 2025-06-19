from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# Emojis
FULL_YELLOW = "<:ystar:1214063559076749312>"
HALF_YELLOW = "<:mystar:1214063655646138408>"
HALF_MIXED  = "<:ysstar:1216072160959922209>"
FULL_GRAY   = "<:sstar:1214063700886036532>"
HALF_GRAY   = "<:msstar:1216072572924596276>"

# Valores por emoji
EMOJI_TO_VALUE = {
    FULL_YELLOW: 1.0,
    HALF_YELLOW: 0.5,
    HALF_MIXED:  1.0,
    FULL_GRAY:   1.0,
    HALF_GRAY:   0.5
}

# Regex para extrair emojis
EMOJI_PATTERN = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

# Mensagens
MENSAGENS_TREINO = [
    "O treino de finalização foi um sucesso e você surpreendeu a comissão técnica!",
    "Após horas batendo bola, aquele toque de classe apareceu!",
    "Chutes certeiros: você deixou todo mundo de queixo caído!",
    "A bola parecia colada no seu pé durante o treino.",
    "Perfeição nos exercícios de perna — resultado visível!",
    "Treino de precisão ativado: 1,5 estrelas a mais!",
    "Vocabulário de finalizações aumentou (e as estrelas também).",
    "Você brilhou no treino e acabou ganhando estrelas extras.",
    "Cada disparo no alvo valia metade de estrela, mas você arrasou e ganhou o dobro!",
    "Finalização mortal: evoluiu de forma impressionante.",
    "O treinador comemora seu desempenho hoje.",
    "Chute potente desbloqueou parte do seu potencial.",
    "A comissão técnica ficou impressionada com sua evolução.",
    "Treino top — estrelas amarelas merecidas.",
    "Seu pé está com milagre hoje!",
    "Precisão cirúrgica no treino de hoje.",
    "Você ditou o ritmo no treino de chute.",
    "Chute certeiro virou rotina hoje — parabéns!",
    "O gol imaginário virou realidade no treino.",
    "Hoje foi dia de mostrar faro de artilheiro."
]

MENSAGENS_SEM_EVOLUCAO = [
    "O treino foi pesado, mas ainda não trouxe evolução nas estrelas.",
    "Você aprendeu muito, mas as estrelas ainda não mudaram.",
    "Hora de fortalecer a base: sem evolução de estrelas hoje.",
    "Treino produtivo em resistência, mas sem upgrade de estrelas.",
    "Hoje foi dia de experiência — na próxima, subimos estrelas!",
    "Dia de aprendizado, evolução técnica ficou para depois.",
    "Você suou a camisa, mas as estrelas ficaram no mesmo lugar.",
    "Foco no preparo físico hoje, estrelas continuam as mesmas.",
    "Mais experiência no corpinho, evolução de estrelas fica pra próxima.",
    "Treino mental e tático faz parte, sem alteração de estrelas."
]

def value_to_emojis(yellow: float, gray: float, mixed_used: bool = False) -> str:
    total = min(yellow + gray, 5.0)
    yellow = min(yellow, total)
    gray = max(0.0, total - yellow)

    result = []
    full_y = int(yellow)
    half_y = 1 if yellow - full_y >= 0.5 else 0
    full_g = int(gray)
    half_g = 1 if gray - full_g >= 0.5 else 0

    result.extend([FULL_YELLOW] * full_y)
    if half_y:
        result.append(HALF_MIXED if mixed_used else HALF_YELLOW)
    result.extend([FULL_GRAY] * full_g)
    if half_g:
        result.append(HALF_GRAY)

    return ''.join(result)

@app.route("/skill-up", methods=["POST"])
def skill_up():
    data = request.get_json(force=True, silent=True)
    if not data or "stars" not in data:
        return jsonify({"error": "Envie um JSON com { 'stars': '<emoji_string>' }"}), 400

    emojis = EMOJI_PATTERN.findall(data["stars"])
    yellow = 0.0
    gray = 0.0
    mixed_used = False

    for e in emojis:
        val = EMOJI_TO_VALUE.get(e, 0)
        if e in [FULL_YELLOW, HALF_YELLOW, HALF_MIXED]:
            yellow += val
        else:
            gray += val

    total = yellow + gray
    if total >= 5.0 or yellow >= 5.0:
        return jsonify({
            "message": "❗ Este jogador já atingiu o limite de 5 estrelas totais.",
            "updated_stars": value_to_emojis(yellow, gray),
            "evolved": 0
        })

    # Sorteio
    outcome = random.choices([0, 0.5, 1.0, 1.5, 2.0], weights=[20, 30, 25, 15, 10])[0]
    evolved = 0.0

    if outcome > 0 and gray > 0:
        while outcome >= 1.0 and gray >= 1.0 and (yellow + gray) < 5.0:
            yellow += 1.0
            gray -= 1.0
            evolved += 1.0
            outcome -= 1.0
        if outcome >= 0.5 and gray >= 0.5 and (yellow + gray) < 5.0:
            yellow += 0.5
            gray -= 0.5
            evolved += 0.5
            mixed_used = True

    # Garante o máximo de 5 estrelas totais
    if yellow + gray > 5.0:
        excess = (yellow + gray) - 5.0
        if gray >= excess:
            gray -= excess
        else:
            yellow -= (excess - gray)
            gray = 0

    msg = random.choice(MENSAGENS_TREINO if evolved > 0 else MENSAGENS_SEM_EVOLUCAO)

    return jsonify({
        "message": msg,
        "updated_stars": value_to_emojis(yellow, gray, mixed_used),
        "evolved": evolved
    })

@app.route("/")
def home():
    return "✅ Skill Up API Online – Versão Final com Validação e Limite Rígido"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
