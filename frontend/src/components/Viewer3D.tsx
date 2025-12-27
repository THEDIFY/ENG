import { useRef, useState, useEffect, Suspense, Component, ErrorInfo, ReactNode } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Environment, PerspectiveCamera, useGLTF, Center } from '@react-three/drei'
import * as THREE from 'three'

interface ViewerProps {
  geometry?: any
  densityField?: number[]
  modelUrl?: string
  showGrid?: boolean
  showAxes?: boolean
  autoRotate?: boolean
  onModelLoad?: () => void
  onModelError?: (error: Error) => void
}

function ChassisPreview({ autoRotate = false }: { autoRotate?: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const groupRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.3
    }
  })

  // Create a simple box geometry as placeholder for chassis
  return (
    <group ref={groupRef}>
      {/* Main chassis body */}
      <mesh ref={meshRef} position={[0, 0.5, 0]}>
        <boxGeometry args={[3, 0.5, 1.5]} />
        <meshStandardMaterial color="#333" metalness={0.8} roughness={0.2} />
      </mesh>

      {/* Roll cage representation */}
      <mesh position={[0, 1.2, 0]}>
        <boxGeometry args={[1.5, 0.8, 1.2]} />
        <meshStandardMaterial color="#222" wireframe metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Wheels (placeholders) */}
      {[
        [-1.2, 0, 0.7],
        [-1.2, 0, -0.7],
        [1.2, 0, 0.7],
        [1.2, 0, -0.7],
      ].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]}>
          <cylinderGeometry args={[0.4, 0.4, 0.3, 32]} />
          <meshStandardMaterial color="#111" />
        </mesh>
      ))}

      {/* Suspension arms (simplified) */}
      {[
        [-1.2, 0.3, 0.5],
        [-1.2, 0.3, -0.5],
        [1.2, 0.3, 0.5],
        [1.2, 0.3, -0.5],
      ].map((pos, i) => (
        <mesh key={`arm-${i}`} position={pos as [number, number, number]}>
          <boxGeometry args={[0.1, 0.05, 0.4]} />
          <meshStandardMaterial color="#444" metalness={0.7} roughness={0.3} />
        </mesh>
      ))}
    </group>
  )
}

function DensityFieldVisualization({ densityField }: { densityField: number[] }) {
  const gridSize = Math.cbrt(densityField.length)
  const threshold = 0.5

  return (
    <group>
      {densityField.map((density, i) => {
        if (density < threshold) return null
        
        const x = (i % gridSize) - gridSize / 2
        const y = Math.floor((i / gridSize) % gridSize) - gridSize / 2
        const z = Math.floor(i / (gridSize * gridSize)) - gridSize / 2
        
        return (
          <mesh key={i} position={[x * 0.1, y * 0.1, z * 0.1]}>
            <boxGeometry args={[0.08, 0.08, 0.08]} />
            <meshStandardMaterial
              color={new THREE.Color().setHSL(0.6 * density, 0.8, 0.5)}
              opacity={density}
              transparent
            />
          </mesh>
        )
      })}
    </group>
  )
}

// Component to load and display GLTF model
// Using useGLTF with React Suspense for proper error handling
function GLTFModelInner({ 
  url, 
  autoRotate = false, 
}: { 
  url: string
  autoRotate?: boolean
}) {
  const groupRef = useRef<THREE.Group>(null)
  const gltf = useGLTF(url)

  useFrame((state) => {
    if (groupRef.current && autoRotate) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.3
    }
  })

  return (
    <Center>
      <group ref={groupRef}>
        <primitive object={gltf.scene.clone()} scale={0.5} />
      </group>
    </Center>
  )
}

// Error boundary fallback component
function GLTFErrorFallback({ autoRotate = false }: { autoRotate?: boolean }) {
  return <ChassisPreview autoRotate={autoRotate} />
}

// Wrapper component with error boundary behavior
function GLTFModel({ 
  url, 
  autoRotate = false, 
  onLoad, 
  onError 
}: { 
  url: string
  autoRotate?: boolean
  onLoad?: () => void
  onError?: (error: Error) => void
}) {
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    // Reset error state when URL changes
    setHasError(false)
  }, [url])

  // Notify parent when component mounts successfully
  useEffect(() => {
    if (!hasError) {
      // Small delay to allow GLTF to load via Suspense
      const timer = setTimeout(() => {
        onLoad?.()
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [hasError, onLoad])

  if (hasError) {
    return <GLTFErrorFallback autoRotate={autoRotate} />
  }

  // Wrapped in ErrorBoundary-like logic using Suspense error handling
  return (
    <ErrorBoundaryGLTF onError={(e: Error) => { setHasError(true); onError?.(e) }}>
      <GLTFModelInner url={url} autoRotate={autoRotate} />
    </ErrorBoundaryGLTF>
  )
}

// Simple error boundary for GLTF loading
interface ErrorBoundaryProps {
  children: ReactNode
  onError?: (error: Error) => void
}

interface ErrorBoundaryState {
  hasError: boolean
}

class ErrorBoundaryGLTF extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(_: Error): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('GLTF loading error:', error, errorInfo)
    this.props.onError?.(error)
  }

  render() {
    if (this.state.hasError) {
      return null
    }
    return this.props.children
  }
}

// Loading placeholder
function LoadingPlaceholder() {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime()
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#666" wireframe />
    </mesh>
  )
}

