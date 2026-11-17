# Short-control RX window: AX211 A/B/A, 2026-11-17

**Result: inconclusive; no repeatable standalone benefit established.** Six monitored Mac→iPhone file transfers completed in an ordered main → #48 → main sequence. The B build armed control leases during its send-control periods, but candidate TCP reply timing varied in both B and the baseline. These observations do not establish either a fix or a causal regression. Keep this PR draft.

This follows [the maintainer's independent-test request](https://github.com/retropineaple/ForbiddenItlwm/pull/48#issuecomment-6901466416). The case targeted is short TCP request/reply latency before bulk transfer, including a repeat after an idle interval. Bulk file rate and user-facing ASK time are separate observations, not the target metric by themselves.

## Builds and setup

- AX211 (8086:7A70), macOS 26.7.3 / 25G342. Actual Mac AP and AWDL listener were verified at **149 / 80 MHz** after each build boot.
- A1/A2: pinned stock main `96ff71e0211789239f6fbf6b64ac8e7fd22b41aa`, 0.6.0-alpha.1, UUID `0CB947B3-5F02-3F95-8C12-ED62F27C8B78`.
- B: isolated #48 at `b66e9831daa91f48f082b2f6e213e364f6f99fc5`, UUID `C8CF904A-8B75-37EE-9F90-6C6D4E518148`, with only `-itlawdlcontrolrx` added. No #49 legacy-rate, #50 handoff, speculative control-peer station, or runtime sysctl experiment was enabled.
- Main includes default-on #47, #57's station-lifetime filter rule and #21, not just beta.2+#47. Those upstream changes were common to every stage. No `-itlawdlnosamechprobe` or old filter-by-session override was used. Bluetooth was unchanged.
- Same 247,636,698-byte reference file, local SHA256 `a31d673c39851f0f6eb3fa53f2570cd06182b402d414e0d5716fab8b96296159`, requested each time. All six monitored sends had system UPLOAD END and user-confirmed receiver completion; **no iPhone-side hash** was collected.
- The iPhone was connected to the test AP and instructed to stay awake/unlocked for each file. The reference native Mac remained **Wi-Fi online for unrelated work throughout**, as required by the user; no test transfer or sniffing was requested from it. This was not single-peer RF isolation, and unrelated traffic/peer ownership was not independently controlled.
- There was a manual reboot between A1/B/A2. Sampling began with BA already `agreed`; these are established-BA connection attempts, not fresh BA negotiations. A1's phone activation relative to capture start is uncertain; B/A2 used an instruction to connect after READY. No cold-activation equivalence is claimed.

## Six monitored files

Decimal MB/s = reference file bytes / sharingd UPLOAD-phase seconds / 1,000,000. ASK is kept separate from TCP packet timing.

| Stage/run | UPLOAD s | MB/s | ASK s | AWDL TX bytes | en0+en1 TX bytes |
|---|---:|---:|---:|---:|---:|
| A1 / 1 | 8.080 | 30.648 | 4.588 | 263,868,868 | 67,727 |
| A1 / 2 | 7.581 | 32.665 | 0.405 | 264,216,804 | 51,552 |
| B / 1 | 10.467 | 23.659 | 6.082 | 264,190,361 | 33,785 |
| B / 2 | 7.781 | 31.826 | 5.689 | 264,195,583 | 15,767 |
| A2 / 1 | 9.590 | 25.822 | 38.150 | 264,122,388 | 17,178 |
| A2 / 2 | 7.529 | 32.891 | 3.835 | 263,979,153 | 31,809 |

Each monitored file has an AWDL TX increment above the reference file size and much smaller ordinary-LAN TX increments, supporting AWDL delivery. Counters include protocol/background traffic. This does not establish that every captured TCP flow is the file's socket; bulk payload was not captured.

## Observed TCP request/reply candidates

The same textual tcpdump filter was used in every stage: direct IPv6 TCP SYN/FIN/RST on `awdl0`, snaplen 128. It excludes IPv6 extension-header flows, pure ACKs and ordinary application payload. This covers the SYN-reply part of #48's hypothesis, **not every small application-data request eligible for the feature**.

A candidate flow starts between Send START−1 s and UPLOAD START. A reply must reverse the same endpoints and acknowledge the initial SYN sequence plus one. The durations below use kernel packet timestamps. This is time-overlap association only: peer identity, driver BA owner, and the connection's exact application role were not independently established. A SYN-ACK reply is not full three-way establishment or application acceptance. Reuse of identical endpoints and initial sequence is not distinguished.

| Stage/run | SYN→first matching SYN-ACK, ms | SYN observations before reply |
|---|---:|---:|
| A1 / 1 | 176.977 | 2 |
| A1 / 2 | 14.556 | 1 |
| B / 1 | 1,907.198 | 9 |
| B / 2 | 176.659 | 2 |
| A2 / 1 | 38,318.838; 3,168.792 | 13; 9 |
| A2 / 2 | 3,237.097 | 9 |

A2/1 has **two** candidate flows. The first began at 23:53:37.848403 and its matching reply arrived at 23:54:16.167241, **after** UPLOAD START (23:54:15.982). The other began at 23:54:08.955325 and received its reply at 23:54:12.124117. Both are retained; neither is silently selected as the definitive phone/file handshake. A2/2 also had a ~3.237 s candidate reply wait with the feature off.

Repeated same-ISN SYN observations include ECN flag variants and may include capture duplicates. The counts are **not asserted to be wire retransmission counts**. No captured SYN is not evidence of zero connection delay.

## Feature activity

The stock main baseline does not publish the new control-window counters. Its loaded identity/arguments and feature gate were verified off; absent counters are not fabricated as measured zeros.

For B, registry samples bracketing Send START→UPLOAD START showed:

| B run | ControlRxArms delta | ControlRxCompletions delta | Either delta during UPLOAD |
|---|---:|---:|---:|
| 1 | +2 | +11 | 0 |
| 2 | +1 | +4 | 0 |

Before the phone-connect instruction, B already had 3 arms / 17 completions. Those preexisting counts are not attributed to the test phone. The per-send deltas show leases armed in the relevant control periods, but are still **global, sampled counters**: another online peer can contribute, registry publication is not exact packet timing, and there is no per-lease applied-window/restore/peer record here. They do not by themselves prove that a particular observed SYN-ACK was admitted by the lease.

## Idle timing, gaps and extra system record

The protocol required at least 90 s after the preceding UPLOAD END before requesting a repeat; actual intervals were not identical:

- A1: 191.172 s from first UPLOAD END to second Send START, one capture segment.
- B: two capture segments on the same boot, with a gap. The first segment reached its 600 s limit; a later system-only send was found at 23:28:25.072, UPLOAD 23:28:26.815→23:28:34.788. User confirmation of that operation became uncertain. It has no simultaneous TCP/counter coverage and is **not one of the two monitored rows**. The monitored continuation began at 23:34:20.586: 345.798 s after that auxiliary UPLOAD END (529.158 s after the first monitored UPLOAD END). This extra exposure/cache history is a confound, not a discarded measured performance result.
- A2: two segments on the same boot, renewed while idle to leave sufficient capture time. Actual first UPLOAD END→repeat Send START was 231.237 s. No extra A2 file was used to force a result.

These are warm repetitions with nonuniform idle/cache history, not repeated independent cold negotiations. The standard phone receiving setting was requested per stage; no additional recovery toggle, sharingd restart, RF sniffer or forced reference-Mac disconnect was used to obtain success. The evidence is one ordered, nonrandomized sequence on one host.

## Wi-Fi-bound gateway ping and capture completeness

Ping was bound to the Wi-Fi interface/DHCP source, configured for 100 ms, and ran concurrently with every monitored file and idle sampling. Whole-segment statistics include nontransfer time; the printed `0.0%` rounds some one-packet losses, so missing counts are explicit.

| Segment | Sent / received | Missing | RTT min / median / max, ms |
|---|---:|---:|---:|
| A1 | 4,674 / 4,673 | 1 | 1.377 / 23.773 / 240.963 |
| B first | 5,846 / 5,845 | 1 | 1.309 / 27.173 / 203.460 |
| B continuation | 1,385 / 1,385 | 0 | 1.681 / 16.073 / 193.192 |
| A2 first | 4,478 / 4,477 | 1 | 1.647 / 18.564 / 212.496 |
| A2 continuation | 1,673 / 1,673 | 0 | 1.561 / 30.708 / 152.317 |

A configured 100 ms interval is not guaranteed actual probe/reader cadence. ICMP reachability/RTT does not prove that all infrastructure frames survive a receive window. There is no matched per-lease window/ping envelope for #48 here, so no such safety conclusion is claimed.

All five tcpdump children failed to exit within the collector's 3 s SIGINT drain deadline and were killed (`-9`). **Final TCP capture/drop statistics are unavailable**, not zero. The positive observed SYN/reply pairs can be reported; absence of other packets and exhaustive capture coverage cannot be inferred. Original raw logs, endpoint addresses and EFI remain local.

## Interpretation and restoration

This exercises the opt-in path enough to observe nonzero B arms/completions, but **does not demonstrate a repeatable standalone connection-latency improvement** over pinned main. B/1 was slower than either A1 candidate, while A2 also exhibited long candidate waits with the feature off. Together with uncontrolled peer attribution, extra B exposure, variable idle timing and missing final capture statistics, the sequence cannot establish a causal regression either. No general bulk-rate, discovery or small-payload-reply fix is claimed. The original combined-driver result is not used as evidence for this PR.

The PR remains draft. Stronger follow-up would need verified test-peer/BA-owner and applied-window attribution, more uniformly controlled repeats, capture shutdown/drop accounting, and coverage of the other eligible short application requests. That follow-up was not substituted into this run or mixed with #49/#50.

After testing, all **67 original EFI files** were restored byte-for-byte. The final manual reboot on 2026-11-18 verified the user's pre-test driver UUID, original arguments, Bluetooth and original defaults; device settings were restored. No test driver or collector remains active. This is restoration to the user's pre-test configuration, distinct from the pinned-main test baseline.
