# Leno 与其他语言对比（Python / JS / Go）

> 一句话：读起来像 **Python 的表达式 + JS 的可选链/异步 + Go 的类型与接口**，
> 但"符号分工、类型规则、多返回值协议、enum 双形态、GC struct 与裸 cstruct 的二分"
> 是 Leno 自己的契约，不是拼盘。
>
> 本文每一条都在 `build\leno.exe` 上实测或对着 `src/` 源码核过。
> 凡标 **实测** 的是运行结果，不是推测；凡标 **有意不做** 的是设计取舍，不是缺口。

---

## 一、怎么读

约定：

- `✔` 支持且语义与对照语言一致
- `~` 支持但语义不同（后面必定有一节解释）
- `✘` 没有

对照语言只说"通常怎么写"，不追求覆盖它们的全部写法。

---

## 二、总览对照

| 概念 | Python | JS / TS | Go | Leno | 关键差异 |
|---|---|---|---|---|---|
| 逻辑运算 | `and/or/not`，返回操作数，空值算假 | `\|\|/&&/!`，返回操作数，空串算假 | `&&/\|\|/!`，恒 bool | `and/or/not` | ~ 返回操作数但**静态类型按 bool**；`&&`/`\|\|` 词法层直接报错 |
| 三目 | `a if c else b` | `c ? a : b` | 无 | `if c then a else b` | ~ 复用 `if/then/else` 关键字，没有 `?:` |
| else if | `elif` | `else if` | `else if` | `eif` | ~ 单独一个关键字 |
| 可空 | `None` + 运行时判空 | `T \| null`（TS，`strictNullChecks`） | 指针 / `sql.Null*` | `T?` + `?.` `??` `??=` | ~ 值类型**不能**为 null，编译期拦 |
| 接口 | 抽象基类 / Protocol | `interface` | `interface` | `face` + `impl` | ~ 没有继承，只有"struct 实现 face" |
| 继承 | class 多继承 | class 单继承 | 组合（无继承） | **没有** | ~ 字段组合 + `extend` 分写方法 |
| 多返回值 | 元组 | 数组 / 对象解构 | 原生多返回值 | `[T1, T2]` + `var[T1,T2](a,b)` | ~ 类型化的解构协议，不是元组值 |
| 枚举 | `Enum`（值可以是任意类型） | `enum`（数字/字符串） | `const iota` | `enum` 双形态 | ~ 纯 int 常量，或带载荷变体；**同一 enum 不能混用** |
| 列表 | `list` | `Array` | slice | `Array[T]` | ✔ |
| 字典 | `dict` | `Map` / `Object` | `map[K]V` | `Dict[K,V]` | ~ 键统一是 `string` |
| 集合 | `set` | `Set` | `map[T]struct{}` | **没有** | ✘ 用 `Dict[string,bool]` 代替 |
| 元组 | `tuple` | 无（数组代替） | 无 | **没有元组值** | ✘ 多返回值不是元组；要打包用 `struct` |
| 切片区间 | `[a:b]` 左闭右开 | `slice(a,b)` 左闭右开 | `[a:b]` 左闭右开 | `[a : b]` **闭区间** | ~ 两端都含；负终点结果是空 |
| 循环 | `for x in xs` / `range` | `for...of` | `for range` | `for xs to x` / `for 0 : 9 to i` | ~ `to` 后面是**循环变量名** |
| 错误处理 | 异常 | 异常 | `(v, err)` 返回值 | `throw` / `try` `catch` `finally` / `defer` | ~ `throw` 任意值，运行时统一包成异常对象 |
| 并发 | `asyncio` / 线程 | 事件循环 / Worker | goroutine + channel | `threads` + `Channel`；另有 `async/await` | ~ 两条独立轨道，不互相转换 |
| 字符串插值 | f-string | 模板串 | 无（`fmt.Sprintf`） | `$"Hi {name}"` | ✔ 还带格式说明符 `{x:.2f}` |
| 裸内存 | `ctypes`（外挂） | 无 | `unsafe.Pointer` | `cstruct` / `union` / `Ptr[T]` | ~ 是**语言级**语法，不是外挂库 |
| 泛型 | 3.12 起 | TS 泛型 | 1.18 起 | `Box[T]` / `[T: 约束]` / `[T = 默认]` | ✔ 约束只能是 face 名或具体类型 |

