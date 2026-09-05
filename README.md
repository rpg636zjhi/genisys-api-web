# Genisys API 文档查询站

一个**本地优先**、零外部依赖的 API 文档查询站，专门收录 **Genisys**（PocketMine-MP 分支）6 个历史版本的源码级 API 文档，并提供一个带版本筛选 + 全文搜索的网页界面。

- **插件用 API 文档**（`docs/<版本>/plugin-api.md`）：教你怎么写插件
- **改核心用 API 文档**（`docs/<版本>/core-api.md`）：教你怎么改 / 扩展核心
- **关于本站**（`docs/pmmp-apidoc-study.md`）：本站说明 + Genisys 与现代 PMMP 的代差避坑指南

文档全部基于本仓库源码实测生成（脚本扫描各版本的 `pocketmine/` 目录，抽取方法签名、事件清单、协议包、命令、注册锚点真实行号），不是凭记忆编写。

---

## 收录版本

| 版本 | 协议号 | API 版本 | Genisys 扩展 API（`geniapi`） | MCPE 版本 |
|------|--------|----------|-------------------------------|-----------|
| `0.13` | 38 | 2.0.0 | 旧命名 `iTX_API_VERSION` 1.5.8（无 `geniapi` 字段） | v0.13.x |
| `0.14.0` | 45 | 2.0.0 | `geniapi` 1.7.2 | v0.14.x |
| `0.14.3` | 70 | 2.0.0 | `geniapi` 1.7.3 | v0.14.3 |
| `0.15.0` | 81 | 2.0.0 | `geniapi` 1.8.0 | v0.15.x |
| `0.16.0` | 91 | 2.1.0 | `geniapi` 1.9.3 | v0.16.x |
| `1.0.0` | 100 | 3.0.0-ALPHA3 | `geniapi` 2.0.0 | v1.0.0 |

> 每个版本的常量 / 协议号均从对应 `pocketmine/PocketMine.php` 源码实测提取。

---

## 目录结构

```
genisys-api-web/
├─ README.md                  # 本文件
├─ .gitignore
├─ docs/                      # 文档源（站点运行时实时读取）
│  ├─ 0.13/      plugin-api.md  core-api.md
│  ├─ 0.14.0/    plugin-api.md  core-api.md
│  ├─ 0.14.3/    plugin-api.md  core-api.md
│  ├─ 0.15.0/    plugin-api.md  core-api.md
│  ├─ 0.16.0/    plugin-api.md  core-api.md
│  ├─ 1.0.0/     plugin-api.md  core-api.md
│  └─ pmmp-apidoc-study.md    # 关于本站 + 代差对照
└─ site/
   ├─ server.py               # 动态服务端（Python 标准库 + markdown）
   └─ shell.html              # 前端 SPA（版本/类型筛选 + 全文搜索 + 目录）
```

---

## 本地运行

需要 Python 3（无需安装任何第三方库）：

```bash
cd genisys-api-web/site
python server.py            # 或 py server.py
# 默认 http://127.0.0.1:8765/
```

换端口：

```bash
set PORT=9000 && python server.py     # Windows
PORT=9000 python server.py            # Linux / macOS
```

### 使用说明

- 顶部**版本筛选**：`全部 / 0.13 / 0.14.0 / 0.14.3 / 0.15.0 / 0.16.0 / 1.0.0 / 关于`
- **类型筛选**：`全部 / 插件 API / 核心 API / 关于`
- **全文搜索**：类名、方法名、事件名、协议包、版本差异都能搜，**中文也可搜**（如「协议」「方块」「事件」）
- 阅读页右侧有**本页目录**，滚动时自动高亮当前章节

### 实现要点

- 服务端**零外部依赖**：优先使用 `markdown` 库渲染，未安装时自动回退到内置纯 Python 渲染器（表格 / 标题锚点 / 代码块均正常）。
- 所有文档在请求时**实时**从 `docs/` 读取渲染，修改任意 `.md` 后刷新浏览器即生效，无需重新生成。
- 站点靠 `http://127.0.0.1:8765/` 这个由 `server.py` 提供的地址访问；不要把 `shell.html` 当静态文件直接双击打开（那样没有后端 API，会加载失败）。

---

## ⚠️ 重要提醒：不要直接套用现代 PocketMine 的 API

本站文档对应的是 **PE 0.13–1.0.0 / 协议 38–100** 的老分支。而现代 PocketMine-MP是**另一代**，方法签名、命名空间、注册方式都已改变，**不能直接照搬**

---

## 文档来源

- 文档由脚本扫描 6 个版本的 `Genisys` 源码生成（类声明、方法签名、事件清单、协议包、命令、注册锚点真实行号）。

---

## License

> 本仓库是基于 Genisys 公开源码进行的独立知识整理与接口描述，不包含 Genisys 的核心源代码副本。文档内容的著作权归本仓库作者所有。若文档内容被司法机关认定为 Genisys 的衍生作品，则本仓库自动遵循 GPLv3 许可证；否则，适用本仓库的自定义许可条款。

> 本仓库采用 [CC BY-NC 4.0](LICENSE) 许可证。

> **使用时必须保留原作者署名：rpg636zjhi，且不得用于商业目的。**