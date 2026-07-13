import type { ApiResponse, PublicKeyResult, SecurePayloadResult } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  const body = (await response.json()) as ApiResponse<T>;
  if (!response.ok) {
    throw new Error(body.message || "Request failed");
  }
  return body.data as T;
}

export async function fetchPublicKey(): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/api/v1/keys/public`);
  const result = await parseJsonOrThrow<PublicKeyResult>(response);
  return result.public_key;
}

export async function submitSecurePayload(encryptedData: string, partnerId: string): Promise<SecurePayloadResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/sandbox/secure-payload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ encrypted_data: encryptedData, partner_id: partnerId }),
  });
  return parseJsonOrThrow<SecurePayloadResult>(response);
}
