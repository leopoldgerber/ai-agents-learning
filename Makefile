# SSE
3-3-server:
	cd 3-tools-and-integrations/3-3-api-json-validation && \
	uvicorn api_json_server:app --reload --port 8000

3-3-client:
	.venv\Scripts\python.exe 3-tools-and-integrations\3-3-api-json-validation\api_json_client.py

# SSE
3-4-1-server:
	cd 3-tools-and-integrations/3-4-streaming-api/3-4-1-sse && \
	uvicorn sse_server:app --reload --port 8000

3-4-1-client:
	.venv\Scripts\python.exe 3-tools-and-integrations\3-4-streaming-api\3-4-1-sse\sse_client.py


# WEBSOCKET
3-4-2-server:
	cd 3-tools-and-integrations/3-4-streaming-api/3-4-2-websocket && \
	uvicorn ws_server:app --reload --port 8000

3-4-2-client:
	.venv\Scripts\python.exe 3-tools-and-integrations\3-4-streaming-api\3-4-2-websocket\ws_client.py
