# `_freeze` 使用指南：大对象跨线程零拷贝

> 适用版本：0.2.4 之后（2026-11-27 起 `_freeze` / `_thaw` / `_is_frozen` / `Frozen[T]`）
> 设计原理与实现细节在 [`大对象零拷贝共享设计.md`](大对象零拷贝共享设计.html)；本文只管**怎么用**。

---

## 1. 一句话

跨线程传数据默认是**深拷贝**（`Array` 1 万元素 = 拷 1 万次）。
`_freeze(x)` 把数据**一次性**拷到共享区并标成只读，之后每次跨线程传递只做一次引用计数（O(1)），**不再拷贝**。

**该用**：

- 同一份大只读数据要被**多次**跨线程传递 / 每个任务都要用（`map`、`parallel_for`、Channel 反复 send）；
- 数据量可观（经验值：**> 10 KB** 或 **> 1000 个元素**）；
- 内容是**只读**的（配置表、字典、图片字节、预计算结果、词表）。

**不该用**：

- 只传一次的小对象 —— `_freeze` 本身是 O(n)，比直接深拷贝还多一次扫描；
- 传过去要**改**的数据 —— frozen 是只读的，要改就传可变值（默认路径）或 `_thaw` 出副本；
- 含 `Ptr` / `cstruct` / `File` / `Channel` / `Atomic` / 闭包的数据 —— 编译期就会拒（见 §6）。

---

## 2. 最小例子

```leno
import threads

main() {
    // ① 造数据（可变的，随便改）
    var rows = []
    for 0 : 99999 to i { rows.add(i) }

    // ② 冻结：一次性 O(n)，之后只读
    Frozen[Array[int]] snap = _freeze(rows)

    print(_str(snap.len()))     // 100000 —— 读法和普通数组完全一样
    print(_str(snap[123]))      // 123
    print(_str(_is_frozen(snap)))   // true

    // ③ 原对象不受影响，照常可写（快照语义）
    rows.add(-1)
    print(_str(rows.len()))     // 100001
    print(_str(snap.len()))     // 100000
}
```

一条命令验证：

```
build\leno.exe 你的文件.leno
```

---

## 3. 三条语义（记住这三条就够）

| 语义 | 含义 |
|---|---|
| **快照** | `_freeze` 返回**新图**，原对象一个字都不动。冻结之后改原对象，冻结的那份不变 |
| **深** | 整图一起冻：数组元素、字典的**键和值**、struct 的每个字段，嵌套多深都冻 |
| **只读** | 对 frozen 的任何原地修改都会报错（编译期能判就编译期，否则运行期） |

想拿回一份**可写**副本：

```leno
Array[int] copy = _thaw(snap)     // 深拷贝回本线程堆
copy.add(42)                      // 现在可以改了
```

`_thaw` 是 O(n)，别放在热循环里。

---

## 4. 类型怎么写：`Frozen[T]`

`_freeze(x)` 的静态类型是 `Frozen[T]`（`T` 是 `x` 的类型）：

```leno
Frozen[Array[int]]            a = _freeze([1, 2, 3])
Frozen[Dict[string, int]]     d = _freeze(m)
Frozen[Array[Array[int]]]     g = _freeze(grid)
Frozen[Point]                 p = _freeze(new Point(x = 1))
```

**关键点：类型要进函数签名**，这样"能不能写"在编译期就有定论：

```leno
// ✅ 传进来就保证只读；函数体里写它会**编译不过**
func total(Frozen[Array[int]] xs): int {
    var s = 0
    for xs to v { s = s + v }
    return s
}

// ❌ 形参写成 Array[int]，函数体里就能写；把 frozen 传进来会**编译不过**（类型不兼容）
func bad(Array[int] xs) { xs.add(1) }
```

`Frozen[...]` 与 `T` **双向不兼容**，必须显式 `_freeze` / `_thaw`：

```leno
Array[int] m = snap        // ✗ 类型错误：Frozen[Array[int]] 不能赋给 Array[int]
Array[int] m = _thaw(snap) // ✓ 要可变副本就明说
Frozen[Array[int]] f = arr // ✗ 错误：必须 _freeze() 得到（否则"只读保证"是假的）
```

