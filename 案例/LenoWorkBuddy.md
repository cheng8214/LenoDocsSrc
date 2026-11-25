# 案例：LenoWorkBuddy —— WorkBuddy 自动签到 + 成长中心

> 本地仓库：`D:\CLeno\LenoWorkBuddy`（16 个 `.leno` / 5,338 行）

![启动](../images/案例/wb-1-startup.png)
![签到结果](../images/案例/wb-2-check.png)

## 它是什么

每天自动签到（可配静默模式给计划任务用），另外把"成长中心"的任务也一并做完；带 GUI 壳与单元/流程测试。

## 规模

| 项 | 数值 |
|---|---|
| `.leno` 文件 | **16** |
| 代码行 | **5,338** |
| 主要文件 | `wb_auth.leno`（934 行，登录态）、`wb_growth.leno`（757 行）、`wb_gui.leno`（750 行）、`wb_sign.leno`（353 行） |
| 测试 | `test_wb_flow.leno`（345 行）、`test_wb_units.leno`（251 行） |

## 用到的模块

```
strings×15  jsons×13  dirs×9  files×8  times×6  Sys×2  SDL3×2
```

## 怎么跑

```bat
leno wb_sign.leno              :: 签到 + 成长中心（默认）
leno wb_sign.leno silent       :: 同 auto，但结果写日志文件（配合无窗口定时任务）
```

## 值得借鉴的几点

- **静默模式**：同一个入口能"给人看"也能"给计划任务跑"，输出目的地可切换。
- **鉴权单独一层**（`wb_auth.leno` 934 行）：token 过期、续期、失效检测都在这里，业务层不用管。
- **测试分两级**：`test_wb_units`（单元）+ `test_wb_flow`（全流程），改逻辑时先跑单元。