export default function Viewer3D({
  geometry: _geometry,
  densityField,
  modelUrl,
  showGrid = true,
  showAxes = true,
  autoRotate = false,
  onModelLoad,
  onModelError,
}: ViewerProps) {
  const [cameraPosition] = useState<[number, number, number]>([5, 5, 5])
  const [isAutoRotating, setIsAutoRotating] = useState(autoRotate)
  const [modelLoaded, setModelLoaded] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  const handleModelLoad = () => {
    setModelLoaded(true)
    setLoadError(null)
    onModelLoad?.()
  }

  const handleModelError = (error: Error) => {
    setLoadError(error.message)
    onModelError?.(error)
  }

  // Determine what to render
  const renderContent = () => {
    // Priority 1: GLTF model URL
    if (modelUrl) {
      return (
        <Suspense fallback={<LoadingPlaceholder />}>
          <GLTFModel 
            url={modelUrl} 
            autoRotate={isAutoRotating}
            onLoad={handleModelLoad}
            onError={handleModelError}
          />
        </Suspense>
      )
    }
    
    // Priority 2: Density field visualization
    if (densityField && densityField.length > 0) {
      return <DensityFieldVisualization densityField={densityField} />
    }
    
    // Priority 3: Sample chassis preview
    return <ChassisPreview autoRotate={isAutoRotating} />
  }

  return (
    <div className="w-full h-full bg-secondary-900 rounded-lg overflow-hidden relative">
      <Canvas shadows>
        <PerspectiveCamera makeDefault position={cameraPosition} fov={50} />
        <OrbitControls enableDamping dampingFactor={0.05} />
        
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize={[2048, 2048]}
        />
        <directionalLight position={[-10, 10, -5]} intensity={0.5} />
        
        {/* Environment */}
        <Environment preset="warehouse" />
        
        {/* Grid */}
        {showGrid && (
          <Grid
            args={[20, 20]}
            cellSize={0.5}
            cellThickness={0.5}
            cellColor="#444"
            sectionSize={2}
            sectionThickness={1}
            sectionColor="#666"
            fadeDistance={30}
            fadeStrength={1}
            followCamera={false}
            infiniteGrid
          />
        )}
        
        {/* Axes helper */}
        {showAxes && <axesHelper args={[2]} />}
        
        {/* Content */}
        {renderContent()}
      </Canvas>
      
      {/* Model status indicator */}
      {modelUrl && (
        <div className="absolute top-4 right-4 text-xs">
          {modelLoaded ? (
            <span className="bg-green-600 text-white px-2 py-1 rounded">
              ✓ Optimized Model Loaded
            </span>
          ) : loadError ? (
            <span className="bg-red-600 text-white px-2 py-1 rounded">
              ✗ Load Error
            </span>
          ) : (
            <span className="bg-blue-600 text-white px-2 py-1 rounded animate-pulse">
              Loading model...
            </span>
          )}
        </div>
      )}
      
      {/* Sample indicator when no project model */}
      {!modelUrl && !densityField && (
        <div className="absolute top-4 right-4 text-xs">
          <span className="bg-gray-600 text-white px-2 py-1 rounded">
            Sample Preview
          </span>
        </div>
      )}
      
      {/* Controls overlay */}
      <div className="absolute bottom-4 left-4 text-white text-xs bg-black/50 px-3 py-2 rounded space-y-1">
        <p>Left-click: Rotate | Right-click: Pan | Scroll: Zoom</p>
        <button
          onClick={() => setIsAutoRotating(!isAutoRotating)}
          className={`mt-1 px-2 py-1 rounded text-xs ${isAutoRotating ? 'bg-green-600' : 'bg-gray-600'} hover:opacity-80`}
        >
          {isAutoRotating ? '⏸ Stop Rotation' : '▶ Auto Rotate'}
        </button>
      </div>
    </div>
  )
}
