import { useQuery } from '@tanstack/react-query'
import { materialsApi } from '../api/materials'

interface Material {
  id: string
  name: string
  material_type: string
  e1: number
  e2: number
  g12: number
  nu12: number
  xt: number
  xc: number
  yt: number
  yc: number
  s12: number
  density: number
  ply_thickness?: number
}

export default function MaterialsPage() {
  const { data: materials, isLoading } = useQuery({
    queryKey: ['materials'],
    queryFn: materialsApi.list,
  })

  const { data: predefinedMaterials } = useQuery({
    queryKey: ['predefined-materials'],
    queryFn: materialsApi.getPredefined,
  })

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Material Library</h1>

      {/* Predefined Materials */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="font-semibold text-lg mb-4">Standard Carbon Fiber Materials</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {predefinedMaterials?.map((material: any) => (
            <div key={material.name} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h3 className="font-medium text-gray-800">{material.name}</h3>
              <p className="text-xs text-gray-500 mb-3">{material.material_type}</p>
              
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">E1:</span>
                  <span className="font-medium">{material.e1} GPa</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">E2:</span>
                  <span className="font-medium">{material.e2} GPa</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">G12:</span>
                  <span className="font-medium">{material.g12} GPa</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Density:</span>
                  <span className="font-medium">{material.density} kg/m³</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Ply:</span>
                  <span className="font-medium">{material.ply_thickness} mm</span>
                </div>
              </div>
              
              <button className="w-full mt-3 px-3 py-1 bg-primary-100 text-primary-700 rounded text-sm hover:bg-primary-200">
                Add to Library
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Custom Materials Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="font-semibold">Custom Materials</h2>
          <button className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
            Add Material
          </button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading materials...</div>
        ) : materials && materials.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">E1 (GPa)</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">E2 (GPa)</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">G12 (GPa)</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Density</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {materials.map((material: Material) => (
                <tr key={material.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{material.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{material.material_type}</td>
                  <td className="px-4 py-3">{material.e1}</td>
                  <td className="px-4 py-3">{material.e2}</td>
                  <td className="px-4 py-3">{material.g12}</td>
                  <td className="px-4 py-3">{material.density}</td>
                  <td className="px-4 py-3">
                    <button className="text-primary-600 hover:text-primary-800 mr-3">Edit</button>
                    <button className="text-red-600 hover:text-red-800">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-8 text-center text-gray-500">
            <p>No custom materials defined</p>
            <p className="text-sm mt-2">Add standard materials from above or create custom ones</p>
          </div>
        )}
      </div>

      {/* Material Properties Reference */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold text-lg mb-4">Property Reference</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <div>
            <h3 className="font-medium mb-2">Elastic Properties</h3>
            <ul className="space-y-1 text-gray-600">
              <li><strong>E1:</strong> Longitudinal (fiber direction) modulus</li>
              <li><strong>E2:</strong> Transverse modulus</li>
              <li><strong>G12:</strong> In-plane shear modulus</li>
              <li><strong>ν12:</strong> In-plane Poisson's ratio</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium mb-2">Strength Properties</h3>
            <ul className="space-y-1 text-gray-600">
              <li><strong>Xt:</strong> Longitudinal tensile strength</li>
              <li><strong>Xc:</strong> Longitudinal compressive strength</li>
              <li><strong>Yt:</strong> Transverse tensile strength</li>
              <li><strong>Yc:</strong> Transverse compressive strength</li>
              <li><strong>S12:</strong> In-plane shear strength</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
