"""API Gateway de SeniorVital.

Proxy inverso que redirige peticiones al microservicio
correspondiente según el prefijo de la ruta.
En producción, también sirve los estáticos del frontend
compilado (frontend/dist/) y gestiona el routing SPA.
"""

import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import httpx

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")

app = FastAPI(
    title="SeniorVital API Gateway",
    version="1.0.0",
    docs_url="/docs",
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTES = {
    "/auth/": "http://localhost:8001",
    "/caregiver/": "http://localhost:8001",
    "/admin/": "http://localhost:8001",
    "/catalog/": "http://localhost:8002",
    "/routines/": "http://localhost:8003",
    "/tracking/": "http://localhost:8004",
    "/habits": "http://localhost:8004",
    "/dashboard/": "http://localhost:8005",
    "/notify/": "http://localhost:8006",
    "/rag/": "http://localhost:8007",
    "/storage/": "http://localhost:8002",
}

client = httpx.AsyncClient(
    base_url="http://localhost:8000",
    follow_redirects=True,
    timeout=httpx.Timeout(600.0, connect=10.0),
    headers={"Connection": "keep-alive"},
)

API_PREFIXES = tuple(ROUTES.keys())


def _is_api_path(path: str) -> bool:
    return path.startswith(API_PREFIXES) or path.startswith("/docs") or path.startswith("/openapi")


async def proxy_request(path: str, request: Request):
    """Reenvía la petición HTTP al microservicio destino."""
    target_base = None
    for prefix, base in ROUTES.items():
        if path.startswith(prefix):
            target_base = base
            break
    if not target_base:
        return JSONResponse(
            status_code=502,
            content={"detail": "No route found"},
        )

    target_url = f"{target_base}{path}"
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    # Detect SSE/streaming endpoints
    is_streaming = path.startswith("/routines/generate-stream")

    try:
        if is_streaming:
            return await _proxy_stream(target_url, request, body, headers)

        resp = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=headers,
            params=request.query_params,
        )
        content = resp.content
        headers_dict = dict(resp.headers)
        ct = headers_dict.get("content-type", "")
        if not ct.startswith("application/json") and content:
            try:
                import json as _json
                _json.loads(content)
            except Exception:
                content = _json.dumps({"detail": "Error interno del servidor"}).encode()
                headers_dict["content-type"] = "application/json"
        return Response(
            content=content,
            status_code=resp.status_code,
            headers=headers_dict,
        )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={"detail": "Service unavailable - timeout (try the streaming endpoint)"},
        )
    except httpx.RequestError:
        return JSONResponse(
            status_code=502,
            content={"detail": "Service unavailable"},
        )


async def _proxy_stream(target_url: str, request: Request, body: bytes, headers: dict):
    """Proxya una petición SSE/streaming manteniendo la conexión viva.

    Lee chunks del microservicio destino y los reenvía al cliente sin
    almacenarlos todos en memoria, permitiendo progreso en tiempo real.
    """
    from fastapi.responses import StreamingResponse as FastAPIStreamingResponse

    async def generate():
        async with httpx.AsyncClient(timeout=600.0) as upstream:
            async with upstream.stream(
                "POST",
                target_url,
                content=body,
                headers=headers,
                params=request.query_params,
            ) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_raw():
                    yield chunk

    return FastAPIStreamingResponse(generate(), media_type="text/event-stream")


# ── Montar estáticos del frontend (producción) ──
if os.path.isdir(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="frontend_assets")

# ── Ruta comodín: API proxy o SPA frontend ──
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(path: str, request: Request):
    """Captura todas las peticiones.

    - Si la ruta coincide con un prefijo API, la redirige al microservicio destino.
    - En producción (frontend/dist/ existe), sirve los estáticos del frontend
      o index.html para SPA routing.
    - En desarrollo, el frontend corre en Vite (5173) y solo se hace proxy.
    """
    full_path = "/" + path
    # 1️⃣ Proxy API si el path coincide con algún prefijo
    if _is_api_path(full_path):
        return await proxy_request(full_path, request)

    # 2️⃣ En producción, servir frontend compilado
    if os.path.isdir(FRONTEND_DIST):
        # 2a. /assets/ es servido por StaticFiles (montado arriba) — skip
        if full_path.startswith("/assets/"):
            return JSONResponse(status_code=404, content={"detail": "Asset not found"})
        # 2b. Archivo estático existente (ej. favicon, robots.txt)
        file_path = os.path.join(FRONTEND_DIST, full_path.lstrip("/"))
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # 2c. SPA fallback: todo lo demás va a index.html
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
        return Response(status_code=404, content="Frontend not built")

    # 3️⃣ En desarrollo, sin frontend compilado → 502
    return JSONResponse(
        status_code=502,
        content={"detail": "No route found"},
    )

