import { useEffect, useState } from 'react'
import { getMetrics, listClaims, getFlagged } from '../lib/api'
import { Card, Badge, ScoreDot } from '../components/ui'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AlertTriangle, TrendingUp, Clock, Shield } from 'lucide-react'
import type { Metrics, ClaimSummary } from '../types'

const COLORS = ['#6366F1', '#10B981', '#F59E0B', '#818CF8', '#EF4444', '#14B8A6']

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [claims, setClaims] = useState<ClaimSummary[]>([])
  const [flagged, setFlagged] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getMetrics(), listClaims(), getFlagged()])
      .then(([m, c, f]) => { setMetrics(m); setClaims(c); setFlagged(f) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
    </div>
  )

  const chartData = metrics
    ? Object.entries(metrics.claims_by_type).map(([name, value]) => ({ name, value }))
    : []

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
      <h1 className="text-2xl font-semibold text-text-primary">Admin Dashboard</h1>

      {/* Metric cards */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Claims', value: metrics.total_claims, icon: TrendingUp, color: 'text-accent-primary' },
            { label: 'Routed', value: metrics.routed_count, icon: Shield, color: 'text-accent-success' },
            { label: 'Flagged', value: metrics.flagged_count, icon: AlertTriangle, color: 'text-accent-danger' },
            { label: 'Avg Time', value: `${(metrics.avg_processing_time_ms / 1000).toFixed(1)}s`, icon: Clock, color: 'text-accent-warning' },
          ].map(({ label, value, icon: Icon, color }) => (
            <Card key={label}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-text-secondary text-xs">{label}</span>
                <Icon className={`w-4 h-4 ${color}`} />
              </div>
              <div className="text-2xl font-bold text-text-primary">{value}</div>
            </Card>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Claims by type chart */}
        <Card>
          <h2 className="text-sm font-medium text-text-primary mb-4">Claims by Type</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#111118', border: '1px solid #1E1E2E', borderRadius: 8 }}
                labelStyle={{ color: '#F8FAFC' }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Rate cards */}
        {metrics && (
          <Card>
            <h2 className="text-sm font-medium text-text-primary mb-4">Performance</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-text-secondary">Routing Rate</span>
                  <span className="text-accent-success">{metrics.routing_rate}%</span>
                </div>
                <div className="h-2 bg-bg-tertiary rounded-full">
                  <div className="h-2 bg-accent-success rounded-full" style={{ width: `${metrics.routing_rate}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-text-secondary">Flag Rate</span>
                  <span className="text-accent-danger">{metrics.flag_rate}%</span>
                </div>
                <div className="h-2 bg-bg-tertiary rounded-full">
                  <div className="h-2 bg-accent-danger rounded-full" style={{ width: `${metrics.flag_rate}%` }} />
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Flagged claims */}
      {flagged.length > 0 && (
        <Card>
          <h2 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-accent-danger" /> Flagged Claims
          </h2>
          <div className="space-y-3">
            {flagged.map((c: any) => (
              <div key={c.claim_id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div>
                  <div className="text-sm text-text-primary font-mono">{c.claim_id.slice(0, 8)}...</div>
                  <div className="text-xs text-text-secondary mt-0.5">{c.description}</div>
                </div>
                <ScoreDot score={c.fraud_score} label="Fraud" />
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* All claims table */}
      <Card>
        <h2 className="text-sm font-medium text-text-primary mb-4">Recent Claims</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-text-muted text-xs border-b border-border">
                <th className="pb-2 pr-4">Claim ID</th>
                <th className="pb-2 pr-4">Company</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2 pr-4">Status</th>
                <th className="pb-2 pr-4">Priority</th>
                <th className="pb-2 pr-4">Department</th>
                <th className="pb-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {claims.map(c => (
                <tr key={c.claim_id} className="border-b border-border last:border-0">
                  <td className="py-2 pr-4 font-mono text-text-muted text-xs">{c.claim_id.slice(0, 8)}...</td>
                  <td className="py-2 pr-4 text-text-secondary">{c.company_slug}</td>
                  <td className="py-2 pr-4">{c.claim_type ? <Badge label={c.claim_type} /> : '—'}</td>
                  <td className="py-2 pr-4">{c.status ? <Badge label={c.status} /> : '—'}</td>
                  <td className="py-2 pr-4 text-text-secondary">{c.priority_score ?? '—'}/5</td>
                  <td className="py-2 pr-4 text-text-secondary text-xs">{c.assigned_department || '—'}</td>
                  <td className="py-2 text-text-muted text-xs">{(c.processing_time_ms / 1000).toFixed(1)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
          {claims.length === 0 && (
            <p className="text-text-muted text-sm text-center py-8">No claims yet. Submit your first claim!</p>
          )}
        </div>
      </Card>
    </div>
  )
}
