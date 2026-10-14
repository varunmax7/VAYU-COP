interface PagePlaceholderProps {
  title: string
  description: string
  phase: string
}

export default function PagePlaceholder({ title, description, phase }: PagePlaceholderProps) {
  return (
    <div className="flex h-full flex-col gap-2 overflow-auto p-6">
      <h1 className="label-text text-lg">{title}</h1>
      <p className="max-w-prose text-sm text-text-muted">{description}</p>
      <p className="label-text mt-2 inline-block w-fit rounded border border-border bg-panel-2 px-2 py-1 text-xs text-accent">
        {phase}
      </p>
    </div>
  )
}
