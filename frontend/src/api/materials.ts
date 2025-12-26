import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Material {
  id: string
  name: string
  material_type: string
  description?: string
  e1: number
  e2: number
  e3?: number
  g12: number
  g13?: number
  g23?: number
  nu12: number
  nu13?: number
  nu23?: number
  xt: number
  xc: number
  yt: number
  yc: number
  s12: number
  density: number
  ply_thickness?: number
  alpha1?: number
  alpha2?: number
  fatigue_params?: any
  drapability_params?: any
  cost_per_kg?: number
  created_at: string
  updated_at: string
}

export interface CreateMaterialRequest {
  name: string
  material_type: string
  description?: string
  e1: number
  e2: number
  e3?: number
  g12: number
  g13?: number
  g23?: number
  nu12: number
  nu13?: number
  nu23?: number
  xt: number
  xc: number
  yt: number
  yc: number
  s12: number
  density: number
  ply_thickness?: number
  alpha1?: number
  alpha2?: number
  fatigue_params?: any
  drapability_params?: any
  cost_per_kg?: number
}

export const materialsApi = {
  list: async (): Promise<Material[]> => {
    const response = await api.get('/materials/')
    return response.data
  },

  get: async (id: string): Promise<Material> => {
    const response = await api.get(`/materials/${id}`)
    return response.data
  },

  create: async (data: CreateMaterialRequest): Promise<Material> => {
    const response = await api.post('/materials/', data)
    return response.data
  },

  update: async (id: string, data: Partial<CreateMaterialRequest>): Promise<Material> => {
    const response = await api.put(`/materials/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/materials/${id}`)
  },

  getPredefined: async (): Promise<any[]> => {
    const response = await api.get('/materials/predefined')
    return response.data
  },

  seedDefaults: async (): Promise<Material[]> => {
    const response = await api.post('/materials/seed-defaults')
    return response.data
  },
}
