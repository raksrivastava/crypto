from fastapi import APIRouter

from app.crypto.keys import RsaKeyPair
from app.models.schemas import ApiResponse, PublicKeyResult

router = APIRouter(prefix="/api/v1/keys", tags=["keys"])


def build_router(key_pair: RsaKeyPair) -> APIRouter:
    @router.get("/public", response_model=ApiResponse[PublicKeyResult])
    def get_public_key() -> ApiResponse[PublicKeyResult]:
        return ApiResponse(data=PublicKeyResult(public_key=key_pair.public_key_pem), message="Public key retrieved successfully")

    return router
