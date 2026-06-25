import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { toast } from 'sonner'
import { submitClaim, getCompanies } from '../lib/api'
import { useStore } from '../store'
import { Card, Spinner, Badge, ScoreDot, AgentTraceRow } from '../components/ui'
import type { ClaimResult, Company } from '../types'
import { CheckCircle, AlertTriangle, Shield, Clock, FileText, Building } from 'lucide-react'

export default function SubmitClaim() {
  const { setLastResult, lastResult } = useStore()
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    company_slug: 'demo_hdfc',
    description: '',
    customer_name: '',
    policy_number: '',
  })

  useEffect(() => {
    getCompanies().then(setCompanies).catch(() => {})
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (form.description.trim().length < 10) {
      toast.error('Please describe your claim in more detail')
      return
    }
    setLoading(true)
    setLastResult(null)
    try {
      const result: ClaimResult = await submitClaim(form)
      setLastResult(result)
      toast.success('Claim processed successfully')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to process claim')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Submit a Claim</h1>
        <p className="text-text-secondary mt-1">AI will classify, validate, and route your claim instantly.</p>
      </div>

      {/* Form */}
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-text-secondary mb-1 block">Insurance Company</label>
              <select
                value={form.company_slug}
                onChange={e => setForm(f => ({ ...f, company_slug: e.target.value }))}
                className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-primary"
              >
                {companies.map(c => (
                  <option key={c.slug} value={c.slug}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm text-text-secondary mb-1 block">Policy Number (optional)</label>
              <input
                type="text"
                value={form.policy_number}
                onChange={e => setForm(f => ({ ...f, policy_number: e.target.value }))}
                placeholder="e.g. HDFC-2024-98765"
                className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-primary"
              />
            </div>
          </div>

          <div>
            <label className="text-sm text-text-secondary mb-1 block">Your Name (optional)</label>
            <input
              type="text"
              value={form.customer_name}
              onChange={e => setForm(f => ({ ...f, customer_name: e.target.value }))}
              placeholder="e.g. Rahul Sharma"
              className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-primary"
            />
          </div>

          <div>
            <label className="text-sm text-text-secondary mb-1 block">Claim Description</label>
            <textarea
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              rows={5}
              placeholder="Describe your claim in detail. E.g. I was hospitalized for 3 days due to dengue fever at Apollo Hospital, Delhi. Total bill is Rs 45,000. I have all original bills and discharge summary..."
              className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-primary resize-none"
              required
            />
            <div className="text-xs text-text-muted mt-1 text-right">{form.description.length}/3000</div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-accent-primary hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {loading ? 'Processing...' : 'Submit Claim'}
          </button>
        </form>
      </Card>

      {/* Loading */}
      {loading && (
        <Card className="flex justify-center py-12">
          <Spinner />
        </Card>
      )}

      {/* Result */}
      <AnimatePresence>
        {lastResult && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Status header */}
            <Card>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    {lastResult.status === 'flagged'
                      ? <AlertTriangle className="text-accent-danger w-5 h-5" />
                      : <CheckCircle className="text-accent-success w-5 h-5" />
                    }
                    <h2 className="text-lg font-semibold text-text-primary">
                      Claim {lastResult.status === 'flagged' ? 'Flagged for Review' : 'Successfully Routed'}
                    </h2>
                  </div>
                  <p className="text-xs text-text-muted font-mono">ID: {lastResult.claim_id}</p>
                </div>
                <div className="flex gap-2">
                  {lastResult.claim_type && <Badge label={lastResult.claim_type} />}
                  <Badge label={lastResult.status} />
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5 pt-5 border-t border-border">
                <div className="text-center">
                  <div className="text-xs text-text-muted mb-1">Department</div>
                  <div className="text-sm text-text-primary font-medium">{lastResult.assigned_department || '—'}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-text-muted mb-1">Timeline</div>
                  <div className="text-sm text-text-primary font-medium">{lastResult.estimated_timeline || '—'}</div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-text-muted mb-1">Covered</div>
                  <div className={`text-sm font-medium ${lastResult.is_covered ? 'text-accent-success' : 'text-accent-danger'}`}>
                    {lastResult.is_covered === null ? '—' : lastResult.is_covered ? 'Yes' : 'Under Review'}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-text-muted mb-1">Processed in</div>
                  <div className="text-sm text-text-primary font-medium">{(lastResult.processing_time_ms / 1000).toFixed(1)}s</div>
                </div>
              </div>
            </Card>

            {/* Scores */}
            <Card>
              <h3 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4 text-accent-primary" /> Risk Assessment
              </h3>
              <div className="space-y-2">
                <ScoreDot score={lastResult.priority_score || 0} label="Priority" />
                <ScoreDot score={lastResult.fraud_score || 0} label="Fraud risk" />
              </div>
              {lastResult.coverage_details && (
                <p className="text-sm text-text-secondary mt-4 pt-4 border-t border-border">
                  {lastResult.coverage_details}
                </p>
              )}
            </Card>

            {/* Customer response */}
            <Card>
              <h3 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
                <FileText className="w-4 h-4 text-accent-primary" /> Customer Response
              </h3>
              <pre className="text-sm text-text-secondary whitespace-pre-wrap font-sans leading-relaxed">
                {lastResult.customer_response}
              </pre>
            </Card>

            {/* Documents required */}
            {lastResult.documents_required.length > 0 && (
              <Card>
                <h3 className="text-sm font-medium text-text-primary mb-3">Documents Required</h3>
                <ul className="space-y-1.5">
                  {lastResult.documents_required.map((doc, i) => (
                    <li key={i} className="text-sm text-text-secondary flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-accent-primary shrink-0" />
                      {doc}
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {/* Agent traces */}
            <Card>
              <h3 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-accent-primary" /> Agent Pipeline Trace
              </h3>
              <div>
                {lastResult.agent_traces.map((t, i) => (
                  <AgentTraceRow key={i} trace={t} />
                ))}
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
