import httpx
from fastapi import FastAPI, Request, Response
from fastapi.params import Depends
from middleware.auth import protect

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
        target_path = f"{path_prefix.rstrip('/')}/{path}"
        
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

def register_proxy_with_header(app: FastAPI, path_prefix: str, target_url: str):
    """
    Reverse proxies a path prefix to a target microservice and 
    injects the authenticated 'X-User-Id' header automatically.
    """
    async_client = httpx.AsyncClient(base_url=target_url)
    route_pattern = f"{path_prefix.rstrip('/')}/{{path:path}}"

    # Enforce authentication right at the proxy doorstep
    async def proxy_with_header_handler(request: Request, path: str, user_data: dict = Depends(protect)):
        target_path = f"{path_prefix.rstrip('/')}/{path}"
        
        # 1. Convert headers to a standard mutable dictionary
        headers = dict(request.headers)
        
        # 2. Inject the authenticated user ID (equivalent to srcReq.user.userId)
        if user_data and "userId" in user_data:
            headers["x-user-id"] = str(user_data["userId"])
        
        # 3. Build and forward the request
        req = async_client.build_request(
            method=request.method,
            url=target_path,
            headers=headers,
            params=request.query_params,
            content=await request.body()
        )
        
        response = await async_client.send(req, stream=True)
        
        return Response(
            content=await response.aread(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    # Register the route to FastAPI
    app.api_route(
        route_pattern, 
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        include_in_schema=False
    )(proxy_with_header_handler)