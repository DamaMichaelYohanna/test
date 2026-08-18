import os
import glob
import re

def fix_content(content):
    # Fix {{ \n var }}
    def clean_var(match):
        inner = match.group(1)
        inner_clean = ' '.join(inner.split())
        return f"{{{{ {inner_clean} }}}}"

    # Fix {% \n tag %}
    def clean_block(match):
        inner = match.group(1)
        inner_clean = ' '.join(inner.split())
        return f"{{% {inner_clean} %}}"

    # Match {{ followed by newlines/spaces
    c1 = re.sub(r'\{\{[\s\n]+(.*?)\}\}', clean_var, content, flags=re.DOTALL)
    # Match {% followed by newlines/spaces
    c2 = re.sub(r'\{\%[\s\n]+(.*?)\%\}', clean_block, c1, flags=re.DOTALL)
    return c2

def main():
    files = glob.glob('templates/**/*.html', recursive=True)
    count = 0
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
        fixed = fix_content(original)
        if fixed != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed)
            count += 1
            print(f"Fixed template: {os.path.relpath(file_path, 'templates')}", flush=True)

    print(f"\nDone! Fixed split template tags in {count} HTML templates.", flush=True)

if __name__ == '__main__':
    main()
