from flask import Flask, request, jsonify
from flask_cors import CORS

from routes.health_routes import health_bp
from routes.dashboard_routes import dashboard_bp
from routes.event_routes import event_bp

app = Flask(__name__)

CORS(app)

# ─────────────────────────────────────────────
# Blueprints
# ─────────────────────────────────────────────

app.register_blueprint(health_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(event_bp)

# ─────────────────────────────────────────────
# Home
# ─────────────────────────────────────────────

@app.route("/")
def home():
    return {
        "message": "Backend rodando!"
    }

# ─────────────────────────────────────────────
# Atualização manual
# ─────────────────────────────────────────────

@app.route("/atualizar", methods=["PUT"])
def transformar_evento_para_ilha():

    evento = request.json

    if not evento:
        return jsonify({
            "erro": "Payload vazio"
        }), 400

    resposta = {
        "id": evento.get("id"),
        "editor": evento.get("editor"),
        "avatar": evento.get("avatar"),
        "ilha": evento.get("ilha"),

        # AQUI ESTAVA O BUG
        "status": evento.get("status", "ocupado"),

        "projeto": evento.get("arquivo"),
    }

    return jsonify(resposta)

# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )