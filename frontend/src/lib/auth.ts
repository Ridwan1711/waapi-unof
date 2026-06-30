import { api } from "@/lib/api";
import { clearToken, setToken } from "@/lib/token";

/**
 * Auth client.
 *
 * The `/v1/auth/*` endpoints are implemented in the Authentication phase; these
 * functions are the real client used by the login/register UI.
 */
export interface Credentials {
  email: string;
  password: string;
}

export interface RegisterInput extends Credentials {
  full_name?: string;
}

interface TokenResponse {
  access: string;
  refresh?: string;
}

export async function login(credentials: Credentials): Promise<void> {
  const { data } = await api.post<TokenResponse>("/auth/login", credentials);
  setToken(data.access);
}

export async function register(input: RegisterInput): Promise<void> {
  await api.post("/auth/register", input);
}

export function logout(): void {
  clearToken();
}
