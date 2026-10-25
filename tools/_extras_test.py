# -*- coding: utf-8 -*-
"""通过 test-command.txt 驱动桌宠，读 test-status.json 验证"""
import json
import os
import time

WORK = r"D:\deepseek\蓝色大肥鱼"
STATUS = os.path.join(WORK, "test-status.json")
CMD = os.path.join(WORK, "test-command.txt")


def status():
    for _ in range(30):
        try:
            with open(STATUS, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            time.sleep(0.1)
    return {}


def send(command, wait=2.0):
    with open(CMD, "w", encoding="utf-8") as f:
        f.write(command)
    time.sleep(wait)
    return status()


def show(tag, s, keys):
    print("  [%s] %s" % (tag, "  ".join("%s=%s" % (k, s.get(k)) for k in keys)))


if __name__ == "__main__":
    keys = ["action", "animationPhase", "affection", "satiety", "energy",
            "pomodoroRunning", "pomodoroLabel", "bubble"]

    print("=== 1. 喂食 ===")
    before = status()
    print("  喂前 satiety=%.1f" % before.get("satiety", 0))
    after = send("feed", 2.5)
    print("  喂后 satiety=%.1f  好感=%.1f  action=%s" % (
        after.get("satiety", 0), after.get("affection", 0), after.get("action")))

    print("=== 2. 番茄钟 ===")
    s = send("pomodoro", 2.0)
    show("开始", s, ["pomodoroRunning", "pomodoroLabel"])
    s = send("pomodoro-stop", 2.0)
    show("停止", s, ["pomodoroRunning", "pomodoroLabel"])

    print("=== 3. 低数值触发动作 ===")
    s = send("vitals", 1.0)
    print("  已设为 satiety=%.0f energy=%.0f" % (s.get("satiety", 0), s.get("energy", 0)))
    hit = None
    for i in range(30):
        time.sleep(1)
        cur = status()
        if cur.get("bubble") and ("饿" in cur.get("bubble", "") or "困" in cur.get("bubble", "")):
            hit = cur.get("bubble")
            break
        if cur.get("action") in ("打瞌睡被惊醒", "原地小憩沉眠", "哈欠连天"):
            hit = cur.get("action")
            break
    print("  触发结果:", hit or "30 秒内未触发（概率性行为，正常）")

    print("=== 4. 看屏幕汇报 ===")
    s = send("report-screen", 45.0)
    bubble = s.get("bubble") or ""
    print("  气泡(%d 字): %s" % (len(bubble), bubble))
    if not bubble:
        print("  !! 没拿到气泡，检查 companion-errors.log / vision-status.json")

    print("=== 5. 好感度语气分级 ===")
    for cmd, label in (("affection-low", "低好感"), ("affection-high", "高好感")):
        s = send(cmd, 1.5)
        print("  %s -> affection=%.0f" % (label, s.get("affection", 0)))

    print("=== 6. 恢复 ===")
    s = send("vitals-reset", 1.5)
    show("恢复", s, keys)
