import time
import os
import requests

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from usuario_map import resolver_usuario

BACKEND_URL = "http://127.0.0.1:5000/events"
PASTA_MONITORADA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "arquivos_teste"
)


def extrair_info_pasta(caminho_arquivo: str) -> dict:

    abs_monitorada = os.path.abspath(PASTA_MONITORADA)
    abs_arquivo = os.path.abspath(caminho_arquivo)

    try:
        rel = os.path.relpath(abs_arquivo, abs_monitorada)
        partes = rel.split(os.sep)
    except ValueError:
        return {}

    print(f"[DEBUG] partes={partes}")

    if len(partes) < 2:
        return {
            "ilha": "",
            "usuario": "",
            "projeto": "",
            "pasta": "",
            "concluido": False,
        }

    pasta_ilha = partes[0]
    pasta_editor = partes[1]

    # ─────────────────────────────────────────────
    # Detecta concluído
    # ─────────────────────────────────────────────

    pasta_base = os.path.join(abs_monitorada, pasta_ilha, pasta_editor)
    pasta_final = os.path.join(pasta_base, "final")
    concluido = False

    if os.path.exists(pasta_final):
        try:
            arquivos_final = [
                f for f in os.listdir(pasta_final)
                if os.path.isfile(os.path.join(pasta_final, f))
            ]
            concluido = len(arquivos_final) > 0
        except Exception:
            concluido = False

    # ─────────────────────────────────────────────
    # Normaliza ilha
    # ─────────────────────────────────────────────

    ilha_num = pasta_ilha.lower().replace("ilha", "").strip()
    ilha = f"ILHA-{ilha_num}" if ilha_num.isdigit() else pasta_ilha.upper()

    # ─────────────────────────────────────────────
    # Usuário / projeto
    # ─────────────────────────────────────────────

    partes_pasta = pasta_editor.split(" - ", 1)
    if len(partes_pasta) == 2:
        projeto = partes_pasta[0].strip()
        codigo  = partes_pasta[1].strip().upper()
    else:
        tokens  = pasta_editor.split()
        codigo  = tokens[0].upper() if tokens else ""
        projeto = " ".join(tokens[1:]) if len(tokens) > 1 else ""
    usuario = resolver_usuario(codigo)

    return {
        "pasta": pasta_editor,
        "ilha": ilha,
        "usuario": usuario,
        "projeto": projeto,
        "concluido": concluido,
    }


class MonitorHandler(FileSystemEventHandler):

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

        if not event.src_path:
            return

        abs_monitorada = os.path.abspath(PASTA_MONITORADA)

        # Pega o caminho relevante antes da guarda
        caminho_evento = getattr(event, "dest_path", None) or event.src_path
        abs_evento = os.path.abspath(caminho_evento)

        # Ignora eventos fora da pasta monitorada
        if not abs_evento.startswith(abs_monitorada):
            return

        if self.evento_duplicado(event):
            return

        print(f"[EVENTO] {event.event_type} -> {caminho_evento}")

        info = extrair_info_pasta(caminho_evento)

        status = "concluido" if info.get("concluido") else "ocupado"

        payload = {
            "tipoEvento": event.event_type,
            "arquivo": os.path.basename(caminho_evento),
            "caminho": abs_evento,
            "diretorio": event.is_directory,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pasta": info.get("pasta", ""),
            "ilha": info.get("ilha", ""),
            "usuario": info.get("usuario", ""),
            "projeto": info.get("projeto", ""),
            "status": status,
        }

        print(f"[DEBUG] payload={payload}")

        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=5)

            print(
                f"[OK] {payload['tipoEvento'].upper():10} | "
                f"{payload['arquivo']}"
            )
            print(
                f"     ilha={payload['ilha']} | "
                f"usuario={payload['usuario']} | "
                f"projeto={payload['projeto']} | "
                f"status={payload['status']}"
            )
            print(f"     backend={response.status_code}")

        except requests.RequestException as e:
            print(f"[ERRO] {e}")

    def on_any_event(self, event):
        self.processar_evento(event)


if __name__ == "__main__":

    os.makedirs(PASTA_MONITORADA, exist_ok=True)

    handler = MonitorHandler()
    observer = Observer()
    observer.schedule(handler, PASTA_MONITORADA, recursive=True)
    observer.start()

    print(f"[WATCHDOG] Monitorando: {os.path.abspath(PASTA_MONITORADA)}")
    print(f"[WATCHDOG] Backend: {BACKEND_URL}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[WATCHDOG] Encerrado.")

    observer.join()