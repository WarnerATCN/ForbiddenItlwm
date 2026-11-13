# portable-rx-p1 部署与参数

本页是本分支的部署说明。原项目的[安装文档](INSTALL.md)是上游方案，尤其蓝牙补丁组合与本机实测组合不同，不应直接混合两份配置。

## 适用条件

| 项目 | 本期验证范围 / 前提 |
|---|---|
| 系统 | 本期预编译包实测 macOS 26.7.2 / 25G332 / x86_64。上游其他目标的声明不自动成为本分支的实机认证 |
| Wi-Fi | 本机 Intel PCI 8086:7A70，现有 AirportItlwm/itlwm 支持的 Intel 卡才有继续验证的基础；没有认证全部同系列卡 |
| macOS网络栈 | 使用系统原生IO80211Family与IOSkywalkFamily。本机未同时注入旧版Skywalk/Legacy IO80211或屏蔽系统Skywalk |
| DMA / IOMMU | 驱动需要可用的设备DMA映射。用上游检查器和IORegistry核对 `ItlwmDMAMapper` / `ItlwmDMARevision`；不能只凭“Wi-Fi可开”推断此条件满足 |
| OpenCore | 现有可启动且可以加载本机自编译/ad-hoc Kext的配置；先保留完整可回滚EFI。本期没有替用户更改SIP、AMFI或安全启动策略，也未验证所有默认安全策略组合 |
| 蓝牙 | Intel蓝牙固件正常，BLE广播与扫描在当前macOS build可用；单独准备合适的蓝牙兼容方案，见下节 |
| 网络 | 本机普通Wi-Fi需正常关联路由器。测试证明关联36或149时均可传输；不以关闭本机Wi-Fi总开关或断开本机路由器连接作为部署条件 |
| 信道 | 只使用固件允许的信道与完整带宽块。149不可用时按对端序列与合法性回退44或6，不通过伪造国家码解锁 |

本期实际部署只替换 Wi-Fi Kext 执行文件与配置说明。没有更改蓝牙、账户、代理、接收设置和已有启动参数。这个事实不是“任意旧配置直接换一个文件就必然可用”的保证。

## 蓝牙前提：选择一种完整方案

**本期发布包只提供 `ForbiddenItlwm.kext`，不包含蓝牙补丁。**

本机保留的实测组合：

| 组件 | 版本 / 说明 |
|---|---|
| Lilu | 保留原有工作版本与依赖配置 |
| IntelBluetoothFirmware |2.5.2|
| IntelBTPatcher |2.5.2，保持启用|
| BlueToolFixup |2.7.3，本机已经使用的Tahoe `mask-fix2`定制构建|
| 该定制BlueToolFixup执行文件SHA-256 |`19b5544ae7285ac6386b84346ed75ab675ade31d90a0cb549314f2d62833dbf1`|
| 蓝牙启动参数 |保留该定制构建支持的`-btlfxadvsets`|
| BTLEAdvFixup |本期没有加载或新增|

同样的“2.7.3”版本名不意味着二进制或补丁相同；**不要认为官方同版本一定支持 `-btlfxadvsets`**。该定制构建属于单独的蓝牙工作，未随本Wi-Fi分支打包。准备新机器时，应先按蓝牙项目对应系统build的说明，验证广播/扫描。

上游ForbiddenItlwm的另一种组合是 `BTLEAdvFixup + -btleadv`，并要求停用与其HCI hook重叠的IntelBTPatcher。那是另一套组合，本期没有把它与现有BlueToolFixup定制方案混用，也没有重新验证它。因此本文不要求你同时启用 `-btleadv`、`-btlfxadvsets`和多个HCI补丁。

仅凭本文不能取得该定制蓝牙构建，且本期发现问题仍未解决；它不是一套已经认证所有机器的Wi-Fi+蓝牙一键套件。

## 部署步骤

