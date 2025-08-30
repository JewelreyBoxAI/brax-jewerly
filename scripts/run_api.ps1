$ErrorActionPreference = "Stop"
. .\.venv\Scripts\Activate.ps1
$host = $env:API_HOST; if(!$host){$host="0.0.0.0"}
$port = $env:API_PORT; if(!$port){$port="8080"}
uvicorn backend.api.app:app --host $host --port $port --workers 1