// src/components/shell.tsx
import * as React from "react"
import { cn } from "@/lib/utils"

interface DashboardShellProps extends React.HTMLAttributes<HTMLDivElement> {}

export function DashboardShell({ className, ...props }: DashboardShellProps) {
  return (
    <div className={cn("flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6", className)} {...props} />
  )
}