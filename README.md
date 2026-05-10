# CHA Document Auto-Fill App

A Python desktop application for Customs House Agents (CHA) to eliminate repetitive manual data entry across Microsoft Word (.docx) and Excel (.xlsx) documents. The app allows users to define reusable "variables" (presets) from recurring values (e.g., B/L No., GSTIN, Shipping Line, Consignee, etc.) and auto-populate them across multiple document templates with a single click.

## Features
- **Variable Management**: Create, edit, and organize variables into categories. Keeps a history of recent values.
- **Document Integration**: Link variables to Word and Excel documents.
- **Auto-Detection**: Automatically scan documents for known variable values and suggest linking.
- **One-Click Apply**: Update multiple linked placeholders across Word/Excel documents instantly.

## Tech Stack
- Python 3.10+
- PyQt6 (GUI Framework)
- python-docx (Word processing)
- openpyxl (Excel processing)
- SQLite (Local database)

## Installation

Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

Start the application by running:
```bash
python app/main.py
```

### Workflow
1. **Create Variables**: Use the "+ Add Variable" button to define values like `bl_number` (e.g., "XYZ1321323").
2. **Open Template**: Go to `File > Open Template...` and select a `.docx` or `.xlsx` file.
3. **Link**: The app will auto-detect matching text.
4. **Apply**: Click "Apply Variables & Save" to generate a new document with replaced values.

## Structure
- `/app`: Main application code.
  - `/core`: Database, logic, and Word/Excel handlers.
  - `/ui`: PyQt6 UI components.
  - `/models`: Data classes.
  - `/utils`: Helper functions and constants.
