# Leno 常见任务 cookbook

> **"我要做 X，代码怎么写？"** —— 照抄就能跑。
>
> 每条都是**完整程序**（含 `main()`），实测跑过、输出写在下面。
> 与 [`Leno零基础入门.md`](Leno零基础入门.md) 的分工：那篇讲"语言怎么用"，这篇讲"具体任务怎么落地"。

| # | 任务 | 用到的模块 |
|---|---|---|
| 1 | 读写文本文件 | `files` |
| 2 | 读写 JSON 配置 | `jsons` |
| 3 | 读命令行参数 | 内置 `_args()` |
| 4 | 调用外部命令并拿输出 | 内置 `_exec()` |
| 5 | 读环境变量 | 内置 `_env()` / `_env_or()` |
| 6 | 数组：筛选 / 变换 / 排序 / 求和 | 内置方法 |
| 7 | 统计词频（字典计数） | 内置 |
| 8 | 字符串切分与拼接 | 内置方法 |
| 9 | 时间戳与格式化 | `times` |
| 10 | 随机数 / 随机取一个 / 打乱 | `rands` |
| 11 | 安全除法（失败返回 null 而不是崩） | 内置 |
| 12 | 多线程并行处理数组 | `threads` |
| 13 | 读用户输入（交互） | `io` |
| 14 | 结构体 + 方法（数据和行为放一起） | 内置 |
| 15 | 枚举 + `switch`（状态机） | 内置 |

---

## 1. 读写文本文件

```leno
import files
import dirs

main() {
    // 落到临时目录，不污染当前目录（想写到项目里就把 dirs.join 那行换成相对路径）
    var path = dirs.join(_tmpdir(), "leno_note.txt")

    // 写（覆盖）。中文没问题，文件是 UTF-8
    files.write(path, "第一行\n第二行\n")

    // 读
    var text = files.read(path)
    print(text)

    // 按行处理
    for text.lines() to line {
        if line != "" {
            print("行内容：" + line)
        }
    }

    // 用完删掉（失败返回 false，不会抛）
    print(files.delete(path))          // true
}
```

输出：

```
第一行
第二行

行内容：第一行
行内容：第二行
true
```

> ⚠ 读不存在的文件会**抛错**（不返回空串），要容错就用 `try` 或先 `files.exists(path)`。
> 写文件不需要手动关——`files.write/read` 内部就关好了；只有 `files.open()` 那种句柄才要 `defer f.close()`。

---

## 2. 读写 JSON 配置

```leno
import jsons

main() {
    // 造一个对象（字典）再编码
    var cfg = {"name": "小工具", "version": 2, "debug": false}
    var text = jsons.encode(cfg)
    print(text)

    // 解码回来
    var back = jsons.decode(text)
    print(jsons.get_str(back, "name", "?"))
    print(jsons.get_int(back, "version", 0))
    print(jsons.get_bool(back, "debug", true))

    // 直接解一段带嵌套的
    var raw = jsons.decode("{\"db\": {\"host\": \"localhost\", \"port\": 5432}}")
    var db = jsons.get_obj(raw, "db")
    print(jsons.get_str(db, "host", "?"))
    print(jsons.get_int(db, "port", 0))
}
```

输出：

```
{"name":"小工具","version":2,"debug":false}
小工具
2
false
localhost
5432
```

> `jsons.decode` 的静态类型是 `any` ⇒ 取值请用 `get_str/get_int/get_bool`（带默认值，不会因为缺键崩）。

---

## 3. 读命令行参数

```leno
main() {
    var args = _args()
    print("共 " + args.len() + " 个参数")
    for args to a {
        print(" - " + a)
    }
}
```

运行 `leno args.leno hello --list`（**文件名之后的参数才进 `_args()`**）：

```
共 2 个参数
 - hello
 - --list
```

---

## 4. 调用外部命令并拿输出

```leno
main() {
    var r = _exec("cmd /c echo hello_from_shell", 10000)
    if r == null {
        print("起不来子进程")
        return
    }
    print("退出码：" + r.code)
    print("输出：" + r.output.trim())
}
```

输出：

```
退出码：0
输出：hello_from_shell
```

> 第二个参数是**超时毫秒**。超时的退出码是 124（不会和普通失败混在一起）——
> 判断时请显式区分，否则"超时"会被当成"命令失败"。

---

## 5. 读环境变量

```leno
main() {
    // 缺失返回 null
    var home = _env("USERPROFILE")
    if home != null {
        print("主目录：" + home)
    }

    // 缺失给默认值（更常用）
    print("端口：" + _env_or("APP_PORT", "8080"))
    print("模式：" + _env_or("APP_MODE", "dev"))
}
```

