# LenoSDL3 窗口与控件参考

> 本文是控件 API 参考，代码块是**片段**，需要 SDL3 窗口环境。

> 本文按 **先窗口、后通用约定、再逐个控件** 的顺序，把 Leno 的桌面 GUI 能力讲清楚。
> 全部内容以 `Leno/leno_gui` 下的**官方活文档与实测用例**为准（`控件/总览/showcase.leno` 一窗展示全部控件，按控件分类的 `test_*.leno` 逐个验证属性），创建参数对照 `SDL3.leno` 门面的 `@optkeys` 白名单。代码照着改就能跑。
> 按项目搭建顺序的实战路线见 [LenoSDL3 控件实战教程](LenoSDL3_控件实战教程.html)；实测坑点见 [SDL3 常用 API 与易踩坑速查](扩展模块/LenoSDL3_常用API与易踩坑速查.html)；官方用例清单见文末[第十章](#十官方活文档导览leno_gui)。

## 目录

- [一、创建窗口](#一创建窗口)
- [二、通用约定（读控件前必看）](#二通用约定读控件前必看)
- [三、文字与按钮](#三文字与按钮)
- [四、输入与选择](#四输入与选择)
- [五、容器与布局](#五容器与布局)
- [六、列表与表格](#六列表与表格)
- [七、图片与图形进度](#七图片与图形进度)
- [八、反馈与浮层](#八反馈与浮层)
- [九、窗口增强](#九窗口增强)
- [十、官方活文档导览（leno_gui）](#十官方活文档导览leno_gui)

---

## 一、创建窗口

### 1.1 最小可运行骨架

```text
import "SDL3" as SDL3
use SDL3.Event
use SDL3.Renderer

main() {
    SDL3.ttfInit()                        // 用文字控件就必须先初始化字体子系统

    var win = SDL3.createWindow({title: "我的窗口", w: 800, h: 600, resizable: true})
    if not win.ok { SDL3.ttfQuit(); return }   // 建窗失败时后续操作全部无效

    win.addLabel({x: 24, y: 24, text: "你好，Leno", font_size: 18})
    var btn = win.addButton({x: 24, y: 60, w: 120, h: 36, text: "点我", type: "primary"})
    btn.on_click(func() { print("被点了") })

    win.run(
        func(Event ev): bool {
            if ev.isQuit() or ev.isWindowClose() { return false }  // 返回 false 结束主循环
            return true
        },
        func(Renderer r) {
            r.clearColor(#F5F6F8FF)       // 每帧清屏（最底层）
        }
    )
    SDL3.ttfQuit()
}
```

四件事缺一不可：

1. **`SDL3.ttfInit()` / `SDL3.ttfQuit()`**：只要用到文字（Label/Button/Edit…）就要一对；`showcase.leno` 和每个测试文件都这么写。
2. **`if not win.ok { ...; return }`**：无显示环境、DLL 缺失时 `createWindow` 返回 `ok=false` 的窗口，继续用它必崩。
3. **`run()` 必须传两个回调**：事件回调 `(Event) -> bool` 和渲染回调 `(Renderer)`。只给一个会报"只能调用函数（不是对象类型）"，看不出缺哪个。
4. **事件回调返回 `false` 才退出**：主循环本来就一直跑，不需要额外 `addTimer` 空转。

### 1.2 `createWindow` 的参数

| 参数 | 说明 |
|---|---|
| `title` | 窗口标题 |
| `w` / `h` | 客户区宽高 |
| `resizable` | 是否可缩放。`showcase` / `settings` 都用 `resizable: true` |
| `flags` | SDL 窗口标志。可写 `WindowFlag.RESIZABLE`（需 `use SDL3.WindowFlag`），老代码也用 `0x20` |
| `icon` | 窗口图标 PNG 路径。跨平台必须显式传（Windows 靠 exe 资源，Linux/macOS 没有） |

```text
import dirs
var icon = dirs.join(dirs.res_dir(), "images/app.png")
var win = SDL3.createWindow({title: "应用", w: 800, h: 600, icon: icon, resizable: true})
```

⚠ 图标路径用 `dirs.res_dir()` 拼，不要用 `script_dir()`（打包后只有 `res_dir` 指向释放出的资源）。

### 1.3 主题：在创建控件之前设置

`test_theme.leno` 演示了完整的主题系统——**顺序很关键：先设主题，再建窗口和控件**。

```text
SDL3.setTheme(SDL3.darkTheme())     // 或 SDL3.lightTheme()
var win = SDL3.createWindow({title: "主题测试", w: 880, h: 580})  // 不传 bg_color
// onRender 回调留空：让窗口内部用主题背景色清屏，别硬编码黑色
win.run(func(Event ev): bool { ... }, func(Renderer r) {})
```

要点：设置主题在**创建控件之前**；窗口**不传 `bg_color`**、`onRender` 留空，主题背景色才生效。

### 1.4 窗口常用方法

显示与状态：

| 方法 | 说明 |
|---|---|
| `show()` / `hide()` | 显示 / 隐藏 |
| `maximize()` / `minimize()` / `restore()` | 最大化 / 最小化 / 还原 |
| `setFullscreen(bool)` | 全屏切换 |
| `setResizable(bool)` / `setBordered(bool)` | 可缩放 / 有边框 |
| `setAlwaysOnTop(bool)` / `setOpacity(float)` | 置顶 / 整体透明度 |
| `setMinSize(w, h)` / `setSize(w, h)` / `setPosition(x, y)` | 尺寸与位置 |
| `getSize()` / `getPosition()` / `getID()` / `getHandle()` | 读取尺寸 / 位置 / 窗口 id / 原生句柄（`handle` 也可当字段用） |

绘制与交互：

| 方法 | 说明 |
|---|---|
| `setRoot(widget)` / `setRootAt(widget, ox, oy)` | 设置根布局（整窗交给一个容器） |
| `addXxx({...})` | 用绝对坐标直接往窗口加控件（见 2.1） |
| `setOverlay(func(Renderer r) {...})` | 顶层自绘，盖住所有控件 |
| `setContextMenu(bar, ctx)` | 注册窗口级右击菜单，由 `run` 统一接管弹出 |
| `addShortcut("Ctrl+C", func(){...})` / `removeShortcut(...)` | 快捷键 |
| `setShortcutGuard(func():bool {...})` | 返回 true 时屏蔽快捷键（如输入框正在编辑） |
| `addTimer(ms, func(){...})` / `addTimerOnce(...)` | 定时器 |
| `dumpLayout()` | 打印整窗布局诊断（见 2.4） |
| `redraw()` / `setMaxFPS(n)` | 主动重绘 / 限帧 |

### 1.5 退出与关闭的四个入口

| 入口 | 用在哪 | 行为 |
|---|---|---|
| `onEvent` 里 `return false` | 事件回调内 | 结束主循环 |
| `win.requestClose()` | 任意位置 | 投递一条"关窗请求"，和点 X 走同一条 `onEvent` 路径；关不关由 `onEvent` 决定 |
| `win.cancelClose()` | `onEvent` 里配合 `isWindowClose()` | 拦下这次销毁 → 做"关闭到托盘" |
| `SDL3.requestExit()` | 托盘回调、定时器、渲染回调 | 请求主循环收尾（下一轮生效），销毁所有窗口 |

```text
win.run(func(Event ev): bool {
    if ev.isWindowClose() {
        if tray == null { return false }   // 没托盘就别拦，否则没入口恢复
        win.hide()
        win.cancelClose()
        return true
    }
    return true
}, func(Renderer r) {})
```

⚠ **不要用 `SDL3.quit()` 退出程序**：它只关 SDL 子系统，**主循环还在跑**，进程不会退出（自更新替换 exe 会失败）。用 `requestExit()`。

### 1.6 三层绘制顺序

```
① onRender（run 的第二个回调） —— 最底层，在控件之下
② 控件树（setRoot 根布局 + addXxx 注册的控件）
③ setOverlay 回调            —— 最上层，盖住一切
```

想让自绘盖在控件之上，必须放 `setOverlay`；放 `onRender` 里会被控件盖掉。

---

## 二、通用约定（读控件前必看）

### 2.1 两种创建方式，别混用

这是 `leno_gui` 里最一致的约定，也是新手最常踩的坑：

| 写法 | 注册进窗口 | 谁绘制 | 用在哪 |
|---|---|---|---|
| `SDL3.createXxx({...})` | ✗ | 交给容器（`box.add(...)` / `panel.add(...)` / `tab.addToPage(...)`） | **放进布局/容器的控件** |
| `win.addXxx({...})` | ✓ | 窗口自动绘制 | 用绝对坐标直接摆的控件 |

⚠ 混用会让同一控件被窗口画一次、又被容器摆一次——重复绘制、位置打架。

**`showcase.leno` 开头的注释把例外写得很清楚**：

- `MenuBar` / `ComboBox` 必须用 `win.addXxx`（依赖窗口的**第二遍弹层绘制**）。
- Panel 边框卡片里，子控件用 `SDL3.createXxx` + `panel.add`。
- ScrollView / TabControl / HBox / VBox / AnchorBox 本身是顶层容器，内部用 `createXxx`。
- 例外中的例外：ComboBox 经 `tab.addToPage` 添加时，靠 `sdl_combobox` 的**全局注册表**兜底画下拉层（`settings.leno` 就这么用）。

一句话：**顶层绝对定位用 `win.addXxx`，容器内用 `createXxx` + `add`；MenuBar 和顶层 ComboBox 走 `win.addXxx`。**

### 2.2 通用参数与颜色

几乎所有 `createXxx` 都支持这些键：

| 参数 | 说明 |
|---|---|
| `x` / `y` / `w` / `h` | 位置与尺寸（放进布局时 `x/y` 一般省略） |
| `visible` / `enabled` | 可见 / 可交互 |
| `cursor` | 悬停光标：`SDL3.SystemCursor.POINTER/WAIT/TEXT/CROSSHAIR/MOVE/NOT_ALLOWED`，`-1` = 不改变 |
| `tip` | 悬停提示文字（要 `SDL3.setTipDelay(ms)` 设延迟） |
| `bg_color` / `border_color` / `text_color` | 背景 / 边框 / 文字颜色 |
| `radius` | 圆角半径（`0` 直角，越大越圆） |
| `font_size` / `font_path` / `font_style` | 字体三件套。`font_style` 用数字：`1` 粗体、`2` 斜体、`4` 下划线，可按位组合 |

颜色统一写 `#RRGGBBAA`，例如 `#282A32FF`（不透明）、`#00000000`（全透明）、`#FF6E8240`（半透明红）。

⚠ 少数 API 用**不带 alpha 的 `0xRRGGBB` 整数**，如 `Table.set_row_color(i, 0xFF6060)`、`set_row_color(i, RED)`；两者别混。

### 2.3 弹性布局四参数 `grow/shrink/basis/align`

`test_layout.leno` 是这套语义的完整实测。容器 `add(widget, opts)`：

```text
HBox row = win.addHBox({x: 10, y: 44, w: 800, h: 46, spacing: 8, pad_x: 6, pad_y: 6})
row.add(SDL3.createButton({text: "grow:2", w: 80, h: 34}), {grow: 2})   // 占 2/4
row.add(SDL3.createButton({text: "grow:1", w: 80, h: 34}), {grow: 1})   // 各占 1/4
row.add(SDL3.createButton({text: "grow:1", w: 80, h: 34}), {grow: 1})
```

| 参数 | 语义 |
|---|---|
| `grow` | **权重，不是像素**。按权重分剩余空间；`grow:2 : grow:1 : grow:1` = 2:1:1 |
| `shrink` | 空间不足时按 `shrink × basis` 比例收缩；`shrink:0` 不收缩、允许溢出（默认 1） |
| `basis` | 主轴分配基数，**不是固定宽度**。不写时用控件加入那一刻的自然尺寸，事后 `set_size` 改了也不影响 |
| `align` | 交叉轴 `0=start / 1=center / 2=end / 3=stretch` |
| `minW` / `maxW` / `minH` / `maxH` | 最小/最大尺寸约束（`{grow:1, maxW:120}`、`{grow:1, minH:60}`） |
| `justify` | 主轴分布：`0` 起始 / `1` 居中 / `3` space-between（`test_layout` 实测） |
| `expand: true` | 老写法，等价 `grow:1`，向后兼容 |

想钉死宽度写 `{basis: w, grow: 0, shrink: 0}`。排障用 `win.dumpLayout()` 或 `SDL3.dumpLayout(容器)`，它会提示"`free 未被吸收`"——正是"没铺开"的最常见根因。

**AnchorBox 用锚点参数**，不是上面那套：`{left:8, top:8}`、`{right:8, top:8}`、`{centerX:true, centerY:true}`、`{right:8, bottom:8}`。

### 2.4 回调签名（按实测，别猜）

```text
btn.on_click(func() { ... })                              // 绝大多数控件：无参
cv.on_click(func(float lx, float ly) { ... })              // Canvas：局部坐标
cb.on_change(func(bool v) { ... })                         // CheckBox/Toggle/Radio
sl.on_change(func(float v) { ... })                        // Slider/SpinBox/ProgressBar
cbx.on_change(func(int idx) { ... })                       // ComboBox
lb.on_change(func(Array[int] idxs) { ... })                // ListBox：选中下标数组
tab.on_change(func(int idx) { ... })                       // TabControl
bar.on_select(func(string menu, string id) { ... })        // MenuBar：菜单名 + 项 id
tbl.on_select(func(int row) { ... })                       // Table
tbl.on_check(func(int col, Array[int] checked) { ... })    // Table 勾选列
cv.on_draw(func(Renderer r, float ox, float oy, float cw, float ch) { ... })
```

事件对象常用方法：`ev.isQuit()`、`ev.isWindowClose()`、`ev.isKeyDown()` + `ev.scancode()`、`ev.isMouseButtonDown()`、`ev.mousePos()`、`ev.isMouseWheel()` + `ev.wheelY()`（**正值 = 往上滚看更早内容**）、`ev.isWindowResized()`。

窗口缩放若要自己重排绝对定位的容器，在 `isWindowResized()` 分支里 `getSize()` 后逐个 `set_size()` / `set_pos()`（`test_layout.leno` 就是这么做的）。

### 2.x 写带动画的控件：实现 `Tickable.tick(dt)`（2026-11-27）

自己写的控件如果有"会持续几帧的过渡"（滑动、渐变、回弹），**不要**在 `render()` 里推进，
也不要自己 `core.requestRedraw()` 续帧——那样漏一处动画就会卡在中间（框架早期就这么踩过）。

改成实现 `Tickable`，只返回"还在动"，续帧和 dt 都由窗口负责：

```text
export struct MyThing impl Widget, Tickable {
    Tween anim              // 内核见 lib/sdl_animator.leno（缓动/弹簧）
    ...
    func tick(float dt): bool {
        bool moving = anim.step(dt)
        if moving { core.markFrameRedraw() }   // 位置变了才标脏；**不是**请求下一帧
        return anim.is_moving()                 // 还在动 ⇒ 窗口自动再画一帧 ✓
    }
    func render(Renderer r) { float t = anim.value() ... }   // 这里只读进度
}
```

规则：

- `tick` 每帧**只调一次**（在绘制前），`dt` 已钳到 33ms，与滚动内核同口径；
- 目标值（target）最好在 `tick` 里也更新一次——`tick` 早于 `render`，只在 `render` 里设会让动画慢一帧；
- 跟手交互（手指拖动）期间要在 `tick` 里直接 `return false`，否则惯性和手指抢方向盘；
- **自己仍然 `core.requestRedraw()`**（即使窗口会汇总续帧）：不把"下一帧"全押在一处。

**写容器的人必须转发 `tick`（这条最容易漏，代价是整页不动）**

窗口只遍历顶层 `_widgets` 和 `setRoot` 的根控件，**容器里的控件不在那个列表里**：

```text
export struct MyBox impl Widget, Tickable {
    Array[Widget] kids = []
    func tick(float dt): bool {
        bool m = false
        for kids to c { if c is Tickable => tk { if tk.tick(dt) { m = true } } }
        return m
    }
}
```

`Panel` / `HBox` / `VBox` / `AnchorBox` / `TabControl` / `Card` / `ScrollView` 都已转发。
⚠ `TabControl` 有**两条**装载路径，必须都转：`setPageLayout()` ⇒ `_pageLayouts[_active]`、
`addToPage()` ⇒ `pages[_active]`。只转一条时，用另一条装载的页会"滚轮有速度、画面一步不动"
（`process` 两条都转发，`tick` 漏一条就是这种症状）。

⚠ 自定义控件的 `export struct` **别用通用名**（`Anim`/`Node`/`State`…）：类型表全局按名字索引，
跨模块重名会静默读错字段。起 `MyThingPanel` 这种带归属的名字，细节见仓库根的 `AGENTS.md` §13。

---

## 三、文字与按钮

### 3.1 Label —— 文字标签

```text
Label lb = SDL3.createLabel({text: "歌曲名", font_size: 14, text_color: #333333FF,
                             align: 0, tip: "完整标题"})
lb.set_text("新标题")
box.add(lb, {grow: 1, align: 1})
```

**主要参数**：`text`、`font_size`、`font_path`、`font_style`、`text_color`、`hover_color`、`align`（`left`/`center`/`right`）、`cursor`、`hover_shift`、`tip`、`max_w`、`truncate`、`wrap`、`wrap_w`、`scroll_always`、`visible`、`enabled`。

**常用方法**：`set_text()`、`set_text_color()`、`set_hover_color()`、`set_font_size()`、`set_font_path()`、`set_align()`、`set_max_w()`、`set_truncate()`、`set_wrap()`、`set_wrap_w()`、`get_text()`、`get_lines()`、`measure_w()`、`measure_h()`、`on_click()`。

### 3.2 Button —— 按钮

`test_button_v3.leno` 逐项测了类型、颜色、外观开关、光标、字体样式和动态方法。

```text
// 五种预设
Button b = win.addButton({text: "Primary", x: 30, y: 55, w: 130, h: 40,
                          type: "primary", tip: "主要操作"})
b.on_click(func() { do_it() })

// 纯图标按钮：不传 text（默认 ""），只给 image_path
Button icon = SDL3.createButton({image_path: ui.ico("d_trash.png"),
                                 image_size: 16, w: 26, h: 26, radius: 6, background: false})
```

**主要参数**：`text`（默认 `""`）、`type`（`primary`/`danger`/`success`/`warning`/`dark`/`normal`）、`w`/`h`、`radius`、`bg_color`、`text_color`、`hover_color`、`pressed_color`、`border`、`border_color`、`shadow`、`background`、`font_size`、`font_path`、`font_style`、`padding`、`align`、`image_path`、`image_size`、`image_pos`、`image_gap`、`image_mode`、`image_alpha`、`image_tint`、`image_path_hover`、`image_path_pressed`、`image_path_disabled`、`bg_image`、`cursor`、`tip`、`enabled`、`visible`。

**导航项选中态（0.1.2 新增，反哺 Aria 侧栏）**：给按钮加一条左侧指示条，不必自己再套 Canvas。

```text
Button nav = SDL3.createButton({text: "首页", w: 150, h: 32, radius: 8,
                                bg_color: #FFFFFFFF, selected: true,
                                select_bar_w: 3, select_bar_pad_y: 6,
                                select_bar_color: #E76F9BFF})
nav.set_selected(false)                 // is_selected() 可读回
nav.set_select_bar(3, #E76F9BFF)        // 也可运行时改宽度 / 颜色
```

`select_bar_w = 0`（默认）时一像素都不画，老行为完全不变。指示条画在背景之上、图标文字之下，两端按按钮圆角收口。

**图标 + 文字的垂直对齐**：中文字体的行盒比可见字形高，按行盒居中时文字会看起来比图标低 1px 左右。侧栏/导航项可用 `text_offset_y` 微调（负值上移文字），也可运行时调 `set_text_offset_y()`。**注意方向**：上移文字会让图标相对显得偏低，微调量要小（Aria 侧栏实测 `-0.6` 最居中，`-1.15` 就过头了）；图标本身若 bbox 不居中（如带底托的下载图标），应修图标画布位置而不是加大文字偏移。

```text
Button nav = SDL3.createButton({text: "首页", image_path: ui.ico("w_home.png"),
                                image_size: 17, image_gap: 9, image_tint: #77646DFF,
                                text_offset_y: -0.6, h: 40, radius: 10})
```

**常量**：`Button.IMG_LEFT/RIGHT/TOP/BOTTOM`、`Button.IMG_ASPECT_FIT/STRETCH/ASPECT_FILL`、`Button.ALIGN_LEFT/CENTER/RIGHT`；`cursor` 用 `SDL3.SystemCursor.*`。

**动态方法**（全是实测）：`set_text()`、`set_type()`、`set_bg_color()`、`set_text_color()`、`set_hover_color()`、`set_font_size()`、`set_font_style()`、`set_radius()`、`set_border()`、`set_shadow()`、`set_background()`、`set_cursor()`、`set_image()`、`set_image_pos()`、`set_image_mode()`、`set_text_offset_y()`、`set_enabled()`、`set_visible()`、`set_pos()`、`set_size()`、`get_text()`、`get_x()/get_y()/get_w()/get_h()`、`focus()`、`blur()`、`activate()`、`on_click()`。

⚠ `background: false` 的纯图标按钮会连 hover 效果一起跳过。

### 3.3 LinkButton —— 链接按钮

**主要参数**：`text`、`url`、`color`、`hover_color`、`visited`、`underline`、`underline_hover`、`font_size`、`font_path`、`tip`、`visible`、`enabled`。

**方法**：`set_text()`、`set_url()`、`set_visited()`、`set_underline()`、`set_text_color()`、`set_hover_color()`、`on_click()`、`get_text()`、`get_url()`。

⚠ `url` 字段**只用于显示**，控件内部只回调 `onClick`——不绑回调点了没反应。

### 3.4 CheckBox —— 复选框

```text
var cb = win.addCheckBox({text: "我同意用户协议", x: 40, y: 40, checked: false})
cb.on_change(func(bool v) { print("复选框 -> " + v) })
bool v = cb.is_checked()
```

**主要参数**：`text`、`checked`、`box`、`gap`、`checked_color`、`unchecked_color`、`border_color`、`font_size`、`font_path`、`font_style`、`text_color`、`cursor`、`tip`、`enabled`、`visible`。
**方法/回调**：`set_checked()`、`is_checked()`、`set_text()`、`on_change(func(bool v){...})`。

### 3.5 RadioButton —— 单选框

同 `group` 字符串的为一组，组内互斥；不同 `group` 互不影响。

```text
win.addRadioButton({text: "选项 A", x: 40, y: 100, group: "mode", checked: true})
win.addRadioButton({text: "选项 B", x: 40, y: 140, group: "mode"})
```

**参数/方法**同 CheckBox，多一个 `group`；回调 `on_change(func(bool v){...})`——**只在被选中时处理 `if v`**，取消选中那次也会回调。

### 3.6 Toggle —— 开关

```text
var tg = win.addToggle({text: "Wi-Fi", x: 240, y: 200, on: true})   // 切换带 ~150ms 滑动
tg.on_change(func(bool v) { ... })
bool on = tg.is_on()
```

**主要参数**：`on`、`text`、`anim`（默认 **true**，`anim:false` 关掉动画）、`anim_speed`、`on_color`、`off_color`、`w`/`h`、`font_size`、`text_color`、`tip`、`enabled`、`visible`。
**方法/回调**：`set_on()`、`is_on()`、`get_anim_pos()`（滑块当前显示位置 0~1）、`on_change(func(bool v){...})`。

⚠ 2026-11-27 起动画**默认开启**（以前默认关，点一下"啪"地跳过去，和新的滚动/悬停/弹层渐变放一起很生硬）。想要瞬时切换传 `anim: false`。

---

## 四、输入与选择

### 4.1 Edit —— 单行 / 多行输入框

`showcase.leno` 的"文本输入"卡片给了三种典型用法；`settings.leno` 演示了 IME 句柄下发。

```text
// 单行 / 密码 / 多行
win.addEdit({x: 90, y: 322, w: 220, h: 30, placeholder: "请输入姓名"})
win.addEdit({x: 90, y: 362, w: 220, h: 30, password: true, placeholder: "密码"})
win.addEdit({x: 90, y: 402, w: 220, h: 80, multiline: true,
             text: "多行编辑框\n支持换行、选区、撤销/重做、IME"})

// 放进容器时，若要用 IME/右键菜单，必须下发窗口句柄
var ed = SDL3.createEdit({placeholder: "用户名", tip: "支持右键菜单：复制/粘贴/全选"})
ed.set_window(win.handle)
panel.add(ed)

ed.on_change(func(string s) { ... })
ed.on_enter(func() { ... })
```

**主要参数**：`text`、`placeholder`、`placeholder_color`、`multiline`、`wordWrap`、`password`、`readonly`、`pad_x`、`radius`、`border`、`border_color`、`bg_color`、`draw_bg`、`focus_color`、`font_size`、`font_path`、`font_style`、`text_color`、`w`/`h`、`tip`、`enabled`、`visible`。

**方法**：`set_text()`、`get_text()`、`get_text_length()`、`set_readonly()`、`set_password()`、`set_multiline()`、`set_word_wrap()`、`set_placeholder()`、`set_pad_x()`、`set_window(handle)`、`set_window_size()`、`focus()`、`blur()`、`get_scroll_y()`、`get_max_scroll_y()`、`on_change()`、`on_enter()`、`set_context_menu_enabled()`、`on_context_select()`。

### 4.2 SpinBox —— 数字输入框

```text
var sp = SDL3.createSpinBox({x: 590, y: 286, w: 120, min: 10, max: 20,
                             value: 14, step: 1, int_mode: true})
sp.on_change(func(float v) { ... })
```

**主要参数**：`value`、`min`、`max`、`step`、`decimals`、`int_mode`、`arrow_color`、`arrow_w`、`focus_color`、`bg_color`、`border_color`、`font_size`、`placeholder`、`tip`、`w`/`h`。
**方法**：`set_value()`、`get_value()`、`set_range()`、`set_step()`、`set_int_mode()`、`set_decimals()`、`on_change(func(float v){...})`、`get_text()`。

### 4.3 Slider —— 滑块

```text
var sl = win.addSlider({x: 470, y: 96, w: 240, h: 24, min: 0, max: 100, value: 40, tip: "拖动调节"})
sl.on_change(func(float v) { status.set_text("滑块 = " + (v as string)) })

var vertical = win.addSlider({x: 470, y: 140, w: 24, h: 150, min: 0, max: 10, value: 3, vertical: true})
```

**主要参数**：`value`、`min`、`max`、`step`、`vertical`、`show_value`、`track_color`、`fill_color`、`thumb_color`、`text_color`、`font_size`、`tip`、`w`/`h`。
**方法**：`set_value()`、`get_value()`、`set_range()`、`set_track_gradient()`、`clear_track_gradient()`、`on_change(func(float v){...})`。

### 4.4 ProgressBar —— 进度条

```text
var pg = win.addProgressBar({x: 560, y: 140, w: 240, h: 22, value: 30, clickable: true})
pg.on_change(func(float v) { ... })
pg.set_value(pg.get_value() + 20.0)
```

**主要参数**：`value`、`min`、`max`、`show_text`、`clickable`、`fill_color`、`track_color`、`text_color`、`font_size`、`anim_speed`、`hit_pad_y`、`tip`、`w`/`h`。
**方法**：`set_value()`、`get_value()`、`get_display_value()`、`on_change()`、`on_hover(func(float v){...})`。

### 4.5 Calendar —— 日历

月历网格 + 每天状态色 + 可选点选/切月。`on_pick` / `on_month_change` 回调；`set_mark()` / `set_marks()` / `clear_marks()` 标记日期；`weekdayName(y, m, d, names)` 的星期名由调用方给，控件不预设语言。

**主要参数**：`year`、`month`、`today`、`month_fmt`、`week_start`、`marks`、`cell_min`、`cell_max`、`cell_radius`、`filled_color`、`plain_color`、`today_color`、`alert_color`、`font_size_day/head/week/legend`、`show_header`、`pad`、`gap`、`w`/`h`。

### 4.6 pickColor —— 颜色选择对话框

跨平台自带 8 色板 + RGBA 滑杆 + 实时预览 + 十六进制值，不依赖系统色板。

```text
SDL3.pickColor({color: 当前色, title: "选个颜色"}, func(Color c) { 当前色 = c })
```

⚠ 结果走**第二个形参的回调**——主循环已跑时 `runModal` 只注册不阻塞，别读返回值；也别把回调塞进 Dict（`opts.get(...) as func(Color):void` 实测恒为 null）。

---

## 五、容器与布局

### 5.1 HBox / VBox / AnchorBox

| 容器 | 排列方式 |
|---|---|
| `HBox` | 子控件沿主轴横向排 |
| `VBox` | 子控件沿主轴纵向排 |
| `AnchorBox` | 按锚点精确落点 |

**HBox / VBox 参数**：`x`/`y`/`w`/`h`、`pad_x`/`pad_y`（或 `padTop`/`padBottom`/`padLeft`/`padRight`）、`spacing`、`justify`、`bg_color`、`bg_radius`、`clip`、`visible`、`enabled`。
**方法**：`add(widget, opts)`、`remove()`、`clear()`、`reset()`、`set_bg_color()`、`set_pos()`、`set_size()`、`measure_w()`、`measure_h()`。

```text
// AnchorBox：锚点定位，不是 grow/basis
var ab = win.addAnchorBox({x: 410, y: 410, w: 390, h: 350, pad_x: 8, pad_y: 8})
ab.add(SDL3.createLabel({text: "左上"}), {left: 8, top: 8})
ab.add(SDL3.createLabel({text: "居中"}), {centerX: true, centerY: true})
ab.add(SDL3.createButton({text: "右下", w: 90, h: 32}), {right: 8, bottom: 8})
```

布局细节见 2.3 和[布局配方](布局配方.html)。

### 5.2 GridLayout —— 网格布局

**参数**：`cols`（列数）、`col_weights`、`col_spacing`、`row_spacing`、`spacing`、`pad_x`/`pad_y`、`min_col_width`、`align`、`w`/`h`。
**方法**：`add(widget, {align: 1})`、`set_cols()`、`remove()`、`clear()`、`count()`、`measure_h()`、`measure_w()`。

```text
GridLayout grid = SDL3.createGridLayout({cols: 2, col_weights: [1, 2], spacing: 8})
grid.add(SDL3.createLabel({text: "名称"}), {align: 1})
grid.add(SDL3.createLabel({text: "值"}),   {align: 1})
```

### 5.3 Panel —— 面板

`showcase` 和 `settings` 都用一个 `card()` 构建器做"边框卡片 + 标题"——**容器加入布局用 `createPanel` + `tab.addToPage`，顶层用 `win.addPanel`**：

```text
// showcase：顶层卡片
func card(Window win, float x, float y, float w, float h, string title): Panel {
    var p = win.addPanel({x:x, y:y, w:w, h:h, bg_color: #1C1E26FF, radius:10, border_color: #5A5F6EFF})
    p.add(SDL3.createLabel({x:x+14, y:y+12, text:title, font_size:16, text_color: #B4C8FFFF}))
    return p
}
```

**参数**：`bg_color`、`border`、`border_color`、`border_alpha`、`radius`、`clip`、`w`/`h`、`enabled`、`visible`。
**方法**：`add()`、`remove()`、`clear_children()`、`setLayout()`、`setLayoutPadded()`、`set_bg_color()`。

### 5.4 GroupBox —— 分组框

带标题的边框容器，可嵌套（`test_new_widgets.leno` 有完整属性实测）。

**参数**：`title`、`title_pad`、`title_color`、`radius`、`border_alpha`、`border_color`、`bg_color`、`clip`、`w`/`h`。
**方法**：`set_title()`、`add()`、`remove()`、`clear_children()`、`setLayout()`、`setLayoutPadded()`、`set_bg_color()`。

### 5.5 ScrollView —— 滚动视图

`showcase` 的标准写法：容器注册进窗口，内容用一个 `createVBox` 自适应。

```text
var sv = win.addScrollView({x: 878, y: 426, w: 372, h: 180, content_w: 340, content_h: 520})
var svBox = SDL3.createVBox({pad_x: 10, pad_y: 10, spacing: 8})
for 12 to i {
    svBox.add(SDL3.createButton({text: "条目 " + i, h: 32}), {})
}
sv.set_content(svBox)
```

**参数**：`content_w`/`content_h`、`fit_w`/`fit_h`、`w`/`h`、`step`、`friction`、`drag_friction`、`smooth`（已废弃）、`bar_w`、`bar_color`、`bar_auto_hide`、`bar_hover_color`、`bg_color`、`border`、`border_color`、`border_alpha`、`radius`、`clip`。
**方法**：`set_content()`、`set_content_size()`、`set_scroll()`、`scroll_to()`、`scroll_by()`、`fling()`、`ensure_visible()`、`near_bottom()`、`get_scroll_x()`、`get_scroll_y()`、`get_max_scroll_y()`、`get_layout_epoch()`、`get_velocity_x()`/`get_velocity_y()`、`get_overscroll_x()`/`get_overscroll_y()`、`is_animating()`。

**滚动是物理的（2026-11-27 起是唯一行为，没有开关）**：滚轮叠加速度后按 dt 滑行（起步加速、停下滑行），手指甩动按 px/秒积分（60Hz 与 144Hz 走同样远），拖出边界是弹性越界、松手由欠阻尼弹簧拉回。

```text
var sv = win.addScrollView({x: 20, y: 20, w: 400, h: 300, content_w: 400, content_h: 1200})
// 可选：friction（滚轮每帧保留率，默认 0.88，越小停得越快；0.96 很"飘"）
//       drag_friction（甩动惯性，默认 0.94，比滚轮滑得更远）
sv.fling(0, -1500)          // 程序化甩一下：给初速度（px/s），走同一套物理
sv.is_animating()           // 还有没有未收敛的运动（做"滚动中"效果时用）
```

⚠ 三件事：

- `content_h` 必须 **≥ 内容的自然高**，否则底部那一截永远滚不到；内容高不确定就别传，让它自动量。
- `scroll_by` / `set_scroll` / `ensure_visible` 仍是**精确位移**（程序语义可预期），"飞"只属于滚轮和甩动。
- `smooth: true` 已废弃（no-op）：滚轮本来就平滑了，老调用方不用改，但新代码别传。

回归见 `test/test_scroll_physics.leno` / `test/test_scroll_touch.leno`。

⚠ 子孙跟不跟着滚，取决于内容根是哪种控件，有三种情况；命中裁剪另见 `自测/test_scrollview_hitclip.leno`。

### 5.6 TabControl —— 标签页

⚠ **页内坐标是"相对内容区左上角"**：内容区原点 = `(tab.x, tab.y + tab_h)`，`settings.leno` 里的 `card()` 就是这么换算的。

```text
var tab = win.addTabControl({x: 878, y: 684, w: 372, h: 250,
                             tabs: ["基础", "高级"], active: 0, tab_h: 30})
tab.addToPage(0, SDL3.createLabel({text: "基础设置"}), 20, 20)      // (widget, dx, dy)
tab.addToPageLayout(0, widget, {grow: 1})
tab.setPageLayout(1, SDL3.createVBox({}))
tab.set_active(0) / tab.get_active()
tab.on_change(func(int idx) { ... })
```

**参数**：`tabs`、`tab_icons`、`active`、`tab_h`、`tab_radius`、`tab_icon_size`、`underline`、`show_header`、`accent_color`、`active_color`、`active_text_color`、`bar_color`、`tab_color`、`bg_color`、`border`、`clip`、`font_size`、`w`/`h`。

**下划线滑动（2026-11-27）**：切页时下划线（`underline:true`）**滑过去**而不是瞬跳（~150ms 缓动，
由 `lib/sdl_animator.leno` 的 `Tween` 驱动）。只读：`get_underline_x()`、`get_underline_w()`、`is_underline_moving()`。

⚠ 同页混用绝对定位和 `addToPageLayout` 会提示一次（警告，不是错误）。

### 5.7 Splitter / Card

- **Splitter**（可拖分割条）：参数 `first`、`second`、`orientation`、`ratio`、`min_first`、`min_second`、`sep_color`、`sep_width`、`hover_color`、`hit_pad`、`w`/`h`；方法 `set_first()`、`set_second()`、`set_ratio()`、`get_ratio()`。常量 `SDL3.SPLIT_HORIZONTAL` / `SPLIT_VERTICAL`。事件实测见 `自测/test_splitter_events.leno`。
- **Card**（海报/商品卡）：参数 `image_path`、`image_mode`、`image_aspect`、`image_h`、`image_radius`、`title`、`title_size`、`subtitle`、`badge`/`badges`、`badge_pos`、`pad`、`gap`、`text_align`、`hover_lift`、`bare`、`selected`、`sel_color`、`bg_color`、`radius`、`w`/`h`；方法 `set_image()`、`set_texture(tex, own)`、`set_title()`、`set_subtitle()`、`add_badge()`、`set_content()`、`set_selected()`、`on_click()`。设计细节见 [Card 卡片控件设计文档](LenoSDL3_Card卡片控件设计文档.html)。

⚠ `set_texture(tex, own)` 的 `own:false` 表示借用共享纹理，销毁时不要重复释放。

---

## 六、列表与表格

> **滚动手感（2026-11-27）**：六个自带滚动的控件（`ScrollView` / `Table` / `VirtualGrid` /
> `ListBox` / `TreeView` / `ComboBox` 弹层）统一用同一套**物理滚动**（`lib/sdl_scrollphys.leno`）：
> 滚轮叠加速度、按 dt 解析积分、撞到上下边界回弹。`ScrollView` / `Table` / `VirtualGrid`
> 另外支持**手指拖动 + 甩动惯性**（只对触摸生效，桌面鼠标左键语义不变）。
> 只读窗口统一为：`get_scroll_velocity()`（px/秒）、`get_overscroll_y()`、`is_scrolling()`。

> **过渡动画（2026-11-27）**：`Card` 的 hover 抬起与底色、`ListBox` / `Table` / `TreeView` 的悬停行、
> `TabControl` 的下划线、`ComboBox` 弹层展开，统一走 `lib/sdl_animator.leno` 的 `Tween`
> （约 150ms 缓动，按 dt 推进 ⇒ 60/144Hz 一致）。只读进度：`get_hover_anim()`（Card/ListBox/Table/TreeView）、
> `get_open_anim()`（ComboBox）、`get_underline_x()` + `is_underline_moving()`（Tab）。

### 6.1 ListBox —— 列表

```text
var lb = SDL3.createListBox({x: 470, y: 396, w: 160, h: 150,
                             items: ["苹果", "香蕉", "橘子"], selected: 0})
lb.on_change(func(Array[int] idxs) { status.set_text("选中 " + idxs.len() + " 项") })

var multi = SDL3.createListBox({items: ["红", "绿", "蓝"], mode: 1})   // mode:1 多选
```

⚠ `on_change` 收的是 **`Array[int]` 选中下标数组**，不是单个 int。单选时点已选中的那一行不回调。

**参数**：`items`、`selected`、`item_h`、`mode`、`image_path`、`image_size`、`image_gap`、`image_pad`、`sel_color`、`hover_color`、`bg_color`、`border_color`、`scroll_color`、`bar_auto_hide`、`w`/`h`。
**方法**：`set_items()`、`add_item()`、`append_item()`、`append_bottom()`、`remove_item()`、`clear()`、`set_selected()`、`set_selected_indices()`、`select_all()`、`clear_selection()`、`get_selected_index()`、`get_selected_indices()`、`get_selected_text()`、`scroll_to_bottom()`、`is_at_bottom()`、`index_at()`、`on_change(func(Array[int] idxs){...})`、`on_activate()`。

### 6.2 ComboBox —— 下拉框

顶层**必须 `win.addComboBox`**；放进 Tab/容器时用 `createComboBox` + `add`（靠全局注册表画弹层）。

```text
var cbx = win.addComboBox({x: 470, y: 700, w: 240, h: 32,
                           items: ["选项一", "选项二"], placeholder: "请选择",
                           selected: 1, tip: "下拉演示"})
cbx.on_change(func(int idx) { status.set_text("下拉: " + cbx.get_selected_text()) })
```

⚠ `on_change` 收 **`int` 下标**——和 ListBox 不同。

**弹层动画（2026-11-27）**：展开时高度从 0 长到目标（~150ms）；收起仍是瞬时（收起后焦点/命中状态已变，
延迟绘制容易点穿）。`get_open_anim()` 返回展开进度（0~1），弹层滚动相关接口同 ListBox。

**参数**：`items`、`selected`、`editable`、`placeholder`、`item_h`、`popup_h`、`item_images`、`icon`、`icon_size`、`image_size`、`image_gap`、`show_arrow`、`sel_color`、`hover_color`、`bg_color`、`border`、`radius`、`w`/`h`。
**方法**：`set_items()`、`set_items_with_images()`、`add_item()`、`clear()`、`set_selected()`、`get_selected()`、`get_selected_text()`、`set_editable()`、`set_suggestions()`、`open_list()`、`close()`、`on_change(func(int idx){...})`、`on_text_change()`、`on_enter()`。

### 6.3 Table —— 表格

`test_table_features.leno` 演示了复选框列、行级颜色和空状态。

```text
Array[string] headers = ["", "任务", "状态", "耗时"]
Array[int] aligns = [1, 0, 1, 2]
Array[Array[string]] rows = [["", "编译模块A", "成功", "1.2s"], ...]

var tbl = win.addTable({
    x: 30, y: 64, w: 580, h: 280,
    headers: headers, aligns: aligns, header_aligns: [1,1,1,1], rows: rows,
    col_widths: [40, 220, 140, 100],
    check_col: 0,                       // 第 0 列为复选框列
    sortable: true, resizable: true, zebra: true, item_h: 28, header_h: 28,
    empty_text: "暂无数据 — 点击\"添加行\"恢复"
})

int RED = 0xFF6060                       // ⚠ 行级颜色是 0xRRGGBB 整数，不是 #RRGGBBAA
for rows.len() to i {
    if rows[i][2] == "错误" { tbl.set_row_color(i, RED) }
}
tbl.on_check(func(int col, Array[int] checked) { print("勾选 " + checked.len() + " 行") })

tbl.set_headers(headers); tbl.set_rows(rows); tbl.add_row([...], "")
tbl.set_cell(row, col, "值"); tbl.get_cell(row, col)
tbl.get_selected_row() / tbl.get_selected_rows()
tbl.sort_by(col); tbl.check_all(); tbl.uncheck_all(); tbl.clear_row_colors()
tbl.set_col_cell_type(col, "progress")   // 进度条列
tbl.on_cell_draw(func(Renderer r, int row, int col, float x, float y, float w, float h) { ... })
tbl.on_select(func(int row) { ... })
tbl.on_edit_commit(func(int row, int col, string v) { ... })
```

**参数（节选）**：`headers`、`rows`、`aligns`、`header_aligns`、`col_widths`/`col_ratios`、`item_h`、`header_h`、`row_numbers`、`zebra`、`sortable`、`multi_select`、`cell_select`、`editable`、`editable_cols`、`frozen_cols`、`cell_types`、`numeric_cols`、`image_col`、`check_col`、`empty_text`、`sel_color`、`hover_color`、`row_radius`、`sep_color`、`w`/`h`。

⚠ 表格方法 100+ 个，全部见 `lib/sdl_table.leno`；单选时点已选行不回调、进度条列与自绘回调的细节见速查。

**滚动手感（2026-11-27）**：滚轮不再"一步跳一行"，而是叠加速度后按 dt 滑行（一格 ≈1.4 行），
撞到上下边界会回弹；**手指按住行往上拖**也能滚（手机上是唯一手势），抬手带惯性。
程序化定位（键盘选行、`ensure_row_visible`、拖滚动条）仍是**立即到位**。
只读状态：`scroll_y()`、`get_scroll_velocity()`、`get_overscroll_y()`、`is_scrolling()`。

### 6.4 TreeView —— 树形列表

**参数**：`items`、`text`、`image`、`image_expanded`、`image_mode`、`image_size`、`checkable`、`show_check`、`show_lines`、`indent`、`item_h`、`line_color`、`check_color`、`sel_color`、`hover_color`、`w`/`h`。
**方法**：`set_items()`、`add_child()`、`remove_node()`、`expand()`、`expand_all()`、`collapse_all()`、`set_checked()`、`get_checked_ids()`、`get_selected_id()`、`get_selected_node()`、`set_data()`、`get_data()`、`get_expand_anim()`、`on_change()`、`on_activate()`、`on_toggle()`、`on_check()`、`on_context()`。占位符行为见 `自测/test_treeview_placeholder.leno`。

**展开动画（2026-11-27）**：展开节点时新出现的**直接子行**从上方 12px 滑到位、文字同时淡入（约 150ms）。
只动绘制不动布局（滚动上限、命中、虚拟化仍按行数算），收起不做动画（行已从拍平表移除）。

### 6.5 VirtualGrid —— 虚拟网格

只构建可见项，成千上万条也不卡（长列表/卡片墙用）。

**参数**：`count`、`item_w`/`item_h`、`cols`、`gap_x`/`gap_y`、`pad_x`/`pad_y`、`scroll_color`、`bar_w`、`bar_auto_hide`、`w`/`h`。
**方法**：`set_count()`、`get_count()`、`set_builder(func(int idx): Widget {...})`、`set_scroll_y()`、`get_scroll_y()`、`get_scroll_velocity()`、`get_overscroll_y()`、`is_scrolling()`。

⚠ 构建器走 **`set_builder()`**，不是 opts 里的 `build:` 键（那个键控件不读，传了只会得到一行"不认识键"的警告）。
滚动同样是物理的（一格 ≈1.4 项、撞到底回弹、手指可拖动 + 甩动惯性）；`set_scroll_y()` 仍立即到位并掐掉惯性。

---

## 七、图片与图形进度

### 7.1 ImageView —— 图片展示

```text
ImageView iv = SDL3.createImageView({image_path: path, image_mode: 0,
                                     border: true, radius: 8,
                                     cursor: SDL3.SystemCursor.POINTER, tip: "封面"})
iv.set_image(newPath)
iv.on_click(func() { ... })
```

`image_mode`：`0`=aspectFit 完整显示，`1`=stretch 拉伸，`2`=aspectFill 覆盖裁剪。
**其他参数**：`overlay_path`、`overlay_hover_only`、`overlay_size`、`overlay_scale`、`alpha`、`image_tint`、`rotation`、`spin`、`radius`、`border`、`border_color`、`w`/`h`。
**方法**：`set_image()`、`set_overlay()`、`set_mode()`、`set_rotation()`、`set_spin()`、`set_alpha()`、`set_tint()`、`set_border()`、`set_radius()`、`on_click()`、`get_image_path()`。

⚠ 同路径图片走共享纹理缓存（`imageCacheCount()` / `setImageCacheMax(n)`）；旋转实测见 `自测/test_imageview_spin.leno`。

### 7.2 Canvas —— 自绘画布

`test_canvas_tab.leno` 把 Canvas 的坐标、裁剪、持久像素层讲得很清楚。

```text
Canvas cv = SDL3.createCanvas({w: 26, h: 26, pad: 0, bg_color: #00000000, border: false})
cv.on_draw(func(Renderer r, float ox, float oy, float cw, float ch) {
    // 局部坐标：(0,0)=左上角，(cw,ch)=右下角；越界图元会被裁剪到画布内
    r.setColor(#58A0FFFF)
    r.fillCircle(cw * 0.3, ch * 0.42, 60.0)
    r.drawText(font, "Canvas 局部坐标", 12.0, ch - 26.0, #FFFFFFE6)
})
cv.on_click(func(float lx, float ly) { ... })   // ⚠ 收局部坐标，不是无参
```

**持久画布**：Canvas 自身**没有**像素级方法（旧的 `persist`/`set_pixel` 那套已不存在）。持久层用 `PixelBuffer` + `Renderer.blitBuffer`：

```text
PixelBuffer buf = new PixelBuffer()
buf.init(260, 190)
cv.on_click(func(float lx, float ly) {
    buf.fillRect(_int(lx*0.5) - 2, _int(ly*0.5) - 2, 5, 5, 255, 170, 80, 255)
    SDL3.markFrameRedraw()               // 改了像素层要主动请求重绘
})
cv.on_draw(func(Renderer r, float ox, float oy, float cw, float ch) {
    r.blitBuffer(buf, ox, oy, cw, ch)     // 先上传持久层
    // 再画每帧声明式内容（不写进持久层）
})
```

**参数**：`bg_color`、`border`、`border_color`、`border_w`、`pad`、`clip`、`focusable`、`focus_border`、`cursor`、`w`/`h`。
**回调**：`on_draw(Renderer, ox, oy, cw, ch)`、`on_click(float lx, float ly)`、`on_mouse_down()`、`on_mouse_up()`、`on_mouse_move()`、`on_drag()`、`on_wheel()`、`on_mouse_enter()`、`on_mouse_leave()`、`on_key()`、`on_dispose()`。

⚠ Canvas 默认有**不透明底**，想透明必须 `bg_color: #00000000` + `border: false`。

### 7.3 Separator —— 分隔线

**参数**：`dir`（`0` 水平 / `1` 垂直）、`thickness`、`margin`、`color`、`alpha`、`w`/`h`。
**方法**：`set_horizontal()`、`set_vertical()`、`set_thickness()`、`set_color()`、`set_alpha()`、`set_margin()`。

### 7.4 Badge / Steps / Alert

- **Badge**（胶囊徽标，不可点）：`text`、`bg_color`、`border_color`、`text_color`、`font_size`、`align`、`pad_x`/`pad_y`、`radius`、`w`/`h`；方法 `set_text()`、`set_bg_color()`、`set_text_color()`。
- **Steps**（步骤条）：`SDL3.createSteps({steps, active, dir, title_side, ...})`，方法 `add_step()`、`set_active()`、`set_state()`、`count()`。
- **Alert**（提示条）：`SDL3.createAlert({kind, text, ...})`，`kind` 取 info/warn/danger/success；方法 `set_kind()`、`set_text()`。要"停留到用户处理"用 Alert，不要用 Toast。

### 7.5 RingProgress / Spinner / 图表

- **RingProgress**（圆环进度，donut 图）：参数 `value`、`mode`（idle/sweep/value）、`size`、`thickness`、`track_color`、`fill_color`、`segments`、`show_text`、`text_fn`、`sub_text_fn`、`font_size`、`sweep_speed`、`tip`；方法 `set_value()`、`set_mode()`、`set_segments()`、`on_click()`。
- **Spinner**（加载动画）：参数 `size`、`thickness`、`speed`、`color`、`track_color`、`track_alpha`、`full_track`、`running`、`tip`；方法 `start()`、`stop()`、`is_running()`、`set_color()`、`set_speed()`。
- **图表**：`createBarChart` / `createLineChart` / `createPieChart`，共用 `data`（`set_data()`）、`title`、`show_grid`、`show_points`、`show_values`、`font_size`、`w`/`h`。独立测试见 `控件/图表/test_charts.leno`。

---

## 八、反馈与浮层

### 8.1 Toast —— 轻提示

一次操作的"回声"，不占布局、不吃事件、自动淡出。

```text
SDL3.toast("已复制")
SDL3.toastKind("保存失败", SDL3.TOAST_ERROR)
SDL3.toastFull("正在解析…", SDL3.TOAST_INFO, 1200, SDL3.TOAST_TOP)
```

常量：`TOAST_INFO/SUCCESS/WARN/ERROR`、`TOAST_BOTTOM/TOP/BOTTOM_RIGHT`。
设置：`setToastDuration(ms)`、`setToastPosition()`、`setToastMaxWidth()`、`setToastFontSize()`。

### 8.2 Tooltip —— 悬停提示

控件通用的 `tip` 参数就够用；`SDL3.setTipDelay(400)` 设全局延迟。内容随光标变化时用 `tipReportEx("owner", text, ax, ay)` + `tipClearEx("owner")`。

⚠ 手动弹气泡必须用带 owner 的版本；用无条件 `tipClear` 会把别人的提示一起清掉。

**淡入（2026-11-27）**：延迟到点后气泡约 120ms 淡入（背景/边框/文字一起渐显），移开立刻消失。
只读：`SDL3.tipVisible()`、`SDL3.tipText()`、`SDL3.tipFade()`（0~1 进度）。

### 8.3 MenuBar / 右击菜单

**淡入（2026-11-27）**：下拉菜单与右键菜单弹出时约 100ms 淡入（底色/分隔线/悬停底/文字/图标/边框一起）。
只做淡入不做高度展开——菜单是高频短促交互，鼠标弹出瞬间已在目标项上，高度动画会让项在移动中撞光标。
只读进度：`SDL3.menuFade()`。子菜单弹出不重播（主面板已经是 1）。

**MenuBar 是构建器写法**，先 `addMenu` 拿 int id，再往 id 里加项（`showcase.leno` / `settings.leno` 一致）：

```text
var bar = win.addMenuBar({x: 0, y: 0, w: 920, h: 30, font_size: 14})

int mFile = bar.addMenu("文件")
bar.addItem(mFile, {label: "新建", id: "new", shortcut: "Ctrl+N", image: imgPath("new.png")})
bar.addItem(mFile, {label: "打开", id: "open"})
bar.addSeparator(mFile)
int mEdit = bar.addMenu("编辑")
int mMore = bar.addItem(mEdit, {label: "更多"})              // 返回子菜单 id
bar.addSubmenuItem(mEdit, mMore, {label: "设置 A", id: "setA"})

bar.on_select(func(string menu, string id) {                // 两个 string 参数
    print("菜单选择: " + menu + " -> " + id)
})

// 窗口级右击菜单：底层 run 统一接管弹出，无需在 onEvent 里处理右键
int ctx = bar.addContextMenu("ctx")
bar.addContextItem(ctx, {label: "复制", id: "copy"})
bar.addContextSeparator(ctx)
bar.addContextItem(ctx, {label: "属性", id: "prop"})
win.setContextMenu(bar, ctx)
```

⚠ MenuBar **必须 `win.addMenuBar()`**；用 `createMenuBar` + `win.add` 时标题会显示、点击有反应，但下拉菜单永远不弹。

### 8.4 PopMenu —— 自绘弹出菜单

无边框、置顶、非模态；图标传图片路径。

```text
PopMenu pm = SDL3.createPopMenu({})
pm.addItem("隐藏窗口", imgPath, func() { ... })
pm.addCheck("窗口置顶", imgPath, false, func() { ... })
pm.addSeparator()
pm.beginSubmenu("显示设置")                 // 下一级，可嵌套
pm.addCheck("12 小时制", imgPath, false, func() { ... })
pm.endSubmenu()
pm.showAt(x, y)
pm.poll()                                   // 主循环里调：点菜单外自动收起
```

**方法**：`addItem()`、`addCheck()`、`addSeparator()`、`beginSubmenu()`、`endSubmenu()`、`setChecked()`、`setText()`、`setIcon()`、`showAt()`、`hide()`、`poll()`、`clickItem(idx)`（无头自测）。

⚠ 子菜单是另一块独立面板，各面板必须紧贴（窗口透明，留缝会透出桌面）。Windows 上原生托盘菜单会冻结画面，所以托盘用这套自绘方案（见速查第六节）。

### 8.5 Scrim —— 遮罩层

半透明遮罩，常用于模态浮层后面。**参数**：`color`、`alpha`、`w`/`h`；**方法**：`show()`、`hide()`、`set_alpha()`、`get_fade()`、`on_window_resize()`。窗口缩放时必须跟着铺满，否则右下露一条"没遮住且点得动"，见 `自测/test_scrim_resize.leno`。

**渐显（2026-11-27）**：`show()` 之后约 150ms 内从透明淡到 `alpha`（背景不会"啪"地变暗）；`hide()` 瞬时消失，`get_fade()` 可读进度。

---

## 九、窗口增强

### 9.1 TitleBar —— 自绘标题栏

无边框窗口自己画标题栏，支持最小化/最大化/关闭、自绘图标、动作按钮、居中控件。

**参数**：`title`、`h`、`bg_color`、`text_color`、`hover_color`、`close_hover_color`、`icon_color`、`sep_color`、`show_minimize`/`show_maximize`/`show_close`、`title_align`、`btn_align`、`actions`、`title_icon`、`icon_minimize`/`icon_maximize`/`icon_restore`/`icon_close`。
**方法**：`set_title()`、`on_close()`、`on_minimize()`、`on_maximize()`、`on_action()`、`add_action()`、`set_maximized()`、`set_center_widget()`、`bind_window()`、`set_bg_color()`、`set_text_color()`、`set_separator_color()`、`set_icon_color()`、`set_close_hover_color()`。

自定义对话框可用 `SDL3.dialogTitleBarEx(dlg, "标题", style)` 覆盖标题栏配色（2026-11-27 门面补导出；`style` 为 `Dict[string, any]`）。注意：主题切换会在建窗后再刷一次颜色，必要时建完再调一遍 `tb.set_bg_color(...)`。

### 9.2 Dialog —— 对话框

```text
// 模态确认：结果走回调，不要读返回值
SDL3.msgBox("确认", ["删除后无法恢复"], "删除", "取消", true, func() { do_delete() })

// 自定义模态窗
var dlg = SDL3.createDialogWindow({title: "设置", w: 480, h: 320})
var done = false
dlg.addLabel({x: 30, y: 36, text: "这是一个模态对话框", font_size: 16})
dlg.addButton({x: 60, y: 120, w: 100, h: 36, text: "确定", type: "primary"})
    .on_click(func():void { done = true })
SDL3.runModal(dlg,
    func(Event ev): bool { if ev.isQuit() or done { return false } return true },
    func(Renderer r) { r.clearColor(#282A32FF) })
```

⚠ **`runModal` 不保证阻塞到窗口关闭**：主循环已在跑时它只注册窗口就返回 ⇒ 结果必须由按钮/关闭回调交出，不要写 `if runModal(...) {}`（恒判 false）。`SDL3.quit()` 也不是退出程序（见 1.5）。

### 9.3 其它

- **系统托盘**：`SDL3.createTray({icon, tooltip})` → `getMenu()` → `addButton()` / `addCheckbox()` / `addSeparator()`，必须靠 `win.run()` 驱动；Windows 上改用 `interceptTrayClick()` + `createPopMenu` 自绘（详见速查第六节）。
- **文件对话框**：`showOpenFileDialog()`、`showSaveFileDialog()`、`showOpenFolderDialog()`。
- **拖拽提示**：`SDL3.createDragHint({...})` + `show()` / `updatePos()` / `hide()`。
- **窗口穿透**：`win.setClickThrough(bool)` / `isClickThrough()`。
- **屏幕可用区**：`SDL3.getDisplayUsableAt(x, y)` 返回 `[x, y, w, h]`（扣掉任务栏，多屏可用），取不到时 w/h 为 0，调用方自己兜底。

---

## 十、官方活文档导览（leno_gui）

`Leno/leno_gui/` 是控件库的"活文档"——每个 `test_*.leno` 都能直接 `leno 文件名` 跑起来。按你要找的东西直接翻对应目录：

| 想找什么 | 去哪个文件 |
|---|---|
| **一个窗口看全部控件 + 三种布局 + 菜单/右击/模态/滚动/Tab** | `控件/总览/showcase.leno` ⭐ 先看这个 |
| 主题（深色/浅色）切换 | `控件/总览/test_theme.leno` |
| 按钮全部属性与动态方法 | `控件/按钮/test_button_v3.leno`（类型/颜色/光标/字体/动态）、`test_button_new.leno`、`test_button_image.leno` |
| Label / Edit / Canvas | `控件/标签/test_label.leno`、`控件/编辑框/test_edit*.leno`、`控件/画布/test_canvas_tab.leno` |
| 弹性布局 grow/shrink/basis/justify/align/锚点 | `控件/布局/test_layout.leno` ⭐ |
| 复选/单选/开关 | `控件/选择控件/test_check_radio_toggle.leno`、`test_toggle_anim.leno` |
| 滑块 / 进度条 / SpinBox | `控件/数值控件/test_slider_progress.leno`、`test_progress_anim.leno`、`test_spinbox.leno` |
| ListBox / ComboBox / TreeView / Panel / ScrollView | `控件/复合控件/选择类/`、`控件/复合控件/容器类/` |
| Tab × Canvas / Table / 重置 | `控件/复合控件/布局类/test_tab_*.leno` |
| Table 全部能力 | `控件/表格/test_table*.leno`（features / advanced / cells / image / keyboard_tooltip） |
| 菜单 / 右击菜单 / 提示 | `控件/复合控件/菜单/`、`控件/复合控件/提示类/test_tooltip.leno` |
| 一整个设置面板怎么拼 | `控件/设置面板/settings.leno` ⭐ |
| 边界与回归（焦点链/裁剪/缓存/缩放） | `自测/` 下 30+ 个 `test_*.leno` |
| **完整真实应用** | `应用/数据看板/dashboard.leno`、`应用/影视海报墙/movie_wall.leno`、`应用/文件管理器/file_manager.leno`、`应用/模拟时钟/clock.leno`、`应用/IDE布局/ide_layout.leno` |

> 这些文件和 `Leno/build/leno_module/LenoSDL3/examples/` 的 40+ 用例合起来，覆盖了每个控件的全部属性。查某个具体参数时，搜文件名比猜 API 快。

---

## 附：控件 → 创建函数速查

| 控件 | 创建函数 | 分类 |
|---|---|---|
| `Label` / `Button` / `LinkButton` | `createLabel` / `createButton` / `createLinkButton` | 文字按钮 |
| `CheckBox` / `RadioButton` / `Toggle` | 同名 `createXxx` | 选择 |
| `Edit` / `SpinBox` / `Slider` / `ProgressBar` | 同名 `createXxx` | 输入数值 |
| `Calendar` / `pickColor` | `createCalendar` / `pickColor` | 选择 |
| `HBox` / `VBox` / `AnchorBox` / `GridLayout` | 同名 `createXxx` | 布局 |
| `Panel` / `GroupBox` / `ScrollView` / `TabControl` / `Splitter` / `Card` | 同名 `createXxx` | 容器 |
| `ListBox` / `ComboBox` / `Table` / `TreeView` / `VirtualGrid` | 同名 `createXxx`（ComboBox 顶层用 `win.addComboBox`） | 列表 |
| `ImageView` / `Canvas` / `Separator` / `Badge` / `RingProgress` / `Spinner` | 同名 `createXxx` | 图形进度 |
| `BarChart` / `LineChart` / `PieChart` | 同名 `createXxx` | 图表 |
| `Toast` / `Tooltip` / `MenuBar` / `PopMenu` / `Scrim` / `Tray` | `toast()` / `tipReport()` / `win.addMenuBar` / `createPopMenu` / `createScrim` / `createTray` | 反馈浮层 |
| `TitleBar` / Dialog | `createTitleBar` / `createDialogWindow` + `runModal` | 窗口增强 |
