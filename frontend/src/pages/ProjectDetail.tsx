import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'
import Viewer3D from '../components/Viewer3D'

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="p-6">
        <p className="text-gray-500">Loading project...</p>
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
            : 'bg-blue-100 text-blue-700'
        }`}>
          {project.status?.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Viewer */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="font-semibold">Design Visualization</h2>
          </div>
          <div className="h-96">
            <Viewer3D />
          </div>
        </div>

        {/* Project Info */}
        <div className="space-y-6">
          {/* Workflow Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Workflow Progress</h2>
            <div className="space-y-3">
              {[
                { step: 'Rules Parsed', key: 'rules_config' },
                { step: 'Components Placed', key: 'components_config' },
                { step: 'Design Space Generated', key: 'design_space_config' },
                { step: 'Loads Defined', key: 'load_cases' },
                { step: 'Materials Assigned', key: 'materials_config' },
                { step: 'Manufacturing Configured', key: 'manufacturing_config' },
                { step: 'Optimization Complete', key: 'optimization_results' },
                { step: 'Validation Complete', key: 'validation_results' },
              ].map((item) => (
                <div key={item.key} className="flex items-center">
                  <div className={`w-4 h-4 rounded-full mr-3 ${
                    project[item.key] ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                  <span className={project[item.key] ? 'text-gray-800' : 'text-gray-400'}>
                    {item.step}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="font-semibold mb-4">Actions</h2>
            <div className="space-y-2">
              <button className="w-full px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
                Edit Configuration
              </button>
              <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Run Optimization
              </button>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                Export Outputs
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Configuration Sections */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Rules Configuration</h2>
          {project.rules_config ? (
            <pre className="text-xs bg-gray-50 p-4 rounded overflow-auto max-h-48">
              {JSON.stringify(project.rules_config, null, 2)}
            </pre>
          ) : (
            <p className="text-gray-400">Not configured</p>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold mb-4">Optimization Parameters</h2>
          {project.optimization_params ? (
            <pre className="text-xs bg-gray-50 p-4 rounded overflow-auto max-h-48">
              {JSON.stringify(project.optimization_params, null, 2)}
            </pre>
          ) : (
            <p className="text-gray-400">Not configured</p>
          )}
        </div>
      </div>
    </div>
  )
}
