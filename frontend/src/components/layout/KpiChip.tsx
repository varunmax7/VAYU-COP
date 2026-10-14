import type { LucideIcon } from 'lucide-react'

import { cn } from '@/lib/utils'

export type KpiTone = 'ok' | 'warn' | 'crit' | 'info'

export interface KpiChipProps {
  icon: LucideIcon
  label: string
  value: string | number
  tone?: KpiTone
  onClick?: () => void
}

const TONE_CLASS: Record<KpiTone, string> = {
  ok: 'text-ok',
  warn: 'text-warn',
  crit: 'text-crit',
  info: 'text-accent',
}

export default function KpiChip({ icon: Icon, label, value, tone = 'info', onClick }: KpiChipProps) {
  const Tag = onClick ? 'button' : 'div'
  return (
    <Tag
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      data-tone={tone}
      className={cn(
        'flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-sm',
        onClick && 'cursor-pointer hover:bg-panel-2',
      )}
    >
      <Icon className={cn('h-4 w-4', TONE_CLASS[tone])} aria-hidden />
      <span className="label-text text-xs text-text-muted">{label}</span>
      <span className={cn('mono-text font-medium', TONE_CLASS[tone])}>{value}</span>
    </Tag>
  )
}
