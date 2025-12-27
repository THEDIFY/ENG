# ============================================================================
# EDIFY Engineering Platform - Startup Script
# ============================================================================
# 
# 🏗️ Trophy Truck Topology Optimization Platform
# Complete Feature Summary
#
# 🎯 Core Features (Always Available)
# ┌────────────────────────────────────────────────────────────────────────┐
# │ Feature              │ Description                                     │
# ├────────────────────────────────────────────────────────────────────────┤
# │ Topology Optimization│ SIMP and level-set optimization algorithms      │
# │ FE Analysis          │ Static, modal, impact analysis                  │
# │ CFD Analysis         │ Aerodynamic simulation and drag analysis        │
# │ Material Library     │ Manage composite materials and properties       │
# │ Rule Parser          │ Parse Baja 1000 racing rules and constraints    │
# │ Manufacturing Check  │ Validate designs for manufacturability          │
# │ CAD Export           │ Generate STEP/IGES geometry files              │
# │ Report Generation    │ PDF technical reports with analysis results     │
# └────────────────────────────────────────────────────────────────────────┘
#
# 📦 Optional Features (Feature Flags)
# ┌────────────────────────────────────────────────────────────────────────┐
# │ Feature              │ Flag                │ Description               │
# ├────────────────────────────────────────────────────────────────────────┤
# │ Database Storage     │ DATABASE_URL        │ PostgreSQL for projects   │
# │ Redis Cache          │ REDIS_URL           │ Caching & task queue      │
# │ Celery Workers       │ CELERY_BROKER_URL   │ Background optimization   │
# │ S3 Storage           │ S3_BUCKET           │ Cloud storage for results │
# │ Advanced FE          │ FE_SOLVER           │ Fenics/Calculix solvers   │
# └────────────────────────────────────────────────────────────────────────┘
#
# 🏗️ Infrastructure
# • Backend: FastAPI + SQLAlchemy + AsyncPG (Port 8000)
# • Frontend: React + TypeScript + Vite + TailwindCSS (Served from /static)
# • 3D Viewer: Three.js with BVH optimization
# • Optimization: NumPy + SciPy + SymPy
# • Visualization: Trimesh + STL export
# • Deployment: Single-port production build
#
# ============================================================================

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  🏁 EDIFY Engineering Platform - Trophy Truck Optimizer" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from correct directory
if (-not (Test-Path ".\backend\app\main.py") -or -not (Test-Path ".\frontend\package.json")) {
    Write-Host "❌ Error: Please run this script from the ENG project root directory" -ForegroundColor Red
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
    return $connection
}

# Function to kill process on port
function Stop-PortProcess {
    param([int]$Port)
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
    if ($process) {
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
}

Write-Host "🔍 Pre-flight checks..." -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "  ✓ Checking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    Write-Host " $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Python not found" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "  ✓ Checking Node.js..." -NoNewline
try {
    $nodeVersion = node --version 2>&1
    Write-Host " $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Node.js not found" -ForegroundColor Red
    exit 1
}

# Check if ports are available
Write-Host ""
Write-Host "🔌 Checking port..." -ForegroundColor Cyan

if (Test-Port -Port 8000) {
    Write-Host "  ⚠️  Port 8000 is in use. Attempting to free..." -ForegroundColor Yellow
    Stop-PortProcess -Port 8000
}

Write-Host "  ✓ Port 8000 is available" -ForegroundColor Green
Write-Host ""

# Setup Backend
Write-Host "🔧 Setting up Backend..." -ForegroundColor Cyan

if (-not (Test-Path ".\backend\venv")) {
    Write-Host "  📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .\backend\venv
}

Write-Host "  📦 Installing backend dependencies..." -ForegroundColor Yellow
Push-Location .\backend

# Activate venv and install dependencies
& .\venv\Scripts\Activate.ps1
if (-not (Test-Path "requirements-base.txt")) {
    Write-Host "  ⚠️  requirements-base.txt not found, using requirements.txt" -ForegroundColor Yellow
    pip install -q -r requirements.txt
} else {
    pip install -q -r requirements-base.txt
}

Write-Host "  ✓ Backend dependencies installed" -ForegroundColor Green
Pop-Location
Write-Host ""

# Setup Frontend
Write-Host "🎨 Building Frontend..." -ForegroundColor Cyan
Push-Location .\frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "  📦 Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "  🔨 Building production bundle..." -ForegroundColor Yellow
$buildOutput = npm run build 2>&1
$buildExitCode = $LASTEXITCODE

if ($buildExitCode -ne 0) {
    Write-Host "  ⚠️  Build had warnings/errors:" -ForegroundColor Yellow
    Write-Host $buildOutput -ForegroundColor Gray
}

if (Test-Path "dist") {
    Write-Host "  📂 Copying build to backend/static..." -ForegroundColor Yellow
    
    # Remove old static files
    if (Test-Path "..\backend\static") {
        Remove-Item -Path "..\backend\static" -Recurse -Force
    }
    
    # Copy new build
    Copy-Item -Path "dist" -Destination "..\backend\static" -Recurse -Force
    Write-Host "  ✓ Frontend built and deployed to /static" -ForegroundColor Green
} else {
    Write-Host "  ❌ Build failed - dist directory not found" -ForegroundColor Red
    Write-Host "  Build output:" -ForegroundColor Yellow
    Write-Host $buildOutput
    Pop-Location
    
    Write-Host ""
    Write-Host "  Continuing without frontend build..." -ForegroundColor Yellow
    Write-Host "  API will still be available at http://localhost:8000/api/v1" -ForegroundColor Cyan
    Write-Host ""
}

Pop-Location
Write-Host ""

# Start services
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  🚀 Starting Application Server" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend (serving both API and Frontend)
Write-Host "🔥 Starting Backend Server (FastAPI + Uvicorn)..." -ForegroundColor Cyan
Write-Host "   📍 Application: http://localhost:8000" -ForegroundColor White
Write-Host "   📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   🔌 API Endpoints: http://localhost:8000/api/v1" -ForegroundColor White
Write-Host ""

Start-Sleep -Seconds 2

Push-Location .\backend
& .\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
