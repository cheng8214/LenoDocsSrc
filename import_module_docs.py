#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 Leno 仓 build/leno_module/<模块>/README.md 导入到本仓 扩展模块/*.md，
供 build_html.py 生成 HTML。源 README 保持不动（仍在 Leno 仓），这里是副本。

用法:  python import_module_docs.py
可重复运行：每次覆盖 扩展模块/*.md；总览页 扩展模块/_总览.md 单独维护，不会被覆盖。
"""
from pathlib import Path
import re

SRC = Path(r"D:/CLeno/Leno/build/leno_module")
DST = Path(__file__).resolve().parent / "扩展模块"
SITE_ARCHIVE = Path(__file__).resolve().parent / "site" / "archive"
# 已归档到 archive/ 的文档文件名（用于修正 README 里指向它们的链接）
ARCHIVED = {p.name for p in SITE_ARCHIVE.glob("*.html")} if SITE_ARCHIVE.is_dir() else set()
# 从 site/扩展模块/xxx.html 出发到 Leno 仓的相对路径（site→LenoDocsSrc→CLeno→Leno）
LENOREPO = "../../../Leno/build/leno_module"

# 包名 → 模块目录名 / import 名（与总 README 的「模块一览」一致，防包名≠import名的坑）
MODULES = [
    ("CLI", "LenoCLI"), ("Compress", "LenoCompress"), ("Crypto", "LenoCrypto"),
    ("CSV", "LenoCSV"), ("FS", "LenoFS"), ("Glob", "LenoGlob"),
    ("GameHelper", "LenoHack"), ("HTTP", "LenoHTTP"), ("Log", "LenoLog"),
    ("Music", "LenoMusic"), ("QR", "LenoQR"), ("Result", "LenoResult"),
    ("SDL3", "LenoSDL3"), ("sqlite3", "LenoSqlite"), ("Stats", "LenoStats"),
    ("Sys", "LenoSys"), ("UUID", "LenoUUID"), ("Win32", "LenoWin32"),
    ("XLSX", "LenoXLSX"), ("Zip", "LenoZip"),
    ("Web", "LenoWeb"),
]
# 多入口模块
MULTI = {"Web": ["WebNet", "WebHtml", "WebCrawl", "Web"]}
# 哪些包在模块目录里有 README（其余从 lib/README.md 找或跳过）
README_PATHS = {
    "Music": "LenoMusic/lib/README.md",
    "SDL3": "LenoSDL3/lib/README.md",
    "sqlite3": "LenoSqlite/lib/README.md",
}


def rewrite(text: str, pkg_dir: str) -> str:
    """把 README 里的相对链接改成站点能用的：文档站链接→站内；源码链接→Leno 仓。"""
    # 1) 指向文档站 HTML 的旧相对链接 → 站内文件名（页面在 site/扩展模块/，需退一层）
    def to_site(m):
        target = m.group(2).split("/")[-1]
        prefix = "archive/" if target in ARCHIVED else ""
        return "[%s](../%s%s)" % (m.group(1), prefix, target)
    text = re.sub(r"\[([^\]]+)\]\((?:\.\./)+docs/([^)]+\.html)\)", to_site, text)

    # 2) 指向本模块内 examples/ tests/ lib/ 的相对目录链接 → Leno 仓路径（HTML 深一级，多退一层）
    def to_src(m):
        label, path = m.group(1), m.group(2)
        if path.startswith(("examples/", "tests/", "test/", "lib/", "docs/")):
            return "[%s](%s/%s/%s)" % (label, LENOREPO, pkg_dir, path)
        return m.group(0)
    text = re.sub(r"\[([^\]]+)\]\((examples/[^)]*|tests?/[^)]*|lib/[^)]*|docs/[^)]*)\)", to_src, text)
    return text


def main():
    DST.mkdir(exist_ok=True)
    done, skipped = [], []
    for import_name, pkg_dir in MODULES:
        rel = README_PATHS.get(import_name, f"{pkg_dir}/README.md")
        src = SRC / rel
        if not src.exists():
            skipped.append(f"{pkg_dir}({rel})")
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        text = rewrite(text, pkg_dir)
        # 顶部加标准头：import 名 + 指向源 README
        multi = MULTI.get(import_name)
        imports = " / ".join(f'"{x}"' for x in multi) if multi else f'"{import_name}"'
        header = (
            "> 📦 **扩展模块**（非语言内置标准库）· 包名 `%s` · import 名 %s\n"
            "> 源 README：`Leno/build/leno_module/%s/README.md`（本页是同步副本，改请改源）\n\n"
        ) % (pkg_dir, imports, pkg_dir)
        (DST / f"{pkg_dir}.md").write_text(header + text, encoding="utf-8", newline="\n")
        done.append(pkg_dir)
    print(f"导入 {len(done)} 篇: {', '.join(done)}")
    if skipped:
        print(f"跳过 {len(skipped)} 篇(无 README): {', '.join(skipped)}")
    sync_sdl3_docs()


# 模块自带的 docs（高价值，站点原来没有）：文件名加 LenoSDL3_ 前缀 → 归到「05 GUI·平台」
SDL3_DOCS = {
    "SDL3常用API与易踩坑速查.md": "LenoSDL3_常用API与易踩坑速查.md",
    "SDL3控件优化清单.md": "LenoSDL3_控件优化清单.md",
}


def sync_sdl3_docs():
    src_dir = SRC / "LenoSDL3" / "docs"
    copied = []
    for src_name, dst_name in SDL3_DOCS.items():
        src = src_dir / src_name
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        header = (
            "> 📦 源文件：`Leno/build/leno_module/LenoSDL3/docs/%s`（本页是同步副本，改请改源）\n\n"
        ) % src_name
        (DST / dst_name).write_text(header + text, encoding="utf-8", newline="\n")
        copied.append(dst_name)
    print(f"同步 SDL3 docs {len(copied)} 篇: {', '.join(copied)}")


if __name__ == "__main__":
    main()
