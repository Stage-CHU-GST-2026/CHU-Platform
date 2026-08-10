# Testing Strategy & Execution Guide - CHU-Platform

This document outlines the test suite structure, unit test files, integration test strategies, and instructions for running tests.

---

## 1. Test Suite Structure

Test scripts are located at the repository root and within component subdirectories:

```
/home/regisx001/CHU-Platform/
├── test_bound.py              # Boundary & dataset limit test script
├── test_tool_node.py          # Agent tool node unit tests
├── test_tool_error.py         # Tool exception recovery test suite
└── example.py                 # Standalone workflow demo script
```

---

## 2. Test Descriptions

### 2.1 Tool Execution Tests (`test_tool_node.py`)
Tests `packages/agents/data_analyst/nodes.py` to ensure tool calls correctly invoke registered functions and return formatted outputs.

### 2.2 Error Recovery Tests (`test_tool_error.py`)
Validates that SQL execution errors and missing file scenarios yield appropriate error objects without crashing the process.

### 2.3 Boundary Tests (`test_bound.py`)
Verifies DuckDB query row limit bounds (`LIMIT 500`) and dataset size threshold handling.

---

## 3. Running Tests

Using `uv` workspace environment:

```bash
# Run root pytest suite
uv run pytest

# Run specific test file with verbose output
uv run pytest test_tool_node.py -v

# Run backend API unit tests
cd apps/api
uv run pytest
```
