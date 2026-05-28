#!/bin/bash
# stop.sh — encerra todo o ecossistema Globo2-PE

PROJECT_DIR="$HOME/Github/globo2-PE"

RED='\033[0;32m'
NC='\033[0m'

echo ""
echo -e "${RED}[STOP]${NC} Encerrando Watchdog..."
pkill -f "monitor.py" 2>/dev/null && echo -e "${RED}[STOP]${NC} Watchdog encerrado." || echo "Watchdog já estava parado."

echo -e "${RED}[STOP]${NC} Encerrando Worker no container..."
docker exec globo2-backend pkill -f "worker/worker.py" 2>/dev/null && echo -e "${RED}[STOP]${NC} Worker encerrado." || echo "Worker já estava parado."

echo -e "${RED}[STOP]${NC} Derrubando containers..."
cd "$PROJECT_DIR" && python3 docker.py down

echo ""
echo "Tudo encerrado."