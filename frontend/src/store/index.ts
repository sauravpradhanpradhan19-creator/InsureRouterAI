import { create } from 'zustand'
import type { ClaimResult, ClaimSummary, Metrics, Company } from '../types'

interface AppStore {
  companies: Company[]
  claims: ClaimSummary[]
  metrics: Metrics | null
  lastResult: ClaimResult | null
  isLoading: boolean
  setCompanies: (c: Company[]) => void
  setClaims: (c: ClaimSummary[]) => void
  setMetrics: (m: Metrics) => void
  setLastResult: (r: ClaimResult | null) => void
  setLoading: (v: boolean) => void
}

export const useStore = create<AppStore>((set) => ({
  companies: [],
  claims: [],
  metrics: null,
  lastResult: null,
  isLoading: false,
  setCompanies: (companies) => set({ companies }),
  setClaims: (claims) => set({ claims }),
  setMetrics: (metrics) => set({ metrics }),
  setLastResult: (lastResult) => set({ lastResult }),
  setLoading: (isLoading) => set({ isLoading }),
}))