---

## 三、十处"长得像、语义不同"

### 1. `and` / `or`：只当条件用，**别当默认值**

```leno
var a = 0 or "abc"      // 运行期 => "abc"（string）
var b = 1 and 2         // 运行期 => 2（int）
var c = not 0           // 运行期 => true（bool，恒 bool）
```

运行期确实返回**操作数本身**（和 Python 一样），但**静态类型不是操作数类型**：

| 写法 | 实测结果 |
|---|---|
| `string s = "" or "默认"` | 编译错误：`期望类型: string / 实际类型: bool` |
| `int x = 0 or "abc"` | 编译通过，**运行期崩溃**：`CAST_INT: 操作数必须是数字（拿到 string "abc"）` |
| `var name = input or "默认"` 之后 `name.len()` | 推断成 `any` ⇒ `不能在 any 类型上调用方法 'len'` |

结论：`x or default` 这个 Python 惯用法在 Leno 里**不能用**。

```leno
// ✘ 别这么写
string name = input or "匿名"

// ✔ 要默认值就写清楚
string name = if input == "" then "匿名" else input
// ✔ 或者用可空 + 空值合并（?? 只对可空生效）
string? input = try_get()
string name = input ?? "匿名"
```

`&&` / `||` / `!` 不走"兼容通道"，词法层直接报错并给出替代写法：

```
error: 意外的字符 '&&'，请使用 'and' 关键字表示逻辑与
```

### 2. 真值口径：**空字符串、空数组、空字典都算真**

只有这些是假（`val_is_truthy`，`src/include/leno_value.h`）：

`false`、`0`、`0.0`、`null`、空的 `Ptr`。

```leno
"" or 7                     // => ""    （不是 7！空串为真）
Array[int] e = []
e or 7                      // => []    （空数组也为真）
if e { … }                  // 条件为真 ⇒ 会进分支（实测）
```

这跟 Python / JS 是**反的**。判断"空不空"要显式写：

```leno
if s.len() == 0 { … }
if arr.len() == 0 { … }
```

### 3. 切片与区间：一律**闭区间**，负终点是空

| 写法 | 语义 |
|---|---|
| `arr[1 : 2]` | 含下标 1、2（**两个**元素） |
| `s.slice(0, 2)` | `"hel"` |
| `for 0 : 9 to i` | 跑 10 轮（`to` 后面是**循环变量名**，不是终点） |
| `switch case 1 : 4` | 命中 1、2、3、4 |

负下标只有**起点**有意义（从末尾数）；**负终点结果恒为空**，编译器给警告：

```leno
arr[-3 : 2]                  // 倒数第 3 个 → 下标 2
arr[0 : -1]                  // [] （空，不是"去掉最后一个"）
arr[0 : arr.len() - 2]       // 要"去掉最后 N 个"这样写
```

> 全仓口径见 `区间口径约定.html`。参数名是 `n` / `len` / `count` 的是**长度**，不是端点。

### 4. 多返回值是**语言协议**，不是元组

```leno
func get_user(): [int, string] { return 42, "Alice" }

var[int, string](id, name) = get_user()
print(_str(id) + " " + name)
```

- 返回类型写成 `[T1, T2]`，解构写成 `var[T1, T2](a, b)`；
- 返回类型也可以带**键名**（键名目前只是说明性信息，解构仍按位置 —— 实测
  `var[bool,int](ok,n)` 拿到 `true, 3`）：

```leno
func stat(): {"ok": bool, "count": int} { return true, 3 }
var[bool, int](ok, n) = stat()
```

