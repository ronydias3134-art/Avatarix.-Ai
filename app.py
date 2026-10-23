import os
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuração da API Key do Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Personas do Avatarx.ai
PERSONAS = {
    "europa_benfica": "Especialista no futebol europeu e no Benfica. Tom profissional, tático e apaixonado.",
    "o_professor": "Analista sénior, focado em tática profunda, estatísticas e visão crítica e calma.",
    "o_reator": "Engajador dinâmico, rápido, focado no impacto de momento e reações às redes sociais.",
    "global": "Visão global sobre desporto, atletas e celebridades. Linguagem universal e acessível."
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Avatarx.ai — Motor de Crescimento Orgânico</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent: #3b82f6;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text);
            margin: 0;
            padding: 15px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 600px;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            font-size: 1.6rem;
            color: var(--accent);
            margin: 0 0 5px 0;
        }
        .header p {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin: 0;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab-btn {
            flex: 1;
            padding: 12px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text-muted);
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            font-size: 0.9rem;
        }
        .tab-btn.active {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }
        .tab-content {
            display: none;
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        .tab-content.active {
            display: block;
        }
        label {
            display: block;
            font-size: 0.85rem;
            margin-bottom: 6px;
            color: var(--text-muted);
        }
        select, textarea, input {
            width: 100%;
            padding: 10px;
            background: var(--bg-color);
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 6px;
            margin-bottom: 15px;
            box-sizing: border-box;
            font-size: 0.95rem;
        }
        button.submit-btn {
            width: 100%;
            padding: 12px;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
        }
        .result-box {
            margin-top: 20px;
            padding: 15px;
            background: var(--bg-color);
            border-radius: 8px;
            border: 1px solid var(--border);
            white-space: pre-wrap;
            font-size: 0.95rem;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AVATARX.AI</h1>
            <p>Motor de Envolvimento & Conteúdo Orgânico</p>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('comment')">🛡️ Comentário Orgânico</button>
            <button class="tab-btn" onclick="switchTab('article')">📝 Gerador de Artigo</button>
        </div>

        <!-- ABA 1: COMENTÁRIO ORGÂNICO -->
        <div id="tab-comment" class="tab-content active">
            <label>Selecione a Persona / Avatar:</label>
            <select id="comment-persona">
                <option value="europa_benfica">🔴 Europa / Benfica</option>
                <option value="o_professor">🧠 O Professor (Análise Tática)</option>
                <option value="o_reator">⚡ O Reator (Engajamento Rápido)</option>
                <option value="global">🌍 Global (Celebridades & Atletas)</option>
            </select>

            <label>Publicação/Contexto (Cole o texto da publicação):</label>
            <textarea id="comment-context" rows="4" placeholder="Ex: Post do atleta X a festejar a vitória..."></textarea>

            <button class="submit-btn" onclick="generateComment()">Gerar Comentário Seguro</button>
            
            <div id="comment-result" class="result-box" style="display:none;"></div>
        </div>

        <!-- ABA 2: GERADOR DE ARTIGOS -->
        <div id="tab-article" class="tab-content">
            <label>Selecione o Estilo do Artigo:</label>
            <select id="article-persona">
                <option value="o_professor">🧠 O Professor (Análise Profunda)</option>
                <option value="europa_benfica">🔴 Notícias & Visão Europeia</option>
            </select>

            <label>Tema do Artigo:</label>
            <input type="text" id="article-topic" placeholder="Ex: O impacto tático do meio-campo...">

            <button class="submit-btn" onclick="generateArticle()">Gerar Artigo Completo</button>
            
            <div id="article-result" class="result-box" style="display:none;"></div>
        </div>
    </div>

    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            if (tab === 'comment') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('tab-comment').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('tab-article').classList.add('active');
            }
        }

        async function generateComment() {
            const persona = document.getElementById('comment-persona').value;
            const context = document.getElementById('comment-context').value;
            const resultBox = document.getElementById('comment-result');

            if (!context) {
                alert('Insira o texto da publicação!');
                return;
            }

            resultBox.style.display = 'block';
            resultBox.innerText = 'A gerar comentário natural anti-ban...';

            try {
                const res = await fetch('/api/generate-comment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ persona, context })
                });
                const data = await res.json();
                if (data.error) {
                    resultBox.innerText = 'Erro: ' + data.error;
                } else {
                    resultBox.innerText = data.result;
                }
            } catch (err) {
                resultBox.innerText = 'Erro de ligação ao servidor.';
            }
        }

        async function generateArticle() {
            const persona = document.getElementById('article-persona').value;
            const topic = document.getElementById('article-topic').value;
            const resultBox = document.getElementById('article-result');

            if (!topic) {
                alert('Insira o tema do artigo!');
                return;
            }

            resultBox.style.display = 'block';
            resultBox.innerText = 'A estruturar e a gerar o artigo...';

            try {
                const res = await fetch('/api/generate-article', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ persona, topic })
                });
                const data = await res.json();
                if (data.error) {
                    resultBox.innerText = 'Erro: ' + data.error;
                } else {
                    resultBox.innerText = data.result;
                }
            } catch (err) {
                resultBox.innerText = 'Erro de ligação ao servidor.';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate-comment', methods=['POST'])
def api_comment():
    if not API_KEY:
        return jsonify({'error': 'Chave GEMINI_API_KEY não configurada no Render.'}), 500
    
    data = request.json or {}
    persona_key = data.get('persona', 'global')
    context = data.get('context', '')

    persona_desc = PERSONAS.get(persona_key, PERSONAS['global'])

    prompt = f"""
    Atua sob o seguinte perfil/persona: {persona_desc}
    
    INSTRUÇÕES RÍGIDAS DE ANTI-BAN E SEGURANÇA:
    - Escreve um comentário 100% natural para redes sociais.
    - NUNCA incluas links, promoções, frases de venda ou apelativos diretos para seguir contas.
    - Mantém um tom humano, autêntico e adaptado à publicação abaixo.
    
    Publicação base:
    "{context}"
    
    Responde APENAS com o texto final do comentário.
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return jsonify({'result': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-article', methods=['POST'])
def api_article():
    if not API_KEY:
        return jsonify({'error': 'Chave GEMINI_API_KEY não configurada no Render.'}), 500

    data = request.json or {}
    persona_key = data.get('persona', 'o_professor')
    topic = data.get('topic', '')

    persona_desc = PERSONAS.get(persona_key, PERSONAS['o_professor'])

    prompt = f"""
    Escreve um artigo estruturado de análise sobre o tema: "{topic}".
    Adota o tom de voz e estilo: {persona_desc}.
    O artigo deve ser bem fundamentado, claro e pronto a publicar.
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return jsonify({'result': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
