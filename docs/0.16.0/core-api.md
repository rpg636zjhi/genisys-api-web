# Genisys (PocketMine-MP 分支) 核心改写 API 文档 — 0.16.0

> 适用版本：`VERSION = （CI 编译时写入 git hash）`（代号 `Kyrios`），`API_VERSION = 2.1.0`
> - `const GENISYS_API_VERSION = '1.9.3';`
> 协议 `CURRENT_PROTOCOL = 91`，目标客户端 `v0.16.0.5 alpha`


本文面向**改核心 / 二次开发**：讲清目录结构、`Server::__construct` 启动链路、各类注册锚点（含真实行号）、如何新增方块/实体/Tile/生成器/存档格式/协议包，以及各版本破坏性变更。

## 一、目录结构与模块职责

源码根目录（本仓库 `<ver>/`）下四个顶层目录：

```
<ver>/
├── pocketmine/   # 核心服务器代码（Server/Player/Level/Entity/Item/Block/event/plugin/scheduler/network…）
├── raklib/       # RakNet 协议库（UDP 传输层）
└── spl/          # SPL 扩展库（线程安全日志、类加载器）
```

`pocketmine/` 关键子目录：`command/`、`event/`、`plugin/`、`scheduler/`、`permission/`、`metadata/`、`level/`、`entity/`、`item/`、`block/`、`inventory/`、`network/`、`nbt/`、`tile/`、`math/`、`utils/`、`resources/`。

## 二、Server::__construct 启动链路

入口 `PocketMine.php` 依次：`CompatibleClassLoader` 注册 → `Terminal::init()` → `MainLogger` → `ThreadManager::init()` → `new Server(...)`。**`Server` 构造函数即一切初始化发生之处**，以下是 0.16.0 中 `Server.php` 的关键注册调用与行号（来自源码扫描）：

| 调用 | 用处 | 锚点 |
|---|---|---|
| `Block::init` | 行 1871 | 方块注册表初始化（建立 `Block::$list`），新增方块在此后登记 |
| `Item::init` | 行 1873 | 物品注册表初始化（建立 `Item::$list`），新增物品在此后登记 |
| `LevelProviderManager::addProvider` | 行 1899, 1900, 1903 | 注册存档格式提供者（anvil/mcregion/leveldb） |
| `Generator::addGenerator` | 7 处，行 1907 … 1913 | 注册世界生成器（normal/flat/hell/void 等） |
| `Entity::registerEntity` | 47 处，行 2902 … 2949 | 实体类注册（含全部原版生物/投掷物/矿车） |
| `Tile::registerTile` | 14 处，行 2953 … 2966 | 方块实体（Tile）注册（箱子/熔炉/告示牌等） |


构造函数内被注释/可改的步骤（部分）：

    - L1712: //Crashes unsupported builds without the correct configuration
    - L1888: //set_exception_handler([$this, "exceptionHandler"]);
    - L1964: //$this->logger->info("正在生成地狱 ".$this->netherName);

## 三、注册锚点速查（改核心落点）

| 注册点 | 行号 | 说明 |
|---|---|---|
| `Block::init` | 行 1871 | 方块注册表初始化（建立 `Block::$list`），新增方块在此后登记 |
| `Item::init` | 行 1873 | 物品注册表初始化（建立 `Item::$list`），新增物品在此后登记 |
| `LevelProviderManager::addProvider` | 行 1899, 1900, 1903 | 注册存档格式提供者（anvil/mcregion/leveldb） |
| `Generator::addGenerator` | 7 处，行 1907 … 1913 | 注册世界生成器（normal/flat/hell/void 等） |
| `Entity::registerEntity` | 47 处，行 2902 … 2949 | 实体类注册（含全部原版生物/投掷物/矿车） |
| `Tile::registerTile` | 14 处，行 2953 … 2966 | 方块实体（Tile）注册（箱子/熔炉/告示牌等） |


> 提示：新增内容时，**必须**在对应 `init`/`addProvider`/`addGenerator` 调用之后登记，否则运行时找不到。行号随版本变动，请以本表为准。

## 四、如何新增（核心扩展点）

### 4.1 新增方块

1. 在 `block/` 下新建 `MyBlock.php`，继承 `pocketmine\block\Block` 并实现 `getId()`、`getDamage()`、各回调。
2. 在 `block/Block.php` 顶部加常量，并在 `Block::init`（行 1871）中 `$list[MyBlock::ID] = MyBlock::class;` 登记。

