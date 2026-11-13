# AX211 蓝牙配套包：Tahoe 25G332 / mask-fix2

这是与本分支 Wi-Fi 候选版一起实测过的蓝牙组合，独立于 Wi-Fi ZIP 发布。只包含驱动、说明、许可证和校验清单，不包含个人 EFI、config.plist、USB 映射、账户或日志。发现偶发不可见、同名重复等问题仍未解决；这个蓝牙包不代表发现稳定性已经修复。

## 下载

在 [portable-rx-p1 发布页](https://github.com/WarnerATCN/ForbiddenItlwm/releases/tag/portable-rx-p1-25G332) 下载：

- `AX211-Bluetooth-Tahoe-25G332-mask-fix2.zip`：四个完整 Kext 和安装说明。
- `AX211-Bluetooth-Sources-mask-fix2.zip`：对应定制 BlueToolFixup 源码、Xcode 工程、修改补丁，以及 IntelBluetoothFirmware v2.5.2 完整上游源码归档。
- `Bluetooth-SHA256SUMS.txt`：两个 ZIP 的 SHA-256。

与 Wi-Fi 配套时，另取同页 `ForbiddenItlwm-portable-rx-p1-Tahoe-25G332.zip`。两包分别安装，不能用蓝牙包代替 Wi-Fi Kext。

## 来源与修改情况

| 组件 | 本包版本 | 来源 / 修改情况 |
|---|---|---|
| Lilu |1.7.2 RELEASE|[acidanthera/Lilu](https://github.com/acidanthera/Lilu/tree/1.7.2)，沿用本机当前加载构建，未在本期改动|
| IntelBluetoothFirmware |2.5.2 RELEASE|[lshbluesky v2.5.2](https://github.com/lshbluesky/IntelBluetoothFirmware/releases/tag/v2.5.2)，继承 OpenIntelWireless；与上游 Release 包逐文件一致，无本地修改|
| IntelBTPatcher |2.5.2 RELEASE|同上，无本地修改|
| BlueToolFixup |2.7.3，Tahoe-mask-fix2 定制|基于 [acidanthera/BrcmPatchRAM](https://github.com/acidanthera/BrcmPatchRAM) 与 [crazyhulk 的 BLE 扩展方案](https://github.com/crazyhulk/BlueToolFixup-FixA2DP-BLE)，本地补充匹配修复；不是官方同版本原包|

BlueToolFixup 的本地修复在 2026-11-10 完成，这轮 ForbiddenItlwm 调优中保持不变。文件复制、解压或重新签名也会改变日期，不能只凭修改日期判断代码是否修改。

定制版修正 LE event mask、advertising set random address、extended create connection 三处匹配：忽略 Tahoe 点版本间变化的 RIP/call 相对位移，替换时保留当前系统的实际位移；再按 Lilu 的真实匹配语义将查找字节规范化为 `find & mask`。补丁由 Lilu 在代码页验证阶段应用，不向磁盘写入替换的 bluetoothd 文件。版本号仍是2.7.3，需通过 `Tahoe-mask-fix2` 标识或下列哈希识别。

BlueToolFixup 执行文件 SHA-256：

```text
19b5544ae7285ac6386b84346ed75ab675ade31d90a0cb549314f2d62833dbf1
```

## 适用条件

已实测 **macOS 26.7.2 / 25G332 / x86_64、Intel AX211**，与本分支 Wi-Fi Kext 配套完成 iPhone 和原生 Mac 双向文件传输。其他 macOS build、其他 Intel 蓝牙控制器未由此认证；本包不是全部 Intel 卡或全部 Tahoe 版本的通用认证包。

AX211 的 Wi-Fi 与蓝牙使用不同的接口：Wi-Fi 驱动不负责蓝牙固件，蓝牙 USB 端口仍须正确映射并配置为内部端口。若系统根本未枚举蓝牙 USB 设备，仅添加这些 Kext 不能替代 USB 映射。使用已支持这些第三方 Kext 的 OpenCore 配置，不照抄个人安全策略、SMBIOS 或账户设置。

## 安装步骤

1. 备份完整可启动 EFI，优先从备用 USB EFI 测试；记录原蓝牙组合与启动参数。
2. 把两个 ZIP 和 `Bluetooth-SHA256SUMS.txt` 放在同一目录，运行 `shasum -a 256 -c Bluetooth-SHA256SUMS.txt`，两项均应 `OK`。如只下载驱动 ZIP，可运行 `shasum -a 256 AX211-Bluetooth-Tahoe-25G332-mask-fix2.zip`，与清单中同名一行比较。
3. 解压驱动包，将 `Kexts/` 下四个完整 Kext 放入 `EFI/OC/Kexts/`。已有相同 Lilu 1.7.2 且哈希一致可保留；已有其他工作版本则先核对依赖与差异，不能同时加载两份 Lilu。
4. 在 `config.plist → Kernel → Add` 中启用下面四项。**Lilu 必须先于依赖它的插件加载；IntelBluetoothFirmware 放在 IntelBTPatcher 前。** 可按下表顺序排在现有相关条目位置，保留其他插件依赖关系。

| 顺序 | BundlePath | ExecutablePath |
|---|---|---|
|1|`Lilu.kext`|`Contents/MacOS/Lilu`|
|2|`IntelBluetoothFirmware.kext`|`Contents/MacOS/IntelBluetoothFirmware`|
|3|`IntelBTPatcher.kext`|`Contents/MacOS/IntelBTPatcher`|
|4|`BlueToolFixup.kext`|`Contents/MacOS/BlueToolFixup`|

每项 `PlistPath=Contents/Info.plist`、`Enabled=true`、`Arch=x86_64`。Lilu 是其他插件的共享依赖，不要仅因本包而将其全部系统适用范围改成 Tahoe；另外三项本套配置可限定 `MinKernel=25.0.0`、`MaxKernel=25.99.99`，但内核范围本身不等于所有 Tahoe build 均已验证。

5. 在 `NVRAM → Add → 7C436110-AB2A-4BBB-A880-FE41995C9F82 → boot-args` 中添加 **`-btlfxadvsets`**，保留 Wi-Fi 和其他已有必要参数。本包不要求另加 `-btlfxa2dpcheck`。
6. 本套方案**保留 IntelBTPatcher，停用 BTLEAdvFixup，不添加 `-btleadv`**；不要混用两个方案的 HCI/广播补丁。Tahoe 不加载旧 `IntelBluetoothInjector.kext`，本包也未包含它。仅使用 AX211 时不需要额外加载给 Broadcom 使用的 BrcmPatchRAM/BrcmFirmwareData。
7. 按当前 OpenCore NVRAM 写入策略确认 boot-args 更新，用匹配版本的 `ocvalidate` 检查配置，再手动重启。不要盲目清空所有 NVRAM，也不要为换蓝牙包改动无关系统配置。

## 启动后检查与使用

```bash
sw_vers -buildVersion
kmutil showloaded --list-only | grep -E 'Lilu|IntelBluetoothFirmware|IntelBTPatcher|BlueToolFixup|BTLEAdvFixup'
nvram boot-args
system_profiler SPBluetoothDataType
```

确认系统 build、四个组件加载，`-btlfxadvsets` 生效，蓝牙可开启且 AX211 控制器/固件正常；不应同时加载 BTLEAdvFixup。`package-manifest.json` 记录全部 Kext 文件的 SHA-256 与本机已加载 UUID。加载成功本身不能证明 BLE 广播/扫描或空投已正常。

正常连接 Wi-Fi、开启蓝牙，在 Finder 打开隔空投送；测试时可暂设“所有人”，手机保持亮屏解锁，双向验证文件完成后恢复个人接收设置。发现故障仍可能发生；切换“不允许任何人→所有人”曾临时恢复可见，不能据此视作永久修复。

更新 macOS 前应重新核对这个定制补丁与目标 bluetoothd build 的兼容性，保留能回滚的 EFI；不能只因 BlueToolFixup 版本号相同就认定补丁相同。

## 回滚

从原有可启动 EFI 启动，恢复旧蓝牙 Kext、对应 Kernel/Add 和原蓝牙参数。若其他插件依赖 Lilu，保留原有共享 Lilu。不要通过修改 Wi-Fi 驱动、SMBIOS、Apple ID 或重装系统代替蓝牙回滚。

## 源码、构建和许可证

定制 BlueToolFixup 的完整目标源码与 Xcode 工程位于本仓库 `extras/bluetooth/BlueToolFixup-mask-fix2/`；对应源码包同时提供上述目录与 IntelBluetoothFirmware v2.5.2 原始源码归档（提交 `14787a2a73210a75c0e5a650f30b42e581da0fe2`）。Intel 二进制原 Release ZIP 的 SHA-256 为 `c26140b2091e7b41aab5e5fbdd322112908efc509f9fde3d71d4e3f91396b991`。

BlueToolFixup 源码包的 `BUILD.md` 列出依赖与构建步骤。工具链/路径变化可能改变 UUID 和哈希，本期打包的是已实机使用的二进制，不用未经验证的重建产物替换。许可证见包内 `Licenses/`：BlueToolFixup GPL-2.0、IntelBluetoothFirmware/IntelBTPatcher GPL-3.0、Intel 固件独立再分发许可、Lilu BSD-3-Clause。保留各项目版权；本分支只对 BlueToolFixup 的本地补丁作增量说明，不把上游组件当作本地原创。
