import os
import json
import logging
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Configuração de Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Configuração Segura da Chave Gemini
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    logging.error("ERRO CRÍTICO: Nenhuma variável GEMINI_API_KEY encontrada no Render!")

# Definição das Personas
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

        prompt = f"""
{persona['prompt_base']}

Tema da Publicação: {topic}

Responde EXCLUSIVAMENTE com um objeto JSON válido no seguinte formato (sem formatação markdown extra fora do JSON):
{{
    "hook": "Uma frase de impacto inicial para prender a atenção em 3 segundos.",
    "body": "O desenvolvimento principal da análise/conteúdo em formato de roteiro falado.",
    "cta": "Uma chamada para ação (Call to Action) para gerar comentários e partilhas.",
    "caption": "A legenda pronta para redes sociais com hashtags relevantes e terminando com a assinatura - RD."
}}
"""

        # Usar o modelo estável
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)

        if not response or not response.text:
            raise Exception("O Gemini não devolveu resposta.")

        # Limpeza de texto para garantir JSON perfeito
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(clean_text)
        
        return jsonify(result_json)

    except Exception as e:
        logging.error(f"Erro no servidor: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
