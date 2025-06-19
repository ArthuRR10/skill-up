from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# Emojis
FULL_YELLOW = "<:ystar:1214063559076749312>"
HALF_YELLOW = "<:mystar:1214063655646138408>"
HALF_MIXED  = "<:ysstar:1216072160959922209>"  # meia amarela + meia cinza
FULL_GRAY   = "<:sstar:1214063700886036532>"
HALF_GRAY   = "<:msstar:1216072572924596276>"

EMOJI_TO_VALUE = {
    FULL_YELLOW: 1.0,
    HALF_YELLOW: 0.5,
    HALF_MIXED:  1.0,  # conta como 1 amarela
    FULL_GRAY:   1.0,
    HALF_GRAY:   0.5
}

EMOJI_PATTERN = re.compile(r'<:[a-zA-Z0-9_]+:[0-9]+>')

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

def value_to_emojis(yellow: float, gray: float, total_slots: float, used_mixed: bool) -> str:
    result = []
    current = 0.0

    # Adiciona amarelas inteiras
    while yellow >= 1.0 and current + 1.0 <= total_slots:
        result.append(FULL_YELLOW)
        yellow -= 1.0
        current += 1.0

    # Se sobrou meia amarela e cabe
    if yellow >= 0.5 and current + 1.0 <= total_slots:
        result.append(HALF_MIXED if used_mixed else HALF_YELLOW)
        yellow -= 0.5
        current += 1.0  # meia amarela + meia cinza = 1 slot

    # Adiciona cinzas inteiras
    while gray >= 1.0 and current + 1.0 <= total_slots:
        result.append(FULL_GRAY)
        gray -= 1.0
        current += 1.0

    # Meia cinza se couber
    if gray >= 0.5 and current + 0.5 <= total_slots:
        result.append(HALF_GRAY)
        gray -= 0.5
        current += 0.5

    return ''.join(result)

@app.route("/skill-up", methods=["POST"])
def skill_up():
    data = request.get_json(force=True, silent=True)
    if not data or "stars" not in data:
        return jsonify({"error": "Envie um JSON com { 'stars': '<emoji_string>' }"}), 400

    emojis = EMOJI_PATTERN.findall(data["stars"])
    yellow = gray = 0.0
    used_mixed = False

    for e in emojis:
        val = EMOJI_TO_VALUE.get(e, 0)
        if e in [FULL_YELLOW, HALF_YELLOW, HALF_MIXED]:
            yellow += val
        elif e in [FULL_GRAY, HALF_GRAY]:
            gray += val

    total_slots = yellow + gray  # slots máximos permitidos (não pode passar disso)
    original_yellow = yellow
    original_gray = gray

    # Sorteio
    outcome = random.choices([0, 0.5, 1.0, 1.5], weights=[25, 35, 25, 15])[0]
    evolved = 0.0

    if outcome > 0:
        while outcome >= 1.0 and gray >= 1.0:
            yellow += 1.0
            gray -= 1.0
            evolved += 1.0
            outcome -= 1.0

        if outcome >= 0.5 and gray >= 0.5:
            yellow += 0.5
            gray -= 0.5
            evolved += 0.5
            used_mixed = True

    # Corrigir se ultrapassou os slots
    if yellow + gray > total_slots:
        excess = (yellow + gray) - total_slots
        if gray >= excess:
            gray -= excess
        else:
            yellow -= (excess - gray)
            gray = 0

    # Garante que o sistema nunca gera mais estrelas do que veio
    updated = value_to_emojis(yellow, gray, total_slots, used_mixed)
    mensagem = random.choice(MENSAGENS_TREINO if evolved > 0 else MENSAGENS_SEM_EVOLUCAO)

    return jsonify({
        "message": mensagem,
        "updated_stars": updated,
        "evolved": evolved
    })

@app.route("/")
def home():
    return "✅ Skill Up API Online – Modo Conversor (sem adicionar estrelas)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
