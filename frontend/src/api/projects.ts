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

export interface ViewerModel {
  has_model: boolean
  model_url: string | null
  model_type?: string
  status: string
  optimization_complete: boolean
  mass_reduction?: number
  volume_fraction?: number
  message?: string
}

export interface ProjectStatus {
  project_id: string
  name: string
  status: string
  stages: {
    rules_parsed: boolean
    components_placed: boolean
    design_space_generated: boolean
    loads_defined: boolean
    loads_count: number
    loads_auto_generated: boolean
    materials_assigned: boolean
    manufacturing_configured: boolean
    optimization_complete: boolean
    validation_complete: boolean
  }
  optimization_params?: any
  optimization_results?: any
  validation_results?: any
  artifacts: {
    viewer_model_url?: string
  }
  created_at: string | null
  updated_at: string | null
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

  runOptimization: async (projectId: string, params?: any) => {
    const response = await api.post(`/projects/${projectId}/optimize`, params)
    return response.data
  },

  runValidation: async (projectId: string) => {
    const response = await api.post(`/projects/${projectId}/validate`)
    return response.data
  },

  // New endpoints for orchestration pipeline

  getViewerModel: async (projectId: string): Promise<ViewerModel> => {
    const response = await api.get(`/projects/${projectId}/viewer_model`)
    return response.data
  },

  getStatus: async (projectId: string): Promise<ProjectStatus> => {
    const response = await api.get(`/projects/${projectId}/status`)
    return response.data
  },

  inferLoads: async (projectId: string, missionProfile: string = 'baja_1000', vehicleMassKg: number = 2500) => {
    const response = await api.post(`/projects/${projectId}/infer_loads`, null, {
      params: { mission_profile: missionProfile, vehicle_mass_kg: vehicleMassKg }
    })
    return response.data
  },

  buildDesignSpace: async (projectId: string) => {
    const response = await api.post(`/projects/${projectId}/build_design_space`)
    return response.data
  },

  uploadModel: async (projectId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(`/projects/${projectId}/upload_model`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  exportProject: async (projectId: string, format: string) => {
    const response = await api.get(`/projects/${projectId}/export`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },
}
