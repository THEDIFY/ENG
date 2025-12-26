import { create } from 'zustand'
import type { Project, OptimizationParams } from '../types'

interface AppState {
  currentProject: Project | null
  setCurrentProject: (project: Project | null) => void
  
  optimizationParams: OptimizationParams
  setOptimizationParams: (params: Partial<OptimizationParams>) => void
  
  viewerSettings: {
    showGrid: boolean
    showAxes: boolean
    densityThreshold: number
  }
  setViewerSettings: (settings: Partial<AppState['viewerSettings']>) => void
}

export const useAppStore = create<AppState>((set) => ({
  currentProject: null,
  setCurrentProject: (project) => set({ currentProject: project }),
  
  optimizationParams: {
    method: 'simp',
    volume_fraction: 0.3,
    penalty_factor: 3.0,
    filter_radius: 2.0,
    max_iterations: 200,
    convergence_tolerance: 0.01,
    move_limit: 0.2,
    compliance_weight: 1.0,
    mass_weight: 0.5,
    aero_weight: 0.3,
    aero_coupling: true,
    aero_update_interval: 50,
  },
  setOptimizationParams: (params) =>
    set((state) => ({
      optimizationParams: { ...state.optimizationParams, ...params },
    })),
  
  viewerSettings: {
    showGrid: true,
    showAxes: true,
    densityThreshold: 0.5,
  },
  setViewerSettings: (settings) =>
    set((state) => ({
      viewerSettings: { ...state.viewerSettings, ...settings },
    })),
}))