### 4.2 新增物品

1. 在 `item/Item.php` 顶部加 `const MY_ITEM = <id>;`。
2. 如需独立类，在 `Item::init`（行 1873）的 `$list` 中映射。

### 4.3 新增实体

1. 在 `entity/` 下新建类继承 `Entity`（或 `Animal`/`Monster` 等）。
2. 在 `Server::registerEntities()`（47 处，行 2902 … 2949）中追加 `Entity::registerEntity(MyEntity::class);`。

### 4.4 新增 Tile（方块实体）

在 `Server::registerTiles()`（14 处，行 2953 … 2966）中追加 `Tile::registerTile(MyTile::class, "MyTile");`。

### 4.5 新增世界生成器

实现 `pocketmine\level\generator\Generator` 接口，在 `Generator::addGenerator`（7 处，行 1907 … 1913）中登记（如 `Generator::addGenerator(MyGen::class, 'mygen', Generator::PRESET_...);`）。同步在 `level/generator/GeneratorRegisterTask` 中允许该名称。

### 4.6 新增存档格式

实现 `LevelProvider` 接口，在 `LevelProviderManager::addProvider`（行 1899, 1900, 1903）中 `addProvider(MyProvider::class, 'myfmt');` 并在 `pocketmine.yml` 注册。

### 4.7 新增协议包

1. 在 `network/protocol/` 新建 `MyPacket.php` 继承 `DataPacket`，定义 `const NETWORK_ID = <id>;` 与 `encode()/decode()`。
2. 在 `Player::handleDataPacket()` 的 `switch($packet::NETWORK_ID)` 中加入分发分支（0.16.0 协议包共 67 个，如：``AddEntityPacket`、`AddHangingEntityPacket`、`AddItemEntityPacket`、`AddItemPacket`、`AddPaintingPacket`、`AddPlayerPacket`、`AdventureSettingsPacket`、`AnimatePacket`、`AvailableCommandsPacket`、`BatchPacket`、`BlockEntityDataPacket`、`BlockEventPacket`、`ChangeDimensionPacket`、`ChunkRadiusUpdatedPacket`、`CommandStepPacket`、`ContainerClosePacket`、`ContainerOpenPacket`、`ContainerSetContentPacket`、`ContainerSetDataPacket`、`ContainerSetSlotPacket`、`CraftingDataPacket`、`CraftingEventPacket`、`DisconnectPacket`、`DropItemPacket`、`EntityEventPacket`、`ExplodePacket`、`FullChunkDataPacket`、`HurtArmorPacket`、`InteractPacket`、`InventoryActionPacket`、`ItemFrameDropItemPacket`、`LevelEventPacket`、`LevelSoundEventPacket`、`LoginPacket`、`MobArmorEquipmentPacket`、`MobEffectPacket`、`MobEquipmentPacket`、`MoveEntityPacket`、`MovePlayerPacket`、`PlayStatusPacket`、`PlayerActionPacket`、`PlayerInputPacket`、`PlayerListPacket`、`RemoveBlockPacket`、`RemoveEntityPacket`、`ReplaceSelectedItemPacket`、`RequestChunkRadiusPacket`、`ResourcePackClientResponsePacket`、`ResourcePacksInfoPacket`、`RespawnPacket`、`SetCommandsEnabledPacket`、`SetDifficultyPacket`、`SetEntityDataPacket`、`SetEntityLinkPacket`、`SetEntityMotionPacket`、`SetHealthPacket`、`SetPlayerGameTypePacket`、`SetSpawnPositionPacket`、`SetTimePacket`、`SpawnExperienceOrbPacket`、`StartGamePacket`、`StrangePacket`、`TakeItemEntityPacket`、`TextPacket`、`UpdateAttributesPacket`、`UpdateBlockPacket`、`UseItemPacket``）。

## 五、事件派发热点

核心派发集中在以下文件（来自源码扫描，数字为该文件 `callEvent` 次数）：

| 文件 | 派发次数 |
|---|---|

| `Player.php` | 52 |

| `level/Level.php` | 16 |

| `entity/Entity.php` | 9 |

| `inventory/PlayerInventory.php` | 5 |

| `Server.php` | 4 |

| `block/Cauldron.php` | 3 |

| `entity/Human.php` | 3 |

| `entity/Projectile.php` | 3 |

| `inventory/BaseInventory.php` | 3 |

