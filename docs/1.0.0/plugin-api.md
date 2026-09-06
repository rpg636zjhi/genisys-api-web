# Genisys (PocketMine-MP 分支) API 文档（插件用）— 1.0.0

> 适用版本：`VERSION = （CI 编译时写入 git hash）`（代号 `Enopoio`），`API_VERSION = 3.0.0-ALPHA3`，`GENISYS_API_VERSION = 2.0.0`
> 目标客户端：`MCPE 1.0`（协议 `CURRENT_PROTOCOL = 100`，网络版本 `1.0`）
> 运行环境：PHP >= 7.0，需要 `pthreads >= 3.1.5`、`sockets`、`yaml`、`sqlite3`、`zlib`、`curl` 扩展
> 本文方法表以 0.14.x 通用 API 为基准，对 1.0.0 适用；本版本差异见上方「版本差异速记」。

---

> **⚠️ 本版本差异速记（相对 0.14.3 基准）**
> - 新增事件：EntityDrinkPotionEvent、EntityEffectAddEvent、EntityEffectRemoveEvent、PlayerCheatEvent、PlayerIllegalMoveEvent、PlayerToggleFlightEvent
> - 0.14.3 有但本版本缺失的事件：EntityMoveEvent、PlayerTransferEvent
> - 新增协议包：AddHangingEntityPacket、AddItemPacket、AvailableCommandsPacket、ChunkRadiusUpdatedPacket、CommandStepPacket、InventoryActionPacket、LevelSoundEventPacket、PlayerFallPacket、ReplaceItemInSlotPacket、ResourcePackClientResponsePacket、ResourcePacksInfoPacket、SetCommandsEnabledPacket、SpawnExperienceOrbPacket
> - 移除协议包：ChunkRadiusUpdatePacket、RemovePlayerPacket
> - `API_VERSION` 升到 `3.0.0-ALPHA3`，`GENISYS_API_VERSION=2.0.0`，协议 `CURRENT_PROTOCOL=100`。
> - **重大重构**：`FullChunk` 被 `Chunk` 取代；实体/方块实体注册由 `registerEntities/registerTiles` 改为 `Entity::init` / `Tile::init`（见注册锚点）。
> - 玩家经验 API（`getExp`/`setExp`/`addExperience` 等）被移除；新增 `PlayerCheatEvent` / `PlayerIllegalMoveEvent`（命名空间 `event\player\cheat`）。
> - 存档格式重构为 `level/format/io/`（Anvil/McRegion/PMAnvil/LevelDB 子目录）。
> - 以下方法表以 0.14.x 通用 API 为基准，1.0.0 请结合本框与 core-api.md 的注册锚点/差异使用。


## 目录