1. **记录当前版本并备份完整EFI。** 记录 `sw_vers -buildVersion`、现有Wi-Fi/蓝牙Kext、OpenCore配置及启动参数；保留可启动的回滚副本。本机每次安装都先完成全EFI ZIP校验，事后逐文件比较。
2. 下载本期Tahoe预发布包，解压 `ForbiddenItlwm.kext`。核对发布页校验值、执行文件UUID与签名；来源为本分支的包才对应本文实测。
3. 放入 `EFI/OC/Kexts/ForbiddenItlwm.kext`。在 `Kernel -> Add` 中只启用一套Intel Wi-Fi驱动，停用旧 `AirportItlwm.kext` / `itlwm.kext`条目，旧文件可以留作回滚。
4. 增加或更新以下条目，其他条目和蓝牙顺序按现有依赖方案保留：

   | 字段 | 值 |
   |---|---|
   |BundlePath|`ForbiddenItlwm.kext`|
   |ExecutablePath|`Contents/MacOS/ForbiddenItlwm`|
   |PlistPath|`Contents/Info.plist`|
   |Enabled|`true`|
   |Arch|`x86_64`（如现有OpenCore版本使用该字段）|
   |MinKernel|`25.0.0`|
   |MaxKernel|`25.99.99`|
   |Comment|`ForbiddenItlwm portable-rx-p1`|

5. 在 `NVRAM -> Add -> 7C436110-AB2A-4BBB-A880-FE41995C9F82 -> boot-args` 添加下一节的Wi-Fi参数，保留与本驱动无关的已有参数。按当前OpenCore的NVRAM写入策略配置对应的 `Delete/boot-args`，确认新参数实际生效；不要为此盲目清空所有NVRAM。本机这次安装没有现场写入NVRAM或更改启动参数。
6. 用 `plutil -lint` 和匹配OpenCore版本的 `ocvalidate` 检查配置。确保没有旧OCLP无线注入、IOSkywalkFamily替换/阻止条目冲突。具体已有补丁的撤销应按原部署方式处理。
7. 手动重启，从待验证EFI启动并正常连接Wi-Fi。脚本不自动重启。
8. 执行“首次启动核验”，再与iPhone/原生Mac双向传文件。发现问题仍可能出现；通过一次传输不代表永久修复。

## Wi-Fi启动参数

这是本期实测的一组参数，不是已经精简过的最小集合；其中有诊断项。

```text
-itlawdlcoexprobe -itlawdliface -itlawdlnativeup -itlawdlcoexrx -itlawdlcoextx -itlawdlcoexmulti -itlawdlcoexdata -itlawdlmitx -itlawdlelicit -itlawdlcaps -itlawdlsvcmerge -itlawdlawsync itlawdlintcoal=4 -itlawdlcoexbatx -itlawdlcoexpeerpause -itlawdlcoexbatrace itlawdltxqueue=4096 -itlawdlcoexsamechprobe
```

| 参数 | 作用 |
|---|---|
|`-itlawdlcoexprobe`|建立并行AWDL监听固件上下文|
|`-itlawdliface`|创建/公布原生`awdl0`接口|
|`-itlawdlnativeup`|接纳系统AWDL启动请求|
|`-itlawdlcoexrx` / `-itlawdlcoextx`|监听上下文收发与同步帧|
|`-itlawdlcoexmulti`|在普通Wi-Fi仍关联时使用AWDL监听信道|
|`-itlawdlcoexdata`|通过监听上下文承载AWDL数据|
|`-itlawdlmitx`|发送系统提供的名称/服务等AWDL通告；受build核验约束|
|`-itlawdlelicit`|补充对端期望的AWDL字段|
|`-itlawdlcaps`|向系统/对端报告本方案的VHT与双流能力|
|`-itlawdlsvcmerge`|处理分散的服务记录，改善记录完整性；不能据此声称发现已稳定|
|`-itlawdlawsync`|按对端可用时段安排空闲同步|
|`itlawdlintcoal=4`|使用本期测试的中断合并值|
|`-itlawdlcoexbatx`|发送Block Ack协商与固件聚合|
|`-itlawdlcoexpeerpause`|对端离开时暂停其聚合队列|
|`-itlawdlcoexbatrace`|Block Ack事件诊断；不直接提升性能|
|`itlawdltxqueue=4096`|AWDL发送队列容量|
|`-itlawdlcoexsamechprobe`|同信道管理回复的受限短窗口，与新增短TCP窗口共同恢复过滤状态|

