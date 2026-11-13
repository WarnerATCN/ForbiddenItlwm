# portable-rx-p1 / Tahoe 25G332 候选包

基于 retropineaple/ForbiddenItlwm `aa707a7` 的本地增量版本。**本发布为 Pre-release：文件互传已实测可用，但发现稳定性验收未通过，修复留待后续。**

## 下载与安装

下载下面的预编译包即可取得 `ForbiddenItlwm.kext`，**不要把 GitHub 自动生成的 Source code ZIP 当成驱动安装包**。

- [下载 Kext 安装包（约15.4 MB）](https://github.com/WarnerATCN/ForbiddenItlwm/releases/download/portable-rx-p1-25G332/ForbiddenItlwm-portable-rx-p1-Tahoe-25G332.zip)
- [下载中文安装说明](https://github.com/WarnerATCN/ForbiddenItlwm/releases/download/portable-rx-p1-25G332/INSTALL-portable-rx-p1.zh-CN.md)
- [下载 SHA256SUMS.txt](https://github.com/WarnerATCN/ForbiddenItlwm/releases/download/portable-rx-p1-25G332/SHA256SUMS.txt)
- [在线阅读完整部署文档](https://github.com/WarnerATCN/ForbiddenItlwm/blob/awdl-portable-rx-p1/docs/PORTABLE-RX-INSTALL.zh-CN.md)

### 安装前提

本包只针对 **Intel Mac / 黑苹果 x86_64、macOS Tahoe** 构建，已实测 macOS **26.7.2（25G332）、Intel Wi-Fi PCI 8086:7A70（AX211）**。其他系统版本或网卡没有由本次测试认证；Sequoia/Sonoma 不应直接使用这个 Tahoe 包。

需要可用的 OpenCore、系统原生 IO80211Family/IOSkywalkFamily、正常的 Intel Wi-Fi DMA 映射，以及已经适配当前系统的蓝牙 BLE 广播/扫描方案。**蓝牙 Kext 不在 Wi-Fi ZIP 内，同页现已提供独立蓝牙配套包**；本机使用的定制 BlueToolFixup 与上游 BTLEAdvFixup 是不同方案，不能混用。完整条件见部署文档。

### OpenCore 安装步骤

1. 备份完整可启动 EFI，优先用备用 USB EFI 测试；记录原 Wi-Fi 驱动和启动参数。
2. 将安装包与 `SHA256SUMS.txt` 放在同一目录，运行 `shasum -a 256 -c SHA256SUMS.txt`，确认 ZIP 项输出 `OK`。
3. 解压，把 **完整的** `ForbiddenItlwm.kext` 文件夹复制到 `EFI/OC/Kexts/`，不要只复制其执行文件。
4. 在 `config.plist → Kernel → Add` 中启用该 Kext：`BundlePath=ForbiddenItlwm.kext`、`ExecutablePath=Contents/MacOS/ForbiddenItlwm`、`PlistPath=Contents/Info.plist`、`Enabled=true`、`Arch=x86_64`、`MinKernel=25.0.0`、`MaxKernel=25.99.99`。同时停用旧 AirportItlwm/itlwm，避免重复加载。
5. 在 `NVRAM → Add → 7C436110-AB2A-4BBB-A880-FE41995C9F82 → boot-args` 中加入下列本期 Wi-Fi 参数，保留原有其他参数；蓝牙参数按自己的完整方案配置。
6. 用匹配版本的 `ocvalidate` 检查配置，手动重启，正常连接 Wi-Fi。不要额外混入 OCLP 的旧无线栈替换补丁。

```text
-itlawdlcoexprobe -itlawdliface -itlawdlnativeup -itlawdlcoexrx -itlawdlcoextx -itlawdlcoexmulti -itlawdlcoexdata -itlawdlmitx -itlawdlelicit -itlawdlcaps -itlawdlsvcmerge -itlawdlawsync itlawdlintcoal=4 -itlawdlcoexbatx -itlawdlcoexpeerpause -itlawdlcoexbatrace itlawdltxqueue=4096 -itlawdlcoexsamechprobe
```

这是本期实测配置，包含诊断项，并非已精简的最小参数集合。四个运行默认值 `control_rx/control_peer/single_legacy/peer_handoff` 为 **1/0/1/1**，无需每次开机手动写入 sysctl。

### 开始使用与核验

打开 Wi-Fi 和蓝牙，正常连接网络，在 Finder 打开“隔空投送”，按需求选择接收范围；测试时可临时用“所有人”，测试后恢复自己的接收设置。手机保持亮屏解锁，分别验证发送和接收。

```bash
sw_vers -buildVersion
kmutil showloaded --list-only | grep -E 'ForbiddenItlwm|AirportItlwm'
ifconfig awdl0
sysctl debug.forbidden_awdl_control_rx debug.forbidden_awdl_control_peer debug.forbidden_awdl_single_legacy debug.forbidden_awdl_peer_handoff
```

应加载 ForbiddenItlwm、存在 awdl0、四项值为1/0/1/1，且不同时加载旧 AirportItlwm。149/80 MHz 在当地允许且固件认可时有较好表现；**无需把所有国家的路由器都强制改成149**。44/6合法回退尚需更多实机验证。

若偶发看不到本机，可尝试在本机 Finder 把“不允许任何人”切回“所有人”；这只是临时恢复。若无法正常启动或 Wi-Fi 异常，从备份 EFI 启动并恢复旧 Wi-Fi Kext、Kernel/Add 和原 Wi-Fi 参数。无需更改无关蓝牙、账户或 SMBIOS。

## AX211 蓝牙配套包

现补充发布本机已实测的蓝牙组合，Wi-Fi ZIP 和已验证二进制不变：

- [蓝牙 Kext 包：AX211-Bluetooth-Tahoe-25G332-mask-fix2.zip](https://github.com/WarnerATCN/ForbiddenItlwm/releases/download/portable-rx-p1-25G332/AX211-Bluetooth-Tahoe-25G332-mask-fix2.zip)
- [对应源码包：AX211-Bluetooth-Sources-mask-fix2.zip](https://github.com/WarnerATCN/ForbiddenItlwm/releases/download/portable-rx-p1-25G332/AX211-Bluetooth-Sources-mask-fix2.zip)
- [蓝牙包 SHA-256 清单](https://github.com/WarnerATCN/ForbiddenItlwm/releases/download/portable-rx-p1-25G332/Bluetooth-SHA256SUMS.txt)
- [蓝牙安装、来源及完整使用说明](https://github.com/WarnerATCN/ForbiddenItlwm/blob/awdl-portable-rx-p1/docs/AX211-BLUETOOTH.zh-CN.md)

包含 Lilu 1.7.2 RELEASE、IntelBluetoothFirmware 2.5.2、IntelBTPatcher 2.5.2、BlueToolFixup 2.7.3 **Tahoe-mask-fix2 定制版**。Intel 两个组件与上游原包一致；本地修改的是 BlueToolFixup 的 Tahoe 相对位移匹配和 Lilu 查找字节规范化。四个 UUID 均与本机当前加载版本一致，具体文件哈希见包内 manifest。

本套需添加 `-btlfxadvsets`，Lilu 先于插件、IntelBluetoothFirmware 先于 IntelBTPatcher 加载；保留 IntelBTPatcher，停用 BTLEAdvFixup，不混入 `-btleadv`，Tahoe 不加载旧 IntelBluetoothInjector。已验证 macOS26.7.2/25G332、AX211；其他 build/控制器未认证。蓝牙包不等于发现故障修复，也不是可直接替换整机 EFI 的套件。

## 内容

- Wi-Fi ZIP：本期驱动 `ForbiddenItlwm.kext`；蓝牙为独立配套 ZIP。均不含个人EFI。
- 默认：短TCP接收窗口1、短控制对端实验0、单帧legacy策略1、空闲接收对端接替1。
- 保留区域合法性约束，整合44回退与宽带边界保护；不伪造国家、不放宽固件信道权限。
- 本分支README、部署参数、验证方法及去标识化结果摘要。

## 本机实测

macOS26.7.2（25G332）、Intel PCI8086:7A70，参考文件247,636,698字节。

| 方向/条件 | 文件阶段平均MB/s |
|---|---:|
| 本机→iPhone，AP149/AWDL149 |30.8|
| iPhone→本机，AP149/AWDL149 |31.8|
| 原生Mac→本机，AP149/AWDL149 |20.7|
| 本机→原生Mac，AP149/AWDL149 |16.9|
| 本机→iPhone，AP149/AWDL149、无BPF、手机断开路由器 |29.4|
| 本机→iPhone，AP36/AWDL149、无BPF、手机断开路由器 |7.2|
| iPhone→本机，AP36/AWDL149、无BPF、手机断开路由器 |22.1|

完整接收文件哈希一致。另一笔18.6MB/s普通使用数据选择了局域网路径，不计入AWDL性能。测量为应用文件阶段平均，包含协议开销。

## 已知问题

1. 原生Mac关闭重开Finder后，仍可能完全看不到本机；十分钟端口观察正常不能替代实际发现验收。
2. 偶发两个同名可用条目，解析到同一本机端点。临时切换发现权限曾恢复可见，但不是永久修复。
3. AP36/AWDL149发送可能有较长聚合协商等待，后续再处理。
4. 44回退、80+80边界有静态回归，未在对应国家/全部硬件做实机认证。

## 版本核对

- Marker：`forbidden-portable-rx-p1`
- UUID：`09066205-14A9-3002-86AB-89ED5A03DC7D`
- 执行文件SHA-256：`6fb37220dd18c20911ae55150633c84745330955645cd365d90a5c835a0be482`
- 包含的签名二进制已由发布源码树干净重建并逐文件复现。

安装前先阅读本分支部署文档。蓝牙BLE兼容属于独立前提，本期发布不包含完整跨机型一键EFI。原项目上游安装文档的BTLEAdvFixup组合不能与本机定制BlueToolFixup组合随意混用。
