export interface IdentityFormData {
  name: string;
  mock_aadhaar_number: string;
  device_id: string;
}

export interface ApiResponse<T> {
  data: T | null;
  message: string;
}

export interface PublicKeyResult {
  public_key: string;
}

export interface SecurePayloadResult {
  transaction_id: string;
  status: string;
}
