from flask import Blueprint, request, jsonify
from database import redis_client
import json

event_bp = Blueprint("events", __name__)

REDIS_QUEUE = "eventos_watchdog"   # fila FIFO consumida pelo worker


@event_bp.route("/events", methods=["POST"])
def receive_event():
    data = request.get_json()

    if not data:
        return jsonify({"status": "erro", "message": "Payload vazio"}), 400

    # ── 1. Fila para o Worker ETL (persistência no Postgres) ──────────────────
    redis_client.rpush(REDIS_QUEUE, json.dumps(data, ensure_ascii=False))

    # ── 2. Estado em tempo real para o Dashboard (sobrescreve por editor) ─────
    usuario = data.get("usuario", "")
    if usuario:
        chave_estado = f"editor:{usuario.lower().replace(' ', '_')}"
        redis_client.hset(chave_estado, mapping={
            "status":      data.get("status", "ocupado"),  
            "editor":      usuario,
            "ilha":        data.get("ilha", ""),
            "projeto":     data.get("projeto", ""),
            "arquivo":     data.get("arquivo", ""),
            "ultimo_save": data.get("timestamp", ""),
            "tipo_evento": data.get("tipoEvento", ""),
        })
        redis_client.expire(chave_estado, 3600)   # expira em 1h sem atividade

    fila_tamanho = redis_client.llen(REDIS_QUEUE)

    print(f"[EVENT] {data.get('tipoEvento','?'):10} | {data.get('arquivo','?')}")
    print(f"        ilha={data.get('ilha','—')} | usuario={usuario or '—'} | projeto={data.get('projeto','—')}")
    print(f"        fila={fila_tamanho} item(s) pendentes")

    return jsonify({
        "status":  "ok",
        "message": "Evento enfileirado com sucesso",
        "fila":    fila_tamanho,
        "data":    data
    }), 200


@event_bp.route("/events/status", methods=["GET"])
def status_editores():
    """Retorna o estado atual de todos os editores (tempo real via Redis)."""
    chaves = redis_client.keys("editor:*")
    editores = []

    for chave in chaves:
        dados = redis_client.hgetall(chave)
        if dados:
            editores.append(dados)

    return jsonify({
        "total":    len(editores),
        "editores": editores
    }), 200


@event_bp.route("/events/fila", methods=["GET"])
def ver_fila():
    """Retorna quantos eventos estão pendentes na fila (sem consumir)."""
    tamanho = redis_client.llen(REDIS_QUEUE)
    return jsonify({
        "fila":    REDIS_QUEUE,
        "tamanho": tamanho
    }), 200