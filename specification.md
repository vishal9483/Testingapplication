🧩 Batch Testing Utility – Application Specification
📌 Purpose
A Python-based desktop application to perform batch testing across three test modules. It allows selection of folders containing structured data and outputs results with logs and summaries. Designed for non-technical users, the application will be packaged as a standalone .exe file.

💻 Platform Requirements
Developed in Python

Must be packaged into a Windows-compatible .exe

Using PyInstaller or cx_Freeze

Should not require Python pre-installed on the user’s system

All dependencies must be bundled

📂 Folder Structure & Data Flow
Input Folder (global at the top):

Selected once before any run.

Contains structured subfolders with batch files.

Used for comparison and validation across all modules.

Output Folder:

Selected by the user.

Will mirror the input folder’s subfolder structure.

All generated outputs (Excel, logs, visualizations, etc.) are stored here.

Will serve as the input for the next stage run (multi-stage chaining supported).

A button is provided to directly open the Output Folder in the system file explorer.

🧪 Module-wise Batch Testing
Each module consists of:

A label indicating the module name:

Test Data Extraction

Test JSON Output (Windows DLL)

Test JSON Output (Linux DLL)

Test Automatic Drawing

A "Browse" button to select the folder containing input data (for the specific module).

A "Run" button to trigger the test for that module only.

All modules process multiple files in batch, operating recursively over the selected subfolders.

▶️ Run All Button
Executes all selected modules in order.

Skips modules where folders are not selected.

Applies input/output structure rules consistently.

📊 Run Status Panel
Displays live, detailed feedback during testing:

✅ Current Module Name in progress

📄 Currently Processed File Name

📈 Progress Status (e.g., "23 of 100 files processed")

❌ Failure Summary (e.g., "3 failed out of 23")

📄 Summary and Logs
At the end of the run:

A short summary is shown in the UI

A detailed summary log is written to a file in the Output Folder (CSV or TXT)

Log includes file names, module names, success/failure flags, failure reasons

📤 Outputs
Module-specific results (e.g., generated Excel, JSON diffs, visualizations)

A detailed run summary file

All files are stored in the Output Folder, maintaining the same subfolder structure as the Input Folder

📎 Additional Requirements
Application should be robust to missing or malformed files

Logs all exceptions with tracebacks where needed

UI should remain responsive during long runs (consider background threads)

Optionally add timestamps to all logs and output folders