| `block/CocoaBlock.php` | 2 |

| `block/Crops.php` | 2 |

| `block/Fire.php` | 2 |

| `block/Grass.php` | 2 |

| `block/MelonStem.php` | 2 |

| `block/PumpkinStem.php` | 2 |


> 派发总数: 146


### 本版本事件清单（按命名空间）

- **(root)**（8 个，可取消 0）：Event(-)、EventPriority(-)、HandlerList(-)、LevelTimings(-)、TextContainer(-)、Timings(-)、TimingsHandler(-)、TranslationContainer(TextContainer)
- **block**（11 个，可取消 10）：BlockBreakEvent(BlockEvent) ✔、BlockBurnEvent(BlockEvent) ✔、BlockEvent(Event)、BlockFormEvent(BlockGrowEvent) ✔、BlockGrowEvent(BlockEvent) ✔、BlockPlaceEvent(BlockEvent) ✔、BlockSpreadEvent(BlockFormEvent) ✔、BlockUpdateEvent(BlockEvent) ✔、ItemFrameDropItemEvent(BlockEvent) ✔、LeavesDecayEvent(BlockEvent) ✔、SignChangeEvent(BlockEvent) ✔
- **entity**（33 个，可取消 21）：CreeperPowerEvent(EntityEvent) ✔、EntityArmorChangeEvent(EntityEvent) ✔、EntityBlockChangeEvent(EntityEvent) ✔、EntityCombustByBlockEvent(EntityCombustEvent)、EntityCombustByEntityEvent(EntityCombustEvent)、EntityCombustEvent(EntityEvent) ✔、EntityDamageByBlockEvent(EntityDamageEvent)、EntityDamageByChildEntityEvent(EntityDamageByEntityEvent)、EntityDamageByEntityEvent(EntityDamageEvent)、EntityDamageEvent(EntityEvent) ✔、EntityDeathEvent(EntityEvent)、EntityDespawnEvent(EntityEvent)、EntityDrinkPotionEvent(EntityEvent) ✔、EntityEatBlockEvent(EntityEatEvent) ✔、EntityEatEvent(EntityEvent) ✔、EntityEatItemEvent(EntityEatEvent)、EntityEffectAddEvent(EntityEvent) ✔、EntityEffectRemoveEvent(EntityEvent) ✔、EntityEvent(Event)、EntityExplodeEvent(EntityEvent) ✔、EntityGenerateEvent(EntityEvent) ✔、EntityInventoryChangeEvent(EntityEvent) ✔、EntityLevelChangeEvent(EntityEvent) ✔、EntityMotionEvent(EntityEvent) ✔、EntityRegainHealthEvent(EntityEvent) ✔、EntityShootBowEvent(EntityEvent) ✔、EntitySpawnEvent(EntityEvent)、EntityTeleportEvent(EntityEvent) ✔、ExplosionPrimeEvent(EntityEvent) ✔、ItemDespawnEvent(EntityEvent) ✔、ItemSpawnEvent(EntityEvent)、ProjectileHitEvent(EntityEvent)、ProjectileLaunchEvent(EntityEvent) ✔
- **inventory**（9 个，可取消 7）：CraftItemEvent(Event) ✔、FurnaceBurnEvent(BlockEvent) ✔、FurnaceSmeltEvent(BlockEvent) ✔、InventoryCloseEvent(InventoryEvent)、InventoryEvent(Event)、InventoryOpenEvent(InventoryEvent) ✔、InventoryPickupArrowEvent(InventoryEvent) ✔、InventoryPickupItemEvent(InventoryEvent) ✔、InventoryTransactionEvent(Event) ✔
- **level**（11 个，可取消 3）：ChunkEvent(LevelEvent)、ChunkLoadEvent(ChunkEvent)、ChunkPopulateEvent(ChunkEvent)、ChunkUnloadEvent(ChunkEvent) ✔、LevelEvent(Event)、LevelInitEvent(LevelEvent)、LevelLoadEvent(LevelEvent)、LevelSaveEvent(LevelEvent)、LevelUnloadEvent(LevelEvent) ✔、SpawnChangeEvent(LevelEvent)、WeatherChangeEvent(LevelEvent) ✔
- **player**（35 个，可取消 26）：PlayerAchievementAwardedEvent(PlayerEvent) ✔、PlayerAnimationEvent(PlayerEvent) ✔、PlayerBedEnterEvent(PlayerEvent) ✔、PlayerBedLeaveEvent(PlayerEvent)、PlayerBucketEmptyEvent(PlayerBucketEvent)、PlayerBucketEvent(PlayerEvent) ✔、PlayerBucketFillEvent(PlayerBucketEvent)、PlayerChatEvent(PlayerEvent) ✔、PlayerCommandPreprocessEvent(PlayerEvent) ✔、PlayerCreationEvent(Event)、PlayerDeathEvent(EntityDeathEvent)、PlayerDropItemEvent(PlayerEvent) ✔、PlayerEvent(Event)、PlayerExhaustEvent(PlayerEvent) ✔、PlayerExperienceChangeEvent(PlayerEvent) ✔、PlayerFishEvent(PlayerEvent) ✔、PlayerGameModeChangeEvent(PlayerEvent) ✔、PlayerGlassBottleEvent(PlayerEvent) ✔、PlayerHungerChangeEvent(PlayerEvent) ✔、PlayerInteractEvent(PlayerEvent) ✔、PlayerItemConsumeEvent(PlayerEvent) ✔、PlayerItemHeldEvent(PlayerEvent) ✔、PlayerJoinEvent(PlayerEvent)、PlayerKickEvent(PlayerEvent) ✔、PlayerLoginEvent(PlayerEvent) ✔、PlayerMoveEvent(PlayerEvent) ✔、PlayerPickupExpOrbEvent(PlayerEvent) ✔、PlayerPreLoginEvent(PlayerEvent) ✔、PlayerQuitEvent(PlayerEvent)、PlayerRespawnEvent(PlayerEvent)、PlayerTextPreSendEvent(PlayerEvent) ✔、PlayerToggleFlightEvent(PlayerEvent) ✔、PlayerToggleSneakEvent(PlayerEvent) ✔、PlayerToggleSprintEvent(PlayerEvent) ✔、PlayerUseFishingRodEvent(PlayerEvent) ✔
- **plugin**（3 个，可取消 0）：PluginDisableEvent(PluginEvent)、PluginEnableEvent(PluginEvent)、PluginEvent(Event)
- **server**（7 个，可取消 3）：DataPacketReceiveEvent(ServerEvent) ✔、DataPacketSendEvent(ServerEvent) ✔、LowMemoryEvent(ServerEvent)、QueryRegenerateEvent(ServerEvent)、RemoteServerCommandEvent(ServerCommandEvent)、ServerCommandEvent(ServerEvent) ✔、ServerEvent(Event)

