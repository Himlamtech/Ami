import * as React from 'react'
import { cn } from '@/lib/utils'

interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
    onCheckedChange?: (checked: boolean) => void
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
    ({ className, checked, defaultChecked, onCheckedChange, ...props }, ref) => {
        const [isChecked, setIsChecked] = React.useState(defaultChecked || false)
        const actualChecked = checked !== undefined ? checked : isChecked

        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            const newChecked = e.target.checked
            if (checked === undefined) {
                setIsChecked(newChecked)
            }
            onCheckedChange?.(newChecked)
        }

        return (
            <label className={cn('relative inline-flex cursor-pointer items-center', className)}>
                <input
                    type="checkbox"
                    className="peer sr-only"
                    checked={actualChecked}
                    onChange={handleChange}
                    ref={ref}
                    {...props}
                />
                <div
                    className={cn(
                        'h-6 w-11 rounded-full bg-neutral-200 transition-colors',
                        'peer-checked:bg-primary peer-disabled:cursor-not-allowed peer-disabled:opacity-50',
                        'after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow-sm after:transition-transform',
                        'peer-checked:after:translate-x-5'
                    )}
                />
            </label>
        )
    }
)
Switch.displayName = 'Switch'

export { Switch }
