> 📦 **扩展模块**（非语言内置标准库）· 包名 `LenoSys` · import 名 "Sys"
> 源：`Leno/build/leno_module/LenoSys/lib/Sys.leno`（本页是**手写**文档，不从 README 同步）

# LenoSys v0.2.0

跨平台的**系统信息与桌面集成**：进程、磁盘卷、回收站、通知、开机自启、已装软件。
Windows 走 Win32 API，Linux 走 `/proc` + 标准命令，**同一套 API 两个平台都能跑**。

```leno
import "Sys" as Sys
use Sys.(VolumeInfo, SysInfo)

SysInfo i = Sys.sysInfo()                       // OS / CPU / 内存 / 运行时长 / 是否管理员
for Sys.listVolumes() to v {                    // 每个盘/挂载点：卷标、文件系统、类型、容量
    print(v.root + "  " + v.label + "  " + v.fsType + "  剩余 " + _str(v.freeBytes))
}
```

> **与 `module_sys.md` 的分工**：那一页讲**内置全局函数**（`_os()` / `_env()` / `_exec()` / `_args()`…，
> 不需要 import）；本页讲**扩展模块** `import "Sys" as Sys` 提供的东西。两者不重叠。

---

## 平台与环境

| 函数 | 说明 |
|---|---|
| `os()` / `isWindows()` / `isLinux()` / `isMacos()` | 平台判定 |
| `env(name, def = "")` | 读环境变量（缺失给默认值；**不抛**） |
| `expandEnv(s)` | 展开 `%VAR%` / `$VAR` |
| `homeDir()` / `tempDir()` / `configDir()` / `dataDir()` / `cacheDir()` | 常用目录（按平台惯例） |
| `systemRoot()` / `pathSep()` / `joinPath(parts)` | 路径基建 |

## 进程

| 函数 | 返回 | 说明 |
|---|---|---|
| `listProcesses()` | `Array[ProcInfo]` | 全量进程（pid / name / 路径…） |
| `findProcess(name)` | `Array[ProcInfo]` | 按名字查 |
| `processExists(pid)` / `killProcess(pid, force=false)` | `bool` | 存在性 / 结束 |
| `processMemoryKb(pid)` / `processPath(pid)` | `int` / `string` | 内存与可执行路径 |
| `currentPid()` / `exePath()` | `int` / `string` | 自身 |
| `exec(cmd, timeoutMs = 30000)` | `Dict` | 跑一次命令（**默认超时**；返回 code/output/err） |

## 磁盘与卷（v0.2 起含 `listVolumes`）

| 函数 | 返回 | 说明 |
|---|---|---|
| `listDrives()` | `Array[string]` | 只要路径（`C:\` / `/`）；**保留兼容** |
| **`listVolumes()`** | `Array[VolumeInfo]` | 卷标 + 文件系统 + 类型 + 容量，一次取齐 |
| `diskSpace(path)` | `Dict{ok,total,free}` | 该路径所在卷的字节数 |
| `diskUsagePercent(path)` | `int` | 0..100；取不到 ⇒ `-1` |
| `volumeOf(path)` | `string` | 该路径属于哪个卷/挂载点（判不出 ⇒ `""`，不猜） |

`VolumeInfo` 字段：

```leno
struct VolumeInfo {
    string root = ""        // "C:\\" 或 "/" 或 "/media/u/U盘"
    string label = ""       // 卷标；Linux 给设备名（/dev/sda1 —— 没有统一卷标概念）
    string fsType = ""      // NTFS / FAT32 / exfat / ext4 …
    int serial = 0          // Windows 卷序列号；Linux 恒 0
    int driveType = 0       // Windows GetDriveTypeW 原值；Linux 恒 0
    string kind = ""        // removable / fixed / network / cdrom / ram / unknown
    int totalBytes = 0
    int freeBytes = 0
    bool ready = false      // 能否取到容量
}
```

**契约（踩过才知道）**：

- **`ready=false` 时 `totalBytes/freeBytes` 一定是 0**，但它的含义是「**未就绪**」而不是「空盘」：
  空的光驱、已拔出的 U 盘、无权限的网络盘都会这样。上层应显示"未就绪"，别画成 0/0 的进度条。
- **取不到就留空，绝不编**：卷标取不到给 `""`，不是 `"本地磁盘"` 之类猜出来的名字。
- **`listVolumes` 每次调用都会真查容量**（Windows: `GetDiskFreeSpaceExW`；Linux: 每个挂载点一次 `df -B1` 子进程）
  ⇒ 别每帧调，缓存到自己的状态里按需刷新。
- Linux 侧**过滤虚拟文件系统**（`proc` / `sysfs` / `tmpfs` / `cgroup*` / `squashfs` …），
  否则容器里能列出几十个无意义条目、白跑几十次 `df`。`kind` 按挂载点前缀推断
  （`/media/`、`/mnt/`、`/run/media/` ⇒ `removable`，其余 `fixed`）。
- ⚠ **Linux 分支未在真实机器上实测**（开发机只有 Windows）：`/proc/mounts` + `df` 的格式解析有单测
  （`parse_mounts_detail` / `parse_df`），但整条链路的实际输出请以你在 Linux 上跑 `test_sys_volumes` 为准。
- macOS 目前**复用 Linux 分支**（没有 `/proc`）⇒ `sysInfo()` 的多数字段会是空/0；
  `volumeOf` / `diskSpace` 走 `df` 仍可用（GNU/BSD 两版的 `df` 输出解析器都吃）。

## 桌面集成

| 函数 | 说明 |
|---|---|
| `openWith(path)` | 用系统默认程序打开文件/目录/**URI**（`https://`、`mailto:` 也认） |
| `revealInFolder(path)` | 在文件管理器里定位并选中 |
| `notify(title, body = "")` | 系统通知（标题必填） |
| `isElevated()` | 是否 root / 管理员 |

## 回收站

| 函数 | 返回 | 说明 |
|---|---|---|
| `deleteToTrash(paths)` | `Dict` | 移入回收站（Windows: `SHFileOperationW`；Linux: freedesktop Trash 规范，**按文件所在分区**挑回收站） |
| `emptyTrash()` | `bool` | 清空（已空也算成功） |
| `listTrash()` | `Array[TrashItem]` | 列表 |

## 开机自启 / 已装软件 / 最近文件

| 函数 | 说明 |
|---|---|
| `listStartupItems()` / `getAutostart(id)` / `setAutostart(id, name, cmd)` / `removeAutostart(id)` | 自启项 |
| `listInstalledSoftware()` | 已装软件（Windows 读注册表 Uninstall；Linux 读包管理器） |
| `recentFiles(max = 100)` | 最近打开的文件 |
| `selfTest()` | 自检：实测磁盘/进程等几项调用，用于排查"模块被顶掉成旧版"（见下） |

## 口径与边界

- **绝不静默返回假数据**：取不到就是 `""` / `0` / `false`，并在注释里写清为什么取不到。
- **不过 shell 做能直连的事**：Windows 侧走 Win32 API（注册表 / Shell），只有必须的场合才起子进程；
  Linux 侧则大量依赖 `/proc` 与标准命令（`df`、`id`、`ps`），这是两个平台的现实差异。
- ⚠ **模块同名冲突**：`import Win32` 走全局搜索路径、**先到先得** —— 曾因别的模块下放着陈旧
  `Win32.leno` 副本而被顶掉（表现为"行为像旧版"）。遇到怪事跑 `Sys.selfTest()` 先确认拿到的是新实现。
- `ProcInfo` / `StartupItem` / `SoftwareItem` / `TrashItem` / `SysInfo` / `VolumeInfo` 都是脚本结构体，
  跨模块使用时按惯例 `use Sys.VolumeInfo`（或用 `var v = ...` 让编译器推断）。
