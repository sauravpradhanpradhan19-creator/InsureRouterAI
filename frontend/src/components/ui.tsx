import { clsx } from 'clsx'

// ── Badge ─────────────────────────────────────────────────────────────────────

const badgeColors: Record<string, string> = {
  health:    'bg-blue-900/40 text-blue-300 border-blue-800',
  motor:     'bg-amber-900/40 text-amber-300 border-amber-800',
  property:  'bg-orange-900/40 text-orange-300 border-orange-800',
  life:      'bg-purple-900/40 text-purple-300 border-purple-800',
  travel:    'bg-teal-900/40 text-teal-300 border-teal-800',
  liability: 'bg-red-900/40 text-red-300 border-red-800',
  routed:    'bg-green-900/40 text-green-300 border-green-800',
  flagged:   'bg-red-900/40 text-red-300 border-red-800',
  pending:   'bg-gray-900/40 text-gray-300 border-gray-700',
  processing:'bg-indigo-900/40 text-indigo-300 border-indigo-800',
}

export function Badge({ label }: { label: string }) {
  const color = badgeColors[label] || 'bg-gray-900/40 text-gray-300 border-gray-700'
  return (
    <span className={clsx('px-2 py-0.5 rounded text-xs font-medium border capitalize', color)}>
      {label}
    </span>
  )
}

// ── Score dot ─────────────────────────────────────────────────────────────────

export function ScoreDot({ score, label }: { score: number; label: string }) {
  const colors = ['', 'bg-green-500', 'bg-teal-400', 'bg-yellow-400', 'bg-orange-400', 'bg-red-500']
  return (
    <div className="flex items-center gap-2">
      <span className="text-text-secondary text-xs">{label}</span>
      <div className="flex gap-1">
        {[1,2,3,4,5].map(i => (
          <div key={i} className={clsx('w-2 h-2 rounded-full', i <= score ? colors[score] : 'bg-border')} />
        ))}
      </div>
      <span className="text-text-secondary text-xs">{score}/5</span>
    </div>
  )
}

// ── Card ──────────────────────────────────────────────────────────────────────

export function Card({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={clsx('bg-bg-secondary border border-border rounded-xl p-5', className)}>
      {children}
    </div>
  )
}

// ── Spinner ───────────────────────────────────────────────────────────────────

export function Spinner() {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
      <p className="text-text-secondary text-sm">Processing claim through AI pipeline...</p>
    </div>
  )
}

// ── Agent trace row ───────────────────────────────────────────────────────────

export function AgentTraceRow({ trace }: { trace: any }) {
  const statusColors: Record<string, string> = {
    complete: 'text-green-400',
    error:    'text-red-400',
    skipped:  'text-gray-500',
  }
  return (
    <div className="flex items-start gap-3 py-2 border-b border-border last:border-0">
      <div className={clsx('text-xs font-mono mt-0.5 w-20 shrink-0', statusColors[trace.status] || 'text-text-secondary')}>
        {trace.status}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-text-primary">{trace.agent_name}</div>
        {trace.output_summary && (
          <div className="text-xs text-text-secondary mt-0.5 truncate">{trace.output_summary}</div>
        )}
      </div>
      {trace.time_ms && (
        <div className="text-xs text-text-muted shrink-0">{trace.time_ms}ms</div>
      )}
    </div>
  )
}
