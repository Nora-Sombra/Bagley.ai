from flask import Flask, request, render_template
from Bagley import responder  # función que genera respuestas

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/responder", methods=["POST"])
def responder_route():
    mensaje = request.form["mensaje"]
    respuesta = responder(mensaje)
    return respuesta

# 👇 ESTA PARTE ES CLAVE PARA RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