没有要求额外添加国家码、80MHz强制解锁或调试版绕过参数。`-itlawdlcoexlowlat`在这套代码中因本机固件拒绝而禁用，不用它调优；`-itlawdlanybuild`也不是正常部署参数。

## 默认运行参数

下面四项是本期编译默认值，正常启动后不用再执行 `sysctl -w`：

| sysctl | 默认 | 含义 |
|---|---:|---|
|`debug.forbidden_awdl_control_rx`|1|受限短TCP接收窗口|
|`debug.forbidden_awdl_control_peer`|0|未经充分对照验证的短控制站点/接替实验保持关闭|
|`debug.forbidden_awdl_single_legacy`|1|受限单帧legacy24策略|
|`debug.forbidden_awdl_peer_handoff`|1|空闲接收对端接替|

旧A/B采样脚本可能在退出时强制把`control_rx`恢复0，不能直接用于本期默认1的配置。关闭/开启调试项属于排障，不应当作为每次开机必跑的部署脚本。

## 首次启动核验

```bash
sw_vers -buildVersion
kmutil showloaded --list-only | grep -E 'ForbiddenItlwm|AirportItlwm|IntelBluetooth|IntelBTPatcher|BlueToolFixup'
sysctl debug.forbidden_awdl_control_rx debug.forbidden_awdl_control_peer debug.forbidden_awdl_single_legacy debug.forbidden_awdl_peer_handoff
ifconfig awdl0
ioreg -l -w0 | grep -E 'ItlwmAWDL(InterfaceBuild|BuildCheck)|ITLAWDLCoex(Added|Channel|OwnWidth|CountryLearned)'
codesign --verify --strict ForbiddenItlwm.kext
```

本期应看到：正确的 `ForbiddenItlwm` UUID、`forbidden-portable-rx-p1`标识、`BuildCheck=verified`，四个默认值依次1/0/1/1；不能同时加载旧AirportItlwm。合法性允许且条件满足时可看到监听149/80，其他区域允许44或6回退。不能把“必须显示149”作为所有国家的通过条件。

若只是端口8770存在，并不能证明原生Mac界面一定可见；还要实际关闭重开Finder、空闲后重试和双向传文件。文件接收应核对大小和SHA-256。抓包可能改变系统选用的传输路径，因此还应使用接口字节计数确认数据究竟走AWDL还是普通局域网。

## 源码构建

```bash
xcode-select --install
git clone https://github.com/acidanthera/MacKernelSDK.git MacKernelSDK
git -C MacKernelSDK checkout 3f75008
python3 tools/build.py --target tahoe --out build -j 8
codesign --force --sign - --timestamp=none build/ForbiddenItlwm.kext
codesign --verify --strict build/ForbiddenItlwm.kext
python3 tools/abi/audit_vtable.py --target tahoe --build build --out build --lifecycle-overrides
python3 tools/abi/check_allocation_layout.py build/ForbiddenItlwm.kext/Contents/MacOS/ForbiddenItlwm --output build/hal-layout.json
python3 tools/abi/check_awdl_allocation.py build/ForbiddenItlwm.kext/Contents/MacOS/ForbiddenItlwm build/awdl-layout.json
```

需要Python 3、Xcode Command Line Tools与对应MacKernelSDK；固件压缩源会由构建脚本按需生成，SDK和生成的`FwBinary.cpp`不提交到仓库。每个输出目录独立全量构建；校验头文件依赖、类分配布局与568个虚函数槽。源码路径/工具链变化会改变UUID和哈希，重建结果不能直接冒充已实测发布二进制。

## 回滚

从保留的可启动EFI启动，恢复备份中的Wi-Fi Kext、对应 `Kernel/Add`条目和原Wi-Fi参数。不要因此改掉无关的蓝牙、SMBIOS、账户或系统服务。保留本期候选与备份即可；本分支未安装后台守护程序，也没有需要清理的自动重启服务。
