# Idle receive-peer handoff host checks

Run `python3 tests/portable_rx/test-handoff.py && python3 tests/portable_rx/test-handoff-rx.py` on macOS with Python3 and CLT. ASan/UBSan production-extraction checks; no driver loading or network traffic. The only new flag is `-itlawdlpeerhandoff`, absent/off by default. These checks are not RF/AirDrop A/B evidence.

## Hardware A/B/A pending on current main

Rebased onto main `96ff71e` (0.6.0-alpha.1), retaining default-on #47 and the upstream #57 filter fix. A1/A2 use this exact main; B adds only this PR and `-itlawdlpeerhandoff`. No control-RX or single-rate policy is enabled.

Target hypothesis: an idle receive BA peer can prevent a newly discovered peer's valid ADDBA request from obtaining the station. This patch permits a bounded, validated challenger to replace an idle owner only after queues and control work are drained. It is not a BLE/mDNS discovery repair and is not evidence for stable Finder visibility.

For each ordered A1/B/A2 stage, keep both an iPhone and a native Mac normally online with explicit Wi-Fi states. Send the same full file from native Mac → AX211, then (after the same idle interval, at least the 3 s minimum) iPhone → AX211, then native Mac → AX211 again. Repeat that alternating sequence. Do not restart sharingd, toggle discovery permission, or disconnect the previous peer to force success. Verify received file hashes, request/acceptance latency, challenger/retirement/error counters and event ordering, queue drain and peer epochs. A no-challenger/no-retirement run does not exercise the feature even if all files complete. Record invisible/waiting/failed outcomes separately instead of attributing them automatically to BA ownership. Check ongoing transfer protection and ordinary Wi-Fi; do not force a handoff during queued work. No standalone hardware result on this base exists yet.
