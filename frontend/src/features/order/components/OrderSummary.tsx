import { Trash2, ShoppingBag } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { formatCurrency } from '@/lib/utils'
import type { CartItem } from '../types'

interface OrderSummaryProps {
  cart: CartItem[]
  onRemove: (index: number) => void
  onSubmit: () => void
  isSubmitting: boolean
}

export function OrderSummary({ cart, onRemove, onSubmit, isSubmitting }: OrderSummaryProps) {
  const subtotal = cart.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0)

  if (cart.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card py-12 text-center">
        <ShoppingBag className="h-10 w-10 text-muted-foreground/40" />
        <p className="mt-3 text-sm text-muted-foreground">No items added yet</p>
        <p className="text-xs text-muted-foreground/70">Select a pizza to get started</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-card shadow-card">
      <div className="p-5 pb-3">
        <h3 className="font-display text-base font-semibold">Current Order</h3>
        <p className="text-sm text-muted-foreground">{cart.length} item{cart.length !== 1 ? 's' : ''}</p>
      </div>

      <Separator />

      <div className="divide-y divide-border">
        {cart.map((item, idx) => (
          <div key={idx} className="flex items-start gap-3 px-5 py-3">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{item.name}</p>
              <p className="text-xs text-muted-foreground">{item.baseSelected}</p>
              {item.toppingsSelected.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  + {item.toppingsSelected.join(', ')}
                </p>
              )}
            </div>
            <div className="flex items-center gap-3 shrink-0">
              <div className="text-right">
                <p className="font-mono-numbers text-sm font-medium">
                  {formatCurrency(item.unitPrice * item.quantity)}
                </p>
                <p className="text-xs text-muted-foreground">×{item.quantity}</p>
              </div>
              <button
                type="button"
                onClick={() => onRemove(idx)}
                className="rounded-md p-1 text-muted-foreground hover:bg-muted hover:text-destructive transition-colors"
                aria-label="Remove item"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <Separator />

      <div className="p-5">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Subtotal</span>
          <span className="font-mono-numbers font-semibold text-foreground">
            {formatCurrency(subtotal)}
          </span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          GST will be applied at checkout
        </p>

        <Button
          type="button"
          className="mt-4 w-full"
          size="lg"
          onClick={onSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Placing Order…' : 'Place Order'}
        </Button>
      </div>
    </div>
  )
}