> 为什么不让可变值直接"当成" frozen 传：那样函数里读着"只读"类型，外面却在改，静态保证立刻变假。

---

## 5. 三个典型场景

### 5.1 `map` / `parallel_for` 共享只读数据集

```leno
import threads

Frozen[Array[int]] 词表 = _freeze(load_words())     // 只冻一次

main() {
    var idx = []
    for 0 : 999 to i { idx.add(i) }

    var hits = threads.map(idx, func(int i, int no) {
        // 每个任务都读同一份词表 —— 零拷贝，不占额外内存
        return 词表[i % 词表.len()]
    })
    print(_str(hits.len()))
}
```

> ⚠ `threads.map` 的回调是 **(元素, 下标)** 两个参数，写一个参数会报"入口函数期望 1 个参数，实际传了 2 个"。

### 5.2 Channel 传大块数据

```leno
import threads

var req = threads.channel(1)
var res = threads.channel(1)

func worker(any c) {
    if c is Channel {
        var got = c.receive()
        if got is Array[int] => a {          // 收到的是同一张冻结图
            res.send([a.len(), _is_frozen(a)])
        }
    }
}

main() {
    var big = []
    for 0 : 99999 to i { big.add(i) }
    Frozen[Array[int]] snap = _freeze(big)

    var t = threads.start(worker, req)
    req.send(snap)                            // 5 µs 左右，与元素数无关
    var r = res.receive() as Array[any]
    print(_str(r[0]) + " frozen=" + _str(r[1]))
    t.join()
}
```

接收侧读法：`receive()` 的静态类型是 `any`（裸 `Channel`），用 `is Array[int]` 收窄；要判断它是不是冻结的，用 `_is_frozen(a)` —— **`a is Frozen[...]` 不支持**（见 §6）。

### 5.3 模块级预计算表

```leno
Frozen[Dict[string, int]] 词频 = _freeze(build_table())   // 模块顶层冻一次

func score_of(string w): int {
    return 词频.get(w, 0)
}
```

子线程 start 时会克隆 globals，但 frozen 只加一次引用 ⇒ N 条线程不会拷 N 份。

---

## 6. 编译期就会拦下来的（不用等运行期）

| 写法 | 结果 |
|---|---|
| `snap[0] = 9` / `snap.f = 1` / `snap += 1` | ✗「不能修改 Frozen[Array[int]] 的元素 / 字段 —— frozen 是**整体不可变**」 |
| `snap.add(1)` / `snap.sort()` … | ✗「不能对 Frozen[Array[int]] 调用修改方法 'add'」 |
| `func g(Frozen[Array[int]] p) { p.add(1) }` | ✗ 同上（形参带 frozen，体内写直接报） |
| frozen struct 上调用 `mut func` | ✗ 同上（判据来自 `mut` 声明） |
| `Array[int] m = snap` / 传给 `Array[int]` 形参 | ✗ 类型不匹配 |
| `snap is Frozen[Array[int]]` / `x as Frozen[...]` | ✗ 显式禁止（运行期只有对象标签，会给错答案） |
| `_freeze(ptr)` / `_freeze(ch)` / `_freeze(atomic)` / `_freeze(闭包)` | ✗「不能冻结 'Ptr'：裸内存/原生指针…」 |

> 想吃准文案：把错误代码丢给 `leno.exe --check 文件.leno`，报错里会直接写为什么。

---

## 7. 只能运行期拦的（类型系统看不见的路径）

| 场景 | 表现 |
|---|---|
| `var v = snap[0]` 之后 `v.add(1)` | 元素类型本身不带 frozen 位 ⇒ 运行期抛「冻结对象（frozen）不可修改」 |
| 把 frozen 塞进 `any` 再收窄去写 | 同上（运行期 `FROZEN` 位兜底） |
| `_freeze(any_val)` 里装的是 Ptr/Channel… | 运行期抛「不能冻结 …」 |
| 数据里**含环**（`a.add(a)`） | 运行期抛「冻结失败：嵌套超过 64 层（可能含循环引用）」 |
| struct 的类型定义是**子线程**加载的 | 运行期抛「…def 是在子线程里创建/加载的…」 |

运行期文案统一含 **`冻结对象（frozen）不可修改`**，`catch` 里可以按这个片段判。

