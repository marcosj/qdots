from pathlib import Path

# --- CORE DIRECTORY PATHS ---
# Anchors securely to the repository root directory
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent

# Output target boundaries
OUT_DIR = ROOT_DIR / "out"
CSV_DIR = OUT_DIR / "csv"
PNG_DIR = OUT_DIR / "png"

# Documentation resources
DOC_DIR = ROOT_DIR / "doc"
IMG_DIR = DOC_DIR / "img"

# Automatically ensure directories exist safely upon first import
for directory in [CSV_DIR, PNG_DIR, IMG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- QUANTUM SIMULATION CONFIGURATIONS (Optional) ---
# Centralize global variables/hyperparameters here instead of coding them blindly
DEFAULT_SHOTS = 2048
QUANTUM_DOT_DECOHERENCE_RATE = 1e-4
