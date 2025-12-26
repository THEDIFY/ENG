import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { rulesApi } from '../api/rules'

interface Rule {
  id: string
  name: string
  description: string
  type: string
  requirements?: Record<string, any>
  value?: number
  unit?: string
}

interface Category {
  name: string
  description: string
  rules: Rule[]
}

export default function RulesEditor() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [customConstraints, setCustomConstraints] = useState<any[]>([])

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
              <h2 className="font-semibold text-lg mb-4">{selectedCategory}</h2>
              <div className="space-y-4">
                {categories
                  .find((c) => c.name === selectedCategory)
                  ?.rules.map((rule) => (
                    <div key={rule.id} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-800">{rule.name}</p>
                          <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                        </div>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                          {rule.type}
                        </span>
                      </div>
                      
                      {rule.value && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-sm">
                            <span className="text-gray-500">Value: </span>
                            <span className="font-medium">{rule.value} {rule.unit}</span>
                          </p>
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
    </div>
  )
}