---

## 8. 常见错误 → 怎么改

**① 「不能修改 Frozen[Array[int]] 的元素」**
你冻了又想改。要么改原对象（`_freeze` 之前那份），要么 `_thaw()` 出副本：

```leno
Array[int] work = _thaw(snap)
work[0] = 9        // ✓ 改副本
```

**② 「类型错误：变量 'm' 声明类型与初始化值类型不匹配 / 期望 Array[int]，实际 Frozen[Array[int]]」**
明确写出转换：

```leno
Frozen[Array[int]] m = _freeze(a)     // 只读用
Array[int]          c = _thaw(m)      // 要改就解冻
```

**③ 「`is` 不支持 Frozen[...]」**
改判冻结状态用 `_is_frozen(x)`；判"是不是数组"用 `x is Array[int]`（frozen 也匹配，因为底层还是数组）。

**④ 「不能冻结 'Channel'」**
Channel 是跨线程**可变**通道，不能冻。要共享数据请冻**数据本身**，Channel 只用来交班。

**⑤ 「冻结 struct 失败：…def 是在子线程里创建/加载的」**
在主线程先把该模块加载起来（`import` 或 `main` 里触达一次），再冻结实例；或在**模块级**声明这个 struct。

**⑥ 冻完发现子线程改不动、还报错**
这不是 bug：frozen 就是只读。子线程要产出结果，请**返回新值**（Channel / `map` 的返回值），不要原地改共享数据。

---

## 9. 性能（本机实测，`build\leno.exe`）

| 场景 | 数字 |
|---|---|
| `_freeze` 10 万元素 `Array[int]` | **0.6 ms**（一次性） |
| 同一冻结图 `send` 一次 | **~5 µs**（与元素数无关） |
| 10 万 × 100 次跨线程传递 | frozen **26.9 ms** vs 可变深拷贝 **138.7 ms** ⇒ **5.2×** |
| 200 个池任务各冻 1000 元素、用完就丢 | `_gc_stats()["frozen_objs"]` 增长 **≤8**（任务结束自动收敛） |
| 内存 | N 条线程读同一份 100 MB 数据 ⇒ 峰值 ≈ 100 MB（不是 N×100 MB） |

看账：

```leno
var st = _gc_stats()
print("frozen 对象 " + _str(st["frozen_objs"]) + "，字节 " + _str(st["frozen_bytes"]))
```

---

## 10. 边界（都是有意为之）

1. **主线程注册表持有到进程结束**：反复 `_freeze` 不同数据不会自动回收，`frozen_bytes` 会累加。
   用法上"**冻一次、长期复用**"；确实要反复冻，注意这部分内存不随 GC 回落。
2. **池任务别把 frozen 存进 worker 的长期状态**（模块级 var / TLS）：任务结束会收敛引用，
   存下来的是个"随时会被放掉"的指针。要缓存就自己持有并确保同一份图被复 freeze。
3. **`_freeze` 是快照，不会去重**：同一份数据冻两次就是两份。要复用就存变量。
4. **含环的数据不能冻**（引用计数回收不了环）。
5. **半冻结**（可变数组里夹一个 frozen 子数组）是支持的：外层可变、内层只读，
   跨线程时外层深拷贝、内层零拷贝。
6. **别在热循环里 `_thaw`**：它是 O(n) 深拷贝，等于把零拷贝的收益吐回去。

---

## 11. 选择表：frozen 还是普通传值？

| 你的数据 | 建议 |
|---|---|
| 小对象 / 只传一次 | 不用 frozen，直接传（深拷贝） |
| 大 + 只读 + 传多次 | **frozen** |
| 大 + 每个线程各改各的 | 不用 frozen：深拷贝本来就是对的（副本隔离） |
| 大 + 需要**共享可变**（计数器 / 队列） | 用 `Atomic` 或 `Channel`，**不要** frozen |
| 大 + 传一次就丢 | 深拷贝即可（frozen 多一次 O(n) 冻结） |

---

### 相关文档

- 线程模型与跨线程规则：`threads使用指南.html`
- 原理 / 实现 / 踩坑记录：`大对象零拷贝共享设计.html`
- 修复追踪（TH19）：`线程并发能力修复追踪.html`
