import httpx
from fastapi import FastAPI, Request, Response

def register_proxy(app: FastAPI, path_prefix: str, target_url: str):
    """
    Dynamically registers a catch-all async reverse proxy route onto the FastAPI app.
    
    Example:
        register_proxy(app, path_prefix="/auth", target_url="http://127.0.0.1:8001")
    """
    # Create a dedicated, persistent async client for this specific microservice backend
    async_client = httpx.AsyncClient(base_url=target_url)
    
    # Formulate the path matcher pattern (e.g., "/auth/{path:path}")
    route_pattern = f"{path_prefix.rstrip('/')}/{{path:path}}"

    # Define the core async proxy request/response pipeline
    async def proxy_handler(request: Request, path: str):
        target_path = f"/{path}"
        
        # 1. Duplicate incoming request details
        req = async_client.build_request(
            method=request.method,
            url=target_path,
            headers=request.headers.raw,
            params=request.query_params,
            content=await request.body()
        )
        
        # 2. Forward the request to the target sub-service
        response = await async_client.send(req, stream=True)
        
        # 3. Seamlessly pipe the response back out to the frontend client
        return Response(
            content=await response.aread(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    # Programmatically inject the route into FastAPI's routing layer
    app.api_route(
        route_pattern, 
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        include_in_schema=False # Hides proxy boilerplate from your automated Swagger docs
    )(proxy_handler)