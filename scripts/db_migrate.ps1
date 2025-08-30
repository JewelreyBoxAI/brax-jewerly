$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1
$env:PYTHONWARNINGS="ignore"
python - << 'PY'
import os, psycopg
url = os.getenv("POSTGRES_URL")
with psycopg.connect(url) as conn, conn.cursor() as cur:
    cur.execute(open("backend/db/migrations/001_init.sql","r",encoding="utf-8").read())
    conn.commit()
print("DB migrated.")
PY