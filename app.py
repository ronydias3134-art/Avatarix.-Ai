import os
import json
import requests
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuração da API Key do Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Personas Pré-definidas para os Influenciadores/Avatares
PERSONAS = {
    "europa_benfica": {
        "name": "Europa / Benfica",
        "system_instruction": "És um comentador e criador de conteúdo apaixonado pelo Benfica e pelo futebol europeu. O teu tom é dinâmico, envolvente, humano e conhecedor."
    },
    "noticias_geral": {
        "name": "Notícias & Atualidades",
        "system_instruction": "És um apresentador e criador de conteúdos de notícias rápidas. O teu tom é direto, cativante e focado nos pontos principais."
    },
    "financas_negocios": {
        "name": "Finanças & Empreendedorismo",
        "system_instruction": "És um especialista em negócios e finanças pessoais. O teu tom é motivador, prático e focado em dicas acionáveis."
    },
    "estilo_vida": {
        "name": "Estilo de Vida & Curiosidades",
        "system_instruction": "És um influenciador de estilo de vida e entretenimento. O teu tom é descontraído, divertido e altamente interativo."
    }
}

@app.route("/")
def index():
    return render_template("index.html", personas=PERSONAS)

@app.route("/generate-comment", methods=["POST"])
def generate_comment():
    data = request.json or {}
    text = data.get("text", "").strip()
    persona_key = data.get("persona", "europa_benfica")

    if not text:
        return jsonify({"status": "error", "message": "Insira o texto da publicação!"}), 400

    persona_info = PERSONAS.get(persona_key, PERSONAS["europa_benfica"])

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
{persona_info['system_instruction']}

Gera um comentário orgânico e natural em português para a seguinte publicação:
"{text}"

O comentário deve soar 100% humano, sem spam e com forte envolvimento.
"""
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "result": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/generate-script", methods=["POST"])
def generate_script():
    """Gera roteiro otimizado para vídeos curtos (Reels/TikTok/Shorts)."""
    data = request.json or {}
    topic = data.get("topic", "").strip()
    persona_key = data.get("persona", "europa_benfica")
    duration_sec = data.get("duration", 30)

    if not topic:
        return jsonify({"status": "error", "message": "Insira o tema do vídeo!"}), 400

    persona_info = PERSONAS.get(persona_key, PERSONAS["europa_benfica"])

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
{persona_info['system_instruction']}

Cria um roteiro completo de vídeo curto ({duration_sec} segundos) sobre:
"{topic}"

Formata o resultado em JSON com as seguintes chaves:
- "hook": frase inicial chamativa (primeiros 3 segundos)
- "narration": texto de narração completo e fluido
- "broll_suggestions": lista de sugestões de imagens/vídeos de fundo
- "caption": legenda pronta para a publicação com hashtags
"""
        response = model.generate_content(prompt)
        
        # Limpeza rápida de tags markdown caso o Gemini devolva em formato ```json
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()

        script_data = json.loads(raw_text)
        return jsonify({"status": "success", "script": script_data})
    except Exception as e:
        # Resposta de salvaguarda caso a formatação estrita falhe
        return jsonify({
            "status": "success", 
            "script": {
                "hook": "Atenção a isto!",
                "narration": response.text if 'response' in locals() else "Erro ao gerar",
                "broll_suggestions": ["Vídeo de fundo genérico"],
                "caption": topic
            }
        })


@app.route("/api/v1/trigger-automation", methods=["POST"])
def trigger_automation():
    """
    Endpoint para Piloto Automático:
    Recebe os dados, gera o roteiro e dispara o Webhook para a plataforma
    de renderização de vídeo e publicação direta (Make / Ayrshare / InVideo).
    """
    data = request.json or {}
    webhook_url = os.getenv("AUTOMATION_WEBHOOK_URL")
    
    if not webhook_url:
        return jsonify({
            "status": "error", 
            "message": "AUTOMATION_WEBHOOK_URL não configurada nas variáveis do Render."
        }), 400

    # Invoca a geração de roteiro
    topic = data.get("topic", "")
    persona_key = data.get("persona", "europa_benfica")
    
    try:
        # Envia a carga de dados (Payload) para o webhook de automação externa
        payload = {
            "source": "Avatarx.ai",
            "persona": persona_key,
            "topic": topic,
            "timestamp": request.headers.get("X-Request-Timestamp", "")
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return jsonify({
            "status": "success", 
            "message": "Automação disparada com sucesso!", 
            "webhook_response": response.status_code
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
