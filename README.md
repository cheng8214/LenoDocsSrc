# LenoDocsSrc —— Leno 文档的**唯一所在**

> md 源 + 生成好的 HTML 站点都放这里；代码仓库 `D:\CLeno\Leno` **不再带文档**。

## 目录

```
LenoDocsSrc/
├── *.md                ← 95 篇文档源（**只改这里**）
├── INDEX.md            ← 门户分类/状态表（生成器读它排版首页）
├── archive/            ← 已归档的源（JIT 等，5 篇）
├── images/             ← 文档图片源（生成时拷进 site/images/）
├── build_html.py       ← 生成器（页面模板 / CSS / JS / 搜索索引全在里面）
├── site/               ← ★ 生成好的 HTML 站点（入口 site/index.html）
│   ├── index.html          ← 门户：按分类翻 + 全文搜索（按 / 聚焦）
│   ├── INDEX_raw.html      ← INDEX.md 的原文页
│   ├── <每篇 md 一个>.html
│   ├── archive/            ← 归档页
│   ├── assets/             ← style.css / app.js / search-index.js(≈3 MB)
│   └── images/
├── _build_vendor/      ← markdown 依赖的隔离安装目录（**不入库**）
└── README.md           ← 本文件（生成器会跳过它）
```

## 怎么生成

```bat
cd /d D:\CLeno\LenoDocsSrc
python build_html.py                     :: 默认输出 ./site（整目录重建：先删后建）
python build_html.py D:\some\where       :: 或指到别处先检查
```

依赖 `markdown`（隔离安装，不污染全局 Python）：

```bat
python -m pip install --target _build_vendor markdown
```

> ⚠ `site/` 是**产物**：整目录会被删除重建。要改内容请改 md，别手改 html
> （手改的内容下次生成就没了，且搜索索引与正文会不一致）。

## 加 / 改一篇文档

1. **改**：直接改 `*.md`，跑一次生成即可。
2. **加**：在根目录（或 `archive/`）放 `.md`，再到 `INDEX.md` 的分类表里登记一行。
   不登记也会被生成出来，但会落到「九、索引未收录」那一节。

生成完如果要让代码仓库那边有更新，只需 `cd D:\CLeno\Leno && git status` 看有没有
需要跟着改的（正常情况下**没有**——文档不在代码仓库里）。

## 约定（都是踩过的坑）

- **页面文件名 = md 名**（`module_regexs.md` → `site/module_regexs.html`）。
  别改名，代码注释里有几百处 `LenoDocsSrc/site/xxx.html` 引用。
- 门户是 `index.html`、原始索引页是 `INDEX_raw.html`。
  **别把后者叫 `INDEX.html`**：Windows 文件名不区分大小写，两者会互相覆盖
  （实测只剩一个，而且"查看原始索引全文"链接指回自己）。
- 分类标题里**不要再手写「（N 篇）」**：真实条数由生成器按 `INDEX.md` 的登记项算，
  写死的数字必然漂（实测 18 vs 19）；生成器已自动剥掉这个括号。
- 文档里引用**模块自带**的文档（`build/leno_module/*/docs/*.md`）要写 `.md`，
  它们没有被转到站点里。
- 引用别的文档写 `LenoDocsSrc/site/<名字>.html`（这是代码仓库里统一的写法）。
- **搜索索引 ≈3 MB**：每次生成都会整份变，所以它是一个"大文件"。如果要托管到静态站点，
  建议后续改成按需加载（现在为了 `file://` 直接双击可用，才用 `script src` 内联全量）。

## 版本控制建议

```bat
git init
echo _build_vendor/ > .gitignore
git add -A && git commit -m "docs: 从 Leno 仓库拆出（md 源 + site 成品）"
```

`site/` 建议一起提交：这样只 clone 这个仓库就能直接双击 `site/index.html` 阅读，
不需要装 Python 与 markdown。
