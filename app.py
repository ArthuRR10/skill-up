from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# Emojis
FULL_YELLOW = "<:ystar:1214063559076749312>"
FULL_GRAY   = "<:sstar:1214063700886036532>"
HALF_YELLOW = "<:mystar:1214063655646138408>"
HALF_GRAY   = "<:msstar:1216072572924596276>"
HALF_MIXED  = "<:ysstar:1216072160959922209>"  # meia amarela + meia cinza combinada

# Mapeia emoji → valor
EMOJI_TO_VALUE = {
    FULL_YELLOW: 1.0,
    HALF_YELLOW: 0.5,
    FULL_GRAY:   1.0,
    HALF_GRAY:   0.5,
    HALF_MIXED:  0.5  # conta como 0.5 amarelo e 0.5 cinza
}

# Regex para capturar qualquer emoji no formato <:nome:id>
EMOJI_PATTERN = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

# Mensagens de treino (quando evolui)
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

# Mensagens de “só experiência” (quando não evolui)
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

def value_to_emojis(yellow: float, gray: float) -> str:
    """
    Converte valores float de amarelas e cinzas em sequência de emojis,
    usando HALF_MIXED apenas quando houver 0.5 amarelo e 0.5 cinza sobressalentes.
    """
    result = []

    # Separar inteiras e frações
    full_yellow = int(yellow)
    full_gray = int(gray)
    rem_yellow = round(yellow - full_yellow, 2)
    rem_gray = round(gray - full_gray, 2)

    # Adiciona inteiras
    result.extend([FULL_YELLOW] * full_yellow)
    result.extend([FULL_GRAY] * full_gray)

    # Se tiver 0.5 de cada, usa HALF_MIXED
    if rem_yellow >= 0.5 and rem_gray >= 0.5:
        result.append(HALF_MIXED)
        rem_yellow -= 0.5
        rem_gray -= 0.5

    # Resto individual
    if rem_yellow >= 0.5:
        result.append(HALF_YELLOW)
    if rem_gray >= 0.5:
        result.append(HALF_GRAY)

    return ''.join(result)

@app.route("/skill-up", methods=["POST"])
def skill_up():
    payload = request.get_json(force=True, silent=True)
    if not payload or "stars" not in payload:
        return jsonify({"error": "Envie JSON: { \"stars\": \"<seu string de emojis>\" }"}), 400

    stars_raw = payload["stars"]
    print("DEBUG: recebido stars_raw =", stars_raw)

    emojis = EMOJI_PATTERN.findall(stars_raw)

    yellow = gray = 0.0
    for e in emojis:
        if e == HALF_MIXED:
            yellow += 0.5
            gray += 0.5
        elif e in (FULL_YELLOW, HALF_YELLOW):
            yellow += EMOJI_TO_VALUE.get(e, 0)
        else:
            gray += EMOJI_TO_VALUE.get(e, 0)

    # Limite
    if yellow >= 5.0:
        return jsonify({
            "message": "❗ Este jogador já possui 5 estrelas amarelas — não há mais evolução possível.",
            "updated_stars": value_to_emojis(yellow, gray),
            "evolved": 0
        })

    # Evolução sorteada
    outcome = random.choices([1.5, 0.5, 0], weights=[25, 50, 25], k=1)[0]
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

    msg = random.choice(MENSAGENS_TREINO) if evolved > 0 else random.choice(MENSAGENS_SEM_EVOLUCAO)

    return jsonify({
        "message": msg,
        "updated_stars": value_to_emojis(yellow, gray),
        "evolved": evolved
    })

@app.route("/")
def home():
    return "Skill Up API Online"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
