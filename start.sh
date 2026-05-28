#!/bin/bash
# start.sh — sobe todo o ecossistema Globo2-PE de uma vez
# Uso: bash start.sh

PROJECT_DIR="$HOME/Github/globo2-PE"
AGENT_DIR="$PROJECT_DIR/agent"
VENV="$AGENT_DIR/.venv"

# ── Cores ──────────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[START]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $1"; }
err()  { echo -e "${RED}[ERRO]${NC}  $1"; }
info() { echo -e "${BLUE}[INFO]${NC}  $1"; }

echo ""
echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Globo2-PE — Iniciando...       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# ── 1. Docker Compose ──────────────────────────────────────────────────────────
log "Subindo containers (Postgres + Redis + Backend)..."
cd "$PROJECT_DIR" || { err "Pasta $PROJECT_DIR não encontrada."; exit 1; }

python3 docker.py up
if [ $? -ne 0 ]; then
    err "Falha ao subir os containers. Verifique o Docker."
    exit 1
fi
log "Containers no ar!"

# ── 2. Aguarda backend estar de pé ────────────────────────────────────────────
info "Aguardando backend responder em :5000..."
for i in $(seq 1 20); do
    if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
        log "Backend respondendo!"
        break
    fi
    if [ $i -eq 20 ]; then
        warn "Backend demorou para responder, continuando mesmo assim..."
    fi
    sleep 1
done

# ── 3. Worker ETL dentro do container ─────────────────────────────────────────
if docker exec globo2-backend pgrep -f "worker/worker.py" > /dev/null 2>&1; then
    info "Worker ETL já está rodando, pulando."
else
    log "Iniciando Worker ETL no container..."
    docker exec -d globo2-backend bash -c "python worker/worker.py >> /tmp/worker.log 2>&1"
    sleep 1
    if docker exec globo2-backend pgrep -f "worker/worker.py" > /dev/null 2>&1; then
        log "Worker ETL rodando!"
    else
        warn "Worker ETL pode não ter subido. Verifique: docker exec globo2-backend cat /tmp/worker.log"
    fi
fi

# ── 4. Venv do agente ─────────────────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
    log "Criando virtualenv do agente..."
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q watchdog requests
    log "Dependências instaladas!"
else
    info "Virtualenv já existe, pulando instalação."
fi

# ── 5. Watchdog ───────────────────────────────────────────────────────────────
pkill -f "monitor.py" 2>/dev/null && info "Watchdog anterior encerrado." || true
log "Iniciando Watchdog (monitor.py)..."
cd "$AGENT_DIR" || { err "Pasta $AGENT_DIR não encontrada."; exit 1; }

source "$VENV/bin/activate"
python monitor.py &
WATCHDOG_PID=$!

sleep 1
if kill -0 $WATCHDOG_PID 2>/dev/null; then
    log "Watchdog rodando (PID=$WATCHDOG_PID)!"
else
    err "Watchdog falhou ao iniciar."
    exit 1
fi

# ── Resumo ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Tudo no ar!                         ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  🐳 Docker:    Postgres + Redis + Backend        ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  ⚙️  Worker:    rodando no container              ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  👁️  Watchdog:  monitorando ./arquivos_teste      ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  🌐 Backend:   http://127.0.0.1:5000             ${GREEN}║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║${NC}  Logs Worker:  docker logs globo2-backend         ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}  Parar tudo:   bash stop.sh                       ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Pressione ${RED}Ctrl+C${NC} para encerrar o watchdog (o resto continua rodando)."
echo ""

# Mantém o watchdog em foreground para ver os logs
wait $WATCHDOG_PID