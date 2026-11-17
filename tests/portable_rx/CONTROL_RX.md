# Short-control RX window host checks

Run `python3 tests/portable_rx/test-control-rx.py && python3 tests/portable_rx/test-control-rx-wanted.py` on macOS with Python3 and CLT. ASan/UBSan production-extraction checks; no driver loading or network traffic. The only new flag is `-itlawdlcontrolrx`, absent/off by default. These checks are not RF/AirDrop A/B evidence.

Also run `python3 tests/portable_rx/test-control-rx-filter.py` for uncertain-open/close restoration and rollback, including independent expiry and failed restoration while the upstream #47 lease overlaps. The speculative control-peer station experiment and the other two unmerged split features are excluded.

Rebased onto main `96ff71e` (0.6.0-alpha.1), retaining its default-on #47 window and #57 station-lifetime filter rule. With this flag absent, that upstream rule is unchanged. Main now includes fixes beyond beta.2+#47; all hardware stages must use this exact common base and report it as such.

## Hardware A/B/A — completed, inconclusive

Target hypothesis: a successful short unicast TCP request may still need a bounded receive window for its reply before bulk traffic starts. This is a **connection/reply-latency** experiment, not a bulk-rate or discovery fix. Upstream #57 may already remove the original idle-connection stall; no additional benefit is assumed.

Compare stock pinned main (A1), this branch with only `-itlawdlcontrolrx` added (B), then stock pinned main again (A2), with default #47 enabled throughout and the same verified AP/AWDL149/80 settings, Bluetooth, file and phone. Capture request/reply and successful-TX attribution before each send; record ASK separately from TCP establishment, window arms/completions, ordinary Wi-Fi ping, actual AWDL bytes and full-file outcome. Include an idle interval long enough to exercise the upstream station-versus-session distinction, with identical timing in each stage. Phone screen state and reference-device radio state must be explicit. A zero-arm/no-improvement result is a result, not proof that the feature fired. The ordered iPhone A/B/A is now complete: [full results and limitations](CONTROL_RX_ABA.md). It did not establish a repeatable standalone benefit; the PR remains draft.
