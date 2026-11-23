# reflect 模块

运行期**只读反射**：把编译器早就写进字节码的类型元数据（字段名、字段声明类型、方法名）
在脚本里开放出来。

```leno
import reflect
```

> **一句话定位**：`jsons.fill` / `jsons.encode` 一直在用这些元数据，但只有 C 侧能读。
> `reflect` 把同一份数据开放给脚本，于是"通用序列化 / 表单 / 表格列 / 文档生成"
> 可以写一次，而不是每个 struct 抄一遍。

---

## 为什么需要它

在这之前，想拿"一个 struct 有哪些字段"只有两条路：

```leno
// ❌ 手抄字段名：加字段忘了改这里，不报错，只是少一行
Array[string] COLS = ["id", "name", "size"]

// ❌ 每个类型写一份 to_dict
func song_to_dict(Song s):Dict[string, any] {
    return {"name": s.name, "dur": s.dur}
}
```

两种都是"抄漏一处不会错，只会少东西"。而编译器**本来就知道** —— `ObjStructDef` 里有
字段名、字段声明类型、`Array[Item]` 的元素 struct 名、`Dict[K,V]` 的键值类型、
完整容器类型树（`Array[Array[int]]` 也逐层记录）、可空标记、泛型实参名、方法表。

`reflect` 只是把那层数据原样读出来，不引入任何新机制、不改字节码格式。

---

## API 总表

| 方法 | 签名 | 说明 |
|---|---|---|
| `reflect.kind(v)` | `(any) -> string` | 宽类别，见下表。**对任意值都有定义**，不抛错 |
| `reflect.type_name(v)` | `(any) -> string` | 有声明名的给声明名（`"Song"` / `"Vec2"`），其余与 `kind` 同名 |
| `reflect.fields(v)` | `(any) -> Array[string]` | 字段名，**按声明顺序**（与 `jsons.encode` 的顺序同源） |
| `reflect.field_count(v)` | `(any) -> int` | 字段个数 |
| `reflect.has_field(v, name)` | `(any, string) -> bool` | 有没有这个字段。**探测用，不抛错** |
| `reflect.get(v, name)` | `(any, string) -> any` | 字段值原样（引用类型是**同一个对象**）。字段名不存在 ⇒ 抛错 |
| `reflect.field_type(v, name)` | `(any, string) -> string` | 字段的声明类型，Leno 写法。字段名不存在 ⇒ 抛错 |
| `reflect.methods(v)` | `(any) -> Array[string]` | 写在 `struct` 体内的方法名 |

`v` 可以是 **GC struct**、**cstruct**、或**带载荷 enum**（三者走同一套 API）。
其余类型（`int` / `Array` / `Dict`…）只有 `kind` / `type_name` 有意义 —— 传给
`fields` / `get` 之类会**明确报错**，不是静默给空结果。

---

## `kind` 返回什么

| 值 | `kind` |
|---|---|
| `null` | `"null"` |
| `true` | `"bool"` |
| `1` | `"int"` |
| `2.5` | `"float"` |
| `"x"` | `"string"` |
| `[1,2]` | `"array"` |
| `{"a":1}` | `"dict"` |
| 大整数 | `"bigint"` |
| `new Song()` | `"struct"` |
| `Vec2.malloc()` | `"cstruct"` |
| `Msg.progress(3, 10)` | `"enum"` |
| 闭包 / 函数 | `"func"` |
| `File` / `Socket` / `Channel` / `Thread` / `Future` | `"File"` / `"Socket"` / … |
| FFI 指针 | `"Ptr"` |

> 带载荷 `enum` 在运行期是"降级 struct"，`kind` 仍报 `"enum"` —— 对外语义是 enum。

---

## `field_type` 的类型串

风格与报错信息、LSP hover、`type_to_string` **一致**，不另起一套写法：

| 字段声明 | `field_type` |
|---|---|
| `int id = 0` | `"int"` |
| `string name = ""` | `"string"` |
| `string? note = null` | `"string?"` |
| `Array[int] nums = []` | `"Array[int]"` |
| `Array[Item] items = []` | `"Array[struct Item]"` |
| `Dict[string, int] score = {}` | `"Dict[string, int]"` |
| `Item? one = null` | `"struct Item?"` |

`cstruct` 那一侧如实给**宽度**（数据导向下 `i32` 和 `int` 不是一回事）：

