import type { EncryptRequest, EncryptResponse } from "./encryptWorker";

/** Runs RSA-OAEP encryption on a Web Worker so the main UI thread never blocks. */
export function encryptOnWorker(publicKeyPem: string, plaintext: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(new URL("./encryptWorker.ts", import.meta.url), { type: "module" });

    worker.onmessage = (event: MessageEvent<EncryptResponse>) => {
      worker.terminate();
      if (event.data.ok && event.data.encryptedData) {
        resolve(event.data.encryptedData);
      } else {
        reject(new Error(event.data.error ?? "Encryption failed"));
      }
    };
    worker.onerror = (event) => {
      worker.terminate();
      reject(new Error(event.message));
    };

    const request: EncryptRequest = { publicKeyPem, plaintext };
    worker.postMessage(request);
  });
}
