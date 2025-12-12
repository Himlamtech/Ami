import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
    'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--ring)] focus:ring-offset-0',
    {
        variants: {
            variant: {
                default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
                secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
                destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
                success: 'border-transparent bg-success text-white hover:bg-success/80',
                warning: 'border-transparent bg-warning text-white hover:bg-warning/80',
                outline: 'text-foreground',
                ghost: 'border-transparent bg-muted text-muted-foreground',
                soft: 'border-transparent bg-[var(--surface2)] text-[var(--muted)]',
                softSuccess: 'border-transparent bg-success/10 text-success',
                softWarning: 'border-transparent bg-warning/10 text-warning',
                softError: 'border-transparent bg-error/10 text-error',
                softNeutral: 'border-transparent bg-neutral-100 text-neutral-600',
            },
        },
        defaultVariants: {
            variant: 'default',
        },
    }
)

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
    return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
