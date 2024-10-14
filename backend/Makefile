.PHONY: build run clean

VENV_DIR = venv
REQUIREMENTS = requirements.txt

build:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	. $(VENV_DIR)/bin/activate && pip install --upgrade pip && pip install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully."

run:
	@echo "Starting FastAPI server..."
	. $(VENV_DIR)/bin/activate && uvicorn app.main:app --reload

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
