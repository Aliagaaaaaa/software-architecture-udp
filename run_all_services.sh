#!/usr/bin/env bash

###############################################################################
# run_all_services.sh                                                         #
# --------------------------------------------------------------------------- #
# Arranca el bus SOA, todos los micro-servicios Python y el gateway Node.js   #
# en segundo plano, redirigiendo la salida a la carpeta ./logs.               #
#                                                                              #
#  Uso:  chmod +x run_all_services.sh && ./run_all_services.sh                #
#        ./run_all_services.sh stop        # detiene todos los procesos        #
#                                                                              #
# Requisitos previos:                                                          #
#   • Python 3.10+ disponible como "python3" o "$PYTHON"                      #
#   • Node.js 18+ disponible como "node"                                       #
#   • Dependencias instaladas (pip install -r requirements.txt y npm install) #
###############################################################################

set -euo pipefail

# ----- Configuración ---------------------------------------------------------
PYTHON=${PYTHON:-python3}
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

# Array con pares "comando|nombre_log"
python_services=(
    "soa_server.py|soa_server"
    "auth_service.py|auth_service"
    "prof_service.py|prof_service"
    "forum_service.py|forum_service"
    "post_service.py|post_service"
    "comment_service.py|comment_service"
    "event_service.py|event_service"
    "message_service.py|message_service"
    "report_service.py|report_service"
    "notification_service.py|notification_service"
)

# Gateway Node.js
GATEWAY_DIR="gateway"
GATEWAY_ENTRY="index.js"
GATEWAY_LOG="$LOG_DIR/gateway.log"

PID_FILE=".soa_pids"

start_services() {
  echo "🔌 Iniciando SOA… (pids se almacenarán en $PID_FILE)"
  : > "$PID_FILE"  # vaciar el archivo

  # Iniciar cada servicio Python
  for entry in "${python_services[@]}"; do
    IFS="|" read -r script logname <<< "$entry"
    echo -n "➤ $script … "
    $PYTHON "$script" > "$LOG_DIR/${logname}.log" 2>&1 &
    pid=$!
    echo "$pid" >> "$PID_FILE"
    echo "PID $pid"
    sleep 1
  done

  # Comprobar dependencias Node
  if [[ ! -d "$GATEWAY_DIR/node_modules" ]]; then
    echo "📦 Instalando dependencias del gateway…"
    (cd "$GATEWAY_DIR" && npm install --silent)
  fi

  echo -n "➤ Gateway Node.js … "
  (cd "$GATEWAY_DIR" && node "$GATEWAY_ENTRY") > "$GATEWAY_LOG" 2>&1 &
  gw_pid=$!
  echo "$gw_pid" >> "$PID_FILE"
  echo "PID $gw_pid"

  echo "✅ Todos los servicios están arrancando. Revisa los logs en $LOG_DIR/"
}

stop_services() {
  if [[ ! -f "$PID_FILE" ]]; then
    echo "Sin archivo PID encontrado. ¿Los servicios están corriendo?"
    exit 1
  fi
  echo "🛑 Deteniendo servicios…"
  while read -r pid; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" && echo "  • Proceso $pid terminado"
    fi
  done < "$PID_FILE"
  rm -f "$PID_FILE"
  echo "✅ Todos los servicios detenidos."
}

case "${1:-}" in
  stop)
    stop_services
    ;;
  *)
    start_services
    ;;
esac 