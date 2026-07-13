import { pemToArrayBuffer } from "./pem";

export interface EncryptRequest {
  publicKeyPem: string;
  plaintext: string;
}

export interface EncryptResponse {
  ok: boolean;
  encryptedData?: string;
  error?: string;
}

self.onmessage = async (event: MessageEvent<EncryptRequest>) => {
  try {
    const { publicKeyPem, plaintext } = event.data;
    const publicKey = await crypto.subtle.importKey(
      "spki",
      pemToArrayBuffer(publicKeyPem),
      { name: "RSA-OAEP", hash: "SHA-256" },
      false,
      ["encrypt"],
    );
    const ciphertext = await crypto.subtle.encrypt({ name: "RSA-OAEP" }, publicKey, new TextEncoder().encode(plaintext));
    const encryptedData = btoa(String.fromCharCode(...new Uint8Array(ciphertext)));
    self.postMessage({ ok: true, encryptedData } satisfies EncryptResponse);
  } catch (error) {
    self.postMessage({ ok: false, error: error instanceof Error ? error.message : "Encryption failed" } satisfies EncryptResponse);
  }
};
