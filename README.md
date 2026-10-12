# Quantum error correcting codes tailored to biased quantum dot noise

A Python-based simulation framework for analyzing thresholds and fidelities across various quantum error-correcting codes (Surface, Bacon-Shor, XZZX, and Clifford deformed Bacon-Shor codes) under code capacity, circuit-level, and real quantum dot noise models.

## Repository Structure

```text
.
├── README.md           # This file
├── requirements.txt    # Third-party dependencies
├── Makefile            # Automation commands (e.g., make run)
├── docs/               # Project documentation and github pages
└── src/                # Source code
    ├── main.py         # Application entry point
    ├── conf.py         # Simulation parameters and configuration
    ├── gen/            # Code layout generators
    ├── noi/            # Noise modeling and error insertion
    ├── sim/            # Simulation execution engine
    └── viz/            # Visualization and plotting scripts
```

## Installation

Ensure you have all the required third-party dependencies installed:

```bash
pip install -r requirements.txt
```

*Note: Execution through the `Makefile` automatically handles setting up your environment paths so the internal modules (`conf`, `gen`, `noi`, `sim`, `viz`) are discoverable.*

## Usage

The main execution script runs specific simulation configurations by passing a key identifier as an argument via the wrapper `Makefile`.

### Running a Simulation
To run a single simulation configuration, execute `make run` followed by the configuration key name:

```bash
make run <config_key>
```

For example, to run the Surface Code circuit level threshold simulation:
```bash
make run sczth
```

### Available Configuration Keys

| Key | Code Family | Type | Description |
| :--- | :--- | :--- | :--- |
| **`sczth`** / **`sczfi`** | Surface Code | Circuit Level | Threshold or Fidelity simulations |
| **`bszth`** / **`bszfi`** | Bacon-Shor | Circuit Level | Threshold or Fidelity simulations |
| **`scz0`** to **`scz100`** | Surface Code | Code Capacity | Sweep across different bias values (η) |
| **`scx0`** to **`scx100`** | Surface Code (memX) | Code Capacity | Sweep across different bias values (η) |
| **`xzz0`** to **`xzz30`** | XZZX Code | Code Capacity | Sweep across different bias values (η) |
| **`xzx0`** to **`xzx100`** | XZZX Code | Code Capacity | Sweep across different bias values (η) |
| **`bsz0`** to **`bsz100`** | Bacon-Shor | Code Capacity | Sweep across different bias values (η) |
| **`xzzth`** / **`xzzfi`** | XZZX Code | Real Noise | Threshold or Fidelity with real noise params |
| **`zxzth`** / **`zxzfi`** | XZZX Bacon-Shor | Real Noise | Threshold or Fidelity with real noise params |

## Output
Data and plots are automatically generated and saved to the directories configured in your environment (`CSV_DIR` and `PNG_DIR`), using unique identifiers defined by each configuration's `fname` parameter.
