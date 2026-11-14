# Single-frame rate policy host checks

Run `python3 tests/portable_rx/test-single-rate.py` on macOS with Python3 and CLT. ASan/UBSan production-extraction checks; no driver loading or network traffic. The only new flag is `-itlawdlsinglelegacy`, absent/off by default. These checks are not RF/AirDrop A/B evidence.
