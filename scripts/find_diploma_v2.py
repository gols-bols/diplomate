from pathlib import Path

downloads = Path(r"c:\Users\Admin\Downloads")
out = Path(__file__).resolve().parent / "diploma_v2_path.txt"

best = None
for p in downloads.glob("*.docx"):
    if "v2" not in p.name.lower() and "_v2" not in p.name:
        continue
    if best is None or p.stat().st_size > best.stat().st_size:
        best = p

if best is None:
    for p in downloads.glob("*.docx"):
        if "3" in p.name and p.stat().st_size > 400_000:
            if best is None or ("расширен" in p.name or "v2" in p.name):
                if best is None or p.stat().st_size > best.stat().st_size:
                    best = p

out.write_text(str(best.resolve()) if best else "", encoding="utf-8")
