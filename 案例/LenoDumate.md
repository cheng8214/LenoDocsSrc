# 案例：LenoDumate —— 百度搭子每日签到

> 仓库：`gitee.com/cheng8214/LenoDumate`（7 个 `.leno` / 2,011 行）

![主界面](../images/案例/dumate-1-app.png)

## 它是什么

百度搭子（千帆桌面客户端）的每日签到：**读本机客户端的登录态 → AES-256-GCM 解密 cookies → 调接口签到**，带积分/到期查询与登录态健康检查。

## 规模

| 项 | 数值 |
|---|---|
| `.leno` 文件 | **7** |
| 代码行 | **2,011** |
| 主要文件 | `dumate_gui.leno`（585 行）、`dumate_sign.leno`（128 行）、`dumate_stub.leno`（156 行，不含 GUI 的轻量入口） |

## 用到的模块

```
jsons×5  dirs×5  strings×4  files×4  times×4  SDL3×3  Crypto×2  Sys×2  threads×1  web_net×1
```

`Crypto` 只有 2 处，但正是这个项目的关键：**AES-256-GCM 解密**本机客户端的 cookies。

## 怎么跑

```bat
leno dumate_sign.leno              :: 签到（默认；今天已签到会提示无需重复）
leno dumate_sign.leno status       :: 只查状态
leno dumate_sign.leno health       :: 登录态健康检查（剩余天数）
leno dumate_sign.leno credits      :: 积分套餐与到期时间
```

## 值得借鉴的几点

- **子命令式 CLI**（`status` / `health` / `credits`）：一个入口多种动作，比做五个脚本好维护。
- **`Crypto` + `jsons` 就能干"协议自动化"**：这类活以前基本是 Python + requests + pycryptodome，现在能编译成单 exe 发给别人。
- `dumate_stub.leno`：把"不含界面的核心"单独留一份，方便在无图形环境跑。
