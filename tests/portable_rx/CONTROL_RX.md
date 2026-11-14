# Short-control RX window host checks

Run `python3 tests/portable_rx/test-control-rx.py && python3 tests/portable_rx/test-control-rx-wanted.py` on macOS with Python3 and CLT. ASan/UBSan production-extraction checks; no driver loading or network traffic. The only new flag is `-itlawdlcontrolrx`, absent/off by default. These checks are not RF/AirDrop A/B evidence.

Also run `python3 tests/portable_rx/test-control-rx-filter.py` for uncertain-open/close restoration and rollback. The speculative control-peer station experiment and the other three split features are excluded. Tahoe build passed; no standalone hardware retest yet.
