import { useState, type ChangeEvent, type FormEvent } from "react";
import { encryptOnWorker } from "../crypto/encryptClient";
import { fetchPublicKey, submitSecurePayload } from "../services/api";
import type { IdentityFormData, SecurePayloadResult } from "../types";

const MOCK_PARTNER_ID = "sandbox-partner-demo";
const EMPTY_FORM: IdentityFormData = { name: "", mock_aadhaar_number: "", device_id: "" };

type SubmissionState = "idle" | "loading" | "success" | "error";

export function SecurePayloadForm() {
  const [formData, setFormData] = useState<IdentityFormData>(EMPTY_FORM);
  const [state, setState] = useState<SubmissionState>("idle");
  const [result, setResult] = useState<SecurePayloadResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleChange = (field: keyof IdentityFormData) => (event: ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setState("loading");
    setErrorMessage(null);
    setResult(null);
    try {
      const publicKeyPem = await fetchPublicKey();
      const encryptedData = await encryptOnWorker(publicKeyPem, JSON.stringify(formData));
      const payloadResult = await submitSecurePayload(encryptedData, MOCK_PARTNER_ID);
      setResult(payloadResult);
      setState("success");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Submission failed");
      setState("error");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="secure-payload-form">
      <h1>E2EE Payload Simulator</h1>
      <p className="form-note">All fields below are simulated data only. Never enter a real Aadhaar number.</p>

      <label>
        Name
        <input value={formData.name} onChange={handleChange("name")} required />
      </label>
      <label>
        Mock Aadhaar Number
        <input
          value={formData.mock_aadhaar_number}
          onChange={handleChange("mock_aadhaar_number")}
          pattern="\d{12}"
          title="12-digit mock number"
          required
        />
      </label>
      <label>
        Device ID
        <input value={formData.device_id} onChange={handleChange("device_id")} required />
      </label>

      <button type="submit" disabled={state === "loading"}>
        {state === "loading" ? "Encrypting & submitting…" : "Submit"}
      </button>

      {state === "success" && result && (
        <p className="status status--success">Received. Transaction ID: {result.transaction_id}</p>
      )}
      {state === "error" && errorMessage && <p className="status status--error">{errorMessage}</p>}
    </form>
  );
}
