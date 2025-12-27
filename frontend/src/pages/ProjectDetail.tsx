import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, UpdateProjectRequest } from '../api/projects'
import { materialsApi } from '../api/materials'
import { rulesApi } from '../api/rules'
import Viewer3D from '../components/Viewer3D'

type WorkflowStep = 
  | 'rules_config'
  | 'components_config'
  | 'design_space_config'
  | 'load_cases'
  | 'materials_config'
  | 'manufacturing_config'
  | 'optimization_results'
  | 'validation_results'

interface LoadForce {
  name: string
  type: string
  x: number
  y: number
  z: number
  magnitude: number
  direction: [number, number, number]
}

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  
  // UI State
  const [activePanel, setActivePanel] = useState<WorkflowStep | null>(null)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const [exportFormat, setExportFormat] = useState('step')
  
  // Configuration State
  const [rulesConfig, setRulesConfig] = useState<any>({
    rule_set_version: '2024',
    max_width: 2438,
    max_length: 5486,
    min_ground_clearance: 254,
    wheelbase_min: 2540,
    wheelbase_max: 3556,
    constraints: []
  })
  
  const [loadCases, setLoadCases] = useState<LoadForce[]>([])
  const [newForce, setNewForce] = useState<LoadForce>({
    name: '',
    type: 'point',
    x: 0, y: 0, z: 0,
    magnitude: 1000,
    direction: [0, -1, 0]
  })
  
  const [selectedMaterial, setSelectedMaterial] = useState<string>('')
  const [materialsConfig, setMaterialsConfig] = useState<any>({
    primary_material: '',
    secondary_material: '',
    layup_angles: [0, 45, -45, 90]
  })
  
  const [optimizationParams, setOptimizationParams] = useState({
    method: 'simp',
    volume_fraction: 0.3,
    penalty_factor: 3.0,
    max_iterations: 500,
    convergence_tolerance: 0.0001,
    compliance_weight: 1.0,
    mass_weight: 0.5
  })

  const [manufacturingConfig, setManufacturingConfig] = useState({
    allowed_ply_angles: [0, 45, -45, 90],
    min_ply_thickness: 0.2,
    max_consecutive_same_angle: 4,
    enforce_symmetry: true,
    enforce_balance: true,
    draft_angle: 3.0
  })

  // Queries
  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
  })

  const { data: materials } = useQuery({
    queryKey: ['materials-predefined'],
    queryFn: materialsApi.getPredefined,
  })

  const { data: rulesData } = useQuery({
    queryKey: ['rules'],
    queryFn: rulesApi.getAll,
  })

  // Initialize state from project data
  useEffect(() => {
    if (project) {
      if (project.rules_config) setRulesConfig(project.rules_config)
      if (project.load_cases?.load_cases) setLoadCases(project.load_cases.load_cases)
      if (project.materials_config) {
        setMaterialsConfig(project.materials_config)
        setSelectedMaterial(project.materials_config.primary_material || '')
      }
      if (project.optimization_params) setOptimizationParams({...optimizationParams, ...project.optimization_params})
      if (project.manufacturing_config) setManufacturingConfig({...manufacturingConfig, ...project.manufacturing_config})
    }
  }, [project])

  // Mutations
  const updateMutation = useMutation({
    mutationFn: (data: UpdateProjectRequest) => projectsApi.update(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', id] })
    },
  })

  const optimizeMutation = useMutation({
    mutationFn: () => projectsApi.runOptimization(id!),
    onMutate: () => setIsOptimizing(true),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project', id] })
      setIsOptimizing(false)
    },
    onError: () => setIsOptimizing(false),
  })

  // Save handlers
  const saveRulesConfig = () => {
    updateMutation.mutate({ rules_config: rulesConfig })
    setActivePanel(null)
  }

  const saveLoadCases = () => {
    updateMutation.mutate({ 
      load_cases: { 
        mission_profile: 'baja_1000',
        load_cases: loadCases,
        max_vertical_g: 5.0,
        max_lateral_g: 2.0
      } 
    })
    setActivePanel(null)
  }

  const saveMaterialsConfig = () => {
    const config = {
      ...materialsConfig,
      primary_material: selectedMaterial
    }
    updateMutation.mutate({ materials_config: config })
    setActivePanel(null)
  }

  const saveOptimizationParams = () => {
    updateMutation.mutate({ optimization_params: optimizationParams })
    setActivePanel(null)
  }

  const saveManufacturingConfig = () => {
    updateMutation.mutate({ manufacturing_config: manufacturingConfig })
    setActivePanel(null)
  }

  const addForce = () => {
    if (newForce.name) {
      setLoadCases([...loadCases, newForce])
      setNewForce({
        name: '',
        type: 'point',
        x: 0, y: 0, z: 0,
        magnitude: 1000,
        direction: [0, -1, 0]
      })
    }
  }

  const workflowSteps = [
    { step: 'Rules Parsed', key: 'rules_config' as WorkflowStep, icon: '📋' },
    { step: 'Components Placed', key: 'components_config' as WorkflowStep, icon: '🔧' },
    { step: 'Design Space Generated', key: 'design_space_config' as WorkflowStep, icon: '📐' },
    { step: 'Loads Defined', key: 'load_cases' as WorkflowStep, icon: '⚡' },
    { step: 'Materials Assigned', key: 'materials_config' as WorkflowStep, icon: '🧱' },
    { step: 'Manufacturing Configured', key: 'manufacturing_config' as WorkflowStep, icon: '🏭' },
    { step: 'Optimization Complete', key: 'optimization_results' as WorkflowStep, icon: '🎯' },
    { step: 'Validation Complete', key: 'validation_results' as WorkflowStep, icon: '✅' },
  ]

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading project...</p>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="p-6">
        <p className="text-red-500">Error loading project</p>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{project.name}</h1>
          <p className="text-gray-500">{project.description || 'No description'}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm ${
          project.status === 'completed' 
            ? 'bg-green-100 text-green-700' 
            : project.status === 'optimizing'
            ? 'bg-yellow-100 text-yellow-700'
            : 'bg-blue-100 text-blue-700'
        }`}>
          {project.status?.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Viewer */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="p-4 border-b flex justify-between items-center">
            <h2 className="font-semibold">Design Visualization</h2>
            {project.optimization_results && (
              <span className="text-sm text-green-600">
                ✓ Optimized ({project.optimization_results.mass_reduction}% mass reduction)
              </span>
            )}
          </div>
          <div className="h-96 relative">
            <Viewer3D 
              densityField={project.optimization_results?.density_field}
            />
            {loadCases.length > 0 && (
              <div className="absolute top-4 right-4 bg-black/70 text-white text-xs px-3 py-2 rounded">
                <p className="font-semibold mb-1">Applied Forces:</p>
                {loadCases.map((f, i) => (
                  <p key={i}>{f.name}: {f.magnitude}N</p>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel */}
        <div className="space-y-6">
          {/* Workflow Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Workflow Progress</h2>
            <div className="space-y-2">
              {workflowSteps.map((item) => {
                const isConfigured = project[item.key]
                const isClickable = item.key !== 'optimization_results' && item.key !== 'validation_results'
                return (
                  <button
                    key={item.key}
                    onClick={() => isClickable && setActivePanel(item.key)}
                    disabled={!isClickable}
                    className={`w-full flex items-center p-2 rounded-lg transition ${
                      isClickable 
                        ? 'hover:bg-gray-100 cursor-pointer' 
                        : 'cursor-default'
                    } ${activePanel === item.key ? 'bg-primary-50 border border-primary-200' : ''}`}
                  >
                    <span className="text-lg mr-2">{item.icon}</span>
                    <div className={`w-3 h-3 rounded-full mr-3 ${
                      isConfigured ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                    <span className={`flex-1 text-left ${isConfigured ? 'text-gray-800' : 'text-gray-400'}`}>
                      {item.step}
                    </span>
                    {isClickable && (
                      <span className="text-gray-400 text-sm">
                        {isConfigured ? '✏️' : '➕'}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Actions</h2>
            <div className="space-y-2">
              <button 
                onClick={() => optimizeMutation.mutate()}
                disabled={isOptimizing || !project.materials_config}
                className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isOptimizing ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Running Optimization...
                  </>
                ) : '🚀 Run Optimization'}
              </button>
              <button 
                onClick={() => setShowExportModal(true)}
                disabled={!project.optimization_results}
                className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition disabled:opacity-50"
              >
                📦 Export Outputs
              </button>
            </div>
            {!project.materials_config && (
              <p className="text-xs text-orange-600 mt-2">
                Configure materials to enable optimization
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Panels */}
      {activePanel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
            {/* Rules Configuration */}
            {activePanel === 'rules_config' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">📋 Baja 1000 Rules Configuration</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Rule Set Version</label>
                    <select
                      value={rulesConfig.rule_set_version}
                      onChange={(e) => setRulesConfig({...rulesConfig, rule_set_version: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="2024">2024 Rules</option>
                      <option value="2023">2023 Rules</option>
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Max Width (mm)</label>
                      <input
                        type="number"
                        value={rulesConfig.max_width}
                        onChange={(e) => setRulesConfig({...rulesConfig, max_width: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Max Length (mm)</label>
                      <input
                        type="number"
                        value={rulesConfig.max_length}
                        onChange={(e) => setRulesConfig({...rulesConfig, max_length: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Min Ground Clearance (mm)</label>
                      <input
                        type="number"
                        value={rulesConfig.min_ground_clearance}
                        onChange={(e) => setRulesConfig({...rulesConfig, min_ground_clearance: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Wheelbase Min (mm)</label>
                      <input
                        type="number"
                        value={rulesConfig.wheelbase_min}
                        onChange={(e) => setRulesConfig({...rulesConfig, wheelbase_min: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                  </div>
                  {rulesData?.categories && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Available Rule Categories</label>
                      <div className="flex flex-wrap gap-2">
                        {rulesData.categories.map((cat: any) => (
                          <span key={cat.name} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                            {cat.name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex gap-2 mt-6">
                  <button onClick={() => setActivePanel(null)} className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                    Cancel
                  </button>
                  <button onClick={saveRulesConfig} className="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                    Save Rules
                  </button>
                </div>
              </div>
            )}

            {/* Components Configuration */}
            {activePanel === 'components_config' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">🔧 Component Placement</h3>
                <p className="text-gray-600 mb-4">Define the placement of major components in your chassis.</p>
                <div className="space-y-4">
                  {['Engine', 'Transmission', 'Fuel Cell', 'Radiator', 'Driver Seat'].map((comp) => (
                    <div key={comp} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{comp}</span>
                        <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">
                          Configure
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2 mt-6">
                  <button onClick={() => setActivePanel(null)} className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                    Cancel
                  </button>
                  <button 
                    onClick={() => {
                      updateMutation.mutate({ components_config: { configured: true } })
                      setActivePanel(null)
                    }} 
                    className="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                  >
                    Save Components
                  </button>
                </div>
              </div>
            )}

            {/* Design Space Configuration */}
            {activePanel === 'design_space_config' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">📐 Design Space</h3>
                <p className="text-gray-600 mb-4">Define the volume where material can be placed during optimization.</p>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Length (mm)</label>
                      <input type="number" defaultValue={4000} className="w-full border border-gray-300 rounded-md px-3 py-2" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Width (mm)</label>
                      <input type="number" defaultValue={2000} className="w-full border border-gray-300 rounded-md px-3 py-2" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Height (mm)</label>
                      <input type="number" defaultValue={1500} className="w-full border border-gray-300 rounded-md px-3 py-2" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Symmetry Plane</label>
                    <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                      <option value="xz">XZ Plane (Left-Right Symmetry)</option>
                      <option value="none">No Symmetry</option>
                    </select>
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <button onClick={() => setActivePanel(null)} className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                    Cancel
                  </button>
                  <button 
                    onClick={() => {
                      updateMutation.mutate({ design_space_config: { configured: true, symmetry: 'xz' } })
                      setActivePanel(null)
                    }} 
                    className="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
                  >
                    Save Design Space
                  </button>
                </div>
              </div>
            )}

            {/* Load Cases (Forces) */}
            {activePanel === 'load_cases' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">⚡ Load Cases & Forces</h3>
                <p className="text-gray-600 mb-4">Define the forces and loads acting on your chassis.</p>
                
                {/* Existing Forces */}
                {loadCases.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium mb-2">Applied Forces</h4>
                    <div className="space-y-2">
                      {loadCases.map((force, i) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <span className="font-medium">{force.name}</span>
                            <span className="text-gray-500 ml-2">
                              {force.magnitude}N at ({force.x}, {force.y}, {force.z})
                            </span>
                          </div>
                          <button 
                            onClick={() => setLoadCases(loadCases.filter((_, idx) => idx !== i))}
                            className="text-red-600 hover:text-red-800"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Add New Force */}
                <div className="border border-dashed border-gray-300 rounded-lg p-4">
                  <h4 className="font-medium mb-3">Add New Force</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Force Name</label>
                      <input
                        type="text"
                        value={newForce.name}
                        onChange={(e) => setNewForce({...newForce, name: e.target.value})}
                        placeholder="e.g., Front Impact, Vertical Load"
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Force Type</label>
                      <select
                        value={newForce.type}
                        onChange={(e) => setNewForce({...newForce, type: e.target.value})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      >
                        <option value="point">Point Force</option>
                        <option value="distributed">Distributed</option>
                        <option value="moment">Moment</option>
                        <option value="gravity">Gravity (G-force)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Magnitude (N)</label>
                      <input
                        type="number"
                        value={newForce.magnitude}
                        onChange={(e) => setNewForce({...newForce, magnitude: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Position X (mm)</label>
                      <input
                        type="number"
                        value={newForce.x}
                        onChange={(e) => setNewForce({...newForce, x: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Position Y (mm)</label>
                      <input
                        type="number"
                        value={newForce.y}
                        onChange={(e) => setNewForce({...newForce, y: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Position Z (mm)</label>
                      <input
                        type="number"
                        value={newForce.z}
                        onChange={(e) => setNewForce({...newForce, z: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div className="col-span-2">
                      <button
                        onClick={addForce}
                        disabled={!newForce.name}
                        className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                      >
                        + Add Force
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 mt-6">
                  <button onClick={() => setActivePanel(null)} className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                    Cancel
                  </button>
                  <button onClick={saveLoadCases} className="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                    Save Load Cases
                  </button>
                </div>
              </div>
            )}

            {/* Materials Configuration */}
            {activePanel === 'materials_config' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">🧱 Materials Configuration</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Primary Material</label>
                    <select
                      value={selectedMaterial}
                      onChange={(e) => setSelectedMaterial(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="">Select a material...</option>
                      {materials?.map((mat: any) => (
                        <option key={mat.id} value={mat.id}>
                          {mat.name} - E: {mat.properties?.youngs_modulus} GPa
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  {selectedMaterial && materials && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium mb-2">Material Properties</h4>
                      {(() => {
                        const mat = materials.find((m: any) => m.id === selectedMaterial)
                        return mat ? (
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <p><span className="text-gray-500">Type:</span> {mat.type}</p>
                            <p><span className="text-gray-500">Density:</span> {mat.properties?.density} kg/m³</p>
                            <p><span className="text-gray-500">Young's Modulus:</span> {mat.properties?.youngs_modulus} GPa</p>
                            <p><span className="text-gray-500">Tensile Strength:</span> {mat.properties?.tensile_strength} MPa</p>
                          </div>
                        ) : null
                      })()}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Layup Angles</label>
                    <div className="flex flex-wrap gap-2">
                      {[0, 45, -45, 90, 30, -30, 60, -60].map((angle) => (
                        <button
                          key={angle}
                          onClick={() => {
                            const angles = materialsConfig.layup_angles || []
                            if (angles.includes(angle)) {
                              setMaterialsConfig({
                                ...materialsConfig,
                                layup_angles: angles.filter((a: number) => a !== angle)
                              })
                            } else {
                              setMaterialsConfig({
                                ...materialsConfig,
                                layup_angles: [...angles, angle].sort((a: number, b: number) => a - b)
                              })
                            }
                          }}
                          className={`px-3 py-1 rounded border ${
                            materialsConfig.layup_angles?.includes(angle)
                              ? 'bg-blue-600 text-white border-blue-600'
                              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                          }`}
                        >
                          {angle}°
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <button onClick={() => setActivePanel(null)} className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                    Cancel
                  </button>
                  <button onClick={saveMaterialsConfig} disabled={!selectedMaterial} className="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50">
                    Save Materials
                  </button>
                </div>
              </div>
            )}

            {/* Manufacturing Configuration */}
            {activePanel === 'manufacturing_config' && (
              <div className="p-6">
                <h3 className="text-xl font-semibold mb-4">🏭 Manufacturing Configuration</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Min Ply Thickness (mm)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={manufacturingConfig.min_ply_thickness}
                        onChange={(e) => setManufacturingConfig({...manufacturingConfig, min_ply_thickness: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Draft Angle (°)</label>
                      <input
                        type="number"
                        step="0.5"
                        value={manufacturingConfig.draft_angle}
                        onChange={(e) => setManufacturingConfig({...manufacturingConfig, draft_angle: parseFloat(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Max Consecutive Same Angle</label>
                      <input
                        type="number"
                        value={manufacturingConfig.max_consecutive_same_angle}
                        onChange={(e) => setManufacturingConfig({...manufacturingConfig, max_consecutive_same_angle: parseInt(e.target.value)})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={manufacturingConfig.enforce_symmetry}
                        onChange={(e) => setManufacturingConfig({...manufacturingConfig, enforce_symmetry: e.target.checked})}
                        className="mr-2"
                      />
                      Enforce Symmetry
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={manufacturingConfig.enforce_balance}
                        onChange={(e) => setManufacturingConfig({...manufacturingConfig, enforce_balance: e.target.checked})}
                        className="mr-2"
                      />
                      Enforce Balance
                    </label>
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <button onClick={() => setActivePanel(null)} className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
                    Cancel
                  </button>
                  <button onClick={saveManufacturingConfig} className="flex-1 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                    Save Manufacturing Config
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Optimization Parameters Quick Config */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold">Optimization Parameters</h2>
            <button 
              onClick={() => saveOptimizationParams()}
              className="px-3 py-1 bg-primary-600 text-white text-sm rounded hover:bg-primary-700"
            >
              Save
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Method</label>
              <select
                value={optimizationParams.method}
                onChange={(e) => setOptimizationParams({...optimizationParams, method: e.target.value})}
                className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value="simp">SIMP</option>
                <option value="level_set">Level Set</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Volume Fraction</label>
              <input
                type="number"
                step="0.05"
                min="0.1"
                max="0.9"
                value={optimizationParams.volume_fraction}
                onChange={(e) => setOptimizationParams({...optimizationParams, volume_fraction: parseFloat(e.target.value)})}
                className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Max Iterations</label>
              <input
                type="number"
                value={optimizationParams.max_iterations}
                onChange={(e) => setOptimizationParams({...optimizationParams, max_iterations: parseInt(e.target.value)})}
                className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Penalty Factor</label>
              <input
                type="number"
                step="0.5"
                value={optimizationParams.penalty_factor}
                onChange={(e) => setOptimizationParams({...optimizationParams, penalty_factor: parseFloat(e.target.value)})}
                className="w-full border border-gray-300 rounded px-2 py-1 text-sm"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Configuration Summary</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Rules:</span>
              <span className={project.rules_config ? 'text-green-600' : 'text-gray-400'}>
                {project.rules_config ? `${rulesConfig.rule_set_version} rules configured` : 'Not configured'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Loads:</span>
              <span className={project.load_cases ? 'text-green-600' : 'text-gray-400'}>
                {project.load_cases ? `${loadCases.length} forces defined` : 'Not configured'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Material:</span>
              <span className={project.materials_config ? 'text-green-600' : 'text-gray-400'}>
                {selectedMaterial || 'Not selected'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Status:</span>
              <span className="font-medium">{project.status?.replace(/_/g, ' ')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">Export Project</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Export Format</label>
                <select 
                  value={exportFormat}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="step">STEP (CAD)</option>
                  <option value="stl">STL (3D Print)</option>
                  <option value="iges">IGES (CAD)</option>
                  <option value="json">JSON (Data)</option>
                </select>
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => setShowExportModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    alert(`Exporting as ${exportFormat.toUpperCase()}...`)
                    setShowExportModal(false)
                  }}
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                >
                  Export
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
