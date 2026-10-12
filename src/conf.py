from pathlib import Path

# --- CORE DIRECTORY PATHS ---
# Anchors securely to the repository root directory
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent

# Output target boundaries
OUT_DIR = ROOT_DIR / "out"
CSV_DIR = OUT_DIR / "csv"
PNG_DIR = OUT_DIR / "png"
TMP_DIR = OUT_DIR / "tmp"

# Documentation resources
DOC_DIR = ROOT_DIR / "docs"
IMG_DIR = DOC_DIR / "img"

# Automatically ensure directories exist safely upon first import
for directory in [IMG_DIR, CSV_DIR, PNG_DIR, TMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- QUANTUM SIMULATION CONFIGURATIONS (Optional) ---
# Centralize global variables/hyperparameters here instead of coding them blindly
DEFAULT_SHOTS = 2048
QUANTUM_DOT_DECOHERENCE_RATE = 1e-4

# Loss–DiVincenzo (LD) qubit
ld = {
    't2': 21e-6, 't2q': 40e-9, 'tr': 24e-6,
    'p1q': 4e-4, 'p2q': 2e-3, 'pr': 2.4e-3, 'pp': 6.5e-3
} # dq
# Singlet–triplet (ST) qubit
st = {
    't2': 14.8e-6, 't2q': 40e-9, 'tr': 2.4e-6,
    'p1q': 4e-3, 'p2q': 4e-3, 'pr': 4e-4, 'pp': 4e-3
} # aq
