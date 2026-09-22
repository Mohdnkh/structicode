import { Slot } from '@radix-ui/react-slot'

export function Button({ className = '', asChild = false, ...props }) {
  const Component = asChild ? Slot : 'button'
  return <Component className={`button ${className}`} {...props} />
}