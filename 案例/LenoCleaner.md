# 案例：LenoCleaner —— C 盘清理工具

> 本地仓库：`D:\CLeno\LenoCleaner`（11 个 `.leno` / 4,529 行 / 20 张界面图）
> 包名：`CleanerMaster 0.1.0`

![清理](../images/案例/cleaner-1-clean.png)
![浏览器缓存](../images/案例/cleaner-2-browser.png)

## 它是什么

扫描并清理 C 盘上的缓存/垃圾（浏览器缓存、聊天记录缓存、崩溃转储、D3D 着色器缓存…），带图形界面与**规则表**。

## 规模

| 项 | 数值 |
|---|---|
| `.leno` 文件 | **11** |
| 代码行 | **4,529** |
| 主要文件 | `cleaner_master.leno`（1,661 行，入口）、`cleaner_rules.leno`（941 行，规则表）、`test_rules.leno`（380 行） |
| 依赖 | `LenoSDL3 >=0.1.1`、`LenoLog >=0.1.0` |

## 用到的模块

```
dirs×11  files×9  strings×7  threads×4  SDL3×3
times×3  jsons×2  Sys×2  Log×1  Win32×1
```

`Win32` 这一项是关键：**要读注册表/调系统 API 时直接下去调**，不用换语言。

## 怎么跑

```bat
leno cleaner_master.leno
```

## 打包

```bat
leno -p --no-console -o=dist cleaner_master.leno
```

## 值得借鉴的几点

- **清理规则独立成表**（`cleaner_rules.leno` 941 行）：加一个"可清理位置"只改规则，不动界面。
- **规则表自带测试**（`test_rules.leno` 380 行）：路径匹配这类逻辑最容易被误改，测试是护栏。
- 界面与扫描线程分离，扫描大目录时界面不卡。
