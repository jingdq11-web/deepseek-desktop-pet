# -*- coding: utf-8 -*-
"""按文件从 GitHub 取 v1.0.1 原版，和本地工作副本比对，生成补丁。"""
import difflib
import os
import subprocess

REPO = "Bai-Cute/big-blue-fish-desktop-pet"
REF = "v1.0.1"
GH = r"C:\Program Files\GitHub CLI\gh.exe"
SRC = r"D:\大肥鱼右键菜单\src"
OUT = r"D:\大肥鱼右键菜单\右键动作菜单.patch"

CANDIDATES = []
for root, dirs, files in os.walk(os.path.join(SRC, "code")):
    dirs[:] = [d for d in dirs if d not in ("bin", "obj", "assets", "media", "tests", "licenses")]
    for name in files:
        if name.endswith((".cs", ".xaml", ".csproj", ".props", ".json")) and not name.endswith(".lock.json"):
            CANDIDATES.append(os.path.join(root, name))


def upstream(rel):
    """返回上游文件内容；不存在返回 None。"""
    r = subprocess.run(
        [GH, "api", f"repos/{REPO}/contents/code/{rel}?ref={REF}", "-H", "Accept: application/vnd.github.raw"],
        capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")


def lines(text):
    return text.splitlines(keepends=True)


chunks = []
changed = []
for path in CANDIDATES:
    rel = os.path.relpath(path, os.path.join(SRC, "code")).replace("\\", "/")
    old = upstream(rel)
    with open(path, encoding="utf-8") as f:
        new = f.read()
    if old is not None and old.replace("\r\n", "\n") == new.replace("\r\n", "\n"):
        continue
    changed.append(rel)
    old_lines = lines(old.replace("\r\n", "\n")) if old is not None else []
    new_lines = lines(new.replace("\r\n", "\n"))
    diff = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=("/dev/null" if old is None else f"a/code/{rel}"),
        tofile=f"b/code/{rel}",
        n=3))
    if not diff:
        continue
    header = f"diff -urN a/code/{rel} b/code/{rel}\n"
    if old is None:
        header = f"diff -urN a/code/{rel} b/code/{rel}\n"
    chunks.append(header + "".join(diff))

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("".join(chunks))

print("改动文件 %d 个：" % len(changed))
for c in changed:
    print("  " + c)
print("补丁大小 %.0f KB" % (os.path.getsize(OUT) / 1024))