输出（APP_PORT / APP_MODE 未设置时）：

```
主目录：C:\Users\Administrator
端口：8080
模式：dev
```

---

## 6. 数组：筛选 / 变换 / 排序 / 求和

```leno
main() {
    var nums = [5, 3, 8, 1, 9, 2]

    // 只留偶数
    var evens = nums.filter(func(int x): bool { return x % 2 == 0 })
    print(evens)                                  // [8, 2]

    // 每个乘 10
    var tens = nums.map(func(int x): int { return x * 10 })
    print(tens)                                   // [50, 30, 80, 10, 90, 20]

    // 升序排（原地）
    nums.sort()
    print(nums)                                   // [1, 2, 3, 5, 8, 9]

    // 求和（结果是 float）
    print(nums.sum())                             // 28.0
    print(_int(nums.sum()))                       // 28

    // 取前三个 / 最后一个
    print(nums[0:2])                              // [1, 2, 3]
    print(nums[nums.len() - 1])                   // 9
}
```

> 区间是**闭区间**：`nums[0:2]` 含 0、1、2 三个元素。

---

## 7. 统计词频（字典计数）

```leno
main() {
    var words = "苹果 香蕉 苹果 橘子 香蕉 苹果".split(" ")
    var counts = {}

    for words to w {
        if counts.has(w) {
            counts[w] = counts[w] + 1
        } else {
            counts[w] = 1
        }
    }

    for counts to k {
        print(k + "：" + counts[k] + " 次")
    }
}
```

输出：

```
苹果：3 次
香蕉：2 次
橘子：1 次
```

> 想按次数排序？字典本身不排序，把 `{键, 次数}` 收进数组再 `sort`（比较器写法见
> [`module_arrays.md`](module_arrays.md) 的 `sort(cmp)`）。

---

## 8. 字符串切分与拼接

```leno
main() {
    var csv = " 张三 , 90 , 北京 "
    var parts = csv.split(",")

    for 0:parts.len() - 1 to i {
        parts[i] = parts[i].trim()
    }

    print(parts)                                  // ["张三", "90", "北京"]
    print(parts.join(" | "))                      // 张三 | 90 | 北京
    print(parts[1].pad_start(4, "0"))             // 0090
    print("ab".rep(3))                            // ababab
    print(csv.replace("北京", "上海").trim())      // 张三 , 90 , 上海
}
```

---

## 9. 时间戳与格式化

```leno
import times

main() {
    var now = times.now()                         // 当前时间戳（整数秒）
    print(times.format(now, "%Y-%m-%d %H:%M:%S"))
    print(times.format(now, "%Y/%m/%d"))
}
```

输出（取决于运行时刻）：

```
2026-11-23 15:04:05
2026/11/23
```

> ⚠ Windows 上 `times.format` **不接受 1970 年之前的负时间戳**（会报错并说明原因），
> 处理历史日期时要自己判一下。

---

## 10. 随机数 / 随机取一个 / 打乱

```leno
import rands

main() {
    rands.seed(42)                                // 固定种子 ⇒ 结果可复现（调试用）

    var dice = rands.ints(1, 6)                   // 1..6 的随机整数
    print(dice)

    var pick = rands.choice(["石头", "剪刀", "布"])
    print(pick)

    // ⚠ shuffle **返回新数组**，不会原地打乱
    var deck = [1, 2, 3, 4, 5]
    var shuffled = rands.shuffle(deck)
    print(shuffled)
    print(deck)                                   // 原数组不变
}
```

输出（实测）：

```
1
剪刀
[1, 5, 4, 3, 2]
[1, 2, 3, 4, 5]
```

> 说明：前两个数在 `seed(42)` 下是**稳定**的；`shuffle` 的结果取决于"前面已经消耗了多少随机数"
> （上面先取了 1 个数、再 `choice` 一次），所以在别处照抄这一段时排列可能不同——这是正常的，
> 不是不确定行为。



---

## 11. 安全除法（失败返回 null 而不是崩）

```leno
main() {
    print(safe_div(10.0, 4.0))     // 2.5
    print(safe_div(10.0, 0.0))     // null

    var r = safe_div(9.0, 0.0)
    if r == null {
        print("除数为 0，我不算")
    } else {
        print(r)
    }
}

func safe_div(float a, float b): float? {
    if b == 0.0 {
        return null                             // 显式"没有结果"
    }
    return a / b
}
```

