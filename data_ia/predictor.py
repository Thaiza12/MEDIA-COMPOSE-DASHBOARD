"""
data_ia/predictor.py
Modelo de predição de tempo de conclusão (ETC) usando Scikit-Learn.
Expõe uma API Flask mínima para ser chamada pelo backend.
"""

import os
import pickle
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PREDICTOR] %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://globo:globo123@localhost:5432/media_compose")
MODEL_PATH   = Path(os.getenv("MODEL_PATH", "/app/modelo_etc.pkl"))

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Treinamento
# ---------------------------------------------------------------------------

def carregar_dados_treino(editor_nome: str = None) -> pd.DataFrame:
    """Busca histórico de edições encerradas para treinar o modelo."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        with conn.cursor() as cur:
            if editor_nome:
                cur.execute(
                    """
                    SELECT tamanho_arquivo_mb, duracao_segundos, editor_nome
                    FROM   edicoes
                    WHERE  status           = 'encerrado'
                      AND  duracao_segundos > 60
                      AND  tamanho_arquivo_mb > 0
                      AND  editor_nome     = %s
                    ORDER BY inicio_edicao DESC
                    LIMIT 500
                    """,
                    (editor_nome,),
                )
            else:
                cur.execute(
                    """
                    SELECT tamanho_arquivo_mb, duracao_segundos, editor_nome
                    FROM   edicoes
                    WHERE  status           = 'encerrado'
                      AND  duracao_segundos > 60
                      AND  tamanho_arquivo_mb > 0
                    ORDER BY inicio_edicao DESC
                    LIMIT 2000
                    """,
                )
            rows = cur.fetchall()
            return pd.DataFrame([dict(r) for r in rows])
    finally:
        conn.close()


def treinar_modelo(editor_nome: str = None) -> LinearRegression | None:
    """
    Treina um modelo de Regressão Linear por editor (ou global).
    Retorna None se não houver dados suficientes.
    """
    df = carregar_dados_treino(editor_nome)

    if len(df) < 10:
        log.warning(
            "Dados insuficientes para treinar modelo (%s registros) — editor: %s",
            len(df), editor_nome or "global",
        )
        return None

    X = df[["tamanho_arquivo_mb"]]
    y = df["duracao_segundos"] / 60  # convertemos para minutos

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    mae = mean_absolute_error(y_test, model.predict(X_test))
    log.info(
        "Modelo treinado (%s) — %d amostras — MAE: %.1f min",
        editor_nome or "global", len(df), mae,
    )
    return model


def salvar_modelo(model: LinearRegression, path: Path = MODEL_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    log.info("Modelo salvo em %s", path)


def carregar_modelo(path: Path = MODEL_PATH) -> LinearRegression | None:
    if path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


# ---------------------------------------------------------------------------
# Predição
# ---------------------------------------------------------------------------

# Cache de modelos por editor (evita I/O a cada predição)
_modelos_cache: dict[str, LinearRegression] = {}
_modelo_global: LinearRegression | None = None


def prever(editor_nome: str, tamanho_mb: float) -> int | None:
    """
    Retorna a previsão de minutos restantes para concluir a edição.
    Tenta modelo por editor → modelo global → fallback linear simples.
    """
    global _modelo_global

    # Tenta modelo personalizado do editor
    if editor_nome not in _modelos_cache:
        modelo_editor = treinar_modelo(editor_nome)
        if modelo_editor:
            _modelos_cache[editor_nome] = modelo_editor

    if editor_nome in _modelos_cache:
        pred = _modelos_cache[editor_nome].predict([[tamanho_mb]])[0]
        return max(1, round(pred))

    # Tenta modelo global
    if _modelo_global is None:
        _modelo_global = carregar_modelo() or treinar_modelo()
        if _modelo_global:
            salvar_modelo(_modelo_global)

    if _modelo_global:
        pred = _modelo_global.predict([[tamanho_mb]])[0]
        return max(1, round(pred))

    # Fallback linear: ~1.8 min por 100 MB
    return max(1, round((tamanho_mb / 100) * 1.8))


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    editor    = data.get("editor", "")
    tamanho   = float(data.get("tamanho_mb", 0))
    minutos   = prever(editor, tamanho)
    return jsonify({"editor": editor, "tamanho_mb": tamanho, "minutos": minutos})


@app.route("/retrain", methods=["POST"])
def retrain():
    """Força retreinamento do modelo global."""
    global _modelo_global, _modelos_cache
    _modelo_global = treinar_modelo()
    _modelos_cache.clear()
    if _modelo_global:
        salvar_modelo(_modelo_global)
        return jsonify({"ok": True, "mensagem": "Modelo retreinado."})
    return jsonify({"ok": False, "mensagem": "Dados insuficientes."}), 400


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Tenta carregar modelo existente ao iniciar
    _modelo_global = carregar_modelo()
    if not _modelo_global:
        log.info("Modelo não encontrado — será treinado após acúmulo de dados.")
    app.run(host="0.0.0.0", port=5001, debug=False)