import os
import json
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
És o motor central do Avatarx.ai, um ecossistema autónomo de geração de conteúdo desportivo e estratégia orgânica de alta visibilidade.
Responde SEMPRE num objeto JSON estrito com as seguintes chaves:
- "avatar_ativo": Nome da persona utilizada (Europa/Benfica, Global, O Professor, O Reator).
- "tipo_conteudo": "artigo", "comentario" ou "impulso_organico".
- "alvo_ou_programa": Nome do jogador, celebridade, programa ou página-alvo.
- "titulo": Título chamativo (se for artigo) ou N/A (se for comentário).
- "conteudo": O texto gerado (se for comentário, DEVE ser 100% discreto, natural, inteligente e contextual. NUNCA incluir links, NUNCA pedir para seguir o perfil, NUNCA usar spam ou hashtags excessivas. Deve parecer a opinião autêntica de um especialista para atrair cliques orgânicos no perfil).
- "hashtags": Lista de hashtags relevantes.
- "prompt_imagem": Descrição detalhada em inglês para geração de imagem.
"""

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Avatarx.ai - Central de Automação & Visibilidade</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 650px; margin: 0 auto; background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        h1 { color: #38bdf8; text-align: center; font-size: 24px; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        .tabs { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        .tab-btn { background: #334155; color: #cbd5e1; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: background 0.2s; font-size: 14px; }
        .tab-btn.active { background: #0284c7; color: white; }
        .section { display: none; }
        .section.active { display: block; }
        label { display: block; margin-top: 15px; font-weight: bold; color: #cbd5e1; }
        select, textarea, button { width: 100%; padding: 12px; margin-top: 5px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 16px; box-sizing: border-box; }
        textarea { height: 100px; resize: vertical; }
        button.action-btn { background: #0284c7; color: white; font-weight: bold; border: none; cursor: pointer; margin-top: 20px; transition: background 0.2s; }
        button.action-btn:hover { background: #0ea5e9; }
        .result { margin-top: 20px; background: #0f172a; padding: 15px; border-radius: 8px; border-left: 4px solid #38bdf8; white-space: pre-wrap; word-break: break-word; }
        .loading { text-align: center; color: #94a3b8; display: none; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Avatarx.ai</h1>
        <p class="subtitle">Central de Conteúdo & Impulso Orgânico Discreto</p>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="mudarTab('conteudo')">📝 Gerar Artigo</button>
            <button class="tab-btn" onclick="mudarTab('comentarios')">🛡️ Comentário Orgânico (Seguro)</button>
        </div>

        <!-- TAB 1: CONTEÚDO PRINCIPAL -->
        <div id="sec-conteudo" class="section active">
            <label for="avatar-c">Selecionar Persona (Avatar):</label>
            <select id="avatar-c">
                <option value="Europa/Benfica">🔴 Europa/Benfica (Foco no Benfica e Futebol Europeu)</option>
                <option value="Global">🌍 Global (Análise Geral do Futebol)</option>
                <option value="O Professor">🧠 O Professor (Análise Tática Profunda)</option>
                <option value="O Reator">🔥 O Reator (Opinião Forte e Direta)</option>
            </select>

            <label for="prompt-c">Tema ou Tópico para o Conteúdo:</label>
            <textarea id="prompt-c" placeholder="Ex: Análise da vitória brilhante na Champions League..."></textarea>

            <button class="action-btn" onclick="gerar('conteudo')">Gerar Conteúdo Automático</button>
        </div>

        <!-- TAB 2: AUTOMAÇÃO DE COMENTÁRIOS DISCRETOS E ANTI-BAN -->
        <div id="sec-comentarios" class="section">
            <label for="avatar-com">Selecionar Persona para o Comentário:</label>
            <select id="avatar-com">
                <option value="O Professor">🧠 O Professor (Autoridade e análise natural - Recomendado)</option>
                <option value="O Reator">🔥 O Reator (Reação genuína e de alto engajamento)</option>
                <option value="Europa/Benfica">🔴 Europa/Benfica (Foco clubístico autêntico)</option>
                <option value="Global">🌍 Global (Visão desportiva neutra)</option>
            </select>

            <label for="prompt-com">Contexto do Post (Jogador, Treinador ou Famoso):</label>
            <textarea id="prompt-com" placeholder="Ex: O jogador publicou uma foto do treino a preparar-se para o grande jogo de sábado..."></textarea>

            <button class="action-btn" onclick="gerar('comentario')">Gerar Comentário Natural & Seguro</button>
        </div>

        <div id="loading" class="loading">A inteligência artificial está a criar a resposta perfeita... ⚽</div>
        <div id="result" class="result" style="display:none;"></div>
    </div>

    <script>
        function mudarTab(tipo) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            
            if(tipo === 'conteudo') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('sec-conteudo').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('sec-comentarios').classList.add('active');
            }
            document.getElementById('result').style.display = 'none';
        }

        async function gerar(tipo) {
            let avatar, prompt, endpoint;
            
            if(tipo === 'conteudo') {
                avatar = document.getElementById('avatar-c').value;
                prompt = document.getElementById('prompt-c').value;
                endpoint = '/gerar';
            } else {
                avatar = document.getElementById('avatar-com').value;
                prompt = "Gera um comentário extremamente discreto, natural, inteligente e envolvente para publicar no post de uma figura pública. O objetivo é causar curiosidade natural sem parecer promoção ou spam. Contexto: " + document.getElementById('prompt-com').value;
                endpoint = '/gerar';
            }

            if (!prompt || prompt.trim() === "" || prompt.includes("Contexto:  $")) {
                alert('Por favor, escreve o tema ou o contexto da publicação!');
                return;
            }

            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');

            loading.style.display = 'block';
            resultDiv.style.display = 'none';

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ avatar, prompt })
                });

                const data = await response.json();
                loading.style.display = 'none';
                resultDiv.style.display = 'block';

                if (response.ok) {
                    resultDiv.innerHTML = `<strong>Avatar Ativo:</strong> ${data.avatar_ativo || 'N/A'}\n\n` +
                                          `<strong>Tipo:</strong> ${data.tipo_conteudo || 'N/A'}\n\n` +
                                          (data.titulo && data.titulo !== 'N/A' ? `<strong>Título:</strong> ${data.titulo}\n\n` : '') +
                                          `<strong>Comentário Gerado (Pronto a Copiar):</strong>\n${data.conteudo || ''}`;
                } else {
                    resultDiv.innerHTML = `Erro: ${data.erro}`;
                }
            } catch (err) {
                loading.style.display = 'none';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `Erro de ligação: ${err.message}`;
            }
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

@app.route("/gerar", methods=["POST"])
def gerar():
    try:
        dados = request.get_json() or {}
        prompt_usuario = dados.get("prompt", "Gera uma análise sobre o momento atual do futebol.")
        avatar = dados.get("avatar", "Europa/Benfica")
        
        if not GEMINI_API_KEY:
            return jsonify({"erro": "GEMINI_API_KEY não configurada no ambiente."}), 500

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt_final = f"Instrução: {SYSTEM_INSTRUCTION}\nAvatar: {avatar}\nPedido: {prompt_usuario}"
        resposta = model.generate_content(prompt_final)
        
        return jsonify(json.loads(resposta.text))
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
