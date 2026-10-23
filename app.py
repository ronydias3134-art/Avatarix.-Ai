import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuração da API do Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Prompts com Suporte a B-Roll (Visual Cues) e A/B Testing de Ganchos (Hooks)
PERSONAS = {
    "us_sports": {
        "name": "US Sports & Culture (NFL, NBA, MLB)",
        "description": "Análises vibrantes de desporto americano e destaques com múltiplos ganchos.",
        "system_instruction": (
            "És um influenciador e especialista em desportos americanos (NBA, NFL, MLB). "
            "Cria um roteiro para vídeo direcionado ao mercado americano calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as seguintes chaves:\n"
            "- 'hook_a': Gancho Curiosidade/Choque (0-3s)\n"
            "- 'hook_b': Gancho Pergunta Direta (0-3s)\n"
            "- 'hook_c': Gancho Estatística/Número Impactante (0-3s)\n"
            "- 'narration': Texto principal de narração para o avatar ler em 23 segundos adicionais\n"
            "- 'visual_prompts': Instruções passo a passo de edição visual/B-roll para cada segmento do vídeo\n"
            "- 'caption': Legenda envolvente com hashtags de desporto US"
        )
    },
    "cozinha_saudavel": {
        "name": "Healthy Cooking & Oil-Free Recipes",
        "description": "Receitas saudáveis sem gordura e truques de air fryer com cortes dinâmicos.",
        "system_instruction": (
            "És um influenciador especialista em culinária saudável e sem gordura/óleo. "
            "Cria um roteiro para vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as seguintes chaves:\n"
            "- 'hook_a': Gancho Dor/Problema (0-3s)\n"
            "- 'hook_b': Gancho Sabor/Desejo sem Culpa (0-3s)\n"
            "- 'hook_c': Gancho Rapidez/Praticidade (0-3s)\n"
            "- 'narration': Passo a passo ou dica explicada de forma rápida para 23 segundos\n"
            "- 'visual_prompts': Sugestões visuais de close-ups de comida, b-roll e textos na tela\n"
            "- 'caption': Legenda explicativa com CTA e hashtags fit"
        )
    },
    "tech_ai": {
        "name": "Tech, AI & Automation",
        "description": "Ferramentas de IA, automação e truques de produtividade em tempo recorde.",
        "system_instruction": (
            "És um especialista em tecnologia, IA e automações digitais. "
            "Cria um roteiro para vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as seguintes chaves:\n"
            "- 'hook_a': Gancho Economia de Tempo (0-3s)\n"
            "- 'hook_b': Gancho Revelação de Ferramenta Secreta (0-3s)\n"
            "- 'hook_c': Gancho 'Pára de fazer isto manualmente' (0-3s)\n"
            "- 'narration': Explicação direta da ferramenta/automação para ler em 23 segundos\n"
            "- 'visual_prompts': Gravação de tela, animação de interface e b-roll de tecnologia\n"
            "- 'caption': Legenda explicativa com hashtags de tecnologia/IA"
        )
    },
    "negocios_financas": {
        "name": "Business, Money & Entrepreneurship",
        "description": "Empreendedorismo, finanças pessoais e mentalidade de crescimento.",
        "system_instruction": (
            "És um mentor de negócios, finanças pessoais e investimentos. "
            "Cria um roteiro para vídeo calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as seguintes chaves:\n"
            "- 'hook_a': Gancho Provocação Financeira (0-3s)\n"
            "- 'hook_b': Gancho Erro Comum de Negócios (0-3s)\n"
            "- 'hook_c': Gancho Estratégia de Rendimento (0-3s)\n"
            "- 'narration': Conselho prático e direto para aplicação imediata em 23 segundos\n"
            "- 'visual_prompts': Gráficos dinâmicos, estilo de vida, b-roll de escritório/foco\n"
            "- 'caption': Legenda reflexiva com hashtags de negócios/finanças"
        )
    },
    "arbitrage_deals": {
        "name": "Central Arbitrage & Direct Sales (Oportunidades de Mercado)",
        "description": "Motor central de arbitragem (odds, e-commerce, ofertas de conversão direta).",
        "system_instruction": (
            "És um especialista em arbitragem de mercado e anúncios de alta conversão (Direct Sales/UGC). "
            "Cria um roteiro para vídeo de VENDAS/ARBITRAGEM calibrado para 26 SEGUNDOS (55 a 65 palavras). "
            "Devolve EXCLUSIVAMENTE um objeto JSON válido com as seguintes chaves:\n"
            "- 'hook_a': Gancho Urgência/Oportunidade Limitada (0-3s)\n"
            "- 'hook_b': Gancho Economia/Margem de Lucro (0-3s)\n"
            "- 'hook_c': Gancho Problema vs. Solução Imediata (0-3s)\n"
            "- 'narration': Exposição clara do spread, vantagem do produto ou oferta em 23 segundos\n"
            "- 'visual_prompts': Demonstração do produto/odds, transições de oferta, indicação da bio/link\n"
            "- 'caption': Legenda com chamada de ação direta (CTA) para conversão/compra"
        )
    }
}

@app.route("/")
def index():
    return render_template("index.html", personas=PERSONAS)

@app.route("/generate-script", methods=["POST"])
def generate_script():
    data = request.get_json()
    persona_key = data.get("persona")
    topic = data.get("topic")

    if not persona_key or persona_key not in PERSONAS:
        return jsonify({"status": "error", "message": "Opção inválida selecionada."}), 400

    if not topic or not topic.strip():
        return jsonify({"status": "error", "message": "Por favor, insira um tema/oportunidade."}), 400

    persona_info = PERSONAS[persona_key]

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = f"{persona_info['system_instruction']}\n\nTema/Tópico/Oportunidade: {topic}"
        response = model.generate_content(prompt)

        script_data = json.loads(response.text)

        return jsonify({
            "status": "success",
            "persona": persona_key,
            "script": script_data,
            "target_duration": "26s"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao gerar roteiro: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
