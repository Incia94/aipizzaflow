import { useState } from 'react'
import { Plus, Minus, ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn, formatCurrency } from '@/lib/utils'
import type { MenuItem } from '@/types'
import type { CartItem } from '../types'

interface PizzaCardProps {
  item: MenuItem
  onAdd: (cartItem: CartItem) => void
}

function PizzaCard({ item, onAdd }: PizzaCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [base, setBase] = useState(item.available_bases[0] ?? '')
  const [toppings, setToppings] = useState<string[]>([])
  const [qty, setQty] = useState(1)

  const toggleTopping = (t: string) =>
    setToppings((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]))

  const handleAdd = () => {
    onAdd({
      menuItemId: item.id,
      name: item.name,
      category: item.category,
      baseSelected: base,
      toppingsSelected: toppings,
      quantity: qty,
      unitPrice: item.price,
    })
    setExpanded(false)
    setToppings([])
    setQty(1)
  }

  return (
    <div
      className={cn(
        'rounded-xl border border-border bg-card shadow-card transition-shadow duration-200',
        expanded && 'shadow-card-hover',
      )}
    >
      {/* Header */}
      <button
        type="button"
        className="flex w-full items-start justify-between p-4 text-left"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-foreground truncate">{item.name}</span>
            <Badge variant="secondary" className="text-xs shrink-0">{item.category}</Badge>
          </div>
          <p className="mt-0.5 font-mono-numbers text-sm text-primary font-medium">
            {formatCurrency(item.price)}
          </p>
        </div>
        {expanded ? (
          <ChevronUp className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronDown className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
        )}
      </button>

      {/* Expanded customisation */}
      {expanded && (
        <div className="border-t border-border px-4 pb-4 pt-3 space-y-4 animate-fade-in">
          {/* Base */}
          <div>
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Crust
            </p>
            <div className="flex flex-wrap gap-2">
              {item.available_bases.map((b) => (
                <button
                  key={b}
                  type="button"
                  onClick={() => setBase(b)}
                  className={cn(
                    'rounded-full border px-3 py-1 text-sm transition-colors duration-100',
                    base === b
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border bg-card text-foreground hover:border-primary/50',
                  )}
                >
                  {b}
                </button>
              ))}
            </div>
          </div>

          {/* Toppings */}
          {item.available_toppings.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Extra Toppings
              </p>
              <div className="flex flex-wrap gap-2">
                {item.available_toppings.map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => toggleTopping(t)}
                    className={cn(
                      'rounded-full border px-3 py-1 text-sm transition-colors duration-100',
                      toppings.includes(t)
                        ? 'border-primary bg-primary text-primary-foreground'
                        : 'border-border bg-card text-foreground hover:border-primary/50',
                    )}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Quantity + Add */}
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setQty((q) => Math.max(1, q - 1))}
              >
                <Minus className="h-3 w-3" />
              </Button>
              <span className="font-mono-numbers w-6 text-center text-sm font-medium">{qty}</span>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setQty((q) => q + 1)}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>

            <Button type="button" size="sm" onClick={handleAdd}>
              <Plus className="h-3.5 w-3.5" />
              Add to Order
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

interface PizzaBuilderProps {
  items: MenuItem[]
  onAdd: (cartItem: CartItem) => void
}

export function PizzaBuilder({ items, onAdd }: PizzaBuilderProps) {
  const categories = [...new Set(items.map((i) => i.category))]

  return (
    <div className="space-y-6">
      {categories.map((cat) => (
        <div key={cat}>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
            {cat}
          </h3>
          <div className="space-y-2">
            {items
              .filter((i) => i.category === cat)
              .map((item) => (
                <PizzaCard key={item.id} item={item} onAdd={onAdd} />
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}
