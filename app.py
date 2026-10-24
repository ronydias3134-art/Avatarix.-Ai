import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from google import genai

# Configuração de Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuração Segura do Cliente Gemini
# ---------------------------------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not api_key:
    logging.error("ERRO CRÍTICO: Nenhuma variável GEMINI_API_KEY encontrada no Render!")

# Injeção direta da chave no cliente
client = genai.Client(api_key=api_key) if api_key else genai.Client()

# ---------------------------------------------------------------------------
# Definição das Personas (AvatarX.AI)
# ---------------------------------------------------------------------------
PERSONAS = {
    "leandro": {
        "name": "Leandro Dias",
        "role": "Analista Desportivo e Entusiasta de Futebol",
        "style": "Apoiado, analítico, direto e envolvente. Usa linguagem desportiva moderna.",
        "prompt_base": "És o Leandro Dias, um influenciador e analista de futebol com opiniões fortes, análise tática precisa e paixão pelo jogo. Cria um roteiro vibrante sobre o tema."
    },
    "rafaela": {
        "name": "Rafaela",
        "role": "Criadora de Conteúdo e Lifestyle",
        "style": "Empática, criativa, autêntica e comunicativa.",
        "prompt_base": "És a Rafaela, uma criadora de conteúdo focada em tendências, comunicação digital e histórias reais."
    },
    "maia": {
        "name": "Maia",
        "role": "Especialista em Tecnologia e Futuro",
        "style": "Visão de futuro, didática, precisa e inovadora.",
        "prompt_base": "És a Maia, especialista em inteligência artificial, inovação e tecnologia do futuro."
    },
    "professor": {
        "name": "O Professor",
        "role": "Mentor de Negócios e Estratégia",
        "style": "Sábio, estruturado, motivador e estratégico.",
        "prompt_base": "És O Professor, focado em desenvolvimento pessoal, negócios e mentalidade de sucesso."
    },
    "sergio": {
        "name": "Sérgio",
        "role": "Comentador de Atualidades e Cultura Pop",
        "style": "Carismático, humorístico, crítico e dinâmico.",
        "prompt_base": "És o Sérgio, perito em tendências da internet, cultura pop e grandes debates atuais."
    }
}

# ---------------------------------------------------------------------------
# Rotas do Flask
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", personas=PERSONAS)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json() or {}
        persona_key = data.get("persona", "leandro")
        topic = data.get("topic", "")

        if not topic:
            return jsonify({"error": "Por favor, fornece um tema ou tópico para a publicação."}), 400

        persona = PERSONAS.get(persona_key, PERSONAS["leandro"])

        # Prompt estruturado forçando resposta JSON válida diretamente no texto
        prompt = f"""
{persona['prompt_base']}

Tema da Publicação: {topic}

Responde EXCLUSIVAMENTE com um objeto JSON válido no seguinte formato (sem formatação markdown ```json ... ```):
{{
    "hook": "Uma frase de impacto inicial para prender a atenção em 3 segundos.",
    "body": "O desenvolvimento principal da análise/conteúdo em formato de roteiro falado.",
    "cta": "Uma chamada para ação (Call to Action) para gerar comentários e partilhas.",
    "caption": "A legenda pronta para redes sociais com hashtags relevantes e terminando com a assinatura - RD."
}}
"""

        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
        response_text = None
        last_error = None

        for model_name in models_to_try:
            try:
                # Chamada direta e compatível com a biblioteca genai
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    response_text = response.text
                    break
            except Exception as err:
                last_error = err
                logging.warning(f"Falha ao usar o modelo {model_name}: {err}")

        if not response_text:
            raise Exception(f"Erro na conexão com o Gemini: {last_error}")

        # Limpeza de potenciais marcadores markdown do texto
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Conversão para JSON
        result_json = json.loads(clean_text)
        return jsonify(result_json)

    except Exception as e:
        logging.error(f"Erro durante a geração: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
