import client from './client'
import type { MenuResponse } from '@/types'

export async function fetchMenu(): Promise<MenuResponse> {
  const { data } = await client.get<MenuResponse>('/menu')
  return data
}
