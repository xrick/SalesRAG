# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SalesRAG is a Retrieval-Augmented Generation (RAG) system designed as a sales assistant for laptop product specifications querying and comparison. The system combines entity recognition, intent detection, and semantic search to provide intelligent responses about laptop specifications.

## Architecture

### Core Components

1. **FastAPI Application** (`sales_rag_app/main.py`):
   - Main application entry point
   - Handles HTTP requests and streaming responses
   - Manages service initialization and routing

2. **Service Layer** (`sales_rag_app/libs/services/`):
   - `SalesAssistantService` - Core business logic for sales queries
   - `BaseService` - Abstract base class for services
   - Entity recognition and intent detection capabilities

3. **RAG System** (`sales_rag_app/libs/RAG/`):
   - **Database Layer**: `DuckDBQuery` for structured queries, `MilvusQuery` for vector search
   - **LLM Integration**: `LLMInitializer` for language model setup
   - **Content Processing**: Text splitting and embedding utilities

4. **Entity Recognition System**:
   - JSON-based configuration for patterns and keywords
   - Multi-language support (Traditional Chinese, Simplified Chinese, English)
   - Regex-based entity extraction for model names, specifications, and intents

### Database Architecture

- **DuckDB**: Stores structured laptop specification data
- **Milvus**: Vector database for semantic search with embeddings
- **Collection Schema**: 34 specification fields including `modeltype`, `cpu`, `gpu`, `memory`, `storage`, etc.

### Key Configuration Files

- `prompts/sales_prompt4.txt`: Main LLM prompt template
- `prompts/query_keywords.json`: Intent detection keywords for different query types
- `prompts/entity_patterns.json`: Regex patterns for entity recognition

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install as package (development mode)
pip install -e .
```

### Running the Application
```bash
# Start the FastAPI server
python sales_rag_app/main.py

# Alternative with uvicorn directly
uvicorn sales_rag_app.main:app --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python tests/test_entity_recognition.py
python tests/test_keyword_management.py
python tests/test_full_flow.py

# Run with report generation
python run_tests.py --report
```

### Keyword Management
```bash
# Interactive keyword management
python manage_keywords.py
```

## Key Implementation Details

### Entity Recognition Flow
1. Load patterns from `entity_patterns.json`
2. Apply regex matching for model names, types, and specifications
3. Extract entities like `MODEL_NAME`, `MODEL_TYPE`, `SPEC_TYPE`, `COMPARISON_WORD`
4. Map entities to database fields for targeted querying

### Intent Detection
Uses keyword matching from `query_keywords.json` to identify query types:
- `display`, `cpu`, `gpu`, `memory`, `storage`, `battery`
- `portability`, `connectivity`, `comparison`, `specifications`
- `latest` (for current product queries)

### RAG Query Process
1. **Entity Recognition**: Extract model names and specification types
2. **Intent Detection**: Determine query category (CPU, GPU, comparison, etc.)
3. **Vector Search**: Query Milvus for semantically similar products
4. **Structured Query**: Use DuckDB for exact specification matching
5. **Response Generation**: Generate structured responses with tables when appropriate

### Available Models
System supports these laptop model types:
- **819 Series**: Various configurations with different mainboards
- **839 Series**: Mid-range laptop specifications
- **958 Series**: Higher-end laptop configurations

Model names follow pattern: `[A-Z]{2,3}\d{3}(?:-[A-Z]+)?(?:\s*:\s*[A-Z]+\d+[A-Z]*)?`

## Testing Strategy

### Test Categories
- **Core Functionality**: Entity recognition, keyword management, data availability
- **Flow Testing**: End-to-end processing, new flow validation
- **Response Testing**: LLM response handling, table generation
- **Edge Cases**: Invalid models, missing data, format errors

### Critical Test Files
- `test_entity_recognition.py`: Validates entity extraction
- `test_full_flow.py`: Tests complete query processing
- `test_table_generation.py`: Validates output formatting
- `test_production_scenario.py`: Real-world scenario testing

## Configuration Management

### Keyword Configuration
- File: `sales_rag_app/libs/services/sales_assistant/prompts/query_keywords.json`
- Structure: Intent categories with multilingual keywords
- Supports dynamic keyword addition/removal

### Entity Patterns
- File: `sales_rag_app/libs/services/sales_assistant/prompts/entity_patterns.json`
- Contains regex patterns for different entity types
- Supports brand recognition (AMD, Intel, NVIDIA, etc.)

### Database Schema
Specification fields include:
```
modeltype, version, modelname, mainboard, devtime, pm, structconfig, lcd, 
touchpanel, iointerface, ledind, powerbutton, keyboard, webcamera, touchpad, 
fingerprint, audio, battery, cpu, gpu, memory, lcdconnector, storage, wifislot, 
thermal, tpm, rtc, wireless, lan, bluetooth, softwareconfig, ai, accessory, 
certifications, otherfeatures
```

## Important Notes

- System uses HuggingFace embeddings model: `all-MiniLM-L6-v2`
- Database files located in `sales_rag_app/db/`
- Static files and templates in `sales_rag_app/static/` and `sales_rag_app/templates/`
- Supports streaming responses for real-time chat experience
- Multi-language support with regex patterns for Chinese and English queries