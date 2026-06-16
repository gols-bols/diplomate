#!/usr/bin/env python3
import sys
from pathlib import Path

p = Path("test.txt")
p.write_text("Hello from Python\nPython version: " + sys.version)
print("Done")
