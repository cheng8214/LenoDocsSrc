# Leno 零基础入门

> 这份教程假设你**从没写过代码**。不需要懂 C、Java、Python，只要能打开记事本、会存文件就行。
>
> 写法参考 Python 官方教程的路子：**先让你跑起来，再解释为什么**；每节都有能直接运行的小程序、
> 真实输出、以及"新手最容易写错的那几种写法"。
>
> 想要查某个细节（某个函数的全部参数、某个报错怎么修），看 [`Leno入门教程.md`](Leno入门教程.md)
> 和 [`语言陷阱速查.md`](语言陷阱速查.md)；这份只管"把你从零带到能自己写小工具"。
>
> 文中标了 **`// 完整程序（可直接运行）`** 的代码块，是可以整段复制、存成 `.leno` 文件后
> 直接跑的；没标的通常是"片段"，只用来演示某一行。

---

## 目录

1. [先跑起来：你的第一个程序](#1-先跑起来-你的第一个程序)
2. [变量：把东西装进盒子](#2-变量-把东西装进盒子)
3. [基本类型：数字、文字、真假、空](#3-基本类型-数字-文字-真假-空)
4. [运算：算数、比较、串门](#4-运算-算数-比较-串门)
5. [让程序做选择：if](#5-让程序做选择-if)
6. [让程序重复做事：循环](#6-让程序重复做事-循环)
7. [一排盒子：数组](#7-一排盒子-数组)
8. [查字典：字典](#8-查字典-字典)
9. [字符串的日常操作](#9-字符串的日常操作)
10. [函数：给一段代码起名字](#10-函数-给一段代码起名字)
11. [结构体：把相关的东西捆在一起](#11-结构体-把相关的东西捆在一起)
12. [枚举：一组固定的选项](#12-枚举-一组固定的选项)
13. [出错怎么办：try / catch / defer](#13-出错怎么办-try-catch-defer)
14. [拆成多个文件：模块](#14-拆成多个文件-模块)
15. [常用工具箱：几个够用的模块](#15-常用工具箱-几个够用的模块)
16. [读懂报错：Leno 的报错会告诉你怎么改](#16-读懂报错-leno-的报错会告诉你怎么改)
17. [十个练习（带答案）](#17-十个练习-带答案)
18. [速查表](#18-速查表)

---

## 1. 先跑起来：你的第一个程序

### 1.1 装什么

你只需要一个东西：**`leno.exe`**（在仓库的 `build\` 目录里）。它同时是编译器、也是运行器。

确认能用：打开"命令提示符"（Win+R 输入 `cmd` 回车），敲：

```bat
leno.exe --version
```

能打出版本号，就说明装好了。**如果提示"不是内部或外部命令"**，说明它不在 PATH 里，
那就用完整路径调用，比如：

```bat
D:\CLeno\Leno\build\leno.exe 我的程序.leno
```

下面为了简洁，一律写 `leno`，你心里替换成完整路径即可。

### 1.2 第一个程序

新建一个文件，名字叫 `hello.leno`（**扩展名必须是 `.leno`**），内容照抄：

```leno
// 完整程序（可直接运行）
main() {
    print("你好，世界！")
}
```

然后在命令行里：

```bat
leno hello.leno
```

屏幕上出现：

```
你好，世界！
```

恭喜，你已经写了一个程序。下面把这三行拆开看：

| 你写的 | 意思 |
|---|---|
| `// 完整程序（可直接运行）` | 注释。`//` 后面到行尾都是给人看的，电脑完全不理它 |
| `main() { … }` | **程序入口**。程序总是从 `main` 里的第一行开始执行 |
| `print("你好，世界！")` | 往屏幕上打印一行字。`print` 是 Leno 自带的功能 |

三个必须记住的小规矩：

1. **中文标点会报错**：`print("你好")` 里的引号必须是英文 `"`，用中文引号 `“”` 会报"语法错误"。
2. **括号、引号要成对**：少一个 `)` 或 `"`，报错会告诉你大概第几行。
3. **`main()` 后面的大括号 `{ }` 圈出"这个程序包含哪些步骤"**，里面的东西要往里缩进（按 Tab 或 4 个空格）。

### 1.3 让程序说更多

```leno
// 完整程序（可直接运行）
main() {
    print("我叫 Leno")
    print("我今年", 1, "岁")
    print("这一行")
    printf("不换行")
    printf("，接着上一行写\n")
}
```

输出：

```
我叫 Leno
我今年 1 岁
这一行
不换行，接着上一行写
```

- `print(...)` 会自动换行；`printf(...)` 不换行，`\n` 是"换行符"。
- `print("我今年", 1, "岁")` 里用**逗号**分隔多个东西，它们之间会自动加一个空格。

---

## 2. 变量：把东西装进盒子

变量就是一个**贴了名字的盒子**，你把值放进去，以后用名字就能取出来。

```leno
// 完整程序（可直接运行）
main() {
    var name = "小明"     // 造一个盒子叫 name，装"小明"
    var age = 12          // 再造一个，装 12

    print(name)
    print(age)
    print(name + "今年" + age + "岁")   // 盒子可以拼起来用
}
```

输出：

```
小明
12
小明今年12岁
```

### 2.1 `var` 和"写清楚类型"

`var` 的意思是"你帮我看看右边是什么，就装什么"（自动推断）。你也可以**自己写清楚**：

```leno
// 完整程序（可直接运行）
main() {
    var a = 10          // 自动推断成整数
    int b = 20          // 明确写"这是一个整数"
    string c = "文字"    // 明确写"这是一段文字"
    float d = 1.5       // 小数

    print(a + b)
    print(c)
    print(d)
}
```

两种写法都对。**新手建议先用 `var`**，等你想让程序"更早发现写错类型"时再手写类型——
手写类型的好处是：如果你不小心把文字塞进 `int` 盒子，程序会在运行前就报错，而不是跑到一半出问题。

### 2.2 名字可以改，但类型不能乱换

```leno
// 完整程序（可直接运行）
main() {
    var score = 60
    print(score)        // 60
    score = 90          // 换个值
    print(score)        // 90
    score = score + 10  // 自己算自己
    print(score)        // 100
}
```

不能做的事：把一段文字塞进已经是数字的盒子。

```leno
var score = 60
score = "满分"     // ❌ 编译期报错：类型不匹配
```

报错大概长这样（Leno 会直接说清哪里不对）：

```
error: [类型不匹配] 无法将值赋值给变量 'score'
期望类型: int
实际类型: string
```

> **Leno 的脾气**：能在你运行之前发现的问题，它一定在运行之前报出来。
> 这是它和脚本类语言最大的不同，习惯之后你会很省心。

### 2.3 一次造好几个

```leno
// 完整程序（可直接运行）
main() {
    var a = 1, b = 2, c = 3
    print(a + b + c)

    int x, y, z          // 只说"我要三个整数盒子"，先不装东西
    x = 10
    y = 20
    z = 30
    print(x + y + z)
}
```

### 2.4 名字的规矩

- 可以用字母、数字、下划线，**不能以数字开头**。
- 区分大小写：`age` 和 `Age` 是两个不同的盒子。
- **可以用中文命名**（这点和多数语言不同，验证过）：

```leno
// 完整程序（可直接运行）
main() {
    var 名字 = "小红"
    var 年龄 = 9
    print(名字 + "今年" + 年龄 + "岁")
}
```

能跑，但**建议还是用英文**：以后查资料、和别人交流都方便。

---

## 3. 基本类型：数字、文字、真假、空

Leno 里你会天天见到的就这几种：

| 类型 | 长什么样 | 例子 |
|---|---|---|
| `int` | 整数 | `42`、`-7`、`0` |
| `float` | 小数 | `3.14`、`-0.5`、`1.0` |
| `string` | 文字（字符串） | `"你好"`、`"abc"`、`""`（空文字） |
| `bool` | 真 / 假 | `true`、`false` |
| `Array[...]` | 一排东西 | `[1, 2, 3]` |
| `Dict[...]` | 键值对表 | `{"a": 1}` |
| `null` | "什么都没有" | `null` |

想知道某个盒子里到底是什么，用 `type()`：

```leno
// 完整程序（可直接运行）
main() {
    print(type(1))          // int
    print(type(1.5))        // float
    print(type("你好"))     // string
    print(type(true))       // bool
    print(type([1, 2, 3]))  // Array[int]
    print(type({"a": 1}))   // Dict[string, int]
}
```

### 3.1 数字：整数和小数的区别很重要

```leno
// 完整程序（可直接运行）
main() {
    print(7 / 2)      // 3       ← 两个整数相除，结果还是整数（余数丢掉）
    print(7 % 2)      // 1       ← % 是"求余数"
    print(7.0 / 2)    // 3.5     ← 有一个是小数，结果就是小数
    print(2 + 3 * 4)  // 14      ← 先乘除后加减
    print((2 + 3) * 4)// 20      ← 括号最优先
}
```

新手最常踩的坑：**`7 / 2` 得到 `3`，不是 `3.5`**。想要小数就写 `7.0 / 2`。

### 3.2 整数没有上限（会自动变大）

多数语言里整数超过 21 亿左右就会"溢出"变成负数。Leno 不会：**它自动换成更大的数字类型**，
所以你可以放心算大数。

```leno
// 完整程序（可直接运行）
main() {
    var big = 9223372036854775807   // 这是一个很大的整数
    print(big + 1)                  // 9223372036854775808，照样正确
    print(2 * 1000000000000)        // 2000000000000
}
```

### 3.3 文字（字符串）

用**双引号**包起来。想要引号本身出现在文字里，用反斜杠转义：

```leno
// 完整程序（可直接运行）
main() {
    print("他说：\"你好\"")   // 他说："你好"
    print("第一行\n第二行")   // \n 是换行
    print("制表\t空一格")     // \t 是一个制表位
}
```

"原样输出"的写法（里面什么都不转义，适合写路径、正则）：

```leno
// 完整程序（可直接运行）
main() {
    print(@"C:\Users\me\文件.txt")   // @ 开头的字符串：里面的 \ 就是普通反斜杠
}
```

### 3.4 真假（bool）

只有两个值：`true`（真）和 `false`（假）。通常由比较得出：

```leno
// 完整程序（可直接运行）
main() {
    print(3 > 2)        // true
    print(3 == 4)       // false
    print("abc" == "abc")  // true（文字也能比）
}
```

### 3.5 空（null）

`null` 表示"这里什么都没有"。**新手最重要的规则**：

> 只有**可空类型**（类型后面加 `?`）才允许装 `null`。

```leno
// 完整程序（可直接运行）
main() {
    int? maybe = null      // ✅ 允许：int? 就是"可能是整数，也可能是空"
    if maybe == null {
        print("现在它是空的")
    }

    int sure = 10          // ✅ 非可空：一定有值
    print(sure + 1)

    // int bad = null      // ❌ 编译期报错：非可空类型不能赋 null
}
```

把 `// int bad = null` 前面的 `//` 去掉试一下，你会立刻看到报错——**这就是"不静默"**：
它不会让你的程序带着空值跑到一半崩掉，而是当场告诉你。

---

## 4. 运算：算数、比较、串门

### 4.1 算术

```leno
// 完整程序（可直接运行）
main() {
    print(10 + 3)   // 13
    print(10 - 3)   // 7
    print(10 * 3)   // 30
    print(10 / 3)   // 3     ← 整数除法
    print(10 % 3)   // 1     ← 余数
    print(10.0 / 3) // 3.3333333333333335
}
```

### 4.2 比较（结果是 true / false）

```leno
// 完整程序（可直接运行）
main() {
    print(5 > 3)     // true
    print(5 >= 5)    // true
    print(5 == 5)    // true    ← 相等是两个等号！
    print(5 != 4)    // true    ← 不相等
    print("a" < "b") // true    ← 文字按字母序比
}
```

**新手最常犯的错**：判断相等写成 `=`（一个等号）。一个等号是"赋值"（放进盒子），
两个等号才是"问它们相等吗"。

### 4.3 逻辑：and / or / not

```leno
// 完整程序（可直接运行）
main() {
    var 下雨 = true
    var 有伞 = false

    print(下雨 and 有伞)   // false  ← 两个都真才真
    print(下雨 or 有伞)    // true   ← 一个真就真
    print(not 有伞)        // true   ← 取反
}
```

### 4.4 把文字接起来

```leno
// 完整程序（可直接运行）
main() {
    var name = "小明"
    var age = 12
    print("我叫" + name)           // 我叫小明
    print(name + "今年" + age + "岁")  // 小明今年12岁  ← 数字会自动变成文字
}
```

### 4.5 更方便的拼接：插值 `$"...{变量}..."`

字符串前面加 `$`，里面的 `{ }` 就会被**换成变量的值**：

```leno
// 完整程序（可直接运行）
main() {
    var name = "小明"
    var age = 12
    var pi = 3.14159

    print($"我叫{name}，今年{age}岁")   // 我叫小明，今年12岁
    print($"圆周率约等于 {pi:.2f}")      // 圆周率约等于 3.14（:.2f = 保留两位小数）
}
```

常用的小数格式：

| 写法 | 意思 | 例子（值 3.14159） |
|---|---|---|
| `{pi}` | 原样 | `3.14159` |
| `{pi:.2f}` | 保留 2 位小数 | `3.14` |
| `{pi:.0f}` | 不要小数 | `3` |

### 4.6 一行内做选择：`if ... then ... else`

```leno
// 完整程序（可直接运行）
main() {
    var a = 10
    var b = 20
    var max = if a > b then a else b
    print("大的那个是 " + max)     // 大的那个是 20
}
```

它的意思就是"如果 a > b 就取 a，否则取 b"，可以嵌进赋值里用（Python 里写作 `a if a > b else b`）。

---

## 5. 让程序做选择：if

```leno
// 完整程序（可直接运行）
main() {
    var score = 85

    if score >= 90 {
        print("优秀")
    } else if score >= 60 {
        print("及格")
    } else {
        print("不及格")
    }
}
```

输出：`及格`

规则：

- `if 条件 { … }`：条件为真才执行大括号里的东西。
- `else if 条件 { … }`：前面不成立时，再看这个条件。
- `else { … }`：前面都不成立时执行。
- **大括号不能省**（不像某些语言可以省）。

> 还有个等价写法 `eif`，作用和 `else if` 完全一样（`eif` 是懒人版，打起来快）。
> 看到别人的代码用 `eif` 不要奇怪。

### 5.1 判断"是不是空"

```leno
// 完整程序（可直接运行）
main() {
    string? name = null

    if name == null {
        print("还没有名字")
    } else {
        print("名字是 " + name)
    }

    name = "Leno"
    if name != null {
        print("现在有名字了：" + name)
    }
}
```

写 `if name != null { … }` 之后，大括号里面 Leno 就**知道它不是空的了**，可以直接用。

### 5.2 多个条件

```leno
// 完整程序（可直接运行）
main() {
    var age = 20
    var has_ticket = true

    if age >= 18 and has_ticket {
        print("可以进场")
    } else {
        print("不能进场")
    }
}
```

---

## 6. 让程序重复做事：循环

### 6.1 `for` 数数（最常用）

```leno
// 完整程序（可直接运行）
main() {
    for 1:5 to i {
        print("第 " + i + " 次")
    }
}
```

输出：

```
第 1 次
第 2 次
第 3 次
第 4 次
第 5 次
```

**重点：`1:5` 是"从 1 到 5，两头都算"，一共 5 次**（很多语言是"到 5 但不含 5"，
Leno 统一成"闭区间"，你只要记住"两头都算"）。

`to` 后面那个 `i` 是你起的名字，每轮它会变成当前数字。

### 6.2 想跳着数 / 倒着数

```leno
// 完整程序（可直接运行）
main() {
    print("偶数：")
    for 0:10:2 to i {          // 第三个数是"步长"
        print(i)
    }

    print("倒着数：")
    for 3:1:-1 to i {          // 步长写 -1 就是倒着数
        print(i)
    }
}
```

输出：

```
偶数：
0
2
4
6
8
10
倒着数：
3
2
1
```

⚠ **新手大坑**：写 `for 3:1 to i`（忘了 `:-1`）**一次都不会执行**。Leno 会给你一条警告：

```
warning: [空循环] for 3:1 是**空区间**（一次都不执行）：本语言的 for 是升序闭区间，倒序要显式写 `for 3:1:-1`
```

看到这条警告就知道自己忘了写步长。

### 6.3 把一排东西挨个过一遍

```leno
// 完整程序（可直接运行）
main() {
    var fruits = ["苹果", "香蕉", "橘子"]
    for fruits to f {
        print("我喜欢吃" + f)
    }
}
```

字符串也能这样过（会按**字符**一个个给）：

```leno
// 完整程序（可直接运行）
main() {
    for "abc" to ch {
        print(ch)
    }
}
```

会打印 `a`、`b`、`c` 三行。

### 6.4 `while`：条件成立就一直做

```leno
// 完整程序（可直接运行）
main() {
    var n = 1
    while n <= 3 {
        print("n = " + n)
        n = n + 1        // ← 千万别忘这句，否则永远循环下去（死循环）
    }
}
```

`for` 和 `while` 的分工：**知道要做几次就 `for`，只知道"做到满足条件为止"就 `while`**。

### 6.5 提前退出 / 跳过这一轮

```leno
// 完整程序（可直接运行）
main() {
    for 1:10 to i {
        if i == 3 {
            continue        // 跳过本轮剩下的，直接下一轮
        }
        if i == 6 {
            break           // 整个循环到此结束
        }
        print(i)
    }
}
```

输出：`1`、`2`、`4`、`5`

（`3` 被 `continue` 跳过，到 `6` 时 `break` 让整个循环结束。）

---

## 7. 一排盒子：数组

数组就是"一排编了号的小抽屉"，编号（下标）**从 0 开始**。

```leno
// 完整程序（可直接运行）
main() {
    var fruits = ["苹果", "香蕉", "橘子"]

    print(fruits[0])        // 苹果   ← 第 0 个
    print(fruits[1])        // 香蕉
    print(fruits[2])        // 橘子
    print(fruits.len())     // 3      ← 一共几个
    print(fruits)           // ["苹果", "香蕉", "橘子"]
}
```

**新手大坑**：`fruits[3]` 会报错（只有 0、1、2）。Leno 的报错会直接说清：

```
[错误] 数组索引越界: 索引 3, 长度 3
```

取最后一个，惯用写法是 `fruits[fruits.len() - 1]`。

### 7.1 增、删、改

```leno
// 完整程序（可直接运行）
main() {
    var a = [10, 20, 30]

    a.add(40)            // 末尾加一个
    print(a)             // [10, 20, 30, 40]

    a[0] = 99            // 改第 0 个
    print(a)             // [99, 20, 30, 40]

    var last = a.pop()   // 拿出末尾那个（数组变短）
    print(last)          // 40
    print(a)             // [99, 20, 30]

    var removed = a.remove(1)   // 删掉"下标 1"那个，返回被删的值
    print(removed)       // 20
    print(a)             // [99, 30]

    a.insert(1, 55)      // 在下标 1 处插入 55
    print(a)             // [99, 55, 30]
}
```

⚠ `remove(...)` 收的是**下标**，不是值。想"删掉值为 20 的那个"，得先查它的位置：

```leno
var pos = a.index_of(20)    // 找不到会给 -1
if pos >= 0 {
    a.remove(pos)
}
```

### 7.2 切片：一次拿一段

```leno
// 完整程序（可直接运行）
main() {
    var a = [1, 2, 3, 4, 5]

    print(a[1:3])    // [2, 3, 4]   ← 还是"两头都算"！
    print(a[:2])     // [1, 2, 3]   ← 从开头到 2
    print(a[3:])     // [4, 5]      ← 从 3 到结尾
    print(a[:])      // [1, 2, 3, 4, 5]  ← 整个复制一份
}
```

### 7.3 常用操作

```leno
// 完整程序（可直接运行）
main() {
    var a = [3, 1, 2]

    a.sort()                    // 从小到大
    print(a)                    // [1, 2, 3]

    a.reverse()                 // 倒过来
    print(a)                    // [3, 2, 1]

    print(a.has(2))             // true    ← 有没有 2
    print(a.index_of(2))        // 1       ← 2 在哪（没有给 -1）
    print(a.sum())              // 6.0     ← 求和（注意：结果是小数）
    print(a.join("-"))          // 3-2-1   ← 用 - 连成一个字符串
}
```

### 7.4 对每个元素做同一件事：map / filter / reduce

这是数组最好用的三个工具，写法是"传一个**函数**进去"：

```leno
// 完整程序（可直接运行）
main() {
    var nums = [1, 2, 3, 4, 5]

    // map：每个都变一次（这里是乘 2）
    var doubled = nums.map(func(int x): int {
        return x * 2
    })
    print(doubled)                 // [2, 4, 6, 8, 10]

    // filter：只留下满足条件的（偶数的）
    var evens = nums.filter(func(int x): bool {
        return x % 2 == 0
    })
    print(evens)                   // [2, 4]

    // reduce：把它们合成一个（这里是求和）
    var total = nums.reduce(func(int acc, int x): int {
        return acc + x
    }, 0)
    print(total)                   // 15
}
```

`func(...): 类型 { ... }` 就是"临时写一个没有名字的函数"（后面第 10 章讲函数）。
看不懂没关系，先照抄用着，它是数组里最省事的写法。

---

## 8. 查字典：字典

字典存的是**"键 → 值"**的对应关系，像真字典：查"apple"得到"苹果"。

```leno
// 完整程序（可直接运行）
main() {
    var 价格 = {"苹果": 5, "香蕉": 3}

    print(价格["苹果"])        // 5    ← 用键取值
    价格["橘子"] = 4           // 加一条
    print(价格)                // {苹果: 5, 香蕉: 3, 橘子: 4}

    print(价格["西瓜"])        // null ← 没有这个键，给你 null（不报错）
}
```

⚠ **"没有这个键"返回 `null`**，这是个容易踩的地方。想区分"没这个键"和"值是空"，
可以用 `has()` 先问一下，或者用 `get()` 给个默认值：

```leno
// 完整程序（可直接运行）
main() {
    var 库存 = {"苹果": 5}

    print(库存.has("苹果"))          // true
    print(库存.has("西瓜"))          // false

    // get(键, 默认值)：没有就给默认值，不会给你 null
    print(库存.get("西瓜", 0))       // 0
    print(库存.get("苹果", 0))       // 5
}
```

### 8.1 遍历字典

```leno
// 完整程序（可直接运行）
main() {
    var scores = {"语文": 90, "数学": 95}

    for scores to 科目 {           // 每轮拿到"键"
        print(科目 + "：" + scores[科目] + " 分")
    }
}
```

输出：

```
语文：90 分
数学：95 分
```

### 8.2 改、删、数

```leno
// 完整程序（可直接运行）
main() {
    var d = {"a": 1, "b": 2}

    d["a"] = 100          // 改
    print(d["a"])         // 100
    print(d.len())        // 2     ← 几条

    d.remove("b")         // 删
    print(d)              // {a: 100}
}
```

> 一个提醒：**不要在 `for d to k` 的循环体里删/加键**。Leno 会警告你（`[遍历中修改]`），
> 因为那样会漏掉元素。要删就先把键收集起来，循环结束后再删。

---

## 9. 字符串的日常操作

字符串自带很多方法，用 `字符串.方法()` 调用：

```leno
// 完整程序（可直接运行）
main() {
    var s = "Hello, Leno"

    print(s.len())               // 11        长度
    print(s.to_upper())          // HELLO, LENO
    print(s.to_lower())          // hello, leno
    print(s.has("Leno"))         // true      包含？
    print(s.find("Leno"))        // 7         在哪（没有给 -1）
    print(s.replace("Leno", "World"))   // Hello, World
    print(s.slice(0, 4))         // Hello     取一小段（两头都算）
    print(s.split(", "))         // ["Hello", "Leno"]  按分隔符切开
    print("  x  ".trim())        // x         去掉两头空白
}
```

### 9.1 拼、重复、补位

```leno
// 完整程序（可直接运行）
main() {
    print("a" + "b")              // ab
    print("ab".rep(3))            // ababab    ← 重复 3 次（注意：不能写 "ab" * 3）
    print("5".pad_start(3, "0"))  // 005       ← 不足 3 位前面补 0
    print("5".pad_end(3, "0"))    // 500
}
```

### 9.2 一条一条看

```leno
// 完整程序（可直接运行）
main() {
    var text = "苹果,香蕉,橘子"
    var parts = text.split(",")
    for parts to p {
        print("我买了 " + p)
    }
}
```

### 9.3 文字和数字互转

```leno
// 完整程序（可直接运行）
main() {
    print(_int("42") + 1)         // 43    ← 文字转整数
    print(_float("1.5") * 2)      // 3.0   ← 文字转小数
    print(_str(42) + "!")         // 42!   ← 数字转文字

    // _int("abc") 会直接报错（不给你 0），
    // 想要"转不了就给默认值"，用 _int_or：
    print(_int_or("abc", -1))     // -1
    print(_int_or("12", -1))      // 12
}
```

---

## 10. 函数：给一段代码起名字

函数就是"打包好的一段代码"，起个名字，以后叫名字就能用。

```leno
// 完整程序（可直接运行）
main() {
    print(add(2, 3))       // 5
    print(add(10, 20))     // 30

    var r = area(3.0)      // 有返回值的函数，可以把结果存起来
    print(r)               // 28.274333882308138
}

func add(int a, int b): int {
    return a + b           // return 把结果交回去
}

func area(float radius): float {
    return 3.14159 * radius * radius
}
```

要看懂的三件事：

| 部分 | 意思 |
|---|---|
| `func add(int a, int b)` | 叫 `add`，需要两个整数（分别叫 `a`、`b`） |
| `: int` | 它会还给你一个整数（返回类型） |
| `return a + b` | 把 `a + b` 交回去 |

**程序员约定**：函数写在 `main` 的**下面**或上面都行（Leno 允许先调用后定义），
但为了好读，通常把 `main` 放最上面，其它函数放下面。

### 10.1 不需要返回值

```leno
// 完整程序（可直接运行）
main() {
    打招呼("小明")
    打招呼("小红")
}

func 打招呼(string name) {
    print("你好，" + name + "！")
}
```

不写 `: 类型` 就是"不还东西"。

### 10.2 参数可以有默认值

```leno
// 完整程序（可直接运行）
main() {
    print(greet("小明"))            // 你好，小明
    print(greet("小明", "早上好"))  // 早上好，小明
}

func greet(string name, string word = "你好"): string {
    return word + "，" + name
}
```

调用时不写第二个参数，就用默认的 `"你好"`。

### 10.3 一次还两个值

```leno
// 完整程序（可直接运行）
main() {
    var[int, int](q, r) = divmod(17, 5)
    print("17 ÷ 5 = " + q + " 余 " + r)     // 17 ÷ 5 = 3 余 2
}

func divmod(int a, int b): [int, int] {
    return a / b, a % b
}
```

注意两个地方：返回类型写成**方括号** `[int, int]`；接收时写 `var[int, int](q, r) = ...`
（方括号里是类型，圆括号里是名字）。

### 10.4 函数也是"可以装进盒子的东西"（闭包）

```leno
// 完整程序（可直接运行）
main() {
    var base = 10

    var addBase = func(int n): int {
        return n + base          // 用到了外面的 base
    }

    print(addBase(5))            // 15
}
```

`func(...) { ... }` 这样写出来的是一个"值"，可以存进变量、传给 `map`。它能记住外面的变量（`base`），
这个能力叫**闭包**。

---

## 11. 结构体：把相关的东西捆在一起

写程序久了你会发现"名字、年龄、成绩"总是要一起出现。**结构体**（`struct`）就是
"自己造一个新类型，把几样东西捆成一个"。

```leno
// 完整程序（可直接运行）
struct Dog {
    string name = ""
    int age = 0
}

main() {
    var d = new Dog(name = "Lucky", age = 3)

    print(d.name)        // Lucky
    print(d.age)         // 3

    d.age = 4            // 改它的字段
    print($"它现在 {d.age} 岁了")
}
```

要点：

- `struct Dog { … }` 定义"一只狗有哪些字段"，`= ""`、`= 0` 是**默认值**。
- 造一只狗要写 `new Dog(...)`，字段可以用 `字段名 = 值` 指定（顺序随意）。
- 用 `d.name` 这样的"点"访问字段。
- ⚠ **字段必须写具体类型**（`int age = 0`、`Array[int] scores = [0]`），**不能写 `var`**：
  写 `var` 编译器会直接说「struct 字段不能使用 var，必须使用具体类型」。

### 11.1 让狗会叫：方法

```leno
// 完整程序（可直接运行）
struct Dog {
    string name = ""
    int age = 0

    func bark(): string {
        return self.name + "：汪汪！"
    }

    func birthday() {
        self.age = self.age + 1
    }
}

main() {
    var d = new Dog(name = "Lucky", age = 3)
    print(d.bark())      // Lucky：汪汪！
    d.birthday()
    print(d.age)         // 4
}
```

- 写在 struct 里的 `func` 叫**方法**，用 `d.bark()` 调用。
- `self` 就是"这只狗自己"，`self.name` 读它自己的字段，`self.age = …` 改它自己。

### 11.2 结构体是"同一个东西"，不是复制

```leno
// 完整程序（可直接运行）
struct Point {
    int x = 0
    int y = 0
}

main() {
    var a = new Point(x = 1)
    var b = a              // b 和 a 指向**同一只** Point
    b.x = 99
    print(a.x)             // 99  ← 改 b 就是改 a
}
```

新手注意：`var b = a` **不是复制一份**。真要复制，就新建一个再把字段抄过去。

---

## 12. 枚举：一组固定的选项

有些东西天生只有几个值：星期几、订单状态、颜色。用**枚举**（`enum`）比用数字清楚得多。

```leno
// 完整程序（可直接运行）
enum Color {
    red
    green
    blue
}

main() {
    var c = Color.green
    print(c)                 // 1   ← 底下是编号，从 0 开始

    if c == Color.green {
        print("是绿色")
    }

    switch c {
        case Color.red {
            print("红")
        }
        case Color.green {
            print("绿")
        }
        case Color.blue {
            print("蓝")
        }
    }
}
```

输出：

```
1
是绿色
绿
```

要点：

- 成员**一行一个**（或同一行用 `;` 分隔，**不能用逗号**）。
- 用 `Color.green` 这样"类型名.成员"访问。
- 想自己指定编号：`enum Page { HOME = 0; SEARCH = 1; LYRIC = 2 }`。

### 12.1 让选项带上数据（很有用）

有时你希望"失败"这个选项顺便说明原因。Leno 的枚举成员**可以带参数**：

```leno
// 完整程序（可直接运行）
enum 结果 {
    ok(int 分数)
    fail(string 原因)
}

main() {
    var r = 结果.ok(95)

    switch r {
        case 结果.ok(分数) {
            print("考了 " + 分数 + " 分")
        }
        case 结果.fail(原因) {
            print("没过，原因：" + 原因)
        }
    }
}
```

`switch` 会按"是哪个成员 + 把参数解出来"。**这比"用一个数字表示状态，把原因存在别处"安全得多**，
因为编译器能检查你有没有漏掉某个成员。

---

## 13. 出错怎么办：try / catch / defer

有些错误是"运行时才知道"的：文件不存在、数组越界、除以 0。这些用 `try` 抓：

```leno
// 完整程序（可直接运行）
main() {
    try {
        var a = [1, 2]
        print(a[10])              // 这里会出错
        print("这行不会执行")
    } catch e {
        print("出错了：" + e)      // 接住错误，程序继续
    }

    print("程序还在继续跑")
}
```

输出：

```
出错了：数组索引越界: 索引 10, 长度 2
程序还在继续跑
```

`catch e` 里的 `e` 就是"错误信息"。

### 13.1 主动报错：`throw`

```leno
// 完整程序（可直接运行）
main() {
    print(取钱(100, 30))    // 70
    try {
        取钱(100, 200)      // 余额不够，会 throw
    } catch e {
        print("失败：" + e)  // 失败：余额不足
    }
}

func 取钱(int 余额, int 要取): int {
    if 要取 > 余额 {
        throw "余额不足"            // 主动抛出错误
    }
    return 余额 - 要取
}
```

### 13.2 `finally`：不管成功失败都执行

```leno
// 完整程序（可直接运行）
main() {
    try {
        print("开门")
        throw "出事了"
    } catch e {
        print("处理：" + e)
    } finally {
        print("关门")            // 一定执行
    }
}
```

### 13.3 `defer`：离开这一块时再做

```leno
// 完整程序（可直接运行）
main() {
    print("开始")
    defer {
        print("结束时清理")       // main 快结束时执行
    }
    print("做正事")
}
```

输出：

```
开始
做正事
结束时清理
```

`defer` 适合"打开文件 → 记得关"这类收尾动作。正常结束、`return`、出错，它都会执行。

---

## 14. 拆成多个文件：模块

程序变大后不能都塞进一个文件。Leno 的做法：**一个文件就是一个模块**，用 `import` 拿来用。

先写一个工具文件 `mylib.leno`：

```leno
// 完整程序（可直接运行）—— 文件名：mylib.leno
export var 版本 = "1.0"

export func double(int n): int {
    return n * 2
}

export func shout(string s): string {
    return s.to_upper() + "!"
}
```

再写主程序 `main.leno`（和它**放在同一个文件夹**）：

```leno
// 完整程序（可直接运行）—— 文件名：main.leno
import "mylib.leno" as lib

main() {
    print(lib.double(21))     // 42
    print(lib.版本)            // 1.0
    print(lib.shout("hello")) // HELLO!
}
```

三个要点：

| 要点 | 说明 |
|---|---|
| `export` | 只有标了 `export` 的东西才能被别的文件用（不标就是"内部私有"） |
| `import "mylib.leno" as lib` | 引号里是**文件名**，`as lib` 是你给它起的简称 |
| `lib.double(21)` | 用"简称.名字"访问 |

> 为什么必须 `export`？因为 Leno 想让你明确"这个函数是给别人用的"。没写 `export` 就调用，
> 报错会直接说"XX 没有导出"，而不是让你猜。

---

## 15. 常用工具箱：几个够用的模块

Leno 自带一批模块，用之前 `import`，然后 `模块名.函数()`。

### 15.1 `maths`：数学

```leno
// 完整程序（可直接运行）
import maths

main() {
    print(maths.sqrt(16.0))    // 4.0     开平方
    print(maths.abs(-7.0))     // 7.0     绝对值
    print(maths.floor(3.8))    // 3.0     向下取整
    print(maths.ceil(3.2))     // 4.0     向上取整
    print(maths.round(3.5))    // 4.0     四舍五入
    print(maths.max(3.0, 9.0)) // 9.0     大的那个
    print(maths.min(3.0, 9.0)) // 3.0
    print(maths.pow(2.0, 10.0))// 1024.0  乘方
}
```

> 注意：`maths` 的函数**都收小数**，整数要先变小数（`maths.sqrt(16)` 也能过，但你心里要知道它是 float 世界）。

### 15.2 `times`：时间

```leno
// 完整程序（可直接运行）
import times

main() {
    var now = times.now()                      // 现在的时间戳（整数秒）
    print(times.format(now, "%Y-%m-%d %H:%M:%S"))   // 2026-11-23 15:04:05
}
```

### 15.3 `files`：读写文件

```leno
// 完整程序（可直接运行）
import files
import dirs

main() {
    // 写到临时目录，不污染当前目录（换成 "笔记.txt" 就是写到程序所在目录）
    var path = dirs.join(_tmpdir(), "笔记.txt")

    files.write(path, "今天学了 Leno\n第二行")
    var text = files.read(path)
    print(text)
    print(files.delete(path))     // true
}
```

⚠ 读不存在的文件会**抛错**（不是给你空字符串），所以要么确定它在，要么用 `try` 包起来。

### 15.4 `io`：输入

```leno
// 完整程序（可直接运行）
import io

main() {
    var name = io.input("你叫什么名字？ ")
    print("你好，" + name)
}
```

运行后程序会停下来等你打字、回车。

### 15.5 想查更多

每个模块都有专门文档（`module_arrays.md`、`module_strings.md`、`module_maths.md`…），
在仓库根目录就能找到。**新手阶段不用背**，写到哪查到哪。

---

## 16. 读懂报错：Leno 的报错会告诉你怎么改

这是 Leno 最省心的地方：**报错不只说"错了"，还说"该改成什么"。** 学会读它，效率翻倍。

### 16.1 报错长什么样

```
C:\code\hello.leno(8,17): error: [类型不匹配] 变量 'a' 是 int（非可空），不能赋 null
```

拆开看：

| 部分 | 意思 |
|---|---|
| `C:\code\hello.leno` | 哪个文件 |
| `(8,17)` | **第 8 行、第 17 列** ← 先看行，再看列 |
| `error:` | 错误（`warning:` 是警告，程序照样能跑） |
| `[类型不匹配]` | 错误类型（方便你判断是哪一类问题） |
| 后面的中文 | 具体原因，通常带"请改成…" |

### 16.2 新手最常遇到的 7 个报错

**① 忘了写引号 / 用了中文引号**

```
error: [语法错误] 期望表达式
```

> 检查：字符串是不是用了英文 `"`，括号是否成对。

**② 类型对不上**

```
error: [类型不匹配] 无法将值赋值给变量 'score'
期望类型: int
实际类型: string
```

> 意思：盒子是装整数的，你塞了文字。改成 `score = 90` 或把盒子改成 `string`。

**③ 把 null 塞进"一定有值"的盒子**

```
error: [类型不匹配] 变量 'a' 是 int（非可空），不能赋 null
```

> 要么别塞 null，要么把类型写成 `int?`（表示"允许空"）。

**④ 数组越界（运行期）**

```
[错误] hello.leno:6: 数组索引越界: 索引 10, 长度 3
[调用栈]
#0 main @ hello.leno:6
```

> 下标从 0 开始，长度 3 的数组只有 0/1/2。

**⑤ 除以 0（运行期）**

```
[错误] hello.leno:4: 除零错误：除数为 0
[操作] 除法 (/)
[操作数a] type=int, value=10
```

> Leno 会连"被除数是多少"都告诉你，方便你回推哪一步把它算成 0 了。

**⑥ 方法名写错**

```
error: [语义错误] 类型 'string' 没有方法 'len2'
```

> 大多数情况它会顺带列出"可用的方法"，照着抄就行。

**⑦ 插值的格式符写错**

```
error: [语法错误] 插值的格式说明符不合法：转换符 `y` 不认识 —— 可用：
f 小数 / d 整数 / s 字符串 / x 十六进制 / X 大写十六 / o 八进制 / b 二进制 /
e E g G 科学计数与通用 / c 字符 / % 百分号
```

> 直接把可用的全列出来——这类报错是"照着改就行"的。

### 16.3 警告（warning）也要看

警告不影响运行，但**往往预示着你写错了**：

| 警告 | 意思 |
|---|---|
| `[空循环]` | 你这个 for 一次都不执行（常见：倒序忘了 `:-1`） |
| `[不可达代码]` | `return` 之后还写了语句，永远执行不到 |
| `[漏写 return]` | 有的分支没返回，调用方可能拿到 null |
| `[未使用变量]` | 造了盒子从没用过（可能打错名字了） |
| `[遍历中修改]` | 一边遍历容器一边增删，会漏元素 |
| `[defer后改值]` | `defer` 里用的变量在之后被改了，`defer` 拿到的不是你想要的旧值 |

### 16.4 三个通用排查步骤

1. **先看行号**，再看报错类型，最后读那句中文——它通常已经写了改法。
2. **一次只改一个地方**，改完重跑。Leno 一次会把同类错误合并显示，别被条数吓到。
3. 实在看不懂，就把可疑的那一行**注释掉**（前面加 `//`）重跑，看错误是否消失——
   快速定位"到底哪一行惹的祸"。

---

## 17. 十个练习（带答案）

每题都给了答案，**但请先自己写**，写完对一下哪里不同。全部答案都实际跑过。

**练习 1**：打印 1 到 10 的平方。

<details><summary>答案</summary>

```leno
main() {
    for 1:10 to i {
        print(i * i)
    }
}
```
</details>

**练习 2**：判断一个数是奇数还是偶数（用 `%`）。

<details><summary>答案</summary>

```leno
main() {
    var n = 7
    if n % 2 == 0 {
        print(n + " 是偶数")
    } else {
        print(n + " 是奇数")
    }
}
```
</details>

**练习 3**：求 1 到 100 的和。

<details><summary>答案</summary>

```leno
main() {
    var total = 0
    for 1:100 to i {
        total = total + i
    }
    print(total)     // 5050
}
```
</details>

**练习 4**：把数组 `[5, 3, 8, 1]` 从小到大排序并打印。

<details><summary>答案</summary>

```leno
main() {
    var a = [5, 3, 8, 1]
    a.sort()
    print(a)         // [1, 3, 5, 8]
}
```
</details>

**练习 5**：统计一段文字里出现了几个逗号。

<details><summary>答案</summary>

```leno
main() {
    var text = "苹果,香蕉,橘子,西瓜"
    print(text.count(","))   // 3
}
```
</details>

**练习 6**：把一句话里的每个词倒序（比如 `"我 爱 学 习"` → `"习 学 爱 我"`）。

<details><summary>答案</summary>

```leno
main() {
    var words = "我 爱 学 习".split(" ")
    var result = ""
    for 0:words.len() - 1 to i {
        var w = words[words.len() - 1 - i]
        if i > 0 {
            result = result + " "
        }
        result = result + w
    }
    print(result)     // 习 学 爱 我
}
```
</details>

**练习 7**：写一个函数 `is_even(int n): bool`。

<details><summary>答案</summary>

```leno
main() {
    print(is_even(4))    // true
    print(is_even(7))    // false
}

func is_even(int n): bool {
    return n % 2 == 0
}
```
</details>

**练习 8**：用字典统计每个字出现的次数（`"aabbb"` → a:2, b:3）。

<details><summary>答案</summary>

```leno
main() {
    var text = "aabbb"
    var counts = {}

    for text to ch {
        if counts.has(ch) {
            counts[ch] = counts[ch] + 1
        } else {
            counts[ch] = 1
        }
    }

    for counts to k {
        print(k + " 出现 " + counts[k] + " 次")
    }
}
```
</details>

**练习 9**：写一个"学生"结构体，有姓名和三门成绩，并算平均分。

<details><summary>答案</summary>

```leno
struct Student {
    string name = ""
    Array[int] scores = [0, 0, 0]     // ← 字段必须写具体类型，不能写 var

    func average(): float {
        var sum = 0
        for self.scores to s {
            sum = sum + s
        }
        return sum / 3.0
    }
}

main() {
    var s = new Student(name = "小明", scores = [90, 80, 70])
    print(s.name + " 的平均分是 " + s.average())   // 小明 的平均分是 80.0
}
```
</details>

**练习 10**：写一个安全的除法：除数为 0 时返回 null 而不是崩溃。

<details><summary>答案</summary>

```leno
main() {
    print(safe_div(10, 2))    // 5.0
    print(safe_div(10, 0))    // null
}

func safe_div(float a, float b): float? {
    if b == 0.0 {
        return null
    }
    return a / b
}
```
</details>

### 接下来写点什么

从**能用起来的小工具**开始最有效，比如：

- 记账：把每天花费写进文件，读出来求和（`files` + 数字）
- 待办清单：命令行里加/删/列出（数组 + `io.input`）
- 词频统计：读一个 txt，统计出现最多的 10 个词（`files` + 字典 + `sort`）
- 猜数字：`rands` 生成随机数 + `io.input` 猜（`while` + `if`）

---

## 18. 速查表

### 18.1 骨架

```leno
// 注释这样写
/* 也可以这样写多行 */

import "其它文件.leno" as 别名

struct 类型名 {
    int 字段 = 0
    func 方法(): int { return self.字段 }
}

enum 选项 { 甲
           乙 }

func 函数名(int 参数): int { return 参数 + 1 }

main() {
    var 变量 = 1
    print(变量)
}
```

### 18.2 常用语法一张表

| 想做的事 | 写法 |
|---|---|
| 造变量 | `var x = 1` / `int x = 1` |
| 打印 | `print(...)` / `printf(...)`（不换行） |
| 拼接文字 | `"a" + x` 或 `$"a{x}"` |
| 格式小数 | `$"{x:.2f}"` |
| 判断 | `if 条件 { } else if 条件 { } else { }` |
| 一行选择 | `var m = if a > b then a else b` |
| 数数循环 | `for 1:10 to i { }`（两头都算） |
| 跳步 / 倒序 | `for 0:10:2 to i { }` / `for 10:1:-1 to i { }` |
| 遍历数组/文字 | `for arr to x { }` / `for "abc" to ch { }` |
| 遍历字典 | `for dict to k { }`（拿到键） |
| 条件循环 | `while 条件 { }` |
| 跳过/跳出 | `continue` / `break` |
| 数组 | `[1, 2, 3]`，`a[0]`、`a.add(x)`、`a.len()`、`a.sort()` |
| 切片（闭区间） | `a[1:3]`（含 1 和 3） |
| 字典 | `{"k": 1}`，`d["k"]`、`d.get("k", 默认)`、`d.has("k")` |
| 枚举 | `enum E { a  b }` → `E.a` |
| 结构体 | `struct S { int x = 0 }` → `var s = new S(x = 1)` |
| 异常 | `try { } catch e { } finally { }` |
| 主动报错 | `throw "原因"` |
| 收尾 | `defer { ... }` |
| 可空类型 | `int? x = null`，用之前 `if x != null { }` |
| 类型转换 | `_int(s)`、`_float(s)`、`_str(n)`、`_int_or(s, 默认)` |
| 看类型 | `type(x)` |
| 多返回值 | `func f(): [int, int]` + `var[int, int](a, b) = f()` |
| 退出程序 | `_exit(0)` |

### 18.3 和 Python 的几处主要不同

| 你熟悉的 Python | Leno |
|---|---|
| 缩进决定块 | **大括号 `{ }`** 决定块（缩进只是给人看） |
| `if x >= 60:` | `if x >= 60 {` |
| `for i in range(1, 10):` | `for 1:9 to i {` ← **两头都算**，所以是 9 不是 10 |
| `len(a)` | `a.len()` |
| `a.append(x)` | `a.add(x)` |
| `d["k"]` 缺键抛 KeyError | `d["k"]` 缺键给 **null**（要默认值用 `d.get(k, 默认)`） |
| `True` / `False` / `None` | `true` / `false` / `null` |
| `and` / `or` / `not` | `and` / `or` / `not`（一样） |
| `print(f"{x}")` | `print($"{x}")` |
| `x = 1 if c else 2` | `var x = if c then 1 else 2` |
| 列表切片 `a[1:3]` 不含 3 | `a[1:3]` **含 3** |
| `def f(x):` | `func f(int x): int {
    return x
}` ← 参数和返回值都要写类型 |
| 整数无限精度 | 也无限（会自动变大，不用 `int` / `long` 区分） |

### 18.4 三条最值钱的经验

1. **报错先看行号，再读中文**：Leno 的报错几乎都写好了改法。
2. **`7 / 2` 是 `3`**：想要小数请写 `7.0 / 2`。
3. **区间都是"两头都算"**：`for 1:5` 是 5 次，`a[1:3]` 是 3 个元素。这一点贯穿全语言。

---

> 学到这里，你已经能读大部分 Leno 代码、写自己的小工具了。接下来按需查：
>
> - 想抠细节 / 查某个函数的所有参数 → [`Leno入门教程.md`](Leno入门教程.md)
> - 遇到诡异现象 → [`语言陷阱速查.md`](语言陷阱速查.md)
> - 写并发/线程 → [`并发选择指引.md`](并发选择指引.md)
> - 想看看真实项目怎么写 → 仓库的 `examples/` 目录（800 多个例子，按主题分文件夹）

