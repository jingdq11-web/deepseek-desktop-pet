# 变更记录

本项目基于上游 [Bai-Cute/big-blue-fish-desktop-pet](https://github.com/Bai-Cute/big-blue-fish-desktop-pet) **v1.0.1**。
版本号是本仓库自己的，和上游不连续。

---

## v1.2 — 首个公开版本（2026-10-25）

基线：上游 `v1.0.1` ｜ 补丁：`patch/右键动作菜单.patch`（20 个文件）

### 新增

**右键动作菜单**
- 「让她做点事」一级菜单，106 个动作按官方元数据 + 关键词自动分成 10 组
  （吃点什么 21 / 过节 13 / 干活 11 / 才艺 9 / 玩耍 17 / 特效 11 / 卖萌与日常 11 / 互动反馈 6 / 其他动作 3 / 已停用 4）
- 「随便来一个」随机播一个
- 「鱼鱼的日常」一级菜单：喂食、番茄钟、看屏幕汇报、剪贴板开关、状态

**全部动作自播**（`CompanionAnimations.ChooseAutoAction()`）
- 候选池从「只有 `Pool=Event` 的 91 个」扩到「除 `Disabled` 和 `Drag` 之外的全部 101 个」
- 被「只在夜里 / 只在某季节 / 只在节日前后 / 只在整点」约束压成 0 权重的动作，给保底值 25
- 权重开 0.35 次方压缩（作者原始跨度 0~1000 是 50 倍，直接轮盘会让低权重动作几小时才轮到一次）
- 池子系数：Click ×0.60、Idle ×0.60、Greeting/Daily ×0.30
- 反重复：上一个播的 ×0.05，最近 8 个播过的 ×0.30
- 实测 2000 次采样覆盖 101/101 个动作
- 新偏好 `AutoPlayAllActions`（默认开），设置页可关

**视觉模式**
- 从 Windows OCR 读文字，升级成 768px 截图 + 多模态看图
- 新增启动参数 `--no-mmproj-offload`、`--image-max-tokens 256`（8 GB 显存必需，否则 llama-server 无报错崩溃）
- 实测首字 3.1 秒

**看屏幕汇报**
- 右键「看看主人在干什么」：看懂画面，说「主人在干什么 + 她自己的想法」
- 替代上游的「读字到剪贴板」，不再往剪贴板写东西
- 新方法 `CompanionBrain.GenerateScreenReportAsync()`，超时 90 秒，温度 0.55

**养成数值**
- 好感 / 饱食 / 精力三个 0~100 数值，落盘 `preferences.json`
- 右上角三格仪表（`CompanionVitalsHud.cs`）：图标 + 短条，低于 25 脉动，数值变化时闪一下
- 气泡自动避让 44 px，不盖住仪表
- 离线最多补算 12 小时

**好感度来源**（6 种，带递减）
- 摸头 +0.5
- 右键点任意动作 +0.5（同动作 10 分钟内重复 +0.1）
- 喂食 / 点菜 +5（10 分钟内再喂 +1）
- 双击开聊 +1（5 分钟冷却）
- 发消息 +0.6（30 秒冷却）
- 时间流逝 −0.25/时，长期不管 −1.2/时

**数值驱动行为**（`CompanionVitals.VitalsSocialTick()`）
- 饱食 < 50 主动讨吃（45 分钟一次，< 25 时 20 分钟一次），深夜不吵
- 精力 < 22 白天念叨「眼睛睁不开了」，夜里安静睡
- 好感 ≥ 85 每 40 分钟概率主动贴贴
- 说话间隔按好感缩放（1.55 − 好感×0.01），按精力调整（<25 ×1.7 / <45 ×1.25 / >75 ×0.9）
- 新增 `CompanionDialogue.IntimacyHint()` 五档语气，明确「不影响事实判断」

**日常功能**
- 番茄钟（25 / 45 分钟，到点播动作 + 提醒喝水）
- 久坐提醒（默认 90 分钟，键鼠空闲 >2 分钟重置计时）
- 生日（设置月/日，同一年只触发一次）
- 剪贴板联动（代码 / 链接 / 外文三类，25 秒冷却，默认关闭）

**其他**
- 工作识别接通：`CompanionAnimations.AnimationContext()` 读前台进程，IDE 时提高 `WorkKind` 动作权重
- 目录保洁 `CompanionHousekeeping`：日志超 512 KB 滚动、清遗留诊断文件
- 测试命令扩充：`feed` / `pomodoro` / `report-screen` / `vitals` / `affection-low|high` / `menu:<动作名>` / `auto-sample` 等

### 改动

- `CompanionAnimationPolicy.Load()`：硬校验 `rules.Count != 106` 放宽成「非空 + 动作名不重复 + 内置三条还在」，用户加新动作不再导致桌宠起不来
- `CompanionPreferences.NextSpeechDelay()`：签名加 `affection` / `energy` 两个参数，间隔随数值缩放
- 投喂饱食 +30 → **+2.5**（50 → 100 正好 20 次）
- 饱食衰减 4/时 → **1.5/时**（配合投喂量降低）
- 讨吃阈值 30 → **50**
- 投喂动作从「只挑 Meal 标了早/午/晚餐的 3 个」改成「吃点什么整组 21 个随机」
- 喂食好感 +2 → **+5**
- `CompanionMenuItem` 模板补 `PART_Popup` + 展开箭头（否则三级菜单展不开）
- `CompanionMenuDismissal` 点击判定把「已展开的子菜单」算进菜单范围

### 移除

- 日记功能（`DiaryTick` / `FlushDiary` / `DiaryEnabled` / `DiaryDate` / `PruneDiary` 全部删除）——用不上，还每天落一个文件
- 「读一下屏幕上的字并复制到剪贴板」——换成看屏幕汇报

### 修复

- 8 GB 显存下视觉模式必崩（`ErrorOutOfDeviceMemory` → llama-server 静默退出 → 请求 502）
- 气泡盖住右上角仪表（`CompanionEdgeLayout` 加 `CompanionBubbleRightInset`）
- 三级菜单点不开（`MenuItem` 模板缺 `PART_Popup`）

---

## v1.0.1 — 上游基线

非本仓库版本，见 [上游 Releases](https://github.com/Bai-Cute/big-blue-fish-desktop-pet/releases/tag/v1.0.1)。