- **没有元组值**：不能把 `(1, "a")` 存进变量、不能作为元素放进 `Array`。
  要"打包成一个值"就用 `struct`（内存里一律 `Array[struct]`）。

### 5. 可空是**类型的一部分**，值类型挂不上 null

```leno
int?  a = null       // ✔
int   b = null       // ✘ 编译错误：变量 'b' 是 int（非可空），不能赋 null
```

实测报错还带三条提示（告诉你怎么改、以及为什么这么设计）。相关运算符：

```leno
obj?.field           // 安全访问（只对可空生效）
var x = a ?? 0       // 空值合并
acc ??= 1            // 空值合并且赋值
if a is int => v { … }   // 收窄 + 一次绑定，v 在分支里就是 int
```

`any` 的用法比 TS 窄：**不能声明局部变量**（只能做参数/返回类型）。

```
error: 'any' 类型只能用于函数参数和返回类型，变量声明请使用 'var' 或指定具体类型
```

### 6. 结构体 + face + extend：没有 class 继承

| 语言 | 复用方式 |
|---|---|
| Java / C# | class 单继承 + interface |
| Python | 多继承 + 鸭子类型 |
| Go | 结构嵌入 + 隐式接口 |
| Rust | struct + impl trait |
| **Leno** | `struct` 字段组合 + `face` 显式 `impl` + `extend` 跨文件写方法 |

```leno
struct Player { string name = ""; int hp = 100 }

export struct Player impl Drawable {
    func draw(Canvas c) { … }
}

// 另一个文件，甚至另一个模块
extend Player {
    func heal(int n) { hp = hp + n }
}
```

- 构造 `func Player()`、析构 `func ~Player()`（写 `__del__` / `destructor` 会得到定向报错）；
- 字段默认全公有，`pri` 是**真私有**（编译期拦，不是命名约定）；
- 没有虚函数表/继承链，多态靠 `face` 值 + `case is Type` 分派。

### 7. enum 双形态，而且**不能混用**

```leno
// 形态 A：纯 int 常量（和 Go iota / C enum 同气质）
enum Color { red; green; blue }
int c = Color.red

// 形态 B：带载荷（和 Rust / OCaml 的变体接近）
enum Msg { progress(int done, int total); finished(string path) }
```

规则刻意窄：

- 同一个 enum 里**要么全带参数、要么全不带**；
- 带载荷的成员**不是 int**（`int x = Msg.progress(1,2)` 报错，也不能 `new Msg(...)`）；
- 带载荷 enum 的 `switch` 主题必须是**变量**，漏成员且无 `default` ⇒ 穷尽性警告；
- `==` 按值比较；`jsons.encode` 输出成员名（`{"progress":{"done":3,"total":10}}`）。

`switch` 本身没有 fallthrough，命中即跳出，`break` 用来"提前离开整个 switch"。

### 8. 集合：Array / Dict 是内置的，容器在扩展模块

内置（不需要 import）：

```leno
Array[int] a = [3, 1, 2]
a.add(4)  a.pop()  a.insert(0, 9)  a.remove(1)
a.has(3)  a.index_of(1)  a.sort(cmp)  a.reverse()
a.map(func(int x) { return x * 2 })
a.filter(func(int x) { return x > 1 })
a.reduce(func(int acc, int x) { return acc + x }, 0)
a.join(",")  a.sum()  a.flatten()  a.copy()

Dict[string, int] m = {"a": 1}
m.put("b", 2)  m.get("b", 0)  m.has("a")  m.keys()  m.values()
```

- `Array` 的方法就是上表这些（**没有** `slice` / `contains` / `first`，切片走 `[a:b]` 语法）；
- `Dict` 的键是 `string`；
- **没有 List**（Array 兼任）、**没有 Set**（`Dict[string,bool]` 代替）；
- 栈/队列/双端队列/优先队列/三种 LRU 在 `LenoContainers` 模块：

