import os

def create_project_structure():
    # Define the base directory
    base_dir = "pathogen_simulation"
    
    # Create base directory
    os.makedirs(base_dir, exist_ok=True)
    
    # Define the directory structure
    directories = [
        "data",
        "models",
        "visualizations",
        "utils"
    ]
    
    # Create directories and their __init__.py files
    for dir_name in directories:
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        # Create __init__.py
        with open(os.path.join(dir_path, "__init__.py"), 'w') as f:
            f.write("# Initialize package")
    
    # Define files to create
    files = {
        "main.py": "# Main application entry point\n",
        "data/country_data.py": "# Country statistics and indices\n",
        "data/disease_params.py": "# Disease parameters handling\n",
        "models/seir_model.py": "# SEIR epidemiological calculations\n",
        "models/risk_calculator.py": "# Risk assessment calculations\n",
        "models/variant_tracker.py": "# Variant tracking calculations\n",
        "visualizations/infection_progress.py": "# Infection progression visualization\n",
        "visualizations/world_heatmap.py": "# World heatmap visualization\n",
        "visualizations/population_health.py": "# Population health visualization\n",
        "visualizations/healthcare_load.py": "# Healthcare system visualization\n",
        "visualizations/variant_analysis.py": "# Variant analysis visualization\n",
        "utils/data_processor.py": "# Data processing utilities\n",
        "utils/validators.py": "# Input validation functions\n",
        "requirements.txt": "pandas\nnumpy\nplotly\nstreamlit\ngeopandas\n"
    }
    
    # Create all files
    for file_path, content in files.items():
        full_path = os.path.join(base_dir, file_path)
        with open(full_path, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    create_project_structure()
    print("Project structure created successfully!")
