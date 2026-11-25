# 案例：AriaDeployd —— 目标机部署守护进程

> 仓库：`gitee.com/cheng8214/AriaDeployd`（2 个 `.leno` / 839 行）

## 它是什么

跑在目标机上的**部署守护进程**：起一个内网 HTTP 小服务，让开发机用 `curl` 就能**上传 exe 到指定目录、停/启/重启进程**——不用远程桌面手点。首次运行会生成 `deployd.json` 配置。

## 规模

| 项 | 数值 |
|---|---|
| `.leno` 文件 | **2** |
| 代码行 | **839** |
| 主文件 | `deployd.leno`（548 行，服务端）、`deploy.leno`（291 行，客户端） |

## 用到的模块

```
strings×2  files×2  dirs×2  jsons×2  times×2  threads×2
sockets×1  WebNet×1  HTTP×1  Sys×1
```

`sockets` + `HTTP` + `Sys`（起停进程）= 一个**能自启动、能管进程**的小服务端。

## 怎么跑

双击运行（或加到启动项），首次运行生成 `deployd.json`；然后在开发机上用 `curl` 调它的接口上传/重启。

## 值得借鉴的几点

- **两个文件就够**：服务端（`deployd.leno`）+ 客户端（`deploy.leno`），没有框架依赖。
- 这类"内网小服务"是 Leno 的舒适区：比 Python 省掉解释器和虚拟环境，比 Go 少一堆样板。
- 上传走**原始字节搬运**，不重压已有内容（避免二次压缩把 exe 弄坏）。