> 返回类型写 `float?`（可空），调用方必须 `if r == null` 判一下才能用——
> 不判而直接参与算术，编译器会警告。

---

## 12. 多线程并行处理数组

```leno
import threads

main() {
    var data = [1, 2, 3, 4, 5, 6, 7, 8]

    // threads.map：每个元素一个线程跑，结果按原顺序回来
    // ⚠ 回调**必须写两个形参** (元素, 下标) —— 与 `arrays.map` 同口径；
    //   只写一个形参会在编译期报「实际传了 2 个（多 1 个）」
    var doubled = threads.map(data, func(int x, int idx): int {
        return x * 2
    })
    print(doubled)                              // [2, 4, 6, 8, 10, 12, 14, 16]
}
```

> 线程里**改外部局部变量不会回传**（各线程各一份）——要结果就用返回值（像上面这样）。
> 跨线程共享可变状态请用 `threads.channel()`，详见 [`并发选择指引.md`](并发选择指引.md)。

---

## 13. 读用户输入（交互）

```leno
import io

main() {
    var name = io.input("你叫什么名字？ ")
    var age = io.input("你多大了？ ")
    print("你好，" + name + "！明年你 " + (_int_or(age, 0) + 1) + " 岁。")
}
```

运行示例（输入 `小明` 和 `12`）：

```
你叫什么名字？ 小明
你多大了？ 12
你好，小明！明年你 13 岁。
```

> 用 `_int_or(age, 0)` 而不是 `_int(age)`：用户随手打字打错了也不会让程序崩。

---

## 14. 结构体 + 方法（数据和行为放一起）

```leno
struct Counter {
    int value = 0

    func add(int n) {
        self.value = self.value + n
    }

    func reset() {
        self.value = 0
    }

    func show(): string {
        return "当前值：" + self.value
    }
}

main() {
    var c = new Counter()
    c.add(3)
    c.add(4)
    print(c.show())        // 当前值：7
    c.reset()
    print(c.show())        // 当前值：0
}
```

> ⚠ 结构体字段**必须写具体类型**（`int value = 0`），不能写 `var`。

---

## 15. 枚举 + switch（状态机）

```leno
enum State {
    idle = 0
    running = 1
    failed = 2
}

func describe(int st): string {
    switch st {
        case State.idle { return "空闲" }
        case State.running { return "运行中" }
        case State.failed { return "失败" }
    }
    return "未知"
}

main() {
    var s = State.running
    print(describe(s))                       // 运行中

    var bad = 9
    print(describe(bad))                     // 未知（switch 全都落空 ⇒ 走到 return "未知"）

    // 带载荷的枚举（成员可带数据 + switch 能查穷尽性）
    print(msg_text(build_msg()))
}

enum Msg {
    progress(int done, int total)
    finished(string path)
}

func build_msg(): Msg {
    return Msg.progress(3, 10)
}

func msg_text(Msg m): string {
    switch m {
        case Msg.progress(d, t) { return "进度 " + d + "/" + t }
        case Msg.finished(p)    { return "完成：" + p }
    }
    return "?"
}
```

输出：

```
运行中
未知
进度 3/10
```

---

## 还想做点什么？

| 想做 | 看这篇 |
|---|---|
| 语法还没摸清 | [`Leno零基础入门.md`](Leno零基础入门.md) |
| 部署/打包/装环境 | [`安装与第一个项目.md`](安装与第一个项目.md) |
| 某个模块的全部函数 | `module_*.md`（arrays / strings / files / jsons …） |
| 报错看不懂 | [`语言陷阱速查.md`](语言陷阱速查.md) |
| 写并发 / 协程 | [`并发选择指引.md`](并发选择指引.md)、[`async_await入门指南.md`](async_await入门指南.md) |
| 调 C 库 / 操作原生内存 | [`FFI使用指南.md`](FFI使用指南.md)、[`module_cstructs.md`](module_cstructs.md) |
| 做图形界面 | [`LenoSDL3_控件实战教程.md`](LenoSDL3_控件实战教程.md) |

---

> **这篇的每段代码都被机器验过**：`verify_doc_code.ps1` 会把文档里每个含 `main()` 的代码块
> 抽出来、用真编译器跑一遍，有任何一块不通过就报错。改了本文档请顺手跑：
>
> ```bat
> powershell -NoProfile -ExecutionPolicy Bypass -File verify_doc_code.ps1
> ```
>
> 实测当前：`ran=86 fail=0`（三篇新手文档合计）。
