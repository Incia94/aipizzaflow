import { z } from 'zod'

export const orderFormSchema = z.object({
  customer: z.object({
    name: z.string().min(1, 'Name is required'),
    phone_number: z
      .string()
      .min(10, 'Enter a valid 10-digit phone number')
      .max(15, 'Phone number too long')
      .regex(/^[0-9+\-\s]+$/, 'Enter a valid phone number'),
  }),
})

export type OrderFormValues = z.infer<typeof orderFormSchema>

export interface CartItem {
  menuItemId: number
  name: string
  category: string
  baseSelected: string
  toppingsSelected: string[]
  quantity: number
  unitPrice: number
}