## 六、网络层与协议

- 链路：`客户端(MCPE) ⇄ RakLib(UDP) ⇄ RakLibInterface ⇄ Network ⇄ 数据包分发`

- 协议号：`CURRENT_PROTOCOL = 91`（v0.16.0.5 alpha 网络版本 `0.16.0.5`）。协议包定义见 `pocketmine/network/protocol/Info.php`。

- 数据包收发可被插件用 `DataPacketReceiveEvent` / `DataPacketSendEvent` 拦截。

- 自定义数据包：参考 §四.4.7。Synapse 已在 0.16.0 从核心移除——核心 `synapse/` 目录已不存在；仅保留 `@deprecated` 的 `Server::getSynapse()` / `isSynapseEnabled()` 转调 **SynapsePM** 插件。

## 七、版本破坏性变更速记

> - `API_VERSION=2.1.0`、`GENISYS_API_VERSION=1.9.3`；新增 `PlayerToggleFlightEvent`、`EntityEffectAddEvent`/`EntityEffectRemoveEvent`、大量 0.16 协议包（如 `AvailableCommandsPacket`、`LevelSoundEventPacket`）。


---

## 附：与 0.14.3 基准的差异（事件/协议包）

- 新增事件：EntityDrinkPotionEvent、EntityEffectAddEvent、EntityEffectRemoveEvent、PlayerToggleFlightEvent

- 缺失事件：EntityMoveEvent、PlayerTransferEvent

- 新增协议包：AddHangingEntityPacket、AddItemPacket、AvailableCommandsPacket、ChunkRadiusUpdatedPacket、CommandStepPacket、InventoryActionPacket、LevelSoundEventPacket、ReplaceSelectedItemPacket、ResourcePackClientResponsePacket、ResourcePacksInfoPacket、SetCommandsEnabledPacket、SpawnExperienceOrbPacket

- 移除协议包：ChunkRadiusUpdatePacket、RemovePlayerPacket
