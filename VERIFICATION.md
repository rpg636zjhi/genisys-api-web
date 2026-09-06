# Genisys API 文档 · 跨版本源码验证报告

> 生成时间：2026-09-06
> 验证对象：6 个版本（0.13 / 0.14.0 / 0.14.3 / 0.15.0 / 0.16.0 / 1.0.0）共 12 份 API 文档
> 验证方式：对每个版本源码做真实扫描，与文档中「事件清单」「方法表」逐条对账

## 1. 验证方法

- **事件清单**：提取各版本 `pocketmine/event/` 下所有 `*Event.php` 文件名，与文档 §5.6「本版本事件完整清单（源码实测）」逐条比对。
- **方法表**：提取各版本文档表格（`| \`method()\` | ...`）中列出的方法名，先在全树搜 `function <name>(`，再放宽到「方法名在源码任何位置出现」；两者皆无 → 判定为**虚构/不匹配**。
- **版本敏感 API**：对跨版本差异大的方法（registerEntities、getSynapse、getExperience 等）单独做存在性矩阵。

## 2. 事件清单（§5.6）—— ✅ 准确，无需修改

- 6 版本文档 §5.6 文本 MD5 各不相同（非模板套用）。
- 文档列出的事件类名，在对应版本源码中 **100% 存在，0 个虚构**。
- 各版本真实事件数：`0.13=95`、`0.14.0=103`、`0.14.3=107`、`0.15.0=107`、`0.16.0=109`、`1.0.0=111`。

## 3. 方法表 —— ⚠️ 发现虚构/不匹配方法，已逐行加注

gen_v2 生成时**事件清单用了真实扫描数据，但方法表沿用了通用 PocketMine API 参考文档基底**，未逐版核对 Genisys 源码。扫描发现以下「文档方法表列出、但源码连调用都没有」的方法（已在对应表格行末尾加注 `⚠️本版Genisys源码未提供`）：

| 版本 | 虚构方法数 | 方法名 |
|---|---|---|
| 0.13 | 19 | fromInteger, getAttributeMap, getDimension, getEnchantmentLevel, getGeniApiVersion, getLore, getVariant, isArmor, onPlace, readString, readVarInt, sendAttributes, sendTitle, setDimension, setExperienceAndLevel, setLocation, setLore, spawnLightning, spawnXPOrb |
| 0.14.0 | 9 | fromInteger, getEnchantmentLevel, getLore, getVariant, onPlace, readString, readVarInt, sendTitle, setLore |
| 0.14.3 | 8 | fromInteger, getLore, getVariant, onPlace, readString, readVarInt, sendTitle, setLore |
| 0.15.0 | 8 | fromInteger, getLore, getVariant, onPlace, readString, readVarInt, sendTitle, setLore |
| 0.16.0 | 12 | fromInteger, getFoodEnabled, getLore, getMovementSpeed, getVariant, onPlace, readString, sendTitle, setFoodEnabled, setLore, setMovementSpeed, subtractFood |
| 1.0.0 | 17 | addExpLevel, addExperience, fromInteger, getExpectedExperience, getFoodEnabled, getLevelUpExpectedExperience, getLore, getMovementSpeed, getVariant, onPlace, readString, sendTitle, setExperienceAndLevel, setFoodEnabled, setLore, setMovementSpeed, subtractFood |

> 说明：标注含义为「**文档给出的方法名在本版 Genisys 源码中不存在**」。其中一部分（如 `getLore/setLore`、`sendTitle`）在更新的 PocketMine 中确实存在，但 Genisys 此版本未提供该方法（或改用不同命名）；另一部分（如 `onPlace`）是事件回调风格写法，Genisys 该版本未采用。请**以源码为准**。

## 4. 1.0.0 getSynapse() 错误 —— ✅ 已修正

- 原文档称 1.0.0「保留两个 `@deprecated` 桩方法 `isSynapseEnabled()` / `getSynapse()`」。
- 源码实测：1.0.0 **已彻底移除 `getSynapse()` 方法定义**（仅 `Server.php` 残留 `isSynapseEnabled()`，且其实现仍会调用不存在的 `getSynapse()`，依赖 SynapsePM 插件）。
- 已修正 `docs/1.0.0/plugin-api.md` §11.3 与 `docs/1.0.0/core-api.md` 第 151 行，明确「仅 `isSynapseEnabled()`，勿直接调用 `getSynapse()`」。
- 0.16.0 因源码确实保留两个方法，原文档正确，未改。

## 5. 已知边界 / 后续

- core-api 方法表经同样的扫描，无虚构方法（准确）。
- 部分标注方法 Genisys 可能用不同命名提供（概念存在但方法名不符）；标注仅针对「方法名不存在」。
- 若希望把标注行直接删除（而非保留警告），或希望我把这些方法替换为 Genisys 该版本真实的方法名，可告知，我再处理。
- 协议号、geniapi 版本号、协议包数量、1.0.0 的 `FullChunk→Chunk` 与 `Entity::init`/`Tile::init` 重构，已于上一轮验证准确，本轮未改动。
