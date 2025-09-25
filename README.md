# 🤖 Data Contract Copilot

Your intelligent assistant for automated data contract management and validation using AI and Great Expectations.

## 📖 Overview

Data Contract Copilot is an AI-powered tool that automatically generates, validates, and manages data contracts using Great Expectations. It combines the power of Large Language Models (LLMs) with robust data validation frameworks to streamline data quality management in your data pipelines.

### Key Features

- 🎯 **Automatic Generation**: Create comprehensive data contracts from CSV files and documentation using AI
- ✨ **Intelligent Validation**: Validate datasets against predefined expectations with detailed reporting
- 🔄 **Easy Integration**: Seamlessly integrate with Great Expectations and existing data pipelines
- 📊 **Interactive Web Interface**: User-friendly Streamlit interface for configuration and validation
- 🛠️ **Extensible Framework**: Built with Pydantic models for type safety and extensibility
- 📈 **Rich Reporting**: Detailed validation results with failure analysis and recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key (for AI-powered generation)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/enriquegrodrigo/data-contract-copilot.git
   cd data-contract-copilot
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

4. **Launch the application:**
   ```bash
   poetry run streamlit run Home.py
   ```

## 💻 Usage

### Web Interface

The application provides two main workflows:

#### 1. 🔄 Generate Data Contract

1. Navigate to "Generate Data Contract" in the sidebar
2. Upload your files:
   - **CSV file**: Sample data for analysis
   - **Documentation file**: Business rules and requirements (TXT/MD format)
3. Let the AI generate your data contract automatically
4. Edit and save the generated data contract

#### 2. 📋 Load Data Contract

1. Navigate to "Load Data Contract" in the sidebar
2. Upload your files:
   - **CSV file**: Data to validate
   - **Data contract file**: Existing data contract (YAML/JSON format)
3. Review validation results and analysis

### Python API

You can also use your downloaded data contract easily in your Python projects:

```python
from src.expectation_manager import ExpectationManager

# Load a YAML configuration file
manager = ExpectationManager.from_yaml("path/to/config.yaml")

# Validate a CSV file against the loaded configuration
results = manager.validate("path/to/data.csv")

# Print validation summary
print(results.summary())
```

## 🏗️ Architecture

### Core Components

- **ExpectationManager**: Central manager for Great Expectations integration
- **DataExtractor**: Extracts statistical profiles and metadata from datasets
- **AI Prompt Engine**: Generates intelligent prompts for LLM-based rule creation
- **Pydantic Models**: Type-safe expectation definitions and metadata
- **Streamlit Interface**: Interactive web application for user workflows

### Supported Expectations

The framework supports various Great Expectations rules:

- **Schema Validation**: Column existence, data types
- **Null Checking**: Non-null constraints with configurable thresholds
- **Value Constraints**: Range validation, set membership, regex patterns
- **Uniqueness**: Primary key and unique constraint validation
- **Statistical Validation**: Mean, min, max, sum validations within ranges
- **Row Count Validation**: Table size expectations

## 📁 Project Structure

```
data-contract-copilot/
├── Home.py                     # Main Streamlit application entry point
├── pages/                      # Streamlit pages
│   ├── Generate_Data_Contract.py   # AI-powered data contract generation
│   └── Load_Data_Contract.py       # Data contract loading and validation
├── src/                        # Core library code
│   ├── expectation_manager.py     # Great Expectations integration
│   ├── expectations.py            # Pydantic expectation models
│   ├── gx_data_extractor.py      # Data profiling and analysis
│   ├── gx_promt_utils.py         # LLM prompt generation
│   └── gx_utils.py               # Utility functions
├── data/                       # Sample data and documentation
├── examples/                   # Usage examples and tutorials
├── output/                     # Generated configurations and reports
└── assets/                     # Static assets (logos, images)
```

## 📚 Documentation

- **Great Expectations**: [Official Documentation](https://greatexpectations.io)
- **Pydantic**: [Type Validation Documentation](https://pydantic-docs.helpmanual.io)
- **Streamlit**: [Web App Framework](https://streamlit.io)
- **OpenAI API**: [AI Integration Guide](https://platform.openai.com/docs)

## 🔗 Dependencies

Key dependencies include:

- `great-expectations>=1.6.2`: Data validation framework
- `pydantic>=2.11.9`: Data validation and serialization
- `streamlit>=1.50.0`: Web interface framework
- `openai>=1.108.1`: AI integration
- `instructor>=1.11.3`: Structured LLM outputs
- `pandas>=2.1.4`: Data manipulation
- `duckdb>=1.4.0`: Fast analytical database

See `pyproject.toml` for complete dependency list.


## 👨‍💻 Authors

- **Enrique González Rodrigo**
- **Jesús García Manzanas**

## Disclaimer

This project has been developed in the context of the 2025 Equinox Hackathon organized by Telefonica Digital Innovation on September 25-26, 2025.

---

*Built with ❤️ using [Streamlit](https://streamlit.io) and [Great Expectations](https://greatexpectations.io)*
