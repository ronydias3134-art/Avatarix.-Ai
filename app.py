def get_best_flash_model():
    """Procura automaticamente o modelo flash disponível na tua conta para evitar erros 404."""
    try:
        for m in client.models.list():
            if "flash" in m.name:
                return m.name
    except Exception:
        pass
    # Fallback seguro caso a listagem falhe
    return "gemini-2.5-flash"

@app.route("/generate-script", methods=["POST"])
def generate_script():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Dados inválidos."}), 400

        persona_key = data.get("persona")
        topic = data.get("topic")

        if not persona_key or persona_key not in PERSONAS:
            return jsonify({"status": "error", "message": "Opção inválida selecionada."}), 400

        if not topic or not topic.strip():
            return jsonify({"status": "error", "message": "Por favor, insira um tema/oportunidade."}), 400

        persona_info = PERSONAS[persona_key]

        # Descobre o modelo ativo dinamicamente (adeus a erros de nomes desatualizados)
        selected_model = get_best_flash_model()

        response = client.models.generate_content(
            model=selected_model,
            contents=f"{persona_info['system_instruction']}\n\nTema/Tópico/Oportunidade: {topic}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        if not response or not response.text:
            return jsonify({
                "status": "error",
                "message": "A API não retornou conteúdo."
            }), 500

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
            "message": f"Erro interno no servidor: {str(e)}"
        }), 500
