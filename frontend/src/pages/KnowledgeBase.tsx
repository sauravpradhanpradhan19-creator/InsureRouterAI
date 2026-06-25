import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { getCompanies, ingestPDF } from '../lib/api'
import { Card } from '../components/ui'
import { Upload, CheckCircle, Database } from 'lucide-react'
import type { Company } from '../types'

export default function KnowledgeBase() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [selectedCompany, setSelectedCompany] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState<string[]>([])

  useEffect(() => {
    getCompanies().then(c => { setCompanies(c); if (c.length) setSelectedCompany(c[0].slug) })
  }, [])

  const handleUpload = async () => {
    if (!file || !selectedCompany) return
    setUploading(true)
    try {
      const form = new FormData()
      form.append('company_slug', selectedCompany)
      form.append('file', file)
      const res = await ingestPDF(form)
      setResults(r => [res.message, ...r])
      setFile(null)
      toast.success(res.message)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Knowledge Base</h1>
        <p className="text-text-secondary mt-1">Upload policy PDFs to train the AI for each insurance company.</p>
      </div>

      <Card>
        <h2 className="text-sm font-medium text-text-primary mb-4 flex items-center gap-2">
          <Upload className="w-4 h-4 text-accent-primary" /> Upload Policy Document
        </h2>

        <div className="space-y-4">
          <div>
            <label className="text-sm text-text-secondary mb-1 block">Insurance Company</label>
            <select
              value={selectedCompany}
              onChange={e => setSelectedCompany(e.target.value)}
              className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-text-primary text-sm focus:outline-none focus:border-accent-primary"
            >
              {companies.map(c => <option key={c.slug} value={c.slug}>{c.name}</option>)}
            </select>
          </div>

          <div>
            <label className="text-sm text-text-secondary mb-1 block">Policy PDF</label>
            <div
              className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-accent-primary transition-colors"
              onClick={() => document.getElementById('pdf-input')?.click()}
            >
              {file ? (
                <div className="flex items-center justify-center gap-2 text-accent-success">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm">{file.name}</span>
                </div>
              ) : (
                <>
                  <Upload className="w-8 h-8 text-text-muted mx-auto mb-2" />
                  <p className="text-text-secondary text-sm">Click to select a PDF</p>
                  <p className="text-text-muted text-xs mt-1">Policy wordings, claim procedures, schedules</p>
                </>
              )}
              <input
                id="pdf-input"
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={e => setFile(e.target.files?.[0] || null)}
              />
            </div>
          </div>

          <button
            onClick={handleUpload}
            disabled={!file || !selectedCompany || uploading}
            className="w-full bg-accent-primary hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2.5 rounded-lg transition-colors"
          >
            {uploading ? 'Ingesting...' : 'Upload & Ingest'}
          </button>
        </div>
      </Card>

      {/* Demo KB info */}
      <Card>
        <h2 className="text-sm font-medium text-text-primary mb-3 flex items-center gap-2">
          <Database className="w-4 h-4 text-accent-primary" /> Pre-loaded Demo Knowledge Base
        </h2>
        <div className="space-y-2">
          {[
            { company: 'HDFC Ergo (demo_hdfc)', docs: ['Health Suraksha Plus policy', 'Motor Package policy'] },
            { company: 'Star Health (demo_star)', docs: ['Star Comprehensive policy'] },
            { company: 'Shared KB', docs: ['IRDAI claim regulations', 'Standard definitions'] },
          ].map(({ company, docs }) => (
            <div key={company} className="py-2 border-b border-border last:border-0">
              <div className="text-sm text-text-primary font-medium">{company}</div>
              <div className="flex flex-wrap gap-2 mt-1">
                {docs.map(d => (
                  <span key={d} className="text-xs bg-bg-tertiary text-text-secondary px-2 py-0.5 rounded">
                    {d}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="text-xs text-text-muted mt-3">
          Demo data is auto-seeded on startup. Upload real PDFs to improve accuracy.
        </p>
      </Card>

      {/* Upload history */}
      {results.length > 0 && (
        <Card>
          <h2 className="text-sm font-medium text-text-primary mb-3">Upload History</h2>
          <div className="space-y-1">
            {results.map((r, i) => (
              <div key={i} className="text-sm text-accent-success flex items-center gap-2">
                <CheckCircle className="w-3.5 h-3.5 shrink-0" /> {r}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
