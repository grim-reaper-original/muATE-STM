import re
from pathlib import Path

root = Path('/home/Acharya/Aryan/Projects/ETM/μATE-STM').resolve()
md_files = sorted([p for p in root.rglob('*.md') if '.git' not in p.parts and '.tmp' not in p.parts])

fence_re = re.compile(r'^(```|~~~)')


def normalize_text(text: str) -> str:
    lines = text.splitlines()
    out = []
    in_fence = False

    for line in lines:
        stripped = line.lstrip()
        if fence_re.match(stripped):
            in_fence = not in_fence
            out.append(line)
            continue

        if not in_fence:
            # Convert inline and display LaTeX delimiters.
            text_line = line
            text_line = re.sub(r'\\\((.*?)\\\)', lambda m: '$' + m.group(1).strip() + '$', text_line, flags=re.S)
            text_line = re.sub(r'\\\[(.*?)\\\]', lambda m: '$$\n' + m.group(1).strip() + '\n$$', text_line, flags=re.S)
            line = text_line

        out.append(line)

    text = '\n'.join(out)

    # Normalize display blocks with blank lines before and after.
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == '$$':
            if out and out[-1].strip() != '':
                out.append('')
            out.append('$$')
            i += 1
            while i < len(lines) and lines[i].strip() != '$$':
                out.append(lines[i])
                i += 1
            if i < len(lines):
                out.append('$$')
                i += 1
            else:
                out.append('$$')
            if i < len(lines) and lines[i].strip() != '':
                out.append('')
            continue
        out.append(line)
        i += 1

    text = '\n'.join(out)

    # Ensure one blank line before/after display blocks.
    text = re.sub(r'([^\n])\n\$\$', r'\1\n\n$$', text)
    text = re.sub(r'\$\$\n([^\n])', r'$$\n\n\1', text)

    # Make table math more GitHub-friendly by replacing complex expressions with concise descriptions.
    lines = text.splitlines()
    out = []
    for line in lines:
        if '|' in line and '$' in line:
            line = line.replace('$V = IR$', "Ohm's law")
            line = line.replace('$f_c = 1 / (2\\pi RC)$', 'RC cutoff frequency')
            line = line.replace('$V_{rms} = sqrt(4k_BT R Δf)$', 'Johnson–Nyquist equation')
            line = line.replace('$V_{rms} = \\sqrt{4 k_B T R \\Delta f}$', 'Johnson–Nyquist equation')
            line = line.replace('$H(s)=\\frac{1}{1+sRC}$', 'RC transfer function')
            line = line.replace('$I = V/R$', "Ohm's law")
            if '$' in line and '|' in line:
                line = re.sub(r'\$[^$]+\$', 'equation', line)
        out.append(line)
    text = '\n'.join(out)

    return text


for path in md_files:
    original = path.read_text(encoding='utf-8')
    updated = normalize_text(original)
    if updated != original:
        path.write_text(updated + ('\n' if updated.endswith('\n') else ''), encoding='utf-8')
