#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

# ---------- CONFIG ----------
html_path = "index.html"
css_dir = "."               # walk this dir for .css files
images_dir = "images"
extras_dir = os.path.join(images_dir, "extra")
dry_run = False          # set to False to actually move files

# ---------- HELPERS ----------
def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""

def norm(name):
    """Normalize filenames for case-insensitive comparison."""
    return name.strip().lower()

# ---------- COLLECT HTML CLASSES ----------
html = read_text(html_path)
# capture class="one two" and class='one two'
class_matches = re.findall(r'class\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
html_classes = set()
for group in class_matches:
    for cls in group.split():
        html_classes.add(cls.strip())
print(f"HTML classes found ({len(html_classes)}): {sorted(list(html_classes))}")

# ---------- COLLECT CSS -> class->image mappings ----------
css_text = ""
for root, _, files in os.walk(css_dir):
    for f in files:
        if f.lower().endswith(".css"):
            path = os.path.join(root, f)
            css_text += "\n/* from: " + path + " */\n" + read_text(path)

# find selector blocks: "selector1, selector2 { ... }"
rule_pattern = re.compile(r'([^{}]+)\{([^}]*)\}', re.MULTILINE | re.DOTALL)
url_pattern = re.compile(
    r'url\(\s*["\']?(?:\.\./|\.\/)?' + re.escape(images_dir) + r'/([^"\')]+)["\']?\s*\)',
    re.IGNORECASE
)
class_pattern = re.compile(r'\.([A-Za-z0-9_-]+)')

class_to_images = {}  # class -> set(images)
for rule_match in rule_pattern.finditer(css_text):
    selector_text = rule_match.group(1)  # e.g. ".a, .b:hover"
    body = rule_match.group(2)

    # get all images referenced in this rule body
    urls = url_pattern.findall(body)
    if not urls:
        continue

    # get classes mentioned in selectors
    selectors = [s.strip() for s in selector_text.split(',')]
    classes = set()
    for sel in selectors:
        for cls in class_pattern.findall(sel):
            classes.add(cls)

    if not classes:
        # no class selector in this rule: could be tag/ID/complex selector; skip
        continue

    for cls in classes:
        class_to_images.setdefault(cls, set()).update(urls)

print(f"CSS classes with image references ({len(class_to_images)}):")
for cls, imgs in class_to_images.items():
    print(f"  .{cls}: {imgs}")

# ---------- Determine images used (by HTML img tags and by CSS classes present in HTML) ----------
# images referenced directly in HTML <img src="images/foo.png">
html_img_pattern = re.compile(r'src\s*=\s*["\'](?:\.\./|\.\/)?' + re.escape(images_dir) + r'/([^"\']+)', re.IGNORECASE)
html_img_refs = set(html_img_pattern.findall(html))
print(f"Images referenced directly in HTML ({len(html_img_refs)}): {sorted(html_img_refs)}")

# images referenced by CSS but only keep those where the class exists in HTML
used_from_css = set()
for cls, imgs in class_to_images.items():
    if cls in html_classes:
        used_from_css.update(imgs)
    else:
        # debugging message
        print(f"Skipping .{cls} (not in HTML) -> images {imgs}")

print(f"Images referenced by CSS for classes present in HTML ({len(used_from_css)}): {sorted(used_from_css)}")

# combined set (normalized)
used_files_norm = {norm(p) for p in html_img_refs | used_from_css}
print(f"Combined used files (normalized) ({len(used_files_norm)}): {sorted(used_files_norm)}")

# ---------- Ensure extras dir ----------
os.makedirs(extras_dir, exist_ok=True)

# ---------- Scan images dir and extras (case-insensitive matching) ----------
images_path = Path(images_dir)
extras_path = Path(extras_dir)

existing_images = []
for p in images_path.iterdir():
    if p.is_file() and p.name != extras_path.name:
        existing_images.append(p)

existing_extras = [p for p in extras_path.iterdir() if p.is_file()] if extras_path.exists() else []

print(f"Found {len(existing_images)} files in {images_dir}, {len(existing_extras)} files in extras.")

# Build map from normalized name -> actual path for both folders
existing_map = {norm(p.name): p for p in existing_images}
extras_map = {norm(p.name): p for p in existing_extras}

# ---------- Restore needed files from extras ----------
to_restore = []
for used_norm in used_files_norm:
    if used_norm in existing_map:
        # already present in images_dir
        continue
    if used_norm in extras_map:
        to_restore.append(extras_map[used_norm])

print(f"Will restore {len(to_restore)} files from extras: {[p.name for p in to_restore]}")
for p in to_restore:
    dest = images_path / p.name
    print(f"Restoring {p} -> {dest}")
    if not dry_run:
        shutil.move(str(p), str(dest))

# ---------- Move unused files to extras ----------
to_move = []
for norm_name, p in existing_map.items():
    if norm_name not in used_files_norm:
        to_move.append(p)

print(f"Will move {len(to_move)} unused files to extras: {[p.name for p in to_move]}")
for p in to_move:
    dest = extras_path / p.name
    print(f"Moving {p} -> {dest}")
    if not dry_run:
        shutil.move(str(p), str(dest))

print("Finished. (dry_run={})".format(dry_run))
