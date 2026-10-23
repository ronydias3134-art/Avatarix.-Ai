import os
import json
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# Instancia o cliente da Google GenAI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_INSTRUCTION = """
És o motor central do Avatarx.ai, um ecossistema autónomo de geração de conteúdo desportivo.
Responde SEMPRE num objeto JSON estrito com as seguintes chaves:
- "avatar_ativo": Nome da persona utilizada (Europa/Benfica, Global, O Professor, O Reator).
- "tipo_conteudo": "artigo" ou "comentario".
- "alvo_ou_programa": Nome do programa, página ou contexto-alvo.
- "titulo": Título chamativo (se for artigo) ou N/A (se for comentário).
- "conteudo": O texto gerado (sem links e sem apelos para seguir páginas).
- "hashtags": Lista de hashtags relevantes.
- "prompt_imagem": Descrição detalhada em inglês para geração de imagem.
"""

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "sistema": "Avatarx.ai API",
        "mensagem": "Servidor ativo e pronto a processar requisições."
    })

@app.route("/gerar", methods=["POST"])
def gerar():
    try:
        dados = request.get_json() or {}
        prompt_usuario = dados.get("prompt", "Gera uma análise sobre o momento atual do futebol.")
        avatar = dados.get("avatar", "Europa/Benfica")
        
        if not GEMINI_API_KEY:
            return jsonify({"erro": "GEMINI_API_KEY não configurada no ambiente."}), 500

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt_final = f"Instrução: {SYSTEM_INSTRUCTION}\nAvatar: {avatar}\nPedido: {prompt_usuario}"
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt_final,
        )
        
        return jsonify(json.loads(response.text))
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