1. [项目架构与目录结构](#一项目架构与目录结构)
2. [启动流程与全局入口](#二启动流程与全局入口)
3. [插件开发指南（Plugin 开发）](#三插件开发指南plugin-开发)
4. [核心开发 API 详解（每个调用的方法与用处）](#四核心开发-api-详解)
5. [事件系统详解](#五事件系统详解)
6. [命令系统详解](#六命令系统详解)
7. [调度器 Scheduler 详解](#七调度器-scheduler-详解)
8. [权限系统详解](#八权限系统详解)
9. [元数据系统详解](#九元数据系统详解)
10. [工具类详解](#十工具类详解)
11. [网络层](#十一网络层)
12. [完整插件示例](#十二完整插件示例)
13. [附录：常用常量表](#十三附录常用常量表)

---

## 一、项目架构与目录结构

本项目是 **Genisys**（iTX Technologies 出品的 PocketMine-MP 分支），用于搭建 Minecraft PE 服务器。源代码分为四个顶层目录：

```
1.0.0/
├── pocketmine/   # 核心服务器代码（主程序、游戏逻辑、API）
├── raklib/       # RakNet 协议库（UDP 传输层，负责网络通信）
└── spl/          # SPL 扩展库（线程安全日志、类加载器等底层支持）
```

### pocketmine/ 核心模块

| 目录/文件 | 作用 |
|---|---|
| `PocketMine.php` | 程序入口（全局函数、常量、环境检测、启动 Server） |
| `Server.php` | **核心管理类**，管理一切（玩家、世界、插件、命令、调度等） |
| `Player.php` | 在线玩家类（继承 Human → Entity），提供全套玩家 API |
| `IPlayer.php` / `OfflinePlayer.php` | 离线玩家接口/实现（用于读取未上线玩家的存档） |
| `command/` | 命令系统（Command、CommandSender、PluginCommand、SimpleCommandMap 等） |
| `event/` | 事件系统（Event、Listener、HandlerList 及各分类事件） |
| `plugin/` | 插件系统（Plugin、PluginBase、PluginManager、各 Loader） |
| `scheduler/` | 调度器（主线程 Task、异步 AsyncTask、CallbackTask 等） |
| `permission/` | 权限系统（Permission、Permissible、BanList 封禁列表） |
| `metadata/` | 元数据系统（给玩家/实体/世界附加自定义数据） |
| `level/` | 世界系统（Level 世界类、区块 Chunk、生成器 generator、格式 format） |
| `entity/` | 实体系统（Entity 基类、Human、各种生物、投掷物、矿车等） |
| `item/` | 物品系统（Item 基类及各物品/方块实现） |
| `block/` | 方块系统（Block 基类及数百种方块实现） |
| `inventory/` | 背包/容器系统（PlayerInventory、ChestInventory 等） |
| `network/` | 网络层（Network、RakLibInterface、protocol 协议数据包、query、rcon） |
| `nbt/` | NBT 数据格式读写（存档、物品标签） |
| `tile/` | 方块实体 Tile（箱子、熔炉、告示牌、刷怪笼等） |
| `math/` | 数学工具（Vector3、AxisAlignedBB、Math 等） |
| `utils/` | 工具类（Config 配置、TextFormat 颜色、Binary、UUID、TextFormat 等） |
| `updater/` | 自动更新模块（AutoUpdater） |
| `wizard/` | 安装向导（首次启动时引导配置） |
| `lang/` | 多语言支持（BaseLang） |
| `resources/` | 内置资源（pocketmine.yml、genisys.yml 等模板） |

### spl/（Server Pocket Library）

| 文件 | 作用 |
|---|---|
| `BaseClassLoader.php` / `ClassLoader.php` | 类自动加载器 |
| `Logger.php` / `AttachableLogger.php` | 日志接口/带附件的日志器 |
| `ThreadedLogger.php` / `AttachableThreadedLogger.php` | 线程安全日志器（多线程中打印日志） |
| `LogLevel.php` | 日志级别常量 |
| `SplFixedByteArray.php` | 定长字节数组（网络缓冲优化） |
| 各类 `*Exception.php` | 自定义异常类 |

### raklib/（RakNet 协议库）

| 目录/文件 | 作用 |
|---|---|
| `RakLib.php` | RakLib 常量与入口 |
| `Binary.php` | 二进制读写工具 |
| `protocol/` | RakNet 各协议包（OPEN_CONNECTION、ACK、DATA_PACKET 等） |
| `server/` | 服务器实现（SessionManager、Session、ServerHandler、UDPServerSocket 等） |

---

## 二、启动流程与全局入口

### 2.1 命令行启动参数

入口脚本为根目录的 `start.sh` / `start.cmd`，最终调用 PHP 执行 `PocketMine.php`。支持以下参数：

```bash
php PocketMine.php
# 可选参数：
#   --data <path>      指定数据目录（默认当前目录）
#   --plugins <path>   指定插件目录（默认 ./plugins）
#   --no-wizard        跳过首次安装向导
#   --enable-profiler  启用性能分析
# 服务器配置项也可以通过命令行覆盖，如：php PocketMine.php --motd "My Server" --server-port 19133
```

### 2.2 启动流程（PocketMine.php 中各调用）

| 调用 | 用处 |
|---|---|
| `safe_var_dump()` | 安全地打印变量（数组循环缩进），用于调试 |
| `CompatibleClassLoader` 创建 + `addPath("src")` + `register(true)` | 注册类自动加载器 |
| `Terminal::init()` | 初始化终端，检测是否支持 ANSI 颜色 |
| `new MainLogger(DATA."server.log", ANSI)` | 创建主日志器（同时写文件和控制台） |
| `detect_system_timezone()` / `parse_offset()` | 自动检测系统时区（读取 /etc/timezone、wmic 等） |
| `ThreadManager::init()` | 初始化线程管理器 |
| `new Server($autoloader, $logger, PATH, DATA, PLUGIN_PATH, $lang)` | **创建服务器核心对象（一切从这里开始）** |
| `ServerKiller(8)->start()` | 8 秒无响应自动强制退出（防卡死） |

### 2.3 全局常量

| 常量 | 值 | 用处 |
|---|---|---|
| `pocketmine\VERSION` | `（CI 编译时写入 git hash）` | 核心版本号 |
| `pocketmine\API_VERSION` | `3.0.0-ALPHA3` | API 版本（插件 api 字段需匹配） |
| `pocketmine\GENISYS_API_VERSION` | `2.0.0` | Genisys 扩展 API 版本（插件 geniapi 字段） |
| `pocketmine\MINECRAFT_VERSION` | `MCPE 1.0` | 目标客户端版本 |
| `pocketmine\PATH` | 程序根目录 | 源码路径 |
| `pocketmine\DATA` | 数据目录 | 存档/配置目录 |
| `pocketmine\PLUGIN_PATH` | 插件目录 | 插件存放目录 |
| `pocketmine\START_TIME` | 启动时间戳 | 用于计算运行时长 |

---

## 三、插件开发指南（Plugin 开发）

### 3.1 插件结构

一个插件可以是 **Phar 文件**（`.phar`）或 **文件夹**（源码插件，目录内有 `plugin.yml` 和 `src/`）。

```
MyPlugin.phar  （或 MyPlugin/ 文件夹）
├── plugin.yml          # 插件描述文件（必须）
├── src/                # 源码目录（main 类所在路径）
│   └── MyPlugin/
│       └── Main.php    # 主类
└── resources/          # 内置资源（可选，如 config.yml）
```

### 3.2 plugin.yml 详解

```yaml
name: MyPlugin              # 插件名（必填，不能含空格，不能以 pocketmine/minecraft/mojang 开头）
version: 1.0.0              # 插件版本（必填）
main: MyPlugin\Main         # 主类全名（必填，命名空间+类名，不能以 pocketmine\ 开头）
api:                        # 兼容的 API 版本（必填）
- 3.0.0-ALPHA3
geniapi:                    # 兼容的 Genisys API 版本（可选，默认 ["1.0.0"]）
- 3.0.0-ALPHA3
load: POSTWORLD             # 加载时机：STARTUP（世界加载前）或 POSTWORLD（默认）
depend:                     # 硬依赖（这些插件必须先加载，缺失则本插件不加载）
- AnotherPlugin
softdepend:                 # 软依赖（有则先加载，没有也可以）
- OptionalPlugin
loadbefore:                 # 要在哪些插件之前加载
- OtherPlugin
website: http://example.com  # 网站
description: A test plugin    # 插件描述
author: MyName               # 作者（单数）
authors:                     # 作者（复数）
- AuthorA
- AuthorB
prefix: TEST                 # 日志前缀（日志显示 [TEST]）
commands:                    # 命令定义（会被自动注册为 PluginCommand）
  mycmd:
    description: My command
    usage: "/mycmd <player>"
    aliases: [mc, myc]
    permission: myplugin.cmd
    permission-message: "你没有权限！"
permissions:                 # 权限定义
  myplugin.cmd:
    default: op              # op / notop / true / false
    description: 允许使用 mycmd
  myplugin.*:
    default: op
    children:                # 子权限
      myplugin.cmd:
        default: true
```

> 注意：`api` 版本比较规则——主版本号高于服务器则拒绝加载；`geniapi` 采用"主.次.补丁"严格比较。

### 3.3 主类（Plugin 接口与 PluginBase 基类）

主类必须实现 `pocketmine\plugin\Plugin` 接口，通常继承 `PluginBase` 抽象类。

`PluginBase` 提供的方法与用处：

| 方法 | 用处 |
|---|---|
| `onLoad()` | 插件被加载时调用（在 onEnable 之前，世界可能尚未就绪）。用于注册外部类加载、读取数据 |
| `onEnable()` | 插件被启用时调用。**在这里注册事件监听器、命令、任务** |
| `onDisable()` | 插件被禁用时调用。用于保存数据、关闭连接、清理资源 |
| `isEnabled()` / `isDisabled()` | 查询插件是否启用/禁用 |
| `getDataFolder()` | 获取插件数据文件夹（`plugins/MyPlugin/`），用于保存配置文件和数据 |
| `getDescription()` | 获取 PluginDescription（插件描述信息对象） |
| `getLogger()` | 获取 PluginLogger（带插件名前缀的日志器） |
| `getServer()` | **获取 Server 单例**，一切核心 API 的入口 |
| `getName()` / `getFullName()` | 获取插件名 / 名+版本 |
| `getConfig()` | 获取 Config 配置对象（首次调用自动加载 config.yml） |
| `saveConfig()` | 把当前配置写回磁盘 |
| `saveDefaultConfig()` | 如果数据目录没有 config.yml，则从 resources/config.yml 复制一份（**常用！**） |
| `reloadConfig()` | 重新从磁盘读取配置 |
| `getResource($filename)` | 读取插件内置资源文件，返回文件流（用完要 fclose） |
| `saveResource($filename, $replace=false)` | 把内置资源保存到数据目录，`$replace` 为 true 时覆盖已存在的文件 |
| `getResources()` | 返回插件内所有内置资源的路径数组 |
| `getCommand($name)` | 获取本插件注册的某个命令对象 |
| `onCommand(CommandSender, Command, $label, array $args)` | **命令执行回调**，返回 true 表示处理成功 |
| `getPluginLoader()` | 获取加载本插件的 Loader |

### 3.4 插件加载器（PluginLoader）

| 加载器 | 匹配规则 | 用处 |
|---|---|---|
| `PharPluginLoader` | `*.phar` | 加载 Phar 打包的插件 |
| `FolderPluginLoader` | 任意文件夹 | 加载源码文件夹插件（需含 plugin.yml 和 src/） |
| `ScriptPluginLoader` | `*.php` | 加载单文件脚本插件 |

`PluginManager` 的加载流程：
1. `registerInterface($loaderClassName)` 注册加载器
2. `loadPlugins($directory)` 扫描插件目录，解析每个 plugin.yml
3. 检查 API 兼容性、依赖关系（depend 必须满足，softdepend 可选）
4. `loadPlugin($path)` 实例化插件，调用 `init()` 初始化，然后触发 `onLoad()`
5. `enablePlugin($plugin)` → Loader 调用 `setEnabled(true)` → 触发 `onEnable()` → 派发 `PluginEnableEvent`
6. 服务器关闭时 `disablePlugins()` → `onDisable()` → 派发 `PluginDisableEvent`

### 3.5 插件生命周期时序图

```
服务器启动
   ↓
PluginManager::loadPlugins()
   ↓ 解析 plugin.yml，检查 api/geniapi/依赖
PluginLoader::loadPlugin()
   ↓ 实例化主类
PluginBase::init()   → 初始化 loader/server/description/dataFolder
   ↓
onLoad()             ← 插件被加载（世界未就绪）
   ↓
PluginManager::enablePlugin()
   ↓
setEnabled(true) → onEnable()   ← 注册监听器/命令/任务
   ↓
PluginEnableEvent 派发
   ↓ ......... 服务器运行中 .........
   ↓
服务器关闭 → disablePlugins()
   ↓
setEnabled(false) → onDisable() ← 保存数据
   ↓
PluginDisableEvent 派发
```

---

## 四、核心开发 API 详解

> 本部分列出核心开发（改服务端 / 写插件）最常用到的每个类的每个公开方法及其用处。所有方法都通过 `Server::getInstance()` 获取 Server 实例后调用。

### 4.1 Server 类（一切 API 的入口）

**获取方式**：`Server::getInstance()`（静态单例），或在插件中 `$this->getServer()`。

#### 基础信息

| 方法 | 用处 |
|---|---|
| `getName()` | 返回服务器软件名 "Genisys" |
| `getPocketMineVersion()` | 返回核心版本 `1.1dev` |
| `getApiVersion()` | 返回 API 版本 `3.0.0-ALPHA3` |
| `getGeniApiVersion()` | 返回 Genisys API 版本 `2.0.0` |
| `getVersion()` | 返回目标客户端版本 `v0.14.x alpha` |
| `getCodename()` | 返回代号 `Ikaros` |
| `getMotd()` / `getServerName()` | 返回服务器 MOTD 标题 |
| `getIp()` / `getPort()` | 返回服务器绑定 IP / 端口 |
| `getMaxPlayers()` | 返回最大玩家数 |
| `getFilePath()` / `getDataPath()` / `getPluginPath()` | 程序根目录 / 数据目录 / 插件目录 |
| `getServerUniqueId()` | 服务器唯一 UUID |
| `getBuild()` / `getGameVersion()` | 构建号 / 客户端版本号 |
| `getTick()` | 服务器已运行 tick 数（20 tick = 1 秒） |

#### 玩家管理

| 方法 | 用处 |
|---|---|
| `getOnlinePlayers()` | 返回所有在线玩家数组 `Player[]`（键为名称小写） |
| `getPlayer($name)` | 按前缀匹配玩家（输入部分名字返回最接近的玩家） |
| `getPlayerExact($name)` | 精确匹配玩家（区分大小写不敏感） |
| `matchPlayer($partialName)` | 返回所有名字包含该子串的玩家数组 |
| `getOfflinePlayer($name)` | 返回离线玩家对象（可读取存档数据） |
| `getOfflinePlayerData($name)` | 读取玩家存档 NBT（CompoundTag），不存在则创建默认 |
| `saveOfflinePlayerData($name, CompoundTag $nbtTag, $async=false)` | 保存玩家存档，`$async=true` 时异步写入（推荐） |
| `removePlayer(Player $player)` | 从玩家列表移除玩家 |

#### 广播与消息

| 方法 | 用处 |
|---|---|
| `broadcastMessage($message, $recipients=null)` | 向所有玩家广播聊天消息（或指定玩家数组），返回接收人数 |
| `broadcastTip(string $tip, $recipients=null)` | 广播右上角 Tip 提示 |
| `broadcastPopup(string $popup, $recipients=null)` | 广播中央 Popup 弹窗 |
| `broadcast($message, string $permissions)` | 向拥有指定权限的玩家广播（权限用 `;` 分隔多个） |
| `broadcastPacket(array $players, DataPacket $packet)` | 向一组玩家广播一个网络数据包 |
| `batchPackets(array $players, array $packets, $forceSync=false)` | 批量发送数据包（自动压缩） |

#### 世界（Level）管理

| 方法 | 用处 |
|---|---|
| `getLevels()` | 返回所有已加载世界 |
| `getLevel($levelId)` | 按 ID 获取世界 |
| `getLevelByName($name)` | 按文件夹名获取世界 |
| `getDefaultLevel()` | 获取默认世界（出生点所在世界） |
| `setDefaultLevel($level)` | 运行时切换默认世界（不改变配置文件） |
| `isLevelLoaded($name)` | 世界是否已加载 |
| `isLevelGenerated($name)` | 世界是否已生成（存在存档文件夹） |
| `loadLevel($name)` | 从存档文件夹加载世界 |
| `generateLevel($name, $seed=null, $generator=null, $options=[])` | 生成新世界（指定种子、生成器类、预设） |
| `unloadLevel(Level $level, $forceUnload=false)` | 卸载世界（默认世界需强制） |

#### 配置读取

| 方法 | 用处 |
|---|---|
| `getProperty($variable, $default=null)` | 读取 pocketmine.yml 的嵌套配置项（如 `"settings.language"`），支持命令行覆盖 |
| `getConfigString($variable, $default="")` | 读取 server.properties 字符串配置 |
| `getConfigInt($variable, $default=0)` | 读取 server.properties 整数配置 |
| `getConfigBoolean($variable, $default=false)` | 读取 server.properties 布尔配置（识别 true/on/1/yes） |
| `setConfigString/Int/Bool(...)` | 修改配置并写入 properties 文件 |
| `getAdvancedProperty($key, $default)` | 读取 genisys.yml 的高级配置 |

#### OP / 白名单 / 封禁

| 方法 | 用处 |
|---|---|
| `addOp($name)` / `removeOp($name)` | 添加/移除 OP（管理员） |
| `isOp($name)` | 是否为 OP |
| `addWhitelist($name)` / `removeWhitelist($name)` | 添加/移除白名单 |
| `isWhitelisted($name)` | 是否在白名单中 |
| `getWhitelisted()` / `getOps()` | 获取白名单/OP 配置文件对象 |
| `reloadWhitelist()` | 重新加载白名单 |
| `getNameBans()` / `getIPBans()` / `getCIDBans()` | 获取名字/IP/客户端ID 封禁列表（BanList 对象） |

#### 系统对象获取

| 方法 | 用处 |
|---|---|
| `getPluginManager()` | 获取插件管理器（注册事件、获取插件等） |
| `getCommandMap()` | 获取命令映射表（注册命令） |
| `getScheduler()` | 获取调度器（注册任务） |
| `getCraftingManager()` | 获取合成管理器 |
| `getLogger()` | 获取主日志器 |
| `getLanguage()` / `isLanguageForced()` | 获取语言对象 / 是否强制语言 |
| `getLoader()` | 获取类加载器 |
| `getEntityMetadata()` / `getPlayerMetadata()` / `getLevelMetadata()` | 获取各元数据仓库 |
| `getMemoryManager()` | 内存管理器 |
| `getTicksPerSecond()` / `getTicksPerSecondAverage()` | 服务器 TPS（每秒 tick 数，正常 20） |
| `getTickUsage()` / `getTickUsageAverage()` | TPS 占用百分比 |

#### 命令执行与关闭

| 方法 | 用处 |
|---|---|
| `dispatchCommand(CommandSender $sender, $commandLine)` | 以某个发送者身份执行命令字符串（如 `dispatchCommand($player, "give a 1")`） |
| `shutdown($restart=false, $msg="")` | 关闭服务器（可重启） |
| `getCrashPath()` | 崩溃报告目录 |
| `addRecipe(Recipe $recipe)` | 注册自定义合成配方 |

### 4.2 Player 类（在线玩家）

Player 继承链：`Player → Human → Creature → Living → Entity`。以下是插件开发最常用的方法。

#### 基本信息

| 方法 | 用处 |
|---|---|
| `getName()` | 玩家名字 |
| `getDisplayName()` / `setDisplayName($name)` | 获取/设置显示名（昵称，不影响真实名） |
| `getClientId()` | 客户端 ID（设备唯一标识，可用于封禁） |
| `getClientSecret()` | 客户端密钥 |
| `getAddress()` / `getPort()` | 玩家 IP 地址 / 端口 |
| `getUniqueId()` | 玩家 UUID（继承自 Entity） |
| `getProtocol()` | 玩家使用的协议版本 |
| `isOnline()` / `isConnected()` | 玩家是否在线 / 连接是否有效 |
| `isOp()` / `setOp($value)` | 是否 OP / 设置 OP（会触发权限重算） |
| `isBanned()` / `setBanned($value)` | 是否被封禁 / 设置封禁状态 |
| `isWhitelisted()` / `setWhitelisted($value)` | 是否在白名单 / 设置白名单 |
| `hasPlayedBefore()` | 是否以前玩过（有存档） |
| `getFirstPlayed()` / `getLastPlayed()` | 首次/上次游玩时间戳（毫秒） |
| `getServer()` | 获取 Server 实例 |

#### 消息发送（重中之重）

| 方法 | 用处 |
|---|---|
| `sendMessage($message)` | **发送普通聊天消息**（支持 TextContainer，自动多行分割） |
| `sendTranslation($message, array $parameters=[])` | 发送翻译消息（`%` 开头键，会自动本地化） |
| `sendPopup($message, $subtitle="")` | 发送屏幕中央弹窗（有副标题参数） |
| `sendTip($message)` | 发送右上角提示（**已废弃**，0.14.2+ 客户端自动重定向到 sendPopup） |
| `sendTitle($title, $subtitle="")` | （部分版本）发送标题大字  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `sendSettings()` | 强制重新下发客户端设置（飞行、自动跳跃等） |
| `sendAttributes()` | 下发属性（生命、饥饿、速度等）给客户端 |
| `sendPosition(Vector3 $pos, $yaw=null, $pitch=null, $mode=0, $targets=null)` | 向客户端同步玩家位置 |

#### 位置与传送

| 方法 | 用处 |
|---|---|
| `getPosition()` / `getLocation()` | 获取坐标（Position 带世界 / Location 带朝向和世界） |
| `getLevel()` | 玩家所在的世界（Level 对象） |
| `teleport(Vector3 $pos, $yaw=null, $pitch=null)` | **传送玩家**（平滑移动，需要区块加载） |
| `teleportImmediate(Vector3 $pos, $yaw=null, $pitch=null)` | 立即传送（跳过移动过程） |
| `setSpawn(Vector3 $pos)` / `getSpawn()` | 设置/获取玩家出生点（死亡后重生于此） |
| `setMotion(Vector3 $mot)` | 设置玩家速度向量（击飞、抛射） |
| `addEntityMotion($entityId, $x, $y, $z)` | 让客户端移动某个实体 |
| `isOnGround()` | 是否在地面 |
| `getDirection()` / `getDirectionVector()` | 玩家朝向（0-3 / 向量） |

#### 游戏模式

| 方法 | 用处 |
|---|---|
| `getGamemode()` | 获取游戏模式（0 生存 / 1 创造 / 2 冒险 / 3 旁观） |
| `setGamemode(int $gm)` | **设置游戏模式**（会派发 PlayerGameModeChangeEvent，可被取消） |
| `isSurvival()` / `isCreative()` / `isAdventure()` / `isSpectator()` | 快捷判断游戏模式 |
| `setAllowFlight($value)` / `getAllowFlight()` | 设置/获取是否允许飞行 |
| `setAutoJump($value)` / `hasAutoJump()` | 设置/获取自动跳跃 |

#### 生命、伤害、食物、经验

| 方法 | 用处 |
|---|---|
| `getHealth()` / `setHealth($amount)` | 获取/设置生命值（注意 setHealth 会派发 EntityDamageEvent，可能被取消） |
| `setMaxHealth($amount)` | 设置最大生命值 |
| `attack($damage, EntityDamageEvent $source)` | 让玩家受到伤害（会派发事件） |
| `heal($amount, EntityRegainHealthEvent $source)` | 治疗（继承自 Entity，需构造事件对象） |
| `kill()` | 杀死玩家（派发死亡事件、掉落物品） |
| `getFood()` / `setFood(float $amount)` | 获取/设置饥饿值 |
| `subtractFood($amount)` | 减少饥饿  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `setFoodEnabled($enabled)` / `getFoodEnabled()` | 开关饥饿系统  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `getExp()` / `getExpLevel()` / `setExp(int)` / `setExpLevel(int)` | 获取/设置经验值 / 等级 |
| `addExperience(int $exp)` / `addExpLevel(int $level)` | 增加经验 / 等级  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `setExperienceAndLevel(int $exp, int $level)` | 同时设置经验与等级  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `getExpectedExperience()` / `getLevelUpExpectedExperience()` | 升到下一级所需经验  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `getMovementSpeed()` / `setMovementSpeed($amount)` | 获取/设置移动速度  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |

#### 效果（药水效果）

| 方法 | 用处 |
|---|---|
| `getEffects()` | 获取所有药水效果 |
| `addEffect(Effect $effect)` | 添加药水效果（如 `Effect::getEffect(Effect::SPEED)->setDuration(100)->setAmplifier(1)`） |
| `removeEffect($effectId)` | 移除指定效果（如 `Effect::POISON`） |
| `hasEffect($effectId)` / `getEffect($effectId)` | 是否有/获取某效果 |
| `removeAllEffects()` | 清除全部效果 |

#### 背包

| 方法 | 用处 |
|---|---|
| `getInventory()` | 获取玩家背包（PlayerInventory 对象） |
| `getItemInHand()` | 玩家手持的物品 |
| `getWindowId(Inventory $inventory)` | 获取某容器的窗口 ID |
| `addWindow(Inventory $inventory, int $forceId=null)` | 向玩家打开一个容器窗口（箱子等） |
| `removeWindow(Inventory $inventory)` | 关闭容器窗口 |

#### 权限

| 方法 | 用处 |
|---|---|
| `hasPermission($name)` | 玩家是否有某权限（含 OP 继承的默认权限） |
| `isPermissionSet($name)` | 是否显式设置过某权限 |
| `addAttachment(Plugin $plugin, $name=null, $value=null)` | 附加插件权限（返回 PermissionAttachment） |
| `removeAttachment(PermissionAttachment $attachment)` | 移除插件权限附件 |
| `recalculatePermissions()` | 重新计算所有权限 |
| `getEffectivePermissions()` | 获取当前生效的权限列表 |

#### 互动与显示

| 方法 | 用处 |
|---|---|
| `hidePlayer(Player $player)` | 隐藏某个玩家（自己看不到他） |
| `showPlayer(Player $player)` | 重新显示玩家 |
| `canSee(Player $player)` | 是否能看见某玩家 |
| `setSkin($str, $skinName)` | 设置玩家皮肤 |
| `isSleeping()` / `sleepOn(Vector3 $pos)` / `stopSleep()` | 睡觉相关 |
| `awardAchievement($achievementId)` / `hasAchievement($achievementId)` | 授予/查询成就 |
| `setMetadata($key, MetadataValue)` / `getMetadata($key)` / `hasMetadata($key)` / `removeMetadata($key, Plugin)` | 玩家自定义元数据 |

#### 踢出与关闭

| 方法 | 用处 |
|---|---|
| `kick($reason="", $isAdmin=true)` | **踢出玩家**（`$isAdmin=true` 显示"Kicked by admin"；`$reason` 为踢出原因） |
| `close($message, $reason)` | 强制关闭连接（`$message` 为广播的退出消息） |
| `getLeaveMessage()` | 退出广播消息 |
| `save($async=false)` | 保存玩家数据到存档（异步可选） |

#### 实体相关（继承自 Entity）

| 方法 | 用处 |
|---|---|
| `spawnTo(Player $player)` / `spawnToAll()` | 使玩家出现在某个/所有玩家视野中 |
| `despawnFrom(Player $player)` / `despawnFromAll()` | 使玩家从视野中消失 |
| `getId()` | 实体 ID |
| `getNameTag()` / `setNameTag($name)` | 获取/设置头顶名字 |
| `setNameTagVisible($value)` | 是否显示名字 |
| `isSneaking()` / `setSneaking($value)` | 潜行 |
| `isSprinting()` / `setSprinting($value)` | 疾跑 |
| `setDataProperty($id, $type, $value)` | 设置实体数据属性（如 DATA_NAMETAG） |
| `isOnFire()` / `setOnFire($seconds)` / `extinguish()` | 着火相关 |
| `getBoundingBox()` | 获取碰撞箱 |
| `move($dx,$dy,$dz)` / `fastMove($dx,$dy,$dz)` | 移动实体 |

### 4.3 PlayerInventory 类（玩家背包）

通过 `$player->getInventory()` 获取。

| 方法 | 用处 |
|---|---|
| `getSize()` / `setSize($size)` | 背包槽位数（默认 36） |
| `getItemInHand()` / `setItemInHand(Item $item)` | 获取/设置手持物品 |
| `getHeldItemIndex()` / `setHeldItemIndex($index)` | 获取/设置选中快捷栏格子索引 |
| `getHeldItemSlot()` / `setHeldItemSlot($slot)` | 获取/设置手持槽位 |
| `getItem($index)` / `setItem($index, Item $item)` | **获取/设置某格物品**（格子索引：0-8 快捷栏，9-35 背包） |
| `clear($index)` / `clearAll()` | 清空某格 / 全部 |
| `getHotbarSlotIndex($index)` / `setHotbarSlotIndex($index, $slot)` | 快捷栏映射 |
| `getArmorItem($index)` / `setArmorItem($index, Item $item)` | 护甲槽（0 头盔 / 1 胸甲 / 2 护腿 / 3 靴子） |
| `getHelmet()` / `setHelmet(Item)` | 头盔 |
| `getChestplate()` / `setChestplate(Item)` | 胸甲 |
| `getLeggings()` / `setLeggings(Item)` | 护腿 |
| `getBoots()` / `setBoots(Item)` | 靴子 |
| `getArmorContents()` / `setArmorContents(array $items)` | 全部护甲 |
| `sendContents($target)` / `sendArmorContents($target)` | 向某玩家发送背包内容/护甲（同步显示） |
| `sendSlot($index, $target)` / `sendArmorSlot($index, $target)` | 向某玩家发送单个格子 |
| `sendHeldItem($target)` | 发送手持物品给目标 |
| `getHolder()` | 背包持有者（Human） |

### 4.4 Level 类（世界）

通过 `$player->getLevel()` 或 `Server::getInstance()->getDefaultLevel()` 获取。

#### 世界信息

| 方法 | 用处 |
|---|---|
| `getName()` / `getFolderName()` | 世界显示名 / 存档文件夹名 |
| `getId()` | 世界 ID |
| `getSeed()` / `setSeed($seed)` | 获取/设置世界种子 |
| `getTime()` / `setTime($time)` | 获取/设置世界时间（0 白天 / 12000 日落 / 14000 夜晚 / 23000 日出 / 24000 全天循环） |
| `stopTime()` / `startTime()` | 冻结 / 恢复时间流动 |
| `getSpawnLocation()` / `setSpawnLocation(Vector3)` | 世界出生点 |
| `getSpawn()` / `getSafeSpawn($spawn=null)` / `setSpawn(Vector3)` | 出生点 / 安全出生点（检测脚下无虚空） |
| `getDimension()` / `setDimension(int)` | 维度（0 主世界 / 1 地狱） |
| `getServer()` | 获取 Server |
| `getAutoSave()` / `setAutoSave($value)` | 自动保存开关 |
| `save($force=false)` / `saveChunks()` | 保存世界 / 保存全部区块 |

#### 方块读写（重中之重）

| 方法 | 用处 |
|---|---|
| `getBlock(Vector3 $pos, $cached=true)` | **获取方块对象**（如 `$level->getBlock(new Vector3($x,$y,$z))`） |
| `getBlockIdAt(int $x, int $y, int $z)` | 获取方块 ID（更快） |
| `getBlockDataAt(int $x, int $y, int $z)` | 获取方块数据值（meta） |
| `setBlock(Vector3 $pos, Block $block, $direct=false, $update=true)` | **放置方块**（`$direct=true` 跳过旧的方块） |
| `setBlockIdAt(int $x, int $y, int $z, int $id)` | 直接写方块 ID（不走事件） |
| `setBlockDataAt(int $x, int $y, int $z, int $data)` | 直接写方块数据 |
| `getFullBlock($x, $y, $z)` | 获取 ID 与 meta 合并的整数值 |
| `getHighestBlockAt($x, $z)` | 获取该坐标最高的非空气方块高度 |
| `getBiomeId($x, $z)` / `setBiomeId($x, $z, $biomeId)` | 获取/设置生物群系 |
| `getHeightMap($x, $z)` / `setHeightMap($x, $z, $value)` | 高度图 |
| `useBreakOn(Vector3 $vector, Item &$item=null, Player $player=null, $createParticles=false)` | 模拟玩家破坏方块（走完整事件流程） |
| `useItemOn(Vector3 $vector, Item &$item, $face, ...)` | 模拟玩家使用物品对方块 |
| `dropItem(Vector3 $source, Item $item, Vector3 $motion=null, $delay=10)` | **掉落物品实体** |
| `updateAround(Vector3 $pos)` | 更新方块周围邻居 |
| `scheduleUpdate(Vector3 $pos, $delay)` | 延迟更新方块 |

#### 实体管理

| 方法 | 用处 |
|---|---|
| `getEntity($entityId)` | 按实体 ID 获取实体 |
| `getEntities()` | 所有实体 |
| `getPlayers()` | 世界内所有玩家 |
| `getNearbyEntities(AxisAlignedBB $bb, Entity $entity=null)` | 获取碰撞箱内的附近实体 |
| `getCollidingEntities(AxisAlignedBB $bb, Entity $entity=null)` | 碰撞实体 |
| `getTiles()` / `getTile(Vector3 $pos)` / `getTileById($tileId)` | 方块实体（箱子/熔炉等） |
| `addEntity(Entity $entity)` / `removeEntity(Entity $entity)` | 添加/移除实体 |
| `spawnLightning(Vector3 $pos)` | 生成闪电 |
| `spawnXPOrb(Vector3 $pos, int $exp=1)` | 生成经验球 |
| `addSound(Sound $sound, array $players=null)` | 播放音效（如 `new ClickSound($pos)`） |
| `addParticle(Particle $particle, array $players=null)` | 生成粒子效果（如 `new ExplodeParticle($pos)`） |

#### 区块管理

| 方法 | 用处 |
|---|---|
| `getChunk(int $x, int $z, bool $create=false)` | 获取区块对象 |
| `loadChunk($x, $z, $generate=true)` | 加载区块 |
| `unloadChunk($x, $z, $safe=true, $trySave=true)` | 卸载区块 |
| `isChunkLoaded($x, $z)` / `isChunkGenerated($x, $z)` / `isChunkPopulated($x, $z)` | 区块状态查询 |
| `populateChunk($x, $z, $force=false)` | 填充（生成建筑）区块 |
| `generateChunk($x, $z, $force=false)` | 生成区块 |
| `regenerateChunk($x, $z)` | 重新生成区块 |
| `unloadChunks($force=false)` | 卸载所有未使用区块 |
| `chunkHash($x, $z)` / `blockHash($x, $y, $z)` | 坐标哈希（用于数组索引） |

#### 元数据

| 方法 | 用处 |
|---|---|
| `setMetadata($key, MetadataValue)` / `getMetadata($key)` / `hasMetadata($key)` / `removeMetadata($key, Plugin)` | 世界级自定义元数据 |

### 4.5 Entity 类（实体基类）

所有生物、玩家、物品、投掷物的基类。常用方法：

| 方法 | 用处 |
|---|---|
| `createEntity($type, FullChunk $chunk, CompoundTag $nbt, ...$args)` | 静态工厂：创建实体 |
| `registerEntity($className, $force=false)` | 注册自定义实体类（用于自定义生物） |
| `getPosition()` / `getLocation()` | 位置（Position/Location） |
| `teleport(Vector3 $pos, $yaw=null, $pitch=null)` | 传送 |
| `getMotion()` / `setMotion(Vector3)` | 速度向量 |
| `setPosition(Vector3 $pos)` / `setLocation(Location)` / `setPositionAndRotation(...)` | 直接设置位置 |
| `move($dx,$dy,$dz)` | 移动（带碰撞检测） |
| `getHealth()` / `setHealth($amount)` / `getMaxHealth()` / `setMaxHealth($amount)` | 生命 |
| `attack($damage, EntityDamageEvent $source)` | 受击（派发 EntityDamageEvent，可取消） |
| `heal($amount, EntityRegainHealthEvent $source)` | 回复 |
| `kill()` | 死亡（掉落物、经验） |
| `isAlive()` | 是否存活 |
| `getLastDamageCause()` / `setLastDamageCause($type)` | 上次伤害原因 |
| `getNameTag()` / `setNameTag($name)` / `setNameTagVisible($value)` | 头顶名字 |
| `getDataProperty($id)` / `setDataProperty($id, $type, $value)` / `getDataFlag(...)` / `setDataFlag(...)` | 实体数据属性/标志 |
| `addEffect(Effect)` / `removeEffect($effectId)` / `getEffects()` / `hasEffect($effectId)` | 药水效果 |
| `getDirection()` / `getDirectionVector()` | 朝向 |
| `setOnFire($seconds)` / `isOnFire()` / `extinguish()` | 着火 |
| `fall($fallDistance)` | 坠落伤害处理 |
| `spawnTo(Player)` / `spawnToAll()` / `despawnFrom(Player)` / `despawnFromAll()` | 视野管理 |
| `getViewers()` | 能看到该实体的玩家 |
| `getAttributeMap()` | 属性映射（生命、移动速度、攻击等） |
| `setMetadata(...)` / `getMetadata(...)` | 实体元数据 |
| `close()` | 关闭（销毁）实体 |

### 4.6 Item 类（物品）

#### 静态方法（最常用）

| 方法 | 用处 |
|---|---|
| `Item::get($id, $meta=0, int $count=1, $tags="")` | **创建物品对象**。如 `Item::get(Item::DIAMOND, 0, 5)` 获得 5 个钻石 |
| `Item::fromString(string $str, bool $multiple=false)` | 从字符串创建（如 `"264:0 5"` 或 `"diamond"`） |
| `Item::getCreativeItems()` / `addCreativeItem(Item)` / `removeCreativeItem(Item)` | 创造模式物品栏管理 |
| `Item::clearCreativeItems()` | 清空创造物品栏 |
| `Item::init($readFromJson=false)` | 初始化物品列表（可读 JSON 扩展） |

#### 实例方法

| 方法 | 用处 |
|---|---|
| `getId()` / `setDamage($meta)` / `getDamage()` | 物品 ID / 数据值（meta） |
| `getCount()` / `setCount(int $count)` | 数量 |
| `getName()` | 物品名 |
| `getMaxStackSize()` | 最大堆叠数 |
| `getBlock()` | 获取物品对应的方块对象（`Item::get(Item::STONE)->getBlock()`） |
| `getCustomName()` / `setCustomName(string)` / `clearCustomName()` / `hasCustomName()` | 自定义显示名（彩色用 TextFormat） |
| `getLore()` / `setLore(array)` | 物品 lore 说明文字  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `hasEnchantments()` / `getEnchantments()` / `getEnchantmentLevel(int)` / `addEnchantment(Enchantment)` | 附魔 |
| `getNamedTag()` / `setNamedTag(CompoundTag)` / `hasCompoundTag()` / `getCompoundTag()` | NBT 标签（给物品附加数据） |
| `isTool()` / `isArmor()` / `isPickaxe()` / `isAxe()` / `isSword()` / `isShovel()` / `isHoe()` | 工具/护甲类型判断 |
| `getFuelTime()` | 燃料燃烧时间（0 表示不可燃烧） |
| `getMaxDurability()` | 最大耐久 |
| `__toString()` | 输出为字符串（`"ID:META xCOUNT"`） |

> 例：给玩家一个带自定义名字的钻石剑
> ```php
> $sword = Item::get(Item::DIAMOND_SWORD);
> $sword->setCustomName(TextFormat::GOLD . "传说之剑");
> $player->getInventory()->addItem($sword);
> ```

### 4.7 Block 类（方块）

`$level->getBlock(new Vector3($x,$y,$z))` 返回方块对象。常用：

| 方法 | 用处 |
|---|---|
| `getId()` / `getDamage()` | 方块 ID / 数据值 |
| `getX()` / `getY()` / `getZ()` | 坐标 |
| `getLevel()` | 所在世界 |
| `getDrops(Item $item)` | 被破坏后掉落的物品数组 |
| `getBreakTime(Item $item)` | 破坏所需时间 |
| `isSolid()` / `isTransparent()` | 是否实心 / 透明 |
| `canBePlaced()` / `canBeActivated()` | 可否放置 / 可否激活 |
| `onActivate(Item $item, Player $player=null)` | 被右键激活时的回调 |
| `onBreak(Item $item)` / `onPlace(Item $item)` | 破坏/放置回调  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `getBoundingBox()` | 碰撞箱 |

> 常用构造：`new Stone()`、`new Dirt()` 等，每个方块一个类。也常用 `Block::get($id)` 按 ID 创建。

---

## 五、事件系统详解

### 5.1 核心概念

事件系统基于监听器。核心类：

| 类 | 作用 |
|---|---|
| `pocketmine\event\Event` | 所有事件的抽象基类 |
| `pocketmine\event\Listener` | 监听器接口（空标记接口） |
| `pocketmine\event\EventPriority` | 事件优先级常量 |
| `pocketmine\event\Cancellable` | 可取消事件接口（实现它的事件可被 `setCancelled()` 取消） |
| `pocketmine\event\HandlerList` | 处理器列表（管理同一事件的所有监听器） |
| `pocketmine\plugin\RegisteredListener` | 已注册的监听器封装 |
| `pocketmine\plugin\MethodEventExecutor` | 方法执行器（把事件派发到监听器方法） |

### 5.2 监听器优先级（EventPriority）

```php
const LOWEST = 5;
const LOW = 4;
const NORMAL = 3;
const HIGH = 2;
const HIGHEST = 1;
const MONITOR = 0;
```

- 按 `LOWEST → LOW → NORMAL → HIGH → HIGHEST → MONITOR` 顺序执行
- 优先级高的（数值小）先执行，可提前 `setCancelled(true)` 阻止后续
- `MONITOR` 最后执行，通常只用来观察记录，不应取消事件

### 5.3 事件注册（PluginManager）

```php
// 方式一：自动注册（推荐）——监听器类所有 public 且带单个事件参数的方法都会被注册
$this->getServer()->getPluginManager()->registerEvents(new MyListener($this), $this);

// 方式二：手动注册
$this->getServer()->getPluginManager()->registerEvent(
    \pocketmine\event\player\PlayerJoinEvent::class,  // 事件类名
    $listener,                                         // 监听器对象
    EventPriority::NORMAL,                             // 优先级
    new MethodEventExecutor("onJoin"),                 // 执行器
    $this                                            // 插件
);
```

监听器写法（注解支持 `@priority` 和 `@ignoreCancelled`）：

```php
class MyListener implements Listener {

    /**
     * @priority HIGH
     * @ignoreCancelled false
     */
    public function onJoin(PlayerJoinEvent $event){
        $event->getPlayer()->sendMessage("欢迎加入！");
    }

    public function onDamage(EntityDamageEvent $event){
        if($event->getEntity() instanceof Player and $event->getCause() === EntityDamageEvent::CAUSE_FALL){
            $event->setCancelled(true);  // 取消掉落伤害
        }
    }
}
```

### 5.4 Event 基类方法

| 方法 | 用处 |
|---|---|
| `getEventName()` | 事件类名 |
| `isCancelled()` | 是否被取消（非 Cancellable 事件调用会抛异常） |
| `setCancelled($value=true)` | 取消/恢复事件（仅 Cancellable 事件） |
| `getHandlers()` | 获取 HandlerList |

### 5.5 事件分类与常用事件

| 分类 | 目录 | 常用事件 |
|---|---|---|
| 玩家 | `event\player\` | `PlayerJoinEvent`（加入）、`PlayerQuitEvent`（退出）、`PlayerPreLoginEvent`（登录前）、`PlayerLoginEvent`（登录）、`PlayerChatEvent`（聊天）、`PlayerCommandPreprocessEvent`（命令）、`PlayerInteractEvent`（交互）、`PlayerMoveEvent`（移动）、`PlayerDropItemEvent`（丢物品）、`PlayerDeathEvent`（死亡）、`PlayerRespawnEvent`（重生）、`PlayerKickEvent`（被踢）、`PlayerGameModeChangeEvent`（模式改变）、`PlayerItemHeldEvent`（手持切换）、`PlayerBucketFillEvent`/`PlayerBucketEmptyEvent`（桶） |
| 实体 | `event\entity\` | `EntityDamageEvent`（受伤）、`EntityDamageByEntityEvent`（被实体攻击）、`EntityDamageByBlockEvent`、`EntityDeathEvent`（死亡）、`EntitySpawnEvent`（生成）、`EntityDespawnEvent`（消失）、`EntityTeleportEvent`（传送）、`EntityMoveEvent`（移动）、`EntityExplodeEvent`（爆炸）、`EntityRegainHealthEvent`（回复）、`EntityLevelChangeEvent`（换世界）、`EntityShootBowEvent`（射箭） |
| 方块 | `event\block\` | `BlockBreakEvent`（破坏）、`BlockPlaceEvent`（放置）、`BlockUpdateEvent`（更新）、`BlockSpreadEvent`（蔓延）、`SignChangeEvent`（写告示牌） |
| 世界 | `event\level\` | `LevelLoadEvent`、`LevelInitEvent`、`LevelUnloadEvent`、`ChunkLoadEvent`、`ChunkPopulateEvent`、`ChunkUnloadEvent`、`SpawnChangeEvent`、`WeatherChangeEvent` |
| 背包 | `event\inventory\` | `InventoryOpenEvent`、`InventoryCloseEvent`、`InventoryTransactionEvent`（物品交易）、`InventoryPickupItemEvent`、`CraftItemEvent`（合成）、`FurnaceSmeltEvent`（熔炼） |
| 服务器 | `event\server\` | `ServerCommandEvent`（执行命令）、`RemoteServerCommandEvent`、`QueryRegenerateEvent`（列表刷新） |
| 插件 | `event\plugin\` | `PluginEnableEvent`、`PluginDisableEvent` |
| 网络 | `event\server\DataPacketSendEvent` / `DataPacketReceiveEvent` | 拦截数据包收发 |

> 每个事件都有对应的 getter，例如 `PlayerJoinEvent::getPlayer()`、`EntityDamageEvent::getEntity()`、`getDamage()`、`setDamage()`、`BlockBreakEvent::getBlock()` 等。所有 `player` 分类事件通常提供 `getPlayer()`。

---

### 5.6 本版本事件完整清单（源码实测）

> 以下为 1.0.0 源码中实际存在的事件，按命名空间分类（`✔` 表示实现 `Cancellable` 可取消）。

**(root)**: Event(-)、EventPriority(-)、HandlerList(-)、LevelTimings(-)、TextContainer(-)、Timings(-)、TimingsHandler(-)、TranslationContainer(TextContainer)

**block**: BlockBreakEvent(BlockEvent) ✔、BlockBurnEvent(BlockEvent) ✔、BlockEvent(Event)、BlockFormEvent(BlockGrowEvent) ✔、BlockGrowEvent(BlockEvent) ✔、BlockPlaceEvent(BlockEvent) ✔、BlockSpreadEvent(BlockFormEvent) ✔、BlockUpdateEvent(BlockEvent) ✔、ItemFrameDropItemEvent(BlockEvent) ✔、LeavesDecayEvent(BlockEvent) ✔、SignChangeEvent(BlockEvent) ✔

**entity**: CreeperPowerEvent(EntityEvent) ✔、EntityArmorChangeEvent(EntityEvent) ✔、EntityBlockChangeEvent(EntityEvent) ✔、EntityCombustByBlockEvent(EntityCombustEvent)、EntityCombustByEntityEvent(EntityCombustEvent)、EntityCombustEvent(EntityEvent) ✔、EntityDamageByBlockEvent(EntityDamageEvent)、EntityDamageByChildEntityEvent(EntityDamageByEntityEvent)、EntityDamageByEntityEvent(EntityDamageEvent)、EntityDamageEvent(EntityEvent) ✔、EntityDeathEvent(EntityEvent)、EntityDespawnEvent(EntityEvent)、EntityDrinkPotionEvent(EntityEvent) ✔、EntityEatBlockEvent(EntityEatEvent) ✔、EntityEatEvent(EntityEvent) ✔、EntityEatItemEvent(EntityEatEvent)、EntityEffectAddEvent(EntityEvent) ✔、EntityEffectRemoveEvent(EntityEvent) ✔、EntityEvent(Event)、EntityExplodeEvent(EntityEvent) ✔、EntityGenerateEvent(EntityEvent) ✔、EntityInventoryChangeEvent(EntityEvent) ✔、EntityLevelChangeEvent(EntityEvent) ✔、EntityMotionEvent(EntityEvent) ✔、EntityRegainHealthEvent(EntityEvent) ✔、EntityShootBowEvent(EntityEvent) ✔、EntitySpawnEvent(EntityEvent)、EntityTeleportEvent(EntityEvent) ✔、ExplosionPrimeEvent(EntityEvent) ✔、ItemDespawnEvent(EntityEvent) ✔、ItemSpawnEvent(EntityEvent)、ProjectileHitEvent(EntityEvent)、ProjectileLaunchEvent(EntityEvent) ✔

**inventory**: CraftItemEvent(Event) ✔、FurnaceBurnEvent(BlockEvent) ✔、FurnaceSmeltEvent(BlockEvent) ✔、InventoryCloseEvent(InventoryEvent)、InventoryEvent(Event)、InventoryOpenEvent(InventoryEvent) ✔、InventoryPickupArrowEvent(InventoryEvent) ✔、InventoryPickupItemEvent(InventoryEvent) ✔、InventoryTransactionEvent(Event) ✔

**level**: ChunkEvent(LevelEvent)、ChunkLoadEvent(ChunkEvent)、ChunkPopulateEvent(ChunkEvent)、ChunkUnloadEvent(ChunkEvent) ✔、LevelEvent(Event)、LevelInitEvent(LevelEvent)、LevelLoadEvent(LevelEvent)、LevelSaveEvent(LevelEvent)、LevelUnloadEvent(LevelEvent) ✔、SpawnChangeEvent(LevelEvent)、WeatherChangeEvent(LevelEvent) ✔

**player**: PlayerAchievementAwardedEvent(PlayerEvent) ✔、PlayerAnimationEvent(PlayerEvent) ✔、PlayerBedEnterEvent(PlayerEvent) ✔、PlayerBedLeaveEvent(PlayerEvent)、PlayerBucketEmptyEvent(PlayerBucketEvent)、PlayerBucketEvent(PlayerEvent) ✔、PlayerBucketFillEvent(PlayerBucketEvent)、PlayerChatEvent(PlayerEvent) ✔、PlayerCommandPreprocessEvent(PlayerEvent) ✔、PlayerCreationEvent(Event)、PlayerDeathEvent(EntityDeathEvent)、PlayerDropItemEvent(PlayerEvent) ✔、PlayerEvent(Event)、PlayerExhaustEvent(PlayerEvent) ✔、PlayerExperienceChangeEvent(PlayerEvent) ✔、PlayerFishEvent(PlayerEvent) ✔、PlayerGameModeChangeEvent(PlayerEvent) ✔、PlayerGlassBottleEvent(PlayerEvent) ✔、PlayerHungerChangeEvent(PlayerEvent) ✔、PlayerInteractEvent(PlayerEvent) ✔、PlayerItemConsumeEvent(PlayerEvent) ✔、PlayerItemHeldEvent(PlayerEvent) ✔、PlayerJoinEvent(PlayerEvent)、PlayerKickEvent(PlayerEvent) ✔、PlayerLoginEvent(PlayerEvent) ✔、PlayerMoveEvent(PlayerEvent) ✔、PlayerPickupExpOrbEvent(PlayerEvent) ✔、PlayerPreLoginEvent(PlayerEvent) ✔、PlayerQuitEvent(PlayerEvent)、PlayerRespawnEvent(PlayerEvent)、PlayerTextPreSendEvent(PlayerEvent) ✔、PlayerToggleFlightEvent(PlayerEvent) ✔、PlayerToggleSneakEvent(PlayerEvent) ✔、PlayerToggleSprintEvent(PlayerEvent) ✔、PlayerUseFishingRodEvent(PlayerEvent) ✔

**player/cheat**: PlayerCheatEvent(PlayerEvent)、PlayerIllegalMoveEvent(PlayerCheatEvent) ✔

**plugin**: PluginDisableEvent(PluginEvent)、PluginEnableEvent(PluginEvent)、PluginEvent(Event)

**server**: DataPacketReceiveEvent(ServerEvent) ✔、DataPacketSendEvent(ServerEvent) ✔、LowMemoryEvent(ServerEvent)、QueryRegenerateEvent(ServerEvent)、RemoteServerCommandEvent(ServerCommandEvent)、ServerCommandEvent(ServerEvent) ✔、ServerEvent(Event)

## 六、命令系统详解

### 6.1 核心接口/类

| 类 | 作用 |
|---|---|
| `pocketmine\command\CommandSender` | 命令发送者接口（玩家、控制台、RCON 都能执行命令） |
| `pocketmine\command\Command` | 命令抽象基类 |
| `pocketmine\command\PluginCommand` | 插件命令类（通过 plugin.yml 自动创建） |
| `pocketmine\command\SimpleCommandMap` | 命令映射表 |
| `pocketmine\command\ConsoleCommandSender` | 控制台发送者 |
| `pocketmine\command\PluginIdentifiableCommand` | 标识命令归属插件的接口 |

### 6.2 CommandSender 接口方法

| 方法 | 用处 |
|---|---|
| `sendMessage($message)` | 发送消息（所有发送者都实现） |
| `getName()` | 发送者名字（玩家名 / "CONSOLE"） |
| `getServer()` | 获取 Server |
| `hasPermission($name)` / `isPermissionSet($name)` | 权限判断 |
| `addAttachment(Plugin, $name, $value)` / `removeAttachment(...)` | 权限附件 |
| `recalculatePermissions()` / `getEffectivePermissions()` | 权限重算 |

### 6.3 在插件中注册命令（两种方式）

**方式一：plugin.yml 定义（推荐）**

```yaml
commands:
  heal:
    description: 恢复满血
    usage: "/heal <player>"
    aliases: [hp]
    permission: myplugin.heal
```

在主类实现 `onCommand`：

```php
public function onCommand(CommandSender $sender, Command $command, $label, array $args){
    switch($command->getName()){
        case "heal":
            $target = isset($args[0]) ? $this->getServer()->getPlayer($args[0]) : ($sender instanceof Player ? $sender : null);
            if($target !== null and $target instanceof Player){
                $target->setHealth($target->getMaxHealth());
                $sender->sendMessage("已治疗 " . $target->getName());
            }else{
                $sender->sendMessage("玩家未找到");
            }
            return true;
    }
    return false;
}
```

**方式二：代码注册**

```php
$cmd = new PluginCommand("mycmd", $this);
$cmd->setDescription("测试命令");
$cmd->setUsage("/mycmd");
$cmd->setExecutor($this);   // 也可 setExecutor 指定实现 CommandExecutor 的对象
$this->getServer()->getCommandMap()->register("myplugin", $cmd);
```

### 6.4 命令执行流程

```
玩家输入 /heal
  → SimpleCommandMap::dispatch($player, "heal ...")
  → 查找到 PluginCommand
  → PluginCommand::execute($player, $label, $args)
     → 检查插件是否启用
     → testPermission() 检查权限（无权限发送 permission-message）
     → $executor->onCommand(...) 调用主类的 onCommand
     → 返回 false 时自动发送 usage 提示
```

### 6.5 控制台相关

| 类/方法 | 用处 |
|---|---|
| `ConsoleCommandSender` | 控制台发送者（服务器内无法直接实例化，通过 `Server::getInstance()->dispatchCommand(new ConsoleCommandSender(), $cmd)` 或由命令系统内部使用） |
| `CommandReader` | 后台命令输入读取线程（服务器主线程循环 `CommandReader::getCommand()` 读取控制台输入） |
| `RemoteConsoleCommandSender` | RCON 远程控制台发送者 |

---

## 七、调度器 Scheduler 详解

调度器用于延迟/循环执行任务，是插件开发的核心之一。通过 `$this->getServer()->getScheduler()` 获取 `ServerScheduler`。

### 7.1 任务类型

| 类 | 用处 |
|---|---|
| `pocketmine\scheduler\Task` | 主线程任务基类（实现 `onRun($currentTick)`） |
| `pocketmine\scheduler\PluginTask` | 关联插件的任务（构造传插件，随插件禁用而取消） |
| `pocketmine\scheduler\CallbackTask` | 回调任务（直接传闭包 `function(){}`，最方便） |
| `pocketmine\scheduler\AsyncTask` | **异步任务**（在独立线程运行，不阻塞主线程，适合 IO/计算） |
| `pocketmine\scheduler\FileWriteTask` | 内置异步写文件任务 |
| `pocketmine\scheduler\GarbageCollectionTask` | 异步 GC 任务 |
| `pocketmine\scheduler\SendUsageTask` | 发送使用统计 |

### 7.2 ServerScheduler 方法

| 方法 | 用处 |
|---|---|
| `scheduleTask(Task $task)` | 下一个 tick 执行一次（立刻） |
| `scheduleDelayedTask(Task $task, $delay)` | 延迟 `$delay` tick 后执行一次（20 tick = 1 秒） |
| `scheduleRepeatingTask(Task $task, $period)` | 每 `$period` tick 循环执行 |
| `scheduleDelayedRepeatingTask(Task $task, $delay, $period)` | 先延迟再循环 |
| `scheduleAsyncTask(AsyncTask $task)` | 提交异步任务 |
| `scheduleAsyncTaskToWorker(AsyncTask $task, $worker)` | 指定 worker 执行异步任务 |
| `getAsyncTaskPoolSize()` / `increaseAsyncTaskPoolSize($newSize)` | 异步池大小 |
| `cancelTask($taskId)` | 按任务 ID 取消 |
| `cancelTasks(Plugin $plugin)` | **取消某插件的全部任务**（插件禁用时自动调用） |
| `cancelAllTasks()` | 取消所有任务 |
| `isQueued($taskId)` | 任务是否在队列中 |
| `mainThreadHeartbeat($currentTick)` | 主线程心跳（内部每 tick 调用） |

### 7.3 任务编写示例

```php
// 方式一：PluginTask + 匿名内部类（PHP 不支持匿名类则用内部类）
$scheduler->scheduleRepeatingTask(new class($this) extends PluginTask {
    public function onRun($currentTick){
        Server::getInstance()->broadcastMessage("第 " . $currentTick . " tick");
    }
}, 20); // 每秒执行一次

// 方式二：CallbackTask（闭包，最简洁）
$scheduler->scheduleDelayedTask(new CallbackTask(function(){
    $this->getServer()->broadcastMessage("5 秒后");
}), 100);

// 方式三：异步任务（不卡主线程）
class MyAsyncTask extends AsyncTask {
    private $playerName;
    public function __construct($playerName){ $this->playerName = $playerName; }
    public function onRun(){
        // 在线程中执行耗时操作
        $this->setResult(file_get_contents("http://example.com/data"));
    }
    public function onCompletion(Server $server){
        // 回到主线程，拿到结果
        $player = $server->getPlayerExact($this->playerName);
        if($player !== null) $player->sendMessage("结果: " . $this->getResult());
    }
}
$scheduler->scheduleAsyncTask(new MyAsyncTask($playerName));
```

### 7.4 Task / AsyncTask 关键方法

| 方法 | 用处 |
|---|---|
| `Task::onRun($currentTick)` | 抽象方法，任务主体逻辑 |
| `Task::onCancel()` | 任务被取消时回调 |
| `Task::getHandler()` / `setHandler($handler)` | 任务处理器（可 `$task->getHandler()->cancel()`） |
| `AsyncTask::onRun()` | 异步执行体 |
| `AsyncTask::onCompletion(Server $server)` | 异步完成后回到主线程回调 |
| `AsyncTask::setResult($result, $serialize=true)` / `getResult()` / `hasResult()` | 异步结果传递 |
| `AsyncTask::isFinished()` / `isCrashed()` | 完成/崩溃状态 |

---

## 八、权限系统详解

### 8.1 权限默认值（PermissionDefault）

```php
Permission::DEFAULT_OP     = "op"      // 仅 OP 有
Permission::DEFAULT_NOT_OP = "notop"   // 仅非 OP 有
Permission::DEFAULT_TRUE   = "true"    // 所有人都有
Permission::DEFAULT_FALSE  = "false"   // 默认没有
```

### 8.2 Permission 类

| 方法 | 用处 |
|---|---|
| `__construct($name, $description=null, $defaultValue=null, array $children=[])` | 创建权限 |
| `getName()` / `getDescription()` / `getDefault()` / `setDefault($value)` | 权限元信息 |
| `addParent($name, $value)` | 添加父权限（如 `myplugin.*` 包含所有子权限） |
| `getChildren()` / `getPermissibles()` | 子权限 / 有该权限的对象 |
| `loadPermissions(array $data, $default=DEFAULT_OP)` | 从数组（plugin.yml permissions）加载权限 |
| `getByName($value)` | 把字符串转成默认值常量 |

### 8.3 Permissible 接口（玩家/实体实现）

| 方法 | 用处 |
|---|---|
| `isPermissionSet($name)` | 是否显式设置过 |
| `hasPermission($name)` | **是否有权限**（最常用） |
| `addAttachment(Plugin, $name=null, $value=null)` | 附加插件权限 |
| `removeAttachment(PermissionAttachment)` | 移除附件 |
| `recalculatePermissions()` | 重算（改 OP 后系统自动调用） |
| `getEffectivePermissions()` | 所有生效权限 |

### 8.4 PermissionAttachment（插件临时权限）

```php
// 给某玩家临时附加权限
$attachment = $player->addAttachment($this, "myplugin.special", true);
// ... 之后移除
$player->removeAttachment($attachment);
```

### 8.5 PluginManager 权限方法

| 方法 | 用处 |
|---|---|
| `addPermission(Permission)` / `removePermission($permission)` | 注册/移除权限 |
| `getPermission($name)` / `getPermissions()` | 查询权限 |
| `getDefaultPermissions($op)` | 获取默认权限列表 |
| `subscribeToPermission($permission, Permissible)` / `unsubscribeFromPermission(...)` | 订阅权限变更通知 |
| `getPermissionSubscriptions($permission)` | 订阅了某权限的所有对象（Server::broadcast 依赖此机制） |

### 8.6 BanList（封禁列表）

通过 `$server->getNameBans()`、`getIPBans()`、`getCIDBans()` 获取。

| 方法 | 用处 |
|---|---|
| `isBanned($name)` | 是否被封禁 |
| `addBan($target, $reason=null, $expires=null, $source=null)` | **添加封禁**（目标、原因、过期时间、封禁者） |
| `add(BanEntry $entry)` | 添加封禁条目 |
| `remove($name)` | 解除封禁 |
| `getEntries()` | 所有封禁条目 |
| `removeExpired()` | 移除已过期封禁 |
| `load()` / `save($flag=true)` | 从文件加载 / 保存 |
| `isEnabled()` / `setEnabled($flag)` | 开关 |

---

## 九、元数据系统详解

给玩家/实体/世界附加自定义数据，随对象生命周期存在。

### 9.1 MetadataStore 方法（实体、玩家、世界各有独立仓库）

| 方法 | 用处 |
|---|---|
| `setMetadata($subject, $metadataKey, MetadataValue $value)` | 附加元数据 |
| `getMetadata($subject, $metadataKey)` | 获取元数据（数组，多个插件的值） |
| `hasMetadata($subject, $metadataKey)` | 是否存在 |
| `removeMetadata($subject, $metadataKey, Plugin $owningPlugin)` | 移除某插件的元数据 |
| `invalidateAll(Plugin $owningPlugin)` | 使某插件的全部元数据失效 |

### 9.2 MetadataValue 抽象类

需要继承实现 `value()` 和 `invalidate()`：

```php
use pocketmine\metadata\MetadataValue;

class FixedMetadataValue extends MetadataValue {
    private $value;
    public function __construct(\pocketmine\plugin\Plugin $owningPlugin, $value){
        parent::__construct($owningPlugin);
        $this->value = $value;
    }
    public function value(){ return $this->value; }
    public function invalidate(){ $this->value = null; }
}
```

### 9.3 使用示例

```php
// 给玩家标记一个自定义数据
$player->setMetadata("myplugin.level", new FixedMetadataValue($this, 100));

// 读取
$meta = $player->getMetadata("myplugin.level");
if(count($meta) > 0){
    $level = $meta[0]->value();
}
```

---

## 十、工具类详解

### 10.1 Config 类（配置读写）

```php
use pocketmine\utils\Config;

// 格式常量
Config::DETECT     = -1   // 根据扩展名自动判断
Config::PROPERTIES = 0    // .properties（键值对）
Config::JSON       = 1    // JSON
Config::YAML       = 2    // YAML
Config::SERIALIZED = 4    // PHP 序列化
Config::ENUM       = 5    // 枚举（每行一个值）
```

| 方法 | 用处 |
|---|---|
| `__construct($file, $type=Config::DETECT, $default=[], &$correct=null)` | 创建配置对象（文件不存在则用默认创建） |
| `get($k, $default=false)` | 获取键值 |
| `set($k, $v=true)` | 设置键值 |
| `exists($k, $lowercase=false)` | 键是否存在 |
| `remove($k)` | 删除键 |
| `getNested($key, $default=null)` | 获取嵌套键（如 `"a.b.c"`） |
| `setNested($key, $value)` | 设置嵌套键 |
| `getAll($keys=false)` | 全部数据（传 true 则只返回键） |
| `setAll($v)` | 批量设置 |
| `save($async=false)` | 保存到文件（可异步） |
| `reload()` | 重新加载 |
| `setDefaults(array $defaults)` | 设置默认值（补充缺失项） |
| `fixYAMLIndexes($str)` | 修正 YAML 索引（静态） |
| 魔术方法 `__get`/`__set`/`__isset`/`__unset` | 可用 `$config->key` 方式访问 |

```php
$config = new Config($this->getDataFolder() . "settings.yml", Config::YAML, [
    "enabled" => true,
    "message" => "Hello"
]);
$config->set("message", "World");
$config->save();
```

### 10.2 TextFormat 类（颜色与格式）

```php
use pocketmine\utils\TextFormat;

TextFormat::BLACK/DARK_BLUE/DARK_GREEN/DARK_AQUA/DARK_RED/DARK_PURPLE/GOLD/GRAY
TextFormat::DARK_GRAY/BLUE/GREEN/AQUA/RED/LIGHT_PURPLE/YELLOW/WHITE
TextFormat::OBFUSCATED/BOLD/STRIKETHROUGH/UNDERLINE/ITALIC/RESET
```

| 方法 | 用处 |
|---|---|
| `clean($string, $removeFormat=true)` | 去除所有颜色代码 |
| `tokenize($string)` | 把带格式字符串拆成数组 |
| `toJSON($string)` | 转成 JSON 格式文本（用于 tellraw） |

```php
$player->sendMessage(TextFormat::GREEN . "生命:" . TextFormat::RED . $player->getHealth());
```

### 10.3 Binary 类（二进制读写）

| 方法 | 用处 |
|---|---|
| `Binary::writeInt($int)` / `readInt($str)` | 读写 32 位整数（大端序） |
| `Binary::writeShort($short)` / `readShort($str)` | 16 位整数 |
| `Binary::writeLong($long)` / `readLong($str)` | 64 位整数 |
| `Binary::writeFloat($float)` / `readFloat($str)` | 单精度浮点 |
| `Binary::writeTriad($triad)` / `readTriad($str)` | 24 位整数 |
| `Binary::writeVarInt($int)` / `readVarInt($str)` | VarInt 压缩整数 |
| `Binary::writeString($str)` / `readString($str)` | 带长度前缀字符串  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |

### 10.4 UUID 类

| 方法 | 用处 |
|---|---|
| `UUID::fromString($uuid)` / `fromData(...)` | 从字符串/数据创建 UUID |
| `UUID::fromBinary($str)` / `fromInteger($integer)` | 从二进制/整数创建  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `getVersion()` / `getVariant()` | 版本/变体  ⚠️本版Genisys源码未提供(来自通用PocketMine API参考) |
| `toString()` | 标准字符串形式 |

---

## 十一、网络层

### 11.1 网络结构

```
客户端(MCPE) ⇄ RakLib (UDP) ⇄ RakLibInterface ⇄ Network ⇄ 数据包分发到各处理器
```

| 类 | 作用 |
|---|---|
| `pocketmine\network\Network` | 网络管理器，转发数据包到各接口 |
| `pocketmine\network\RakLibInterface` | 连接 RakLib 与核心的桥梁 |
| `pocketmine\network\SourceInterface` / `AdvancedSourceInterface` | 网络接口抽象 |
| `pocketmine\network\protocol\DataPacket` | 数据包基类（encode/decode） |
| `pocketmine\network\protocol\BatchPacket` | 批量数据包（压缩） |
| `pocketmine\network\query\QueryHandler` | 局域网列表查询（motd、玩家数） |
| `pocketmine\network\rcon\RCON` | 远程控制台 |
| `pocketmine\network\upnp\UPnP` | 端口映射 |

### 11.2 数据包处理

玩家数据包统一在 `Player::handleDataPacket(DataPacket $packet)` 中按 `switch($packet::NETWORK_ID)` 分发。自定义数据包发送：

```php
$pk = new TextPacket();
$pk->type = TextPacket::TYPE_RAW;
$pk->message = "自定义消息";
$player->dataPacket($pk);      // 发送（自动批量/压缩）
$player->directDataPacket($pk); // 直接发送（不做批处理）
```

拦截数据包事件：`DataPacketReceiveEvent` / `DataPacketSendEvent`。

### 11.3 Synapse（已从核心移除 / 改用 SynapsePM 插件）

> 本版本（1.0.0）已把内置的 Synapse 多服务器互联模块从核心**整体移除**，核心中不再有 `synapse/` 目录。
> 仅保留一个已标记 `@deprecated` 的兼容方法 `Server::isSynapseEnabled()`：判断 **SynapsePM** 插件是否已加载且未禁用。
> 注意：`getSynapse()` 方法在 1.0.0 已**彻底移除**（源码中无此方法定义），`isSynapseEnabled()` 内部仍会尝试调用它并依赖 SynapsePM 插件提供；**不要直接调用 `getSynapse()`**。
>
> 因此本版本**没有** `synapse\Synapse`、`synapse\network\SynapseInterface` 等核心类，也没有 `getDServerMaxPlayers()` 之类的跨服 API。
> 需要多服互联请安装 SynapsePM 插件，不要再依赖核心内置模块。

### 11.3 RakLib（传输层）

| 类 | 作用 |
|---|---|
| `raklib\server\SessionManager` | 会话管理器（处理所有连接） |
| `raklib\server\Session` | 单个连接会话 |
| `raklib\server\ServerHandler` | 主线程与 RakLib 线程通信 |
| `raklib\server\UDPServerSocket` | UDP 套接字 |
| `raklib\protocol\*` | RakNet 各协议数据包 |

---

## 十二、完整插件示例

下面是一个完整的源码插件示例（文件夹格式），整合了配置、命令、事件、任务。

**plugin.yml**

```yaml
name: ExamplePlugin
version: 1.0.0
main: ExamplePlugin\Main
api:
- 3.0.0-ALPHA3
geniapi:
- 3.0.0-ALPHA3
author: Dev
website: http://example.com
prefix: EX
commands:
  hello:
    description: 打招呼
    usage: "/hello <player>"
    aliases: [hi]
    permission: example.hello
    permission-message: "你没有使用该命令的权限"
permissions:
  example.hello:
    default: true
    description: 允许使用 hello 命令
```

**src/ExamplePlugin/Main.php**

```php
<?php

namespace ExamplePlugin;

use pocketmine\command\Command;
use pocketmine\command\CommandSender;
use pocketmine\event\Listener;
use pocketmine\event\player\PlayerChatEvent;
use pocketmine\event\player\PlayerJoinEvent;
use pocketmine\Player;
use pocketmine\plugin\PluginBase;
use pocketmine\scheduler\CallbackTask;
use pocketmine\utils\Config;
use pocketmine\utils\TextFormat;

class Main extends PluginBase implements Listener {

    /** @var Config */
    private $data;

    public function onEnable(){
        $this->getLogger()->info("ExamplePlugin 已启用");

        // 1. 复制默认配置
        $this->saveDefaultConfig();
        $this->data = $this->getConfig();

        // 2. 注册事件监听器（本类即监听器）
        $this->getServer()->getPluginManager()->registerEvents($this, $this);

        // 3. 定时任务：每 5 秒广播一次（通过 getConfig 控制开关）
        $this->getServer()->getScheduler()->scheduleRepeatingTask(new CallbackTask(function(){
            if($this->data->get("broadcast-tip", false)){
                $this->getServer()->broadcastTip(TextFormat::GOLD . "来自 ExamplePlugin 的定时提示");
            }
        }), 100);
    }

    public function onDisable(){
        $this->getLogger()->info("ExamplePlugin 已禁用");
    }

    // ---- 事件监听 ----
    public function onJoin(PlayerJoinEvent $event){
        $player = $event->getPlayer();
        $player->sendMessage(TextFormat::GREEN . "欢迎, " . $player->getName());
        $player->sendTip(TextFormat::AQUA . "欢迎来到服务器");
    }

    public function onChat(PlayerChatEvent $event){
        $msg = $event->getMessage();
        if(strpos($msg, "敏感词") !== false){
            $event->setCancelled(true);  // 屏蔽消息
            $event->getPlayer()->sendMessage(TextFormat::RED . "消息包含敏感词");
        }
    }

    // ---- 命令处理 ----
    public function onCommand(CommandSender $sender, Command $command, $label, array $args){
        switch($command->getName()){
            case "hello":
                // 未指定玩家时给自己发送
                $target = isset($args[0]) ? $this->getServer()->getPlayer($args[0]) : $sender;
                if($target instanceof Player){
                    $target->sendMessage(TextFormat::YELLOW . "你好, " . $target->getName());
                }else{
                    $sender->sendMessage("目标玩家不在线");
                }
                return true;
        }
        return false;
    }
}
```

**resources/config.yml**（可选，会被 saveDefaultConfig 复制）

```yaml
broadcast-tip: true
welcome-message: "欢迎来到我的服务器"
```

### 打包为 Phar

```bash
# 目录结构
# ExamplePlugin/
# ├── plugin.yml
# ├── resources/
# └── src/
php -r "$p=new Phar('ExamplePlugin.phar'); $p->buildFromDirectory('ExamplePlugin/'); $p->setStub('<?php __HALT_COMPILER();');"
# 把生成的 .phar 放入服务器 plugins/ 目录
```

---

## 十三、附录：常用常量表

### 13.1 游戏模式（Player）

| 常量 | 值 |
|---|---|
| `Player::SURVIVAL` | 0 |
| `Player::CREATIVE` | 1 |
| `Player::ADVENTURE` | 2 |
| `Player::SPECTATOR` | 3 |

### 13.2 药水效果（Effect）

常用效果 ID：`Effect::SPEED=1`、`SLOWNESS=2`、`HASTE=3`、`FATIGUE=4`、`STRENGTH=5`、`HEALING=6`、`HARMING=7`、`JUMP=8`、`NAUSEA=9`、`REGENERATION=10`、`RESISTANCE=11`、`FIRE_RESISTANCE=12`、`WATER_BREATHING=13`、`INVISIBILITY=14`、`BLINDNESS=15`、`NIGHT_VISION=16`、`HUNGER=17`、`WEAKNESS=18`、`POISON=19`、`WITHER=20`

### 13.3 常见方块/物品 ID（Item 常量）

见 `pocketmine\item\Item.php` 顶部常量。常用：
`Item::AIR=0`、`STONE=1`、`DIRT=3`、`PLANK=5`、`BEDROCK=7`、`WATER=8`、`LAVA=10`、`SAND=12`、`WOOL=35`、`GLASS=20`、`TNT=46`、`CHEST=54`、`FURNACE=61`、`CRAFTING_TABLE=58`、`TORCH=50`、`IRON_INGOT=265`、`GOLD_INGOT=266`、`DIAMOND=264`、`IRON_SWORD=267`、`DIAMOND_SWORD=276`、`APPLE=260`、`BREAD=297`、`STICK=280`、`REDSTONE=331`、`DIAMOND_BLOCK=57`、`ENCHANTING_TABLE=116`、`SPAWN_EGG=383`

### 13.4 世界时间（Level）

| 常量 | 值 |
|---|---|
| `Level::TIME_DAY` | 0 |
| `Level::TIME_SUNSET` | 12000 |
| `Level::TIME_NIGHT` | 14000 |
| `Level::TIME_SUNRISE` | 23000 |
| `Level::TIME_FULL` | 24000 |

### 13.5 广播频道（Server）

| 常量 | 值 |
|---|---|
| `Server::BROADCAST_CHANNEL_ADMINISTRATIVE` | `pocketmine.broadcast.admin` |
| `Server::BROADCAST_CHANNEL_USERS` | `pocketmine.broadcast.user` |

### 13.6 实体数据属性（Entity）

`Entity::DATA_TYPE_*`：BYTE=0、SHORT=1、INT=2、FLOAT=3、STRING=4、SLOT=5、POS=6、ROTATION=7、LONG=8
`Entity::DATA_*`：FLAGS=0、AIR=1、NAMETAG=2、SHOW_NAMETAG=3、SILENT=4、POTION_COLOR=7、POTION_AMBIENT=8、NO_AI=15
`Entity::DATA_FLAG_*`：ONFIRE=0、SNEAKING=1、RIDING=2、SPRINTING=3、ACTION=4、INVISIBLE=5

---

## 结语

本文档覆盖了 Genisys 核心的调用方式、插件开发全流程以及核心开发所需的每个常用方法与其用处。开发时记住几个要点：

1. **一切从 `Server::getInstance()` 开始**，插件内用 `$this->getServer()`。
2. **事件注册**在 `onEnable()` 中完成，实现 `Listener` 接口，方法名任意、参数为具体事件类。
3. **命令**推荐在 plugin.yml 中声明，处理逻辑写在 `onCommand()`。
4. **定时/异步任务**通过 `getScheduler()` 提交，注意异步任务中不能直接操作玩家/世界对象，用 `onCompletion` 回主线程处理。
5. **保存数据**用 `Config` 类；玩家存档用 `getOfflinePlayerData()` / `saveOfflinePlayerData()`。
6. 修改核心源码（`pocketmine/` 目录）后属于二次开发，请保持 `API_VERSION` 兼容，避免破坏插件生态。
