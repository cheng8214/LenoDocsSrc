# 案例：LenoTrae —— Trae 每日自动签到

> 本地仓库：`D:\CLeno\LenoTrae`（12 个 `.leno` / 3,460 行）
> 特点：托盘 GUI + 定时调度 + 失败重试

![设置](../images/案例/trae-1-settings.png)
![启动](../images/案例/trae-2-startup.png)

## 它是什么

每天自动完成 Trae 的签到，托盘常驻、可配置重试间隔（1/15/30/60/120 分钟），带设置对话框与历史记录。

## 规模

| 项 | 数值 |
|---|---|
| `.leno` 文件 | **12** |
| 代码行 | **3,460** |
| 主要文件 | `trae_gui.leno`（943 行，托盘/界面）、`trae_auto.leno`（455 行，调度器）、`trae_settings.leno`（418 行）、`trae_sign.leno`（257 行） |

## 用到的模块

```
dirs×8  files×7  Sys×6  jsons×5  strings×5  SDL3×4  times×2  rands×2
```

## 怎么跑

```bat
leno trae_sign.leno            :: 签到（默认；今天已签到会提示无需重复）
leno trae_gui.leno --tray      :: 启动即隐藏到托盘
```

## 打包

```bat
leno -p --no-console trae_gui.leno
```

> README 原话：双击即用，首次运行会自动把依赖解包到用户缓存目录。

## 值得借鉴的几点

- **"签到"是纯函数层**（`trae_sign.leno`），GUI/托盘只是壳：命令行能跑、托盘也能跑。
- **定时 + 重试单独一个调度文件**（`trae_auto.leno`），调策略不用碰界面。
- 配置走 `trae_settings.leno` + JSON，升级不丢用户设置。
