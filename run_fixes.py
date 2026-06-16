#!/usr/bin/env python3
"""Run both diploma DOCX fixes and presentation generation."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCX_SOURCE = ROOT / "docs" / "Диплом - правки_исправлено_final6.docx"
DOCX_OUTPUT = ROOT / "docs" / "Диплом - правки_исправлено_final6.docx"

print("=" * 60)
print("STEP 1: Normalize diploma lists and formatting")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "scripts/fix_diploma_docx.py", str(DOCX_SOURCE), str(DOCX_OUTPUT), str(ROOT)],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
if result.returncode != 0:
    print(f"❌ fix_diploma_docx.py failed with code {result.returncode}")
    sys.exit(1)
else:
    print("✓ Diploma formatting complete")

print()
print("=" * 60)
print("STEP 2: Generate presentation from updated diploma")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "scripts/generate_presentation_pptx.py"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
if result.returncode != 0:
    print(f"❌ generate_presentation_pptx.py failed with code {result.returncode}")
    sys.exit(1)
else:
    print("✓ Presentation generation complete")

print()
print("=" * 60)
print("✓ ALL DONE! Results:")
print("=" * 60)
print(f"✓ Diploma: {DOCX_OUTPUT}")
print(f"✓ Presentation: {ROOT / 'docs' / 'Презентация_к_курсовой.pptx'}")
