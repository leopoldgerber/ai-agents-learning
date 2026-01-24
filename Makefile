# SSE
sse-server:
	cd 3-tools-and-integrations/3-4-streaming-api/3-4-1-sse && \
	uvicorn sse_server:app --reload --port 8000

sse-client:
	.venv\Scripts\python.exe 3-tools-and-integrations\3-4-streaming-api\3-4-1-sse\sse_client.py


# WEBSOCKET
ws-server:
	cd 3-tools-and-integrations/3-4-streaming-api/3-4-2-websocket && \
	uvicorn ws_server:app --reload --port 8000

ws-client:
	.venv\Scripts\python.exe 3-tools-and-integrations\3-4-streaming-api\3-4-2-websocket\ws_client.py
