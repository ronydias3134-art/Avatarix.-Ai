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

        # Lista de modelos atualizada e compatível com a nova SDK google-genai
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash-8b"]
        response_text = None
        last_error = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"{persona_info['system_instruction']}\n\nTema/Tópico/Oportunidade: {topic}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )
                if response and response.text:
                    response_text = response.text
                    break
            except Exception as e:
                last_error = e
                continue

        if not response_text:
            return jsonify({
                "status": "error",
                "message": f"Erro ao comunicar com a API do Gemini: {str(last_error)}"
            }), 500

        script_data = json.loads(response_text)
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
