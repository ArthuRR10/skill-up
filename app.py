from flask import Flask, request, jsonify
import random
import re

app = Flask(__name__)

# Emojis
FULL_YELLOW = "<:ystar:1214063559076749312>"
FULL_GRAY   = "<:sstar:1214063700886036532>"
HALF_YELLOW = "<:mystar:1214063655646138408>"
HALF_GRAY   = "<:msstar:1216072572924596276>"

# Mapeia emoji → valor
EMOJI_TO_VALUE = {
    FULL_YELLOW: 1.0,
    HALF_YELLOW: 0.5,
    FULL_GRAY:   1.0,
    HALF_GRAY:   0.5
}

# Pega qualquer emoji do tipo <:nome:id>
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
    """Converte as quantidades float de amarelas/ cinzas em emojis."""
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
    payload = request.get_json(force=True)
    stars_raw = payload.get("stars", "")
    
    # DEBUG: veja no log o que chegou
    print("DEBUG payload:", payload)
    
    # Extrai emojis mesmo que grudados
    emojis = EMOJI_PATTERN.findall(stars_raw)
    
    yellow = 0.0
    gray   = 0.0
    for e in emojis:
        val = EMOJI_TO_VALUE.get(e, 0)
        if e in (FULL_YELLOW, HALF_YELLOW):
            yellow += val
        else:
            gray += val
    
    # Limite de amarelas
    if yellow >= 5.0:
        return jsonify({
            "message": "❗️ Este jogador já tem 5 estrelas amarelas — não pode evoluir mais!",
            "updated_stars": value_to_emojis(yellow, gray),
            "evolved": 0
        })
    
    # Chance de outcome
    outcome = random.choices([1.5, 0.5, 0], weights=[25,50,25], k=1)[0]
    evolved = 0.0
    
    # Converte cinza → amarelo até outcome zerar
    while outcome >= 1.0 and gray >= 1.0 and yellow < 5.0:
        yellow += 1.0; gray -= 1.0; evolved += 1.0; outcome -= 1.0
    if outcome >= 0.5 and gray >= 0.5 and yellow < 5.0:
        yellow += 0.5; gray -= 0.5; evolved += 0.5
    
    # Monta resposta
    if evolved > 0:
        msg = random.choice(MENSAGENS_TREINO)
    else:
        msg = random.choice(MENSAGENS_SEM_EVOLUCAO)
    
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
