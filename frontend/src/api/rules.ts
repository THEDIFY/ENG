import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface BajaRulesSet {
  version: string
  categories: RuleCategory[]
}

export interface RuleCategory {
  name: string
  description: string
  rules: Rule[]
}

export interface Rule {
  id: string
  name: string
  description: string
  type: string
  value?: number
  unit?: string
  min_value?: number
  max_value?: number
  limit_type?: string
  requirements?: Record<string, any>
}

export interface ParseRulesRequest {
  rule_set_version: string
  custom_constraints?: any[]
  override_rules?: string[]
}

export interface ParseRulesResponse {
  version: string
  total_rules: number
  categories: string[]
  constraints: any[]
  dimensional_constraints: Record<string, any>
  safety_requirements: any[]
}

export const rulesApi = {
  getAll: async (): Promise<BajaRulesSet> => {
    const response = await api.get('/rules/')
    return response.data
  },

  listCategories: async (): Promise<string[]> => {
    const response = await api.get('/rules/categories')
    return response.data
  },

  getCategory: async (name: string): Promise<RuleCategory> => {
    const response = await api.get(`/rules/categories/${encodeURIComponent(name)}`)
    return response.data
  },

  parse: async (request: ParseRulesRequest): Promise<ParseRulesResponse> => {
    const response = await api.post('/rules/parse', request)
    return response.data
  },

  getDimensionalDefaults: async (): Promise<Record<string, number>> => {
    const response = await api.get('/rules/dimensional-defaults')
    return response.data
  },
}
