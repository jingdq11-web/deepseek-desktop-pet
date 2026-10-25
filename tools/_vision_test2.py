# -*- coding: utf-8 -*-
"""干净复测：记录气泡变化过程，确认走的是「看图说话」而不是抄字"""
import json
import os
import subprocess
import time

WORK = r"D:\deepseek\蓝色大肥鱼"
STATUS = os.path.join(WORK, "test-status.json")
CMD = os.path.join(WORK, "test-command.txt")
VP = os.path.join(WORK, "vision-status.json")


def status():
    try:
        with open(STATUS, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


if os.path.exists(VP):
    os.remove(VP)

before = status()
print("触发前气泡:", before.get("bubble"))
print("触发前状态:", before.get("status"))

with open(CMD, "w", encoding="utf-8") as f:
    f.write("generate")

last = None
for i in range(90):
    s = status()
    cur = (s.get("status"), s.get("bubble"), s.get("bubbleVisible"))
    if cur != last:
        print("  %02ds  状态=%s  气泡=%s  可见=%s" % (i, cur[0], (cur[1] or "")[:60], cur[2]))
        last = cur
    if os.path.exists(VP) and s.get("bubbleVisible") and s.get("status", "").startswith("本地模型就绪"):
        break
    time.sleep(1)

print("vision-status 存在:", os.path.exists(VP))
if os.path.exists(VP):
    with open(VP, encoding="utf-8") as f:
        v = json.load(f)
    print(json.dumps(v, ensure_ascii=False)[:600])
