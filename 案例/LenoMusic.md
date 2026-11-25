# 案例：LenoMusic —— 多音源音乐搜索与下载

> 本地仓库：`D:\CLeno\LenoMusic`（46 个 `.leno` / 16,420 行 / 28 张界面图）

![榜单](../images/案例/music-1-bangdan.png)
![试听](../images/案例/music-2-audition.png)

## 它是什么

多音源的音乐**搜索 / 试听 / 下载**工具，**GUI 与 CLI 两个入口共用一套引擎**（`leno.toml` 里 `name = "LenoMusic"`, `version = "0.2.2"`）。

## 规模

| 项 | 数值 |
|---|---|
| `.leno` 文件 | **46** |
| 代码行 | **16,420** |
| 最大文件 | `musicdl_gui.leno` 2,082 行、`player_bar.leno` 1,671 行、`player.leno` 1,585 行 |
| 入口 | `musicdl_gui.leno`（GUI）、`musicdl.leno`（CLI，216 行） |
| 依赖 | `LenoSDL3 >=0.1.1` |

## 用到的模块

```
strings×29  files×16  web_net×15  dirs×14  jsons×14
times×10  SDL3×9  threads×6  Crypto×3  rands×2
```

`web_net×15` + `jsons×14` 说明它的核心工作量是**抓接口 + 解 JSON**；`threads×6` 对应并行下载。

## 怎么跑

```bat
leno musicdl_gui.leno          :: 图形界面
leno musicdl.leno              :: 命令行
```

## 打包

```bat
leno -p --no-console -o=dist musicdl_gui.leno
```

## 值得借鉴的几点

- **同一套引擎两个入口**：GUI 和 CLI 都只调下层函数，不复制业务逻辑。
- **下载与界面解耦**：`threads` 并行下载，界面只订阅进度。
- 附带 3 个 `test_*.leno`（约 800 行）：下载状态机、并行下载都有断言。
