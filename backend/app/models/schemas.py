"""Request/response contracts. All responses use the standard {data, message} envelope."""
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T]
    message: str


class SecurePayloadRequest(BaseModel):
    encrypted_data: str = Field(..., min_length=1)
    partner_id: str = Field(..., min_length=1)


class IdentityPayload(BaseModel):
    """Mock identity fields only, never populated with real citizen data."""

    name: str
    mock_aadhaar_number: str
    device_id: str


class SecurePayloadResult(BaseModel):
    transaction_id: str
    status: str


class PublicKeyResult(BaseModel):
    public_key: str
