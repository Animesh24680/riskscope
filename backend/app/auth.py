from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer(auto_error=False)


def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str | None:
    if credentials:
        return credentials.credentials
    return None


def verify_api_key(request: Request) -> None:
    if not settings.api_keys:
        return

    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").removeprefix("Bearer ")
    if not api_key or api_key not in settings.api_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_rate_limit_key(request: Request) -> str:
    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").removeprefix("Bearer ")
    if api_key and api_key in settings.api_keys:
        return f"key:{api_key}"
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"
