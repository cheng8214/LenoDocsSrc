# LenoSDL3 控件实战教程

> 这份教程不罗列 API 签名，而是按**真实项目的搭建顺序**讲：怎么开窗、怎么摆控件、怎么让它们响应、怎么避开已经踩过的坑。
> 代码全部取自 Aria（音乐播放器）和 `LenoSDL3/examples/` 的实测用例——都是跑得起来的写法。
> API 速查与附录里的几十条实测坑点见 [SDL3 常用 API 与易踩坑速查](扩展模块/LenoSDL3_常用API与易踩坑速查.html)；单个控件的设计细节见 [Card 卡片控件设计文档](LenoSDL3_Card卡片控件设计文档.html)。

## 一、最小可运行：一个窗口 + 一个按钮

```leno
import "SDL3" as SDL3

main() {
    var win = SDL3.createWindow({title: "我的第一个窗口", w: 600, h: 400, flags: 0x20})
    if not win.ok { return }          // ⚠ 必须判 ok：建窗失败时用 win 会崩

    Button btn = win.addButton({text: "点我", x: 20, y: 20, w: 100, h: 36})
    btn.on_click(func() { print("被点了") })

    win.run(func() {}, func(Event ev) {})   // 两个回调：绘制 / 事件，都不能少
}
```

三个要点：

- `flags: 0x20` 是 SDL3 的 `SDL_WINDOW_RESIZABLE`，Aria 的所有窗口都用这个值。
- `win.ok` 一定要判。建窗失败（无显示环境、DLL 缺失）时后面的操作全无效。
- `run()` 需要**两个**回调，哪怕是空的。详见速查第一节。

## 二、两种创建路径，别混用

这是新手最常踩的坑，也是 Aria 代码里最一致的约定：

| 写法 | 注册进窗口 | 谁绘制 | 用在哪 |
|---|---|---|---|
| `SDL3.createXxx({...})` | ✗ | 交给容器（`add` 到布局/Panel/Tab 页） | **放进布局的控件** |
| `win.addXxx({...})` | ✓ | 窗口自动绘制 | 用绝对坐标直接摆的控件 |

⚠ 混用会让同一控件被窗口画一次、又被布局摆一次——重复绘制、位置打架。

**Aria 的实际分工**：根容器 `win.add(qRoot)` 走 `win.addXxx`，里面所有子控件都走 `createXxx` 再 `root.add(...)`。测试文件 `test_new_widgets.leno` 则用 `win.addGroupBox` 做容器，再用 `gb1.add(iv1)` 装子控件——同一个原则：**顶层绝对定位用 `win.addXxx`，容器内用 `createXxx` + `add`**。

## 三、布局：HBox / VBox / AnchorBox

Aria 的界面几乎全靠 `HBox`（横排）和 `VBox`（竖排）嵌套拼出来，少量需要精确落点的用 `AnchorBox`。

```leno
// 取自 Aria/lib/page_widgets.leno ——「正在加载…」行：Spinner + 文案
HBox row = SDL3.createHBox({x: 0, y: 0, w: w, h: 40,
                            pad_x: 0, pad_y: 0, spacing: 12, justify: 1})
row.add(SDL3.createSpinner({size: 22, thickness: 2.5, color: ACCENT,
                            track_color: #F6DCE5FF, running: true}),
        {grow: 0, shrink: 0, basis: 22, align: 1})
row.add(SDL3.createLabel({text: text, font_size: 12.5, text_color: TXT_MID}),
        {grow: 0, shrink: 0, align: 1})
```

`add(widget, opts)` 的四个参数是核心：

- **`grow` 是权重，不是像素**。想让控件按比例铺开，写 `{basis: w, grow: w}` 这种成对比值。
- **`basis` 是分配基数，不是固定宽度**。真要钉死写 `{basis: w, grow: 0, shrink: 0}`；注意 `shrink` 默认是 1。
- **`align`**：交叉轴 `0=start / 1=center / 2=end / 3=stretch`。
- 不写 `basis` 时用控件**加入那一刻的自然尺寸**，后来 `set_size` 改了也不影响。

Aria 的嵌套层次（取自 `player_core.leno`）：`root`(VBox) → `body`(HBox) → `side`(VBox) → `sideNav`(VBox) → 一堆 Button，每层都显式写 `grow/shrink/basis/align`。这种写法看起来啰嗦，但窗口缩放时不会错位。

排障时用 `dumpLayout`，别靠截图扫像素——速查第三节有具体做法。

## 四、事件：按钮、输入、自绘

### 4.1 点击回调

```leno
// 取自 Aria/lib/player_core.leno
Button qClear = SDL3.createButton({image_path: ui.ico("menu_delete_all.png"),
                                   image_size: 16, w: 26, h: 26, radius: 6})
qClear.on_click(func() { confirm_clear_queue() })
qh.add(qClear, {grow: 0, shrink: 0, basis: 26, align: 1})
```

