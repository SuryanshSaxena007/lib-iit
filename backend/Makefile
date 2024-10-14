# Makefile for setting up virtual environment, installing dependencies, and running FastAPI server

.PHONY: build run clean

# Variables
VENV_DIR = venv
REQUIREMENTS = requirements.txt

# Step 1: Create a virtual environment and install dependencies
build:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "Activating virtual environment and installing dependencies..."
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully."

# Step 2: Run the FastAPI server
run:
	@echo "Starting FastAPI server..."
	. $(VENV_DIR)/bin/activate && uvicorn app.main:app --reload

# Optional: Clean up the virtual environment
clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed."
