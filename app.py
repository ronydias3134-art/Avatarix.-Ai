import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Inicializa o cliente lendo automaticamente a GEMINI_API_KEY do ambiente
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key) if api_key else genai.Client()

PERSONAS = {
    "sport": {
        "name": "Leandro Dias — Global & US Sports",
        "system_instruction": (
            "És o Leandro Dias, um influencer e especialista em futebol e desporto internacional. "
            "Cria um roteiro de vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as chaves: "
            "'hook_a', 'hook_b', 'hook_c', 'narration', 'visual_prompts', 'caption'. "
            "A assinatura RD deve estar subtilmente sugerida na legenda."
        )
    },
    "cozinha_saudavel": {
        "name": "Rafaela Dias — Healthy Cooking",
        "system_instruction": (
            "És a Rafaela Dias, especialista em culinária saudável e sem gordura. "
            "Cria um roteiro de vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as chaves: "
            "'hook_a', 'hook_b', 'hook_c', 'narration', 'visual_prompts', 'caption'. "
            "A assinatura RD deve estar subtilmente sugerida na legenda."
        )
    },
    "tech_ai": {
        "name": "Maia Dias — Tech & AI",
        "system_instruction": (
            "És a Maia Dias, especialista em tecnologia e ferramentas de IA. "
            "Cria um roteiro de vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as chaves: "
            "'hook_a', 'hook_b', 'hook_c', 'narration', 'visual_prompts', 'caption'. "
            "A assinatura RD deve estar subtilmente sugerida na legenda."
        )
    },
    "negocios_financas": {
        "name": "O Professor — Business & Money",
        "system_instruction": (
            "És O Professor, mentor de negócios, finanças pessoais e empreendedorismo. "
            "Cria um roteiro de vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as chaves: "
            "'hook_a', 'hook_b', 'hook_c', 'narration', 'visual_prompts', 'caption'. "
            "A assinatura RD deve estar subtilmente sugerida na legenda."
        )
    },
    "arbitrage_deals": {
        "name": "Sérgio Dias — Central Arbitrage & Sales",
        "system_instruction": (
            "És o Sérgio Dias, especialista em arbitragem e vendas diretas. "
            "Cria um roteiro de vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as chaves: "
            "'hook_a', 'hook_b', 'hook_c', 'narration', 'visual_prompts', 'caption'. "
            "A assinatura RD deve estar subtilmente sugerida na legenda."
        )
    }
}

@app.route("/")
def index():
    return render_template("index.html", personas=PERSONAS)

@app.route("/generate-script", methods=["POST"])
def generate_script():
    try:
        data = request.get_json() or {}
        persona_key = data.get("persona")
        topic = data.get("topic")

        if not persona_key or persona_key not in PERSONAS:
            return jsonify({"status": "error", "message": "Por favor, seleciona um influencer válido."}), 400

        if not topic or not topic.strip():
            return jsonify({"status": "error", "message": "Por favor, insira um tema ou tópico."}), 400

        persona_info = PERSONAS[persona_key]
        prompt = f"{persona_info['system_instruction']}\n\nTema do vídeo: {topic}"

        # Tenta os dois modelos suportados
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
        response_text = None
        last_error = None

        for model_name in models_to_try:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                if res and res.text:
                    response_text = res.text
                    break
            except Exception as e:
                logging.warning(f"Erro com {model_name}: {str(e)}")
                last_error = e

        if not response_text:
            return jsonify({
                "status": "error",
                "message": f"Erro na conexão com o Gemini: {str(last_error)}"
            }), 500

        # Limpeza de marcadores Markdown caso existam
        raw = response_text.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        parsed_json = json.loads(raw.strip())

        return jsonify({
            "status": "success",
            "persona": persona_key,
            "script": parsed_json
        })

    except Exception as err:
        logging.error(f"Erro interno: {str(err)}")
        return jsonify({"status": "error", "message": f"Falha ao processar: {str(err)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
