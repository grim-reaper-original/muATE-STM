import re
import shutil
import subprocess
from pathlib import Path

root = Path('/home/Acharya/Aryan/Projects/ETM/μATE-STM').resolve()
docs_dir = root / 'docs' / 'engineering-design-dossier'
out_dir = root / '.tmp' / 'inline-math'
out_dir.mkdir(parents=True, exist_ok=True)
orig_dir = out_dir / 'before'
mod_dir = out_dir / 'after'
for d in [orig_dir, mod_dir]:
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True, exist_ok=True)

files = sorted(docs_dir.rglob('*.md'))
for path in files:
    rel = path.relative_to(root)
    src = path.read_text(encoding='utf-8')
    lines = src.splitlines()
    out = []
    in_fence = False
    for line in lines:
        stripped = line.lstrip()
        if re.match(r'^(```|~~~)', stripped):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and not re.match(r'^\s*\|', line):
            line = line.replace('\\(', '$').replace('\\)', '$')
        out.append(line)
    new_text = '\n'.join(out) + ('\n' if src.endswith('\n') else '')
    (orig_dir / rel.as_posix()).parent.mkdir(parents=True, exist_ok=True)
    (mod_dir / rel.as_posix()).parent.mkdir(parents=True, exist_ok=True)
    (orig_dir / rel.as_posix()).write_text(src, encoding='utf-8')
    (mod_dir / rel.as_posix()).write_text(new_text, encoding='utf-8')

# Write a unified diff before applying changes.
diff_path = out_dir / 'diff.patch'
with diff_path.open('w', encoding='utf-8') as fh:
    proc = subprocess.run(
        ['git', '-C', str(root), 'diff', '--no-index', '--no-color', '--', str(orig_dir), str(mod_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    fh.write(proc.stdout)
    if proc.stderr:
        fh.write(proc.stderr)

# Apply changes to the repository files.
for path in files:
    src = path.read_text(encoding='utf-8')
    lines = src.splitlines()
    out = []
    in_fence = False
    for line in lines:
        stripped = line.lstrip()
        if re.match(r'^(```|~~~)', stripped):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and not re.match(r'^\s*\|', line):
            line = line.replace('\\(', '$').replace('\\)', '$')
        out.append(line)
    new_text = '\n'.join(out) + ('\n' if src.endswith('\n') else '')
    if new_text != src:
        path.write_text(new_text, encoding='utf-8')

print(diff_path.read_text(encoding='utf-8'))