⚠ 两个真实踩过的坑：

- `LinkButton` 的 `url` 字段**只用于显示**，控件内部只回调 `onClick`——不绑回调点了没反应。Aria 统一封装成 `ui.link()`。
- 图标按钮如果有 `background: false`，会连 hover 效果一起跳过。

### 4.2 自绘控件 Canvas

Aria 里大量小图形（圆形播放钮、角标、进度环）都用 `Canvas.on_draw` 画，而不是塞图片：

```leno
// 取自 Aria/lib/page_widgets.leno 的 play_dot()
Canvas cv = SDL3.createCanvas({x: 0, y: 0, w: 26, h: 26, pad: 0,
                               bg_color: TRANS, border: false})
cv.on_draw(func(Renderer rr, float ox, float oy, float cw2, float ch2) {
    float d = 26.0
    if d > cw2 { d = cw2 }          // ⚠ 必须夹到容器给的尺寸内
    if d > ch2 { d = ch2 }
    rr.setColor(#DCCBF2FF)
    rr.fillRoundedRect(ox, oy, d, d, d / 2.0)
    // ...
})
```

⚠ `Canvas` 默认有**不透明底**，想透明必须 `bg_color: #00000000` + `border: false`。

### 4.3 常见控件的特殊语义

这些是实测结论，不看源码根本猜不到：

- `ListBox` 单选时**点已选中的那一行不回调**（要处理就得自己绕）。
- `ScrollView` 里子孙跟不跟着滚，取决于内容根是哪种控件，有三种情况。
- `Table` 支持进度条列（`cell_types`）和自绘回调（`on_cell_draw`）。
- `TabControl` 同页混用两种定位方式会提示一次——是警告，不是错误。
- 滚轮 `wheelY()` 正值 = 远离用户（往上滚），框架语义是"往上滚看更早内容"。

## 五、控件速查（按用途）

`LenoSDL3/examples/` 里有 40+ 个可运行用例，覆盖每个控件的全部属性。按用途索引：

| 用途 | 控件 | 参考用例 |
|---|---|---|
| 文字 / 按钮 | `Label` `Button` `LinkButton` `CheckBox` `RadioButton` `Toggle` | `examples/基础示例/test_new_api.leno` |
| 容器 / 布局 | `HBox` `VBox` `GridLayout` `AnchorBox` `Panel` `GroupBox` `Splitter` | `test_layout*.leno` `test_new_widgets.leno` |
| 列表 / 表格 | `ListBox` `ComboBox` `Table` `VirtualGrid` `TreeView` | `test_table*.leno` `examples/UI组件/…` |
| 图片 / 图形 | `ImageView` `Canvas` `RingProgress` `Chart` | `examples/图像处理/*.leno` `test_draw.leno` |
| 输入 | `Edit` `SpinBox` `Slider` `ColorPicker` `Calendar` | `test_edit*.leno` |
| 反馈 / 浮层 | `Toast` `Tooltip` `Dialog` `PopMenu` `Scrim` `AnchorBox` | `test_dialog_api.leno` |
| 窗口增强 | `TitleBar` `Tray` `Menu` `FileDialog` `Alert` | `examples/基础示例/窗口管理/*.leno` |

创建方式一律遵循第二节的规则：容器内 `createXxx` + `add`，顶层 `win.addXxx`。

## 六、生命周期与资源

- **ImageView 的纹理**：`set_texture(tex, own)` 的 `own:false` 表示借用共享纹理，销毁时不要重复释放。
- **列表频繁刷新**：Aria 的 `build_queue_rows()` 里每次重建行前先 `qList.dispose()` 再 `clear()`——不 dispose 旧行的 ImageView 会占着纹理缓存不释放，导致切歌时内存持续涨。
- **定时器**：不要补跑积压周期，电脑睡眠唤醒后会"假死"（速查附录 C 有实测）。
- **退出**：`win.cancelClose()` 用于"关闭到托盘"，不要用 `_exit(0)` 强杀——那样测不出"退出卡住"的缺陷。

## 七、跟着真实项目学

教程讲不完所有细节，最快的办法是读真实代码：

| 项目 | 看什么 |
|---|---|
| Aria `lib/player_core.leno` | 完整主窗口：Toolbar → VBox/HBox 多层嵌套 → 侧边栏 → 列表 → 事件绑定 |
| Aria `lib/ui_kit.leno` | 复用控件的封装：`lbl()` / `link()` / `lblFit()`，以及每个函数上的踩坑注释 |
| Aria `lib/page_widgets.leno` | Canvas 自绘、Spinner+Label 组合、图标按钮 |
| `examples/基础示例/test_new_widgets.leno` | 一组控件的全部属性逐一实测 |
| `examples/基础示例/窗口管理/` | 对话框、托盘、多窗口、模态死锁等边界场景 |

这些代码文件都在 `Leno/build/leno_module/LenoSDL3/` 与 Aria 仓库中。
