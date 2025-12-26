import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import Viewer3D from '../components/Viewer3D'

interface OptimizationState {
  status: 'idle' | 'running' | 'completed' | 'failed'
  iteration: number
  totalIterations: number
  compliance: number
  volumeFraction: number
  convergence: number
  densityField: number[]
}

export default function OptimizationPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [optimizationState, setOptimizationState] = useState<OptimizationState>({
    status: 'idle',
    iteration: 0,
    totalIterations: 200,
    compliance: 0,
    volumeFraction: 0.4,
    convergence: 1.0,
    densityField: [],
  })

  const [config, setConfig] = useState({
    method: 'simp',
    volumeFraction: 0.3,
    penaltyFactor: 3.0,
    filterRadius: 2.0,
    maxIterations: 200,
    convergenceTolerance: 0.01,
  })

  // Track interval reference for cleanup
  const [intervalId, setIntervalId] = useState<ReturnType<typeof setInterval> | null>(null)

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [intervalId])

  // Simulate optimization progress
  const runOptimization = () => {
    setOptimizationState((prev) => ({ ...prev, status: 'running', iteration: 0 }))
    
    const interval = setInterval(() => {
      setOptimizationState((prev) => {
        if (prev.iteration >= config.maxIterations || prev.convergence < config.convergenceTolerance) {
          clearInterval(interval)
          setIntervalId(null)
          return { ...prev, status: 'completed' }
        }
        
        const newIteration = prev.iteration + 1
        const newCompliance = 1000 * Math.exp(-newIteration * 0.02)
        const newConvergence = Math.max(0.001, prev.convergence * 0.95)
        
        return {
          ...prev,
          iteration: newIteration,
          compliance: newCompliance,
          convergence: newConvergence,
        }
      })
    }, 100)
    
    setIntervalId(interval)
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Topology Optimization</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Optimization Parameters</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Method</label>
                <select
                  value={config.method}
                  onChange={(e) => setConfig({ ...config, method: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="simp">SIMP (Solid Isotropic Material)</option>
                  <option value="level_set">Level-Set</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Volume Fraction: {config.volumeFraction}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="0.6"
                  step="0.05"
                  value={config.volumeFraction}
                  onChange={(e) => setConfig({ ...config, volumeFraction: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Penalty Factor: {config.penaltyFactor}
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="0.5"
                  value={config.penaltyFactor}
                  onChange={(e) => setConfig({ ...config, penaltyFactor: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter Radius: {config.filterRadius}
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  step="0.5"
                  value={config.filterRadius}
                  onChange={(e) => setConfig({ ...config, filterRadius: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Iterations</label>
                <input
                  type="number"
                  value={config.maxIterations}
                  onChange={(e) => setConfig({ ...config, maxIterations: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>
            
            <button
              onClick={runOptimization}
              disabled={optimizationState.status === 'running'}
              className="w-full mt-6 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {optimizationState.status === 'running' ? 'Running...' : 'Start Optimization'}
            </button>
          </div>

          {/* Progress */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Progress</h2>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Iteration</span>
                  <span>{optimizationState.iteration} / {config.maxIterations}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(optimizationState.iteration / config.maxIterations) * 100}%` }}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="p-3 bg-gray-50 rounded">
                  <p className="text-gray-500">Compliance</p>
                  <p className="font-semibold">{optimizationState.compliance.toFixed(2)}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded">
                  <p className="text-gray-500">Convergence</p>
                  <p className="font-semibold">{optimizationState.convergence.toFixed(4)}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded">
                  <p className="text-gray-500">Volume</p>
                  <p className="font-semibold">{(optimizationState.volumeFraction * 100).toFixed(1)}%</p>
                </div>
                <div className="p-3 bg-gray-50 rounded">
                  <p className="text-gray-500">Status</p>
                  <p className={`font-semibold ${
                    optimizationState.status === 'running' ? 'text-yellow-600' :
                    optimizationState.status === 'completed' ? 'text-green-600' :
                    'text-gray-600'
                  }`}>
                    {optimizationState.status.charAt(0).toUpperCase() + optimizationState.status.slice(1)}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Visualization */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold">Design Space Visualization</h2>
          </div>
          <div className="h-[600px]">
            <Viewer3D densityField={optimizationState.densityField} />
          </div>
        </div>
      </div>

      {/* Convergence History */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold mb-4">Convergence History</h2>
        <div className="h-48 flex items-end space-x-1">
          {Array.from({ length: Math.min(100, optimizationState.iteration) }).map((_, i) => (
            <div
              key={i}
              className="flex-1 bg-primary-500"
              style={{
                height: `${Math.max(5, 100 * Math.exp(-i * 0.02))}%`,
              }}
            />
          ))}
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>Iteration 1</span>
          <span>Iteration {optimizationState.iteration}</span>
        </div>
      </div>
    </div>
  )
}
