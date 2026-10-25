# -*- coding: utf-8 -*-
"""验证：投喂 +2.5 / 投喂动作来自「吃点什么」21 个 / 106 个动作都能自播"""
import json
import os
import time

WORK = r"D:\deepseek\蓝色大肥鱼"
STATUS = os.path.join(WORK, "test-status.json")
CMD = os.path.join(WORK, "test-command.txt")
ANIM = os.path.join(WORK, "assets", "fish", "animations.json")

KW = [("吃点什么", ["吃"]),
      ("过节", ["孔明灯", "河灯", "茱萸", "雪人", "福字", "红包", "烟花", "赏月", "月饼", "元宵",
              "粽子", "年糕", "腊八", "重阳", "七夕", "圣诞", "南瓜灯"]),
      ("干活", ["工作状态", "碎碎念", "记录", "写代码", "思考"]),
      ("才艺", ["舞", "小提琴", "笛", "魔术", "魔方", "五子棋", "扑克", "演奏", "抛接"]),
      ("玩耍", ["玩", "水枪", "风筝", "秋千", "陀螺", "毽子", "木马", "气球", "拆礼物", "摇扇",
              "撸猫", "照镜子", "散步", "漂浮", "敲击", "跳跃", "奔跑"]),
      ("特效", ["鲸鱼", "蓝鲸", "泡泡", "生花", "鸽子", "环绕", "蝴蝶", "落叶", "螃蟹", "重力",
              "360", "换装", "开花", "旋转"]),
      ("卖萌与日常", ["哈欠", "伸懒腰", "幽灵", "吓", "东张西望", "呼吸", "哼歌", "小憩", "打瞌睡",
                  "沉眠", "待机", "发呆", "可爱", "礼仪", "刷牙"])]

RULES = {r["Id"]: r for r in json.load(open(ANIM, encoding="utf-8"))}


def group_of(rid):
    r = RULES.get(rid)
    if not r:
        return "?"
    if r.get("Pool") == "Disabled":
        return "已停用"
    if r.get("Meal") is not None:
        return "吃点什么"
    if r.get("Festival") is not None:
        return "过节"
    if r.get("WorkKind") is not None:
        return "干活"
    if r.get("Pool") in ("Click", "Drag"):
        return "互动反馈"
    for name, kws in KW:
        if any(k in rid for k in kws):
            return name
    return "其他动作"


def status():
    for _ in range(40):
        try:
            with open(STATUS, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            time.sleep(0.15)
    return {}


def send(command, wait=1.5):
    with open(CMD, "w", encoding="utf-8") as f:
        f.write(command)
    time.sleep(wait)
    return status()


print("=== 0. 等启动 ===")
s = {}
for _ in range(60):
    s = status()
    if s.get("ready"):
        break
    time.sleep(0.5)
print("  ready=%s  interval=%s  初始 satiety=%.1f" % (
    s.get("ready"), s.get("animationInterval"), s.get("satiety", -1)))

print("=== 1. 投喂一次，看涨多少 ===")
before = status().get("satiety", 0)
s = send("feed", 2.0)
after = s.get("satiety", 0)
print("  %.2f -> %.2f  Δ=%.2f  （期望 2.5）" % (before, after, after - before))
print("  50 -> 100 需要 %d 次" % round(50 / max(after - before, .01)))

print("=== 2. 投喂动作是不是「吃点什么」里的 ===")
seen_meal = []
for i in range(14):
    s = send("feed", 1.2)
    act = s.get("action")
    g = group_of(act)
    seen_meal.append((act, g))
    print("  %-18s 分组=%s %s" % (act, g, "OK" if g == "吃点什么" else "!! 不在吃饭组"))
uniq = sorted({a for a, _ in seen_meal})
print("  14 次投喂共出现 %d 种吃饭动作: %s" % (len(uniq), "、".join(uniq)))

print("=== 3. 自播：连续采样动作变化（间隔 %ss）===" % status().get("animationInterval"))
picked = []
last = None
deadline = time.time() + 100
while time.time() < deadline:
    cur = status().get("action")
    if cur and cur != last:
        picked.append(cur)
        last = cur
        print("  + %-22s 分组=%-8s Pool=%s" % (cur, group_of(cur), RULES.get(cur, {}).get("Pool")))
    time.sleep(0.4)

print("=== 4. 结论 ===")
print("  采样到 %d 个不同动作" % len(picked))
from collections import Counter
c = Counter(group_of(a) for a in picked)
print("  分组分布: %s" % dict(c))
pools = Counter(RULES.get(a, {}).get("Pool") for a in picked)
print("  Pool 分布: %s" % dict(pools))
print("  是否出现过 Event 池以外的动作: %s" % ("是" if any(p != "Event" for p in pools) else "否"))

print("=== 5. 恢复 ===")
s = send("vitals-reset", 1.5)
print("  affection=%.1f satiety=%.1f energy=%.1f" % (
    s.get("affection", 0), s.get("satiety", 0), s.get("energy", 0)))
