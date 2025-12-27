import { useState, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { rulesApi } from '../api/rules'

interface Rule {
  id: string
  name: string
  description: string
  type: string
  requirements?: Record<string, any>
  value?: number
  unit?: string
  min_value?: number
  max_value?: number
}

interface Category {
  name: string
  description: string
  rules: Rule[]
}

interface CustomConstraint {
  name: string
  type: string
  value: number
  unit: string
}

export default function RulesEditor() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [customConstraints, setCustomConstraints] = useState<CustomConstraint[]>([])
  const [editingRule, setEditingRule] = useState<string | null>(null)
  const [editedValues, setEditedValues] = useState<Record<string, number>>({})
  const [showAddConstraint, setShowAddConstraint] = useState(false)
  const [newConstraint, setNewConstraint] = useState<CustomConstraint>({
    name: '',
    type: 'dimensional',
    value: 0,
    unit: 'mm',
  })

  const { data: rulesData, isLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: rulesApi.getAll,
  })

  const { data: parsedRules } = useQuery({
    queryKey: ['parsed-rules', customConstraints],
    queryFn: () => rulesApi.parse({
      rule_set_version: '2024',
      custom_constraints: customConstraints,
    }),
  })

  const categories: Category[] = rulesData?.categories || []

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Baja 1000 Rules Configuration</h1>

      {isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading rules...</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Categories List */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="font-semibold mb-4">Rule Categories</h2>
          <div className="space-y-2">
            {categories.map((category) => (
              <button
                key={category.name}
                onClick={() => setSelectedCategory(category.name)}
                className={`w-full text-left px-4 py-3 rounded-lg transition ${
                  selectedCategory === category.name
                    ? 'bg-primary-100 text-primary-700 border border-primary-200'
                    : 'hover:bg-gray-100'
                }`}
              >
                <p className="font-medium">{category.name}</p>
                <p className="text-xs text-gray-500">{category.rules?.length || 0} rules</p>
              </button>
            ))}
          </div>
        </div>

        {/* Rules Detail */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          {selectedCategory ? (
            <>
              <div className="flex justify-between items-center mb-4">
                <h2 className="font-semibold text-lg">{selectedCategory}</h2>
                <button
                  onClick={() => setShowAddConstraint(true)}
                  className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition"
                >
                  + Add Constraint
                </button>
              </div>
              <div className="space-y-4">
                {categories
                  .find((c) => c.name === selectedCategory)
                  ?.rules.map((rule) => (
                    <div key={rule.id} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium text-gray-800">{rule.name}</p>
                          <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                            {rule.type}
                          </span>
                          {rule.value !== undefined && (
                            <button
                              onClick={() => {
                                setEditingRule(editingRule === rule.id ? null : rule.id)
                                setEditedValues({ ...editedValues, [rule.id]: rule.value || 0 })
                              }}
                              className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded hover:bg-gray-300"
                            >
                              {editingRule === rule.id ? 'Cancel' : 'Edit'}
                            </button>
                          )}
                        </div>
                      </div>
                      
                      {rule.value !== undefined && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          {editingRule === rule.id ? (
                            <div className="flex items-center gap-2">
                              <input
                                type="number"
                                value={editedValues[rule.id] ?? rule.value}
                                onChange={(e) => setEditedValues({ 
                                  ...editedValues, 
                                  [rule.id]: parseFloat(e.target.value) 
                                })}
                                className="w-32 px-2 py-1 border border-gray-300 rounded text-sm"
                                step={rule.unit === 'mm' ? 1 : 0.1}
                              />
                              <span className="text-sm text-gray-500">{rule.unit}</span>
                              <button
                                onClick={() => {
                                  setCustomConstraints([
                                    ...customConstraints.filter(c => c.name !== rule.name),
                                    { name: rule.name, type: rule.type, value: editedValues[rule.id], unit: rule.unit || '' }
                                  ])
                                  setEditingRule(null)
                                }}
                                className="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                              >
                                Save
                              </button>
                            </div>
                          ) : (
                            <p className="text-sm">
                              <span className="text-gray-500">Value: </span>
                              <span className="font-medium">
                                {customConstraints.find(c => c.name === rule.name)?.value ?? rule.value} {rule.unit}
                              </span>
                              {customConstraints.find(c => c.name === rule.name) && (
                                <span className="ml-2 text-xs text-orange-600">(modified)</span>
                              )}
                            </p>
                          )}
                        </div>
                      )}
                      
                      {rule.requirements && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-sm text-gray-500 mb-2">Requirements:</p>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            {Object.entries(rule.requirements).map(([key, value]) => (
                              <div key={key}>
                                <span className="text-gray-500">{key.replace(/_/g, ' ')}: </span>
                                <span className="font-medium">{String(value)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            </>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Select a category to view rules</p>
            </div>
          )}
        </div>
      </div>

      {/* Parsed Constraints Summary */}
      {parsedRules && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold text-lg mb-4">Parsed Constraints Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-700">{parsedRules.total_rules}</p>
              <p className="text-sm text-blue-600">Total Rules</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-700">
                {Object.keys(parsedRules.dimensional_constraints || {}).length}
              </p>
              <p className="text-sm text-green-600">Dimensional Constraints</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-700">
                {parsedRules.safety_requirements?.length || 0}
              </p>
              <p className="text-sm text-orange-600">Safety Requirements</p>
            </div>
          </div>
        </div>
      )}

      {/* Custom Constraints List */}
      {customConstraints.length > 0 && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold text-lg mb-4">Custom Constraints ({customConstraints.length})</h2>
          <div className="space-y-2">
            {customConstraints.map((constraint, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                <div>
                  <span className="font-medium">{constraint.name}</span>
                  <span className="mx-2 text-gray-400">|</span>
                  <span className="text-gray-600">{constraint.value} {constraint.unit}</span>
                </div>
                <button
                  onClick={() => setCustomConstraints(customConstraints.filter((_, i) => i !== index))}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Constraint Modal */}
      {showAddConstraint && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">Add Custom Constraint</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={newConstraint.name}
                  onChange={(e) => setNewConstraint({ ...newConstraint, name: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="e.g., Custom Clearance"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={newConstraint.type}
                  onChange={(e) => setNewConstraint({ ...newConstraint, type: e.target.value })}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="dimensional">Dimensional</option>
                  <option value="structural">Structural</option>
                  <option value="safety">Safety</option>
                  <option value="performance">Performance</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                  <input
                    type="number"
                    value={newConstraint.value}
                    onChange={(e) => setNewConstraint({ ...newConstraint, value: parseFloat(e.target.value) })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                  <select
                    value={newConstraint.unit}
                    onChange={(e) => setNewConstraint({ ...newConstraint, unit: e.target.value })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="mm">mm</option>
                    <option value="kg">kg</option>
                    <option value="kN">kN</option>
                    <option value="MPa">MPa</option>
                    <option value="deg">degrees</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => {
                    setShowAddConstraint(false)
                    setNewConstraint({ name: '', type: 'dimensional', value: 0, unit: 'mm' })
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    if (newConstraint.name) {
                      setCustomConstraints([...customConstraints, newConstraint])
                      setShowAddConstraint(false)
                      setNewConstraint({ name: '', type: 'dimensional', value: 0, unit: 'mm' })
                    }
                  }}
                  disabled={!newConstraint.name}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  Add Constraint
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
