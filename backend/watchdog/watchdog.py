import json
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from database import redis_client
import time

# ─── MAPA DE CÓDIGOS → NOME COMPLETO DO USUÁRIO ────────────────────────────────
# Chave: primeiro token do nome da pasta (maiúsculo)
# Valor: nome completo que vai pro PostgreSQL
USUARIO_MAP = {
    "LUC":    "Lucas Cardoso Alecrim",
    "SAM":    "Samuel Santos",
    "SAMUEL": "Samuel Santos",
    "JOA":    "João Oliveira",
    "ANA":    "Ana Paula Ferreira",
}

PASTA_MONITORADA = "./arquivos"


def extrair_info_pasta(caminho_arquivo: str) -> dict:
    """
    Dado o caminho absoluto de um arquivo, sobe até encontrar
    a primeira subpasta dentro de PASTA_MONITORADA e extrai:
      - pasta   → nome bruto  ex: "LUC ANIVERSARIO RECIFE"
      - usuario → nome completo via USUARIO_MAP
      - projeto → resto do nome ex: "ANIVERSARIO RECIFE"

    Retorna {} se o arquivo estiver direto na raiz monitorada
    (sem subpasta de projeto).
    """
    abs_monitorada = os.path.abspath(PASTA_MONITORADA)
    abs_arquivo    = os.path.abspath(caminho_arquivo)

    try:
        rel = os.path.relpath(abs_arquivo, abs_monitorada)
    except ValueError:
        return {}

    partes = rel.split(os.sep)   # ["LUC ANIVERSARIO RECIFE", "foto.jpg"]

    if len(partes) < 2:
        # arquivo está direto na raiz — sem contexto de projeto
        return {}

    pasta_nome = partes[0]

    partes_pasta = pasta_nome.split(" - ", 1)
    if len(partes_pasta) == 2:
        projeto = partes_pasta[0].strip()
        codigo  = partes_pasta[1].strip().upper()
    else:
        tokens  = pasta_nome.split()
        if not tokens:
            return {}
        codigo  = tokens[0].upper()
        projeto = " ".join(tokens[1:]) if len(tokens) > 1 else ""
    usuario = USUARIO_MAP.get(codigo, codigo)

    return {
        "pasta":   pasta_nome,
        "usuario": usuario,
        "projeto": projeto,
    }


class Monitorar(FileSystemEventHandler):

    def __init__(self):
        self.ultimos_eventos = {}
        self.intervalo = 1

    def evento_duplicado(self, event):
        chave = (event.event_type, event.src_path)
        agora = time.time()

        if chave in self.ultimos_eventos:
            if agora - self.ultimos_eventos[chave] < self.intervalo:
                return True

        self.ultimos_eventos[chave] = agora
        return False

    def processar_evento(self, event):
        if event.is_directory:
            return

        if self.evento_duplicado(event):
            return

        # ── campos originais ──────────────────────────────────────────────────
        evento = {
            "tipo":      event.event_type,
            "caminho":   event.src_path,
            "arquivo":   os.path.basename(event.src_path),
            "diretorio": event.is_directory,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # ── campos novos: pasta → usuário + projeto ───────────────────────────
        info = extrair_info_pasta(event.src_path)
        if info:
            evento["pasta"]   = info["pasta"]
            evento["usuario"] = info["usuario"]
            evento["projeto"] = info["projeto"]
        else:
            evento["pasta"]   = ""
            evento["usuario"] = ""
            evento["projeto"] = ""

        redis_client.rpush("eventos_watchdog", json.dumps(evento, ensure_ascii=False))

        print(f"[{evento['tipo'].upper():10}] {evento['arquivo']}")
        if info:
            print(f"             usuario={evento['usuario']} | projeto={evento['projeto']}")

    def on_any_event(self, event):
        self.processar_evento(event)


def iniciar_watchdog(pasta):
    observer = Observer()
    handler  = Monitorar()
    observer.schedule(handler, path=pasta, recursive=True)
    observer.start()
    return observer


if __name__ == "__main__":
    os.makedirs(PASTA_MONITORADA, exist_ok=True)

    observer = iniciar_watchdog(PASTA_MONITORADA)
    print(f"[WATCHDOG] Monitorando: {os.path.abspath(PASTA_MONITORADA)}")
    print("           Ctrl+C para encerrar.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[WATCHDOG] Encerrado.")

    observer.join()