#!/bin/zsh
set -u
cd "${0:A:h}"
if ! /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:19329/api/library >/dev/null 2>&1; then
  mkdir -p .local
  nohup /usr/bin/python3 "$PWD/app/server.py" > "$PWD/.local/studio.log" 2>&1 < /dev/null &
  for attempt in {1..30}; do
    /usr/bin/curl -fsS --max-time 1 http://127.0.0.1:19329/api/library >/dev/null 2>&1 && break
    sleep 0.2
  done
fi
/usr/bin/open http://127.0.0.1:19329
