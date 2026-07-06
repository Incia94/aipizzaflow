import client from './client'

interface TokenResponse {
  access_token: string
  token_type: string
}

export async function loginAdmin(username: string, password: string): Promise<string> {
  const { data } = await client.post<TokenResponse>('/auth/login', { username, password })
  return data.access_token
}
