# 关于本站 · Genisys API 文档查询站

> 本页是这站的「关于」说明。站点由 `site/server.py`（Python 标准库 + markdown）动态提供，所有文档实时从 `docs/` 目录读取渲染，改完刷新浏览器即生效。

---

## 1. 这是什么

一个**本地优先**的 API 文档查询站，专门收录 **Genisys（PocketMine-MP 分支）** 6 个历史版本的源码级 API 文档：

- **插件用 API 文档**（`docs/<版本>/plugin-api.md`）：教你怎么写插件
- **改核心用 API 文档**（`docs/<版本>/core-api.md`）：教你怎么改/扩展核心

配套还收录了一份 **Genisys 与现代 PMMP 的代差对照**（见第 5 节），避免你直接套用现代 PocketMine 的 API 踩坑。

---

## 2. 收录的版本

| 版本 | 协议号 | API 版本 | Genisys 扩展 API | MCPE 版本 |
|------|--------|----------|------------------|-----------|
| `0.13` | 38 | 2.0.0 | `iTX_API_VERSION` 1.5.8（旧命名，无 `geniapi` 字段） | v0.13.x |
| `0.14.0` | 45 | 2.0.0 | `geniapi` 1.7.2 | v0.14.x |
| `0.14.3` | 70 | 2.0.0 | `geniapi` 1.7.3 | v0.14.3 |
| `0.15.0` | 81 | 2.0.0 | `geniapi` 1.8.0 | v0.15.x |
| `0.16.0` | 91 | 2.1.0 | `geniapi` 1.9.3 | v0.16.x |
| `1.0.0` | 100 | 3.0.0-ALPHA3 | `geniapi` 2.0.0 | v1.0.0 |

> 每个版本的常量/协议号均从对应 `pocketmine/PocketMine.php` 源码实测提取，不是凭记忆填写。

---

## 3. 文档是怎么来的

- 全部文档基于**本仓库源码实测**：用脚本扫描 6 个版本的 `Genisys` ，抽取类声明、方法签名、事件清单、协议包、命令、注册锚点（含真实行号）。
- `core-api.md` 的注册锚点行号、启动链路步骤、`callEvent` 派发热点，均来自源码扫描结果，**可直接点进源码核对**。

---

## 4. 怎么用这个站

### 浏览
- 顶部**版本筛选**：`全部 / 0.13 / 0.14.0 / 0.14.3 / 0.15.0 / 0.16.0 / 1.0.0 / 关于`
- **类型筛选**：`全部 / 插件 API / 核心 API / 关于`
- **全文搜索框**：类名、方法名、事件名、协议包、版本差异都能搜，**中文也可搜**（例如搜「协议」「方块」「事件」）
- 点列表项进入阅读页，右侧有**本页目录**，滚动时自动高亮当前章节；顶部可一键切回列表或切「关于」页

### 阅读页结构
**插件 API 文档**通常包含：
架构与启动流程 · 插件开发（生命周期/加载器）· `Server` / `Player` / `Inventory` / `Level` / `Entity` / `Item` / `Block` 逐方法「用处」表 · 事件系统（含可取消标记）· 命令 · 调度器（含 AsyncTask 线程安全铁律）· 权限 · 元数据 · 工具类 · 网络 · 完整示例 · 全局常量附录。

**改核心 API 文档**通常包含：
目录结构与 `Server::__construct` 启动链路 · **注册锚点真实行号**（方块/物品/`LevelProvider`/生成器/实体/Tile）· 如何新增方块/实体/Tile/生成器/存档格式/协议包 · 事件派发热点 · 网络层（raklib/协议）· 各版本破坏性变更速记。

### 本地起服务
```
cd C:\Users\31877\Desktop\Genisys源码合集\site
py server.py            # 默认 http://127.0.0.1:8765/
set PORT=9000 && py server.py   # 换端口
```
- 服务端**零外部依赖**：优先用 `markdown` 库，没装就自动走内置纯 Python 渲染器（表格 / 标题锚点 / 代码块均正常）。
- 站点靠 `http://127.0.0.1:8765/` 这个由 `server.py` 提供的地址访问；不要把 `shell.html` 当静态文件直接双击打开（那样没有后端 API，`/api/list` 会失败）。

---

## 5. 重要提醒：别直接套现代 PocketMine 的 API

本站文档对应的是 **PE 0.13–1.0.0 / 协议 38–100** 的老分支。而现代 PocketMine-MP（`apidoc.pmmp.io`，约 MCPE 1.21+ / 协议 700+）是**另一代**，方法签名、命名空间、注册方式都变了，**不能直接照搬**。常见代差：

| 维度 | 现代 PMMP（apidoc） | Genisys | 正确做法 |
|------|--------------------|--------------|----------|
| 方块注册 | `BlockTypeInfo`/`RuntimeBlockStateRegistry` | `Block::init()` + 数字 ID `$list` | 改方块看 `docs/*/core-api.md` 的注册锚点 |
| 世界 | `pocketmine\world\World` | `Level` + `LevelProviderManager::addProvider` | 概念一致，类名不同 |
| 实体注册 | `EntityFactory` | 0.13–0.16 `Entity::registerEntities()`；**1.0.0 改 `Entity::init()`** | 见 `docs/1.0.0/core-api.md` |
| Chunk | `Chunk` + `SubChunk` | 0.13–0.16 `FullChunk`；**1.0.0 改 `Chunk`** | 见 `docs/1.0.0` 破坏性变更 |
| 网络协议包 | `network\mcpe\protocol\Packet` | `protocol\*` 的 `DataPacket` | 协议号天差地别（70 vs 700+），不可复用 |

**结论**：写 Genisys 代码/插件时，以本站对应版本文档 + 你本地源码为准；现代 PMMP API 只适合理解架构演进方向。

---

## 6. 文件清单

```
/
├─ docs/                         # 文档源（站点实时读取这里）
│  ├─ 0.13/      plugin-api.md  core-api.md
│  ├─ 0.14.0/    plugin-api.md  core-api.md
│  ├─ 0.14.3/    plugin-api.md  core-api.md
│  ├─ 0.15.0/    plugin-api.md  core-api.md
│  ├─ 0.16.0/    plugin-api.md  core-api.md
│  ├─ 1.0.0/     plugin-api.md  core-api.md
│  └─ pmmp-apidoc-study.md      # 本页（关于本站）
└─ site/
   ├─ server.py                  # 动态服务端（stdlib http.server + markdown）
   └─ shell.html                 # 前端 SPA（筛选 + 搜索 + 目录）
```

