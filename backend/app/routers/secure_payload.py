import uuid

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.crypto.decryptor import PayloadDecryptor
from app.events.kafka_publisher import EventPublisher
from app.exceptions import DecryptionError, EventPublishError, MalformedPayloadError
from app.models.schemas import ApiResponse, IdentityPayload, SecurePayloadRequest, SecurePayloadResult

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])


def build_router(decryptor: PayloadDecryptor, publisher: EventPublisher, kafka_topic: str) -> APIRouter:
    @router.post("/secure-payload", response_model=ApiResponse[SecurePayloadResult])
    def receive_secure_payload(payload: SecurePayloadRequest) -> ApiResponse[SecurePayloadResult]:
        try:
            decrypted = decryptor.decrypt(payload.encrypted_data)
            identity = IdentityPayload(**decrypted)
        except DecryptionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (MalformedPayloadError, ValidationError) as exc:
            raise HTTPException(
                status_code=400, detail="Decrypted payload does not match the expected identity schema"
            ) from exc

        transaction_id = str(uuid.uuid4())
        event = {
            "event_type": "Secure_Payload_Received",
            "transaction_id": transaction_id,
            "partner_id": payload.partner_id,
            "identity": identity.model_dump(),
        }

        try:
            publisher.publish(kafka_topic, event)
        except Exception as exc:
            raise EventPublishError("Failed to publish verified payload event") from exc

        return ApiResponse(
            data=SecurePayloadResult(transaction_id=transaction_id, status="received"),
            message="Payload decrypted and event published successfully",
        )

    return router
