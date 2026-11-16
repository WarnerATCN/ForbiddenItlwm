# Single-frame rate policy host checks

Run `python3 tests/portable_rx/test-single-rate.py` on macOS with Python3 and CLT. ASan/UBSan production-extraction checks; no driver loading or network traffic. The only new flag is `-itlawdlsinglelegacy`, absent/off by default. These checks are not RF/AirDrop A/B evidence.

## Hardware A/B/A pending on current main

Rebased onto main `96ff71e` (0.6.0-alpha.1), retaining default-on #47 and the upstream #57 filter fix. A1/A2 use that exact main; B adds only this PR and `-itlawdlsinglelegacy`. The control-RX and idle-handoff experiments must remain absent.

Target hypothesis: native Mac → AX211 transfers can be limited by delivery of the AX211's single-frame TCP replies/ACKs. The flag selects legacy 24 Mbps for the existing eligible single-unicast path; it does not fix aggregate TX or change infrastructure rate control. Earlier combined-driver observations are not evidence for this rebased branch.

Use the same full file, devices, verified AP/AWDL channels and width, screen/radio states and receive settings throughout ordered A1/B/A2. Repeat native Mac → AX211 at least twice per stage, hash received files, and check the reverse direction for regression. Record TCP progress/retransmissions, actual AWDL versus LAN bytes, single-frame mode/status counters, aggregate counters and Wi-Fi gateway ping. A complete transfer or a higher instantaneous rate alone does not show this policy was exercised; correlate the selected single-frame mode with completions. No standalone hardware result on this base exists yet.