```leno
import "Containers" as ct
var st = new ct.Stack[int]()
st.push(1)
for st to v { print(v) }     // 容器实现了 Iterable ⇒ 直接遍历元素
```

### 9. 错误处理：throw 任意值，但统一变成异常对象

```leno
try {
    risky()
} catch e {
    print(e.msg)         // e 是 Dict{msg, file, line, stack}
    print(e.stack)
} finally {
    cleanup()
}
```

- `throw` 可以抛任意值（字符串、int、甚至一个 struct）；到 `catch` 时**统一包装**成
  带 `msg / file / line / stack` 的异常对象 —— 所以 `catch e` 的类型永远一致；
- 已经是异常对象的值会**原样抛出**（位置保留在真正出错的地方，不被改写成"接住它的那行"）；
- 与 Go 的 `if err != nil` 不同：错误走控制流，不是返回值。

`defer` 是块级清理（不是 Go 的函数级）：

```leno
Ptr p = ffi.malloc(4)
defer ffi.free(p)      // 所在 {} 退出时执行；多个 defer 逆序
```

### 10. 字符串：插值、原始串、格式说明符

| 写法 | 含义 |
|---|---|
| `$"Hi {name}"` | 插值 |
| `@"C:\path\to"` | 原始串（不转义） |
| `$@"Hi {name} \n"` | 原始 + 插值 |
| `$"pi={x:.2f}"` | 带格式说明符，脱糖成 `format("%.2f", x)` |

格式说明符是**编译期校验**的（`{n:y}`、`{pi:.2F}` 这类手误直接报错，不会静默输出垃圾）。

字符串函数先查标准库，别自己写：

```leno
strings.pad_start(_str(v), 2, "0")   // "07"
strings.split(s, ",")
strings.trim_unicode(s)              // 认全角空格 / NBSP
strings.lines(s)                     // 按行切，认 \r\n
strings.fmt_size(1536)               // "1 KB"
```

---

## 四、符号一览（按符号查语义）

| 符号 | 位置 | 语义 |
|---|---|---|
| `=>` | 控制流 | 类型守卫的一次绑定：`if x is T => v`、`case is T => v` |
| `=>` | 表达式 | 单表达式匿名函数：`x => x + 1`、`(int a, int b) => a * b` |
| `?.` | 表达式 | 可空安全访问 |
| `??` | 表达式 | 空值合并 |
| `??=` | 语句 | 空值合并且赋值 |
| `:` | 类型 | `name: int?`、`T: Face`（泛型约束）、`[T = int]`（默认） |
| `:` | 切片 / case | 闭区间：`arr[a : b]`、`case 1 : 4` |
| `:` | 插值 | 格式说明符：`$"{x:.2f}"` |
| `~` | 方法名 | 析构：`func ~Player()` |
| `@` | 声明前 | 注解：`@optkeys(["visible:bool"])`；`@"..."` 是原始串 |
| `$` | 字符串 | 插值前缀 |
| `mut` | 方法 | 结构性修改：`mut func push(v)`；在 `for` 里调用会得到 `WARN_ITER_MUTATE` |
| `eif` | 语句 | `else if` |
| `pri` | 字段/方法 | 真私有（编译期拦） |
| `defer` | 语句 | 块级延迟执行（逆序、降级成 try/finally） |

箭头函数的边界（实测）：**只能单表达式**。写返回类型 `(int x): int => …` 或块体 `x => { … }`
都会得到定向报错 —— 要这些就用 `func`。

---

## 五、没有的东西（诚实清单）

| 没有 | 替代 |
|---|---|
| class / 继承 / 虚方法 | `struct` 组合 + `face` + `case is Type` |
| `List` | `Array` |
| `Set` | `Dict[string, bool]` |
| 元组值 | 多返回值（`[T1,T2]`）或 `struct` |
| `&&` `\|\|` `?:` `!` | `and` `or` `if…then…else` `not`（词法层拒绝，不是风格问题） |
| switch fallthrough | 命中即跳出 |
| 字符串值枚举 | `export const` / `Dict`（有意不做） |
| IANA 时区名 | `times.utc_offset` 自己加减秒（只有本地/UTC 两种口径） |
| `gcd` / `lcm` / `is_prime` / `factorial` / `cbrt` / `comb` | 自己写（标准库确实没有） |

