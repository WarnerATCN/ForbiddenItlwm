# Same-channel management-response probe

Run `python3 tests/portable_rx/test-samech.py` on macOS with Python3/CLT. Production-extraction tests use ASan/UBSan, compare emitted MAC commands with a beta.2 oracle while the flag is off, inject firmware restore failures, and verify unchanged RX parser/guard function hashes. No driver is loaded by this test.

The only new boot flag is `-itlawdlcoexsamechprobe`, **absent/off by default**. No control-TCP window, single-rate policy, idle handoff, regional picker, sysctl, or new Bluetooth patch is included.

## Required hardware gate (not completed)

Maintainer request: https://github.com/retropineaple/ForbiddenItlwm/pull/44#issuecomment-6877530248 . The old combined candidate's speed is not evidence that this isolated change fixes #24.

1. Use upstream 0.5.4-beta.2 (`69e88fa`) as A; this branch plus `-itlawdlcoexsamechprobe` as B. Retain the same existing AWDL flags, Bluetooth stack, phone, file, placement and network configuration. Do not enable any of the other experiments. Only change the tested driver/flag, keeping a verified bootable EFI backup; manually reboot between builds.
2. Confirm **Mac AP149/80 MHz and AWDL149/80 MHz** for each run. Keep iPhone Wi-Fi connection, unlock state and all other devices consistent. If either channel differs, mark the run invalid for this comparison.
3. Before Mac→iPhone transfer, run `python3 tests/portable_rx/collect_same_channel.py --label beta2-baseline --seconds 60 --out baseline.json`; for B use `--label same-channel-on --out enabled.json`. No root or packet capture required. The sampler saves only allowlisted counters, including `ITLAWDLCoexBaTxStateName` and the four decoded `ITLAWDLCoexBaActionSeen` buckets. It never changes boot args or toggles the feature.
4. Transfer the same file each run; record byte size, receiver-confirmed outcome, file-phase duration, handshake duration separately, and interface-byte evidence for AWDL versus ordinary LAN. Repeat A/B/A if possible. Save driver executable SHA/UUID, actual boot args, AP channel and build identity locally alongside each run.
5. Compare whether the BA state leaves `asking`, how ActionSeen changes, window opens/closes/restore failures, and successful application throughput. Do not infer a fix from one negotiated BA or a host test. If the isolated window does not reproduce the improvement, report that result and keep the PR draft.

No A/B values are fabricated or copied from the combined release. This PR does not claim discovery is fixed. Prepared binaries are not installed automatically.
