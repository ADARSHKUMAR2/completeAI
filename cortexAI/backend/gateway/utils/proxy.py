import httpx
from fastapi import FastAPI, Request, Response
from fastapi.params import Depends
from gateway.middleware.auth import protect

PROXY_TIMEOUT = httpx.Timeout(60.0, connect=10.0)

def register_proxy(app: FastAPI, path_prefix: str, target_url: str):
    """
    Dynamically registers a catch-all async reverse proxy route onto the FastAPI app.
    
    Example:
        register_proxy(app, path_prefix="/auth", target_url="http://0.0.0.0:8001")
    """
    # Create a dedicated, persistent async client for this specific microservice backend
    async_client = httpx.AsyncClient(base_url=target_url, timeout=PROXY_TIMEOUT)
    
    # Formulate the path matcher pattern (e.g., "/auth/{path:path}")
    route_pattern = f"{path_prefix.rstrip('/')}/{{path:path}}"

    # Define the core async proxy request/response pipeline
    async def proxy_handler(request: Request, path: str):
        target_path = f"{path_prefix.rstrip('/')}/{path}"
        
        # 1. Filter out host & content-length so httpx recalculates boundaries properly
        # This prevents Cloud Run from rejecting the request due to mismatched hosts
        headers = {
            k: v for k, v in request.headers.items() 
            if k.lower() not in ("host", "content-length")
        }
        
        # 2. Forward the request to the target sub-service
        req = async_client.build_request(
            method=request.method,
            url=target_path,
            headers=headers,
            params=request.query_params,
            content=await request.body()
        )
        
        response = await async_client.send(req, stream=True)
        
        # 3. Clean up the response headers before sending back to Unity
        # This prevents UnityWebRequest from hanging due to conflicting encoding headers
        res_headers = dict(response.headers)
        res_headers.pop("content-encoding", None)
        res_headers.pop("content-length", None)
        res_headers.pop("transfer-encoding", None)
        
        return Response(
            content=await response.aread(),
            status_code=response.status_code,
            headers=res_headers
        )

    app.api_route(
        route_pattern, 
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        include_in_schema=False
    )(proxy_handler)

def register_proxy_with_header(app: FastAPI, path_prefix: str, target_url: str):
    """
    Reverse proxies a path prefix to a target microservice and 
    injects the authenticated 'X-User-Id' header automatically.
    """
    async_client = httpx.AsyncClient(base_url=target_url, timeout=PROXY_TIMEOUT)
    route_pattern = f"{path_prefix.rstrip('/')}/{{path:path}}"

    async def proxy_with_header_handler(request: Request, path: str, user_data: dict = Depends(protect)):
        target_path = f"{path_prefix.rstrip('/')}/{path}"
        
        body_bytes = await request.body()
        
        # Filter out host & content-length
        headers = {
            k: v for k, v in request.headers.items() 
            if k.lower() not in ("host", "content-length")
        }
        
        # Inject user ID header
        if user_data and "userId" in user_data:
            headers["x-user-id"] = str(user_data["userId"])
        
        req = async_client.build_request(
            method=request.method,
            url=target_path,
            headers=headers,
            params=request.query_params,
            content=body_bytes
        )
        
        response = await async_client.send(req, stream=True)
        
        # Clean up response headers for Unity
        res_headers = dict(response.headers)
        res_headers.pop("content-encoding", None)
        res_headers.pop("content-length", None)
        res_headers.pop("transfer-encoding", None)
        
        return Response(
            content=await response.aread(),
            status_code=response.status_code,
            headers=res_headers
        )

    app.api_route(
        route_pattern, 
        methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        include_in_schema=False
    )(proxy_with_header_handler)
