# 3-1-5-1
server-3-1-5-1:
	cd 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-5-webhooks-sign-retries-dedup/3-1-5-1-webhook-signature && \
	uvicorn webhook_sig_server:app --reload --port 8000

client-3-1-5-1:
	.venv\Scripts\python.exe 3-tools-and-integrations\3-1-http-and-external-api-connection\3-1-5-webhooks-sign-retries-dedup\3-1-5-1-webhook-signature\webhook_sig_client.py

# 3-1-4-2
server-3-1-4-2:
	cd 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-4-streaming-api/3-1-4-2-websocket && \
	uvicorn ws_server:app --reload --port 8000

client-3-1-4-2:
	.venv\Scripts\python.exe 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-4-streaming-api/3-1-4-2-websocket/ws_client.py

# 3-1-4-1
server-3-1-4-1:
	cd 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-4-streaming-api/3-1-4-1-sse && \
	uvicorn sse_server:app --reload --port 8000

client-3-1-4-1:
	.venv\Scripts\python.exe 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-4-streaming-api/3-1-4-1-sse/sse_client.py

# 3-1-3
server-3-3-1:
	cd 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-3-api-json-validation && \
	uvicorn api_json_server:app --reload --port 8000

client-3-3-1:
	.venv\Scripts\python.exe 3-tools-and-integrations/3-1-http-and-external-api-connection/3-1-3-api-json-validation/api_json_client.py