---

## 六、运行时气质（决定"写起来的感觉"）

| 项 | 现状 |
|---|---|
| VM | **寄存器式**，4 字节定长指令（op + A + B + C，各 8 位） |
| 寄存器上限 | 号 ≥ 256 是**编译硬错误**（曾经静默截断 ⇒ 读到别的槽位） |
| 值表示 | NaN-boxing，`Value` 8 字节；整数内联 **int48**（约 ±1.4e14），超了自动升 BigInt |
| GC | 分代 + 写屏障（remembered set） |
| 产物裁剪 | 方法级 DCE，**只在入口 `.lenb` 序列化时**剪（`.leno` 直跑不剪），`LENO_NO_DCE=1` 可关 |
| 分支 | `switch` ≥ 16 个互不相同的整型 case 自动变二叉比较树（100 case 实测 66ms → 21ms） |
| 并发 | `threads` 真线程 + `Channel`；`thread_local var` 每线程一份；另有 `async/await` 协程 |
| FFI | `cstruct`/`union`/`Ptr[T]` 是语言级语法，`free()`/`free_all()` 手动管内存 |

线程模型有一处与 Go 差别很大：**闭包捕获是副本**。

```leno
int progress = 0
threads.start(func() { progress = 100 })   // ✘ 改的是副本，外面还是 0，且不报错
```

线程入口必须是**模块级函数**，结果走 `Channel` 回来；缓存/表一律用 `thread_local var`。
（详见 `threads使用指南.html`、`module_threads_api.html`。）

---

## 七、从各语言过来，最容易踩的 5 条

### 从 Python

1. `and/or` **不能当默认值**（见三.1），`x or default` 编译报错或运行期崩；
2. **空串/空列表为真**（三.2），`if not s:` 要写成 `if s.len() == 0`；
3. 切片是**闭区间**（三.3）：`arr[0:2]` 是**两个**元素（含下标 2）；
4. 没有元组 — 多返回值是类型化协议，不能存进变量（三.4）；
5. 变量有静态类型：`var` 能推断，但 `int a = null` 直接编译错误（三.5）。

### 从 JS / TS

1. `&&` `||` `?:` **写不出来**（词法报错），换 `and` `or` `if…then…else`；
2. 可空要显式写 `T?`，`undefined` 不存在，只有 `null`；
3. `any` 只能出现在函数签名上，局部变量用 `var` 或具体类型；
4. 数组方法不是 JS 那套：没有 `slice`/`includes`/`sort()` 无参版，切片用 `[a:b]`，
   `sort` 必须给比较器（返回 bool 是运行期错误）；
5. 对象不是字典：`struct` 是编译期字段表（字段名写错直接编译失败），动态键值用 `Dict`。

### 从 Go

1. 错误不是返回值，是 `throw`（`catch e` 给 `msg/file/line/stack`）；
2. `defer` 是**块级**，不是函数级 —— 写在循环里每轮都执行；
3. 接口叫 `face`，且必须显式 `impl`（没有隐式满足）；
4. 多返回值要写返回类型 `[int, string]`，解构是 `var[int,string](a,b)`；
5. 没有 goroutine/channel 那种"轻量并发"：`threads` 是真线程 + 深拷贝传值，
   要共享内存得自己上锁或用 `thread_local`。

---

## 八、一句话

Leno 的**读法**像 Python + JS，**写法**上更接近 Go / Rust（显式类型、显式 impl、
显式解构），而**内存模型**是"GC struct + 裸 cstruct"两套并列 —— 目标是一边写业务、
一边能直接 FFI 接 SDL3 和 C 库，不用外挂 ctypes / FFI 绑定生成器。