| cstruct 字段 | `field_type` |
|---|---|
| `i32 id` | `"i32"` |
| `u8 flag` | `"u8"` |
| `f32 ratio` | `"f32"` |
| `u8 data[4]` | `"u8[4]"` |
| `u32 bits : 3` | `"u32 : 3"` |
| `Ptr[i32] p` | `"Ptr[i32]"` |
| `Vec2 inner` | `"struct Vec2"` |

---

## 例子：通用 struct → Dict

这是反射最直接的收益 —— 一个函数覆盖所有类型：

```leno
import reflect

struct Song {
    string name = ""
    int dur = 0
}

func to_dict(any obj):Dict[string, any] {
    Dict[string, any] out = {}
    var fs = reflect.fields(obj)
    for fs to f {
        out[f] = reflect.get(obj, f)
    }
    return out
}

main() {
    var s = new Song(name = "晴天", dur = 269)
    var d = to_dict(s)
    print(_str(d["name"]))     // 晴天
    print(_str(d["dur"]))      // 269
}
```

> `fields` 的顺序就是声明顺序，所以 `to_dict` 的结果在 `Dict` 里也是稳定的插入顺序。

---

## 例子：按类型分派（表格 / 表单）

```leno
import reflect

struct Row {
    int id = 0
    string title = ""
    Array[string] tags = []
}

func describe(any obj) {
    var fs = reflect.fields(obj)
    for fs to f {
        var t = reflect.field_type(obj, f)
        if t == "int" {
            print(f + " 是整数")
        } else if t == "Array[string]" {
            print(f + " 是字符串数组")
        } else {
            print(f + " 是 " + t)
        }
    }
}

main() {
    describe(new Row())
}
```

---

## 对 cstruct

```leno
import reflect

cstruct V3 {
    f32 x
    f32 y
    f32 z
}

main() {
    var v = V3.malloc()
    v.x = 1.5

    print(reflect.kind(v))          // cstruct
    print(reflect.type_name(v))     // V3
    print(reflect.field_type(v, "x"))  // f32

    var xv = reflect.get(v, "x")
    if xv is float => xf {
        print(_str(xf))             // 1.5
    }

    v.free()
}
```

`reflect.get` 对 cstruct 和 VM 的字段指令走**同一条存活判定**：`free()` / `free_all()`
之后读会抛错，不会读已释放内存。

---

## 带载荷 enum

```leno
import reflect

enum Msg {
    progress(int done, int total)
    finished()
}

main() {
    var m = Msg.progress(3, 10)
    print(reflect.kind(m))            // enum
    print(_str(reflect.fields(m).len()))  // 0
}
```

`fields` / `field_count` 对带载荷 enum 返回**空** —— 它的字段是 `tag` / `p0` / `p1`
这类内部表示，不是对外契约。读载荷请用 `case`：

```leno
switch m {
    case Msg.progress(d, t) { print(_str(d) + "/" + _str(t)) }
    case Msg.finished() { print("done") }
}
```

---

## 有意不做的三件事

| 没有 | 为什么 |
|---|---|
| `reflect.set(v, name, val)` | 写已有两条**安全**通道：`s.f = x`（编译期检查）、`jsons.fill(s, dict)`（按声明类型转换）。`set` 会绕过类型检查，`set(s, "age", "abc")` 要跑到很远才炸 —— 与"写错就要报出来"相反 |
| `reflect.enum_members(e)` / 值反查名字 | 本语言的 enum 成员运行期就是 `int` 常量（不带载荷时连对象都没有）⇒ 从 `1` 无从知道它属于哪个 enum。**靠猜的 API 比没有更糟**；按名取成员用 `Color.RED` 这类编译期常量 |
| 宏 / 语法改写 | 会削弱定向诊断（报错行号指向展开产物、`--check` 的处方失效）。这是本语言最稀缺的能力，不拿它换元编程 |

---

## 与 `jsons` 的分工

| 需求 | 用哪个 |
|---|---|
| struct ↔ JSON | `jsons.encode` / `jsons.fill` |
| struct ← `Dict`（DB 行） | `jsons.fill` |
| 遍历字段（展示 / 表格 / 表单） | `reflect.fields` + `reflect.get` |
| 按声明类型分派 | `reflect.field_type` |
| 按下标/名字读写单个已知字段 | 直接 `s.field` |

`reflect` 只回答"有什么"，不负责"怎么变成 JSON"—— 那件事 `jsons` 已经做对了
（含容器逐层转换、字符串转数字、未知字段忽略）。
