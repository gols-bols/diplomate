#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

# Write all output to a single file
with open(ROOT / "process.log", "w", encoding="utf-8") as log:
    log.write("Starting diploma and presentation fixes...\n\n")
    
    # Step 1: Fix DOCX
    log.write("=" * 70 + "\n")
    log.write("STEP 1: Fixing diploma DOCX lists and formatting\n")
    log.write("=" * 70 + "\n")
    
    docx_path = ROOT / "docs" / "Диплом - правки_исправлено_final6.docx"
    cmd1 = [sys.executable, str(ROOT / "scripts" / "fix_diploma_docx.py"), 
            str(docx_path), str(docx_path), str(ROOT)]
    
    log.write(f"Command: {' '.join(cmd1)}\n\n")
    result = subprocess.run(cmd1, capture_output=True, text=True)
    log.write(f"Return code: {result.returncode}\n")
    log.write(f"STDOUT:\n{result.stdout}\n")
    if result.stderr:
        log.write(f"STDERR:\n{result.stderr}\n")
    
    # Step 2: Generate presentation
    log.write("\n" + "=" * 70 + "\n")
    log.write("STEP 2: Generating presentation\n")
    log.write("=" * 70 + "\n")
    
    cmd2 = [sys.executable, str(ROOT / "scripts" / "generate_presentation_pptx.py")]
    log.write(f"Command: {' '.join(cmd2)}\n\n")
    result = subprocess.run(cmd2, cwd=ROOT, capture_output=True, text=True)
    log.write(f"Return code: {result.returncode}\n")
    log.write(f"STDOUT:\n{result.stdout}\n")
    if result.stderr:
        log.write(f"STDERR:\n{result.stderr}\n")
    
    # Summary
    log.write("\n" + "=" * 70 + "\n")
    log.write("FINAL RESULTS\n")
    log.write("=" * 70 + "\n")
    docx_path.exists() and log.write(f"✓ Diploma file exists: {docx_path}\n")
    pptx_path = ROOT / "docs" / "Презентация_к_курсовой.pptx"
    pptx_path.exists() and log.write(f"✓ Presentation file exists: {pptx_path}\n")

print("Process log written to: process.log")
