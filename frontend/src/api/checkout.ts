import client from './client'
import type { CompleteCheckoutRequest, CompleteCheckoutResponse } from '@/types'

export async function completeCheckout(
  request: CompleteCheckoutRequest,
): Promise<CompleteCheckoutResponse> {
  const { data } = await client.post<CompleteCheckoutResponse>('/checkout', request)
  return data
}
