# -*- coding: utf-8 -*-
"""验证补丁能否干净应用到上游 v1.0.1：
   1. 从补丁里解析出「被修改的文件」（--- 不是 /dev/null 的那些）
   2. 用 gh api 逐个拉上游原文，铺到临时目录
   3. git apply --check 检查

用法（在仓库根目录）：python tools/_verify_patch.py
需要已登录的 gh CLI。
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

GH = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
REPO = "Bai-Cute/big-blue-fish-desktop-pet"
REF = "v1.0.1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCH = os.path.join(ROOT, "patch", "右键动作菜单.patch")
WORK = os.path.join(tempfile.gettempdir(), "_verify_patch")

# 解析补丁
modified, created = [], []
cur = None
with open(PATCH, encoding="utf-8") as f:
    for line in f:
        if line.startswith("diff -urN "):
            m = re.match(r"diff -urN a/(\S+) b/(\S+)", line)
            cur = m.group(2) if m else None
        elif line.startswith("--- /dev/null") and cur:
            created.append(cur)
        elif line.startswith("--- a/") and cur:
            modified.append(cur)

print("补丁里：修改 %d 个，新增 %d 个，合计 %d" % (len(modified), len(created), len(modified) + len(created)))

shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK, exist_ok=True)

fail = []
for rel in modified:
    r = subprocess.run(
        [GH, "api", f"repos/{REPO}/contents/{rel}?ref={REF}",
         "-H", "Accept: application/vnd.github.raw"],
        capture_output=True)
    if r.returncode != 0:
        fail.append(rel)
        print("  拉取失败:", rel)
        continue
    dst = os.path.join(WORK, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(r.stdout)
print("上游原文就位 %d / %d" % (len(modified) - len(fail), len(modified)))

print("=== git apply --check ===")
p = subprocess.run(["git", "apply", "--check", "-p1", "--verbose", PATCH],
                   cwd=WORK, capture_output=True)
out = (p.stdout + p.stderr).decode("utf-8", "replace")
print(out.strip()[-2500:] if out.strip() else "(无输出)")
print("退出码:", p.returncode)
