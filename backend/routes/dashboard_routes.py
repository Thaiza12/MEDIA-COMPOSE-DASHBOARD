from flask import Blueprint, jsonify
from datetime import datetime
from database import redis_client

dashboard_bp = Blueprint("dashboard", __name__)


def _avatar(nome: str) -> str:
    """Gera as iniciais do editor para o avatar."""
    partes = nome.strip().split()
    if len(partes) >= 2:
        return (partes[0][0] + partes[-1][0]).upper()
    return nome[:2].upper() if nome else "?"


@dashboard_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    # ── Lê todos os editores ativos do Redis ──────────────────────────────────
    chaves = redis_client.keys("editor:*")
    ilhas_raw = []

    for chave in chaves:
        dados = redis_client.hgetall(chave)
        if dados:
            ilhas_raw.append(dados)

    # ── Monta os cards das ilhas ──────────────────────────────────────────────
    # Ordena por ilha para exibição consistente
    ilhas_raw.sort(key=lambda x: x.get("ilha", ""))

    ilhas = []
    for i, ed in enumerate(ilhas_raw, start=1):
        editor  = ed.get("editor", "")
        projeto = ed.get("projeto", "")
        ilha    = ed.get("ilha", f"ILHA-{i:02d}")

        # separa programa e retranca do projeto (ex: "ANIVERSARIO RECIFE")
        # por convenção o front usa projeto diretamente; programa/retranca são opcionais
        ilhas.append({
            "id":                 i,
            "editor":             editor,
            "avatar":             _avatar(editor),
            "ilha":               ilha,
            "status":             ed.get("status", "ocupado").capitalize(),
            "projeto":            projeto,
            "programa":           ed.get("programa", ""),
            "retranca":           ed.get("retranca", ""),
            "progresso":          int(ed.get("progresso", 0)),
            "inicio":             ed.get("inicio", "--:--"),
            "arquivoGb":          round(float(ed.get("tamanho_mb", 0)) / 1024, 2),
            "previsaoRestanteMin": int(ed.get("previsao_restante_min", 0)),
            "previsaoFim":        ed.get("previsao_fim", "--:--"),
            "ultimoSave":         ed.get("ultimo_save", ""),
        })

    # ── Summary ───────────────────────────────────────────────────────────────
    total_ilhas  = len(ilhas)
    ilhas_ativas = sum(1 for il in ilhas if il["status"].lower() == "ocupado")

    # ── Fila IA (editores com previsão de entrega) ────────────────────────────
    fila_ia = sorted(
        [il for il in ilhas if il["previsaoRestanteMin"] > 0],
        key=lambda x: x["previsaoRestanteMin"]
    )
    fila_formatada = [
        {
            "id":          j + 1,
            "editor":      il["editor"],
            "projeto":     il["projeto"],
            "horario":     il["previsaoFim"],
            "restanteMin": il["previsaoRestanteMin"],
        }
        for j, il in enumerate(fila_ia)
    ]

    proxima_entrega = fila_formatada[0] if fila_formatada else None

    return jsonify({
        "atualizadoEm":  datetime.now().strftime("%H:%M:%S"),
        "statusSistema": "Online",

        "summary": {
            "totalIlhas":    total_ilhas,
            "ilhasAtivas":   ilhas_ativas,
            "tempoMedioMin": 0,   # calculado futuramente via Postgres
            "concluidosHoje": 0,  # calculado futuramente via Postgres
        },

        "ilhas": ilhas,

        "ia": {
            "proximaEntrega": proxima_entrega,
            "fila":           fila_formatada,
            "precisaoModelo": 0,
            "dadosTreinamento": 0,
        },

        # gráficos ainda sem dados reais — virão do Postgres via worker
        "horasPorDia":      [],
        "atividadePorHora": [],
    })