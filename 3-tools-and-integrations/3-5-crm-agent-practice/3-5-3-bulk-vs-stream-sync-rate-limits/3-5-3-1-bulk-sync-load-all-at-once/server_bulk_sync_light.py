from fastapi import FastAPI, Request
from typing import Optional


app = FastAPI()


DATA = [
    {'id': i, 'name': f'Lead {i}'} for i in range(1, 501)
]


@app.get('/api/v1/leads')
async def get_leads(
    request: Request,
    limit: int = 100,
    after: Optional[int] = None
):
    headers = request.headers
    print(f'headers: {headers}')

    start_index = 0
    if after:
        start_index = after

    end_index = start_index + limit
    items = DATA[start_index:end_index]

    next_cursor = None
    if end_index < len(DATA):
        next_cursor = end_index

    response = {
        'items': items,
        'paging': {
            'next': {
                'after': next_cursor
            }
        } if next_cursor else {}
    }

    return response


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'server_bulk_sync_light:app', host='0.0.0.0', port=8000, reload=True)
