import * as React from "react"

// Fix: Use type instead of interface for extension
type CardProps = React.HTMLAttributes<HTMLDivElement>

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = '', ...props }, ref) => (
    <div
      ref={ref}
      className={`rounded-lg border bg-white shadow-sm ${className}`}
      {...props}
    />
  )
)
Card.displayName = "Card"

export { Card }
export type { CardProps }