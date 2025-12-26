import { Link } from 'react-router-dom'
import Viewer3D from '../components/Viewer3D'

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">
        Trophy Truck Topology Optimizer
      </h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 3D Preview */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-lg font-semibold">Chassis Preview</h2>
          </div>
          <div className="h-96">
            <Viewer3D />
          </div>
        </div>
        
        {/* Quick Actions */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                to="/projects"
                className="block w-full p-4 bg-primary-50 hover:bg-primary-100 rounded-lg border border-primary-200"
              >
                <h3 className="font-medium text-primary-700">Create New Project</h3>
                <p className="text-sm text-primary-600">Start a new topology optimization project</p>
              </Link>
              <Link
                to="/rules"
                className="block w-full p-4 bg-green-50 hover:bg-green-100 rounded-lg border border-green-200"
              >
                <h3 className="font-medium text-green-700">Configure Baja Rules</h3>
                <p className="text-sm text-green-600">Set up Baja 1000 rules and constraints</p>
              </Link>
              <Link
                to="/materials"
                className="block w-full p-4 bg-purple-50 hover:bg-purple-100 rounded-lg border border-purple-200"
              >
                <h3 className="font-medium text-purple-700">Material Library</h3>
                <p className="text-sm text-purple-600">Manage carbon fiber material properties</p>
              </Link>
            </div>
          </div>
          
          {/* Stats */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold mb-4">System Status</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-800">0</p>
                <p className="text-sm text-gray-500">Active Jobs</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-gray-800">0</p>
                <p className="text-sm text-gray-500">Projects</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">Ready</p>
                <p className="text-sm text-gray-500">FE Solver</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">Ready</p>
                <p className="text-sm text-gray-500">CFD Solver</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Features Overview */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-800 mb-2">Topology Optimization</h3>
          <p className="text-sm text-gray-600">
            SIMP and level-set methods for multi-objective optimization with
            structural, aero, and manufacturing constraints.
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-800 mb-2">FE & CFD Analysis</h3>
          <p className="text-sm text-gray-600">
            Integrated static, modal, impact FE analysis and RANS CFD for
            external aero and cooling flow validation.
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold text-gray-800 mb-2">Manufacturing Export</h3>
          <p className="text-sm text-gray-600">
            STEP/IGES/STL CAD export, layup schedules, fastener maps, BOM,
            and technical validation reports.
          </p>
        </div>
      </div>
    </div>
  )
}
