.PHONY: run clean cleanout help test-noi test-sim test-viz

# Default target when you just type 'make'
help:
	@echo "Available commands:"
	@echo "  make run            - Run the main simulation pipeline"
	@echo "  make clean          - Remove Python caching artifacts (__pycache__)"
	@echo "  make cleanout       - Wipe all generated CSVs and PNGs from outputs/"
	@echo "  make test-noi        - Run isolated noise injection tests"
	@echo "  make test-sim        - Run isolated simulation pipeline tests"
	@echo "  make test-viz        - Run isolated visualization utility tests"

# Run the project pipeline
run:
	python src/main.py

# Clean Python compilation bloat
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Wipe generated data to reset simulation runs
cleanout:
	rm -f out/csv/*.csv
	rm -f out/png/*.png

test-noi:
	python -m src.noi.add_noise

test-sim:
	python -m src.sim.sim

test-viz:
	python -m src.viz.viz
