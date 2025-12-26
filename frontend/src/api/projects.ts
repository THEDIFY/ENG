import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Project {
  id: string
  name: string
  description?: string
  status: string
  rules_config?: any
  components_config?: any
  design_space_config?: any
  load_cases?: any
  materials_config?: any
  manufacturing_config?: any
  optimization_params?: any
  optimization_results?: any
  validation_results?: any
  created_at: string
  updated_at: string
}

export interface CreateProjectRequest {
  name: string
  description?: string
}

export interface UpdateProjectRequest {
  name?: string
  description?: string
  rules_config?: any
  components_config?: any
  design_space_config?: any
  load_cases?: any
  materials_config?: any
  manufacturing_config?: any
  optimization_params?: any
}

export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const response = await api.get('/projects/')
    return response.data
  },

  get: async (id: string): Promise<Project> => {
    const response = await api.get(`/projects/${id}`)
    return response.data
  },

  create: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await api.post('/projects/', data)
    return response.data
  },

  update: async (id: string, data: UpdateProjectRequest): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/projects/${id}`)
  },

  listJobs: async (projectId: string) => {
    const response = await api.get(`/projects/${projectId}/jobs`)
    return response.data
  },

  createJob: async (projectId: string, jobType: string, config?: any) => {
    const response = await api.post(`/projects/${projectId}/jobs`, {
      job_type: jobType,
      config,
    })
    return response.data
  },

  listOutputs: async (projectId: string) => {
    const response = await api.get(`/projects/${projectId}/outputs`)
    return response.data
  },
}
