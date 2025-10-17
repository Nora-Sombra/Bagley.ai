import google.generativeai as genai

# ⚠️ IMPORTANTE: configura tu clave API antes de usar
# genai.configure(api_key="AIzaSyAVVZ-fUa3bYoNqFAXXseEYNg7oO1OO4_w")

def responder(mensaje, modo="programacion", historial=None):
    """Versión simplificada del cerebro de Bagley, sin interfaz gráfica."""
    try:
        modelo = genai.GenerativeModel('models/gemini-2.0-flash')
        
        prompts = {
            "psicologo": "Actúa como un psicólogo empático llamado Bagley. Escucha y responde con comprensión y calma.",
            "deberes": "Eres Bagley, un asistente que ayuda con los deberes explicando las cosas paso a paso y con paciencia.",
            "programacion": "Eres Bagley, un programador experto que explica código y ayuda a depurar problemas en Python u otros lenguajes."
        }

        contexto = prompts.get(modo, prompts["programacion"]) + "\n\n"

        if historial:
            for msg in historial[-6:]:
                contexto += f"{msg['role']}: {msg['content']}\n"

        contexto += f"Usuario: {mensaje}\nBagley:"

        respuesta = modelo.generate_content(contexto)
        texto_respuesta = respuesta.text.strip()
        return texto_respuesta

    except Exception as e:
        return f"Lo siento, tuve un problema: {str(e)}"
