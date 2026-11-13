# ForbiddenItlwm：portable-rx-p1 空投优化分支

本分支基于 [retropineaple/ForbiddenItlwm](https://github.com/retropineaple/ForbiddenItlwm) 的 `aa707a7afcd4eda793e0d9ffa7ee7d515cb2294e`，整理本地完成并实机验证的 AWDL 优化。保留原项目历史与许可证；[上游原始说明](UPSTREAM_README.md)单独保留。

**当前是带已知问题的候选版，不是稳定版。** 文件互传和速度优化已经落地；原生 Mac 关闭重开 Finder 后偶发完全看不到本机的问题仍未修复。本期保留当前版本，发现故障与跨信道发送等待留到后续迭代。

下载已编译驱动请进入 **[Release 发布页](https://github.com/WarnerATCN/ForbiddenItlwm/releases/tag/portable-rx-p1-25G332)**，选择 `ForbiddenItlwm-portable-rx-p1-Tahoe-25G332.zip`。安装包内含完整 Kext；发布页提供安装步骤、启动参数与回滚指引，另有独立中文安装说明。GitHub 的 Source code ZIP 仅为源码。

- 本期版本标识：`forbidden-portable-rx-p1`
- 已实测：macOS 26.7.2（25G332）、Intel Wi-Fi PCI `8086:7A70`，与同一台 iPhone、原生 Mac 互传
- 预编译包：只针对 Tahoe x86_64；没有据此认证其他系统版本或全部 Intel 网卡
- 驱动 UUID：`09066205-14A9-3002-86AB-89ED5A03DC7D`
- 执行文件 SHA-256：`6fb37220dd18c20911ae55150633c84745330955645cd365d90a5c835a0be482`

## 项目来源

| 层次 | 来源 | 本分支的关系 |
|---|---|---|
| Intel Wi-Fi 驱动基础 | [OpenIntelWireless/itlwm](https://github.com/OpenIntelWireless/itlwm)、laobamac 的 Tahoe/Sequoia AirportItlwm，以及 OpenBSD iwx/iwm/iwn | 继承原驱动与平台适配，不是从零实现 |
| AWDL / AirDrop 基础 | [retropineaple/ForbiddenItlwm](https://github.com/retropineaple/ForbiddenItlwm)，基线 `aa707a7` | 继承原生 AWDL 接口、并行 Wi-Fi 监听、80 MHz/VHT、Block Ack 聚合等能力 |
| 通用区域信道思路 | 上游 [PR #21](https://github.com/retropineaple/ForbiddenItlwm/pull/21)，参考头提交 `db25e6dcd65e63e84130c16a012d6795b81fee5a` | 整合区域回退，并补充宽带边界与接收窗口换信道保护 |
| 本地增量 | 本分支的提交、回归测试和验证记录 | 短包接收窗口、受限单帧速率策略、空闲对端接替、诊断及构建完整性检查 |

蓝牙补丁、原生 Mac 的系统服务以及 Apple 的账户/发现协议不是本 Wi-Fi 分支重新实现的部分。没有加入账户绕过、联系人哈希合并、国家码伪装或后台自动重启服务。

## 本期新增与保留的优化

1. **短 TCP 控制包接收窗口。** 对已知 AWDL 对端的短 SYN/非空小数据，在归属明确的成功发送完成后，允许约250 ms的受限接收窗口；重复请求不能延长窗口，至少1秒冷却。限制为实际相同的基础网络/监听主信道、安静时段及当前生命周期；保留软件地址、BSSID和格式隔离。默认开启，支持只读检查和 root 调试关闭。
2. **窗口恢复及换信道约束。** 失败的打开/关闭仍保留恢复义务，下一轮重试；描述符与窗口绑定实际发送信道、generation和listener token，旧149事件不能在44上继续生效。
3. **单帧发送策略。** 对受条件限制的 AWDL 单播单帧使用已验证的 legacy 24 Mbps策略；聚合包保留固件速率控制，普通 Wi-Fi 速率不由该策略固定。
4. **空闲接收对端接替。** 已知新对端的 ADDBA 请求可以在旧对端充分空闲、队列和控制工作排空后接替，改善手机与原生 Mac 交替发送。它不等同于修复蓝牙发现。
5. **同信道管理回复探针。** 结合原有聚合协商，在严格条件下短时允许管理回复，并恢复接收过滤；通过 `-itlawdlcoexsamechprobe`启用。
6. **通用信道保护。** 优先使用固件允许的149/80；不能使用时，按对端实际序列考虑合法44/80或44/20，最后回退6/20。检查完整带宽块、DFS/NOADHOC/被动信道条件及真实国家变更；修正80+80有效副中心重叠和错误80 MHz中心提示。
7. **构建与诊断。** 补充头文件依赖记录、干净构建/布局核对，以及接收阶段、队列、Block Ack和恢复计数。诊断本身不代表问题已修复。

本分支保留但**默认关闭**的短控制包站点选择/接替实验，没有在有效对照中证明额外收益，不作为本期已验证优化推广。

## 当前速度

同一个247,636,698字节文件，系统记录的文件阶段耗时换算为十进制MB/s，包含协议开销，不是PHY速率；每项均确认完成。基础网络信道与 AWDL 信道分开记录。

| 基础网络 | AWDL | 方向 | 平均速度 | 证据与条件 |
|---|---|---|---:|---|
|149 / 80 MHz|149 / 80 MHz|本机→iPhone|30.8 MB/s|重启后的首笔；AWDL完整文件字节量；抓包开启|
|149 / 80 MHz|149 / 80 MHz|iPhone→本机|31.8 MB/s|AWDL完整文件；SHA-256一致|
|149 / 80 MHz|149 / 80 MHz|原生Mac→本机|20.7 MB/s|AWDL完整文件；SHA-256一致|
|149 / 80 MHz|149 / 80 MHz|本机→原生Mac|16.9 MB/s|AWDL完整文件；接收端确认完成|
|149 / 80 MHz|149 / 80 MHz|本机→iPhone|29.4 MB/s|未启用抓包；手机临时断开路由器但Wi-Fi开启，确保走AWDL|
|36 / 80 MHz|149 / 80 MHz|本机→iPhone|7.2 MB/s|同样未抓包、手机临时断开路由器；AWDL完整文件|
|36 / 80 MHz|149 / 80 MHz|iPhone→本机|22.1 MB/s|未抓包；AWDL完整文件；SHA-256一致|

另一次未抓包、双方正常连路由器的普通使用复测为18.6 MB/s，系统选择了普通Wi-Fi局域网路径；**这笔没有计入AWDL性能证明**。上述是本机观测值，不是所有国家、网卡、手机或射频环境的速度承诺。详见[测试说明](docs/PORTABLE-RX-VALIDATION.zh-CN.md)。

## 部署与参数

完整条件、OpenCore步骤、回滚和蓝牙方案区别见[部署文档](docs/PORTABLE-RX-INSTALL.zh-CN.md)。本分支只提供Wi-Fi驱动，不包含个人EFI、账户信息、原始日志或抓包。

本期Wi-Fi启动参数：

```text
-itlawdlcoexprobe -itlawdliface -itlawdlnativeup -itlawdlcoexrx -itlawdlcoextx -itlawdlcoexmulti -itlawdlcoexdata -itlawdlmitx -itlawdlelicit -itlawdlcaps -itlawdlsvcmerge -itlawdlawsync itlawdlintcoal=4 -itlawdlcoexbatx -itlawdlcoexpeerpause -itlawdlcoexbatrace itlawdltxqueue=4096 -itlawdlcoexsamechprobe
```

默认运行参数，无需启动后再写入：

```text
debug.forbidden_awdl_control_rx = 1
debug.forbidden_awdl_control_peer = 0
debug.forbidden_awdl_single_legacy = 1
debug.forbidden_awdl_peer_handoff = 1
```

`-btleadv`与`-btlfxadvsets`属于不同蓝牙方案，不能因为本README列出了Wi-Fi参数，就随意混用蓝牙补丁。本文实测保留了原有可用的蓝牙组合，未新增BTLEAdvFixup。详见部署文档。

## 已知问题与下期工作

- **发现故障未修复。** 十分钟空闲观察中276次端口采样均正常，但随后原生Mac关闭重开Finder，仍可能完全看不到本机。因此没有通过最终发现稳定性验收。
- 临时切换本机Finder中的“允许这些人发现我”：不允许任何人→所有人，曾能恢复可见；这只是临时恢复，不是永久修复。
- **偶发同名重复条目。** 曾有两个条目指向同一本机无线地址和接收端口，且两个均能收文件。清理与身份生命周期仍需处理。
- **跨信道发送等待。** 在AP36/AWDL149的发送样本中，较长时间处于聚合握手等待；握手完成后连续采样可达约30～40 MB/s。需要后续核对超时退避策略，而不是直接放宽信道权限。
- 建连/许可阶段仍有波动；文件阶段速度与前期等待必须分开看，不能用单次快连接证明所有场景都已解决。
- 44信道区域回退、80+80边界和其他系统/硬件尚未做对应地区实机验证；静态回归通过不等于全部国家硬件认证。

## 构建与校验

```bash
git clone https://github.com/acidanthera/MacKernelSDK.git MacKernelSDK
python3 tools/build.py --target tahoe --out build -j 8
codesign --force --sign - --timestamp=none build/ForbiddenItlwm.kext
codesign --verify --strict build/ForbiddenItlwm.kext
python3 tools/abi/audit_vtable.py --target tahoe --build build --out build --lifecycle-overrides
python3 tools/abi/check_allocation_layout.py build/ForbiddenItlwm.kext/Contents/MacOS/ForbiddenItlwm --output build/hal-layout.json
python3 tools/abi/check_awdl_allocation.py build/ForbiddenItlwm.kext/Contents/MacOS/ForbiddenItlwm build/awdl-layout.json
```

MacKernelSDK按上游已验证的`3f75008`检出；完整构建说明见部署文档。不同输出路径/工具链重建后UUID和哈希会变化，不能声称自动等同于本期发布二进制。新增回归测试：`python3 tests/portable_rx/run.py`；说明见[测试目录](tests/portable_rx/README.md)。

## 许可证与致谢

保留[原项目许可证](LICENSE)和上游版权信息。完整上游致谢见[原始README](UPSTREAM_README.md#credits)。本分支基于上游成果与本地硬件观测进行增量开发，不把继承的AWDL、VHT或聚合实现声称为从零原创。
