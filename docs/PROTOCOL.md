# Captured FMS profile: observed, inferred and unknown

Observed on one FMS F4 / Beaver pair. Not a complete manufacturer protocol specification.

- 250K XN297-compatible **normal scrambled** control framing with CC2500 emulation.
- Logical address5: `7F FF FF FF 7F`; transmitted address bytes: `9C 4E B4 15 FA`.
- Payload16 bytes; XN297 CRC16 initialized0xB5D2, polynomial0x1021, scrambled length-specific XOR table inherited from upstream.
- Opaque payload prefix `67 10`, suffix `51 40`; their meaning is unproven. Do not replace them with random bind IDs.
- Eight12-bit fields: `value[i] = payload[2+i] | (((payload[10+i/2] >> (4*(i%2))) & 15) << 8)` using integer division.

| Field | Current interpretation |
|---|---|
| 0 | Aileron approximately1000..2000 |
| 1 | Elevator approximately1000..2000 |
| 2 | Inverse throttle: physical low1989, high1000 |
| 3 | Rudder, inverse relative to the tested Pocket mapping |
| 4 | Three mode values1000/1500/2000 |
| 5 | Constant1500 in captured operation; meaning unknown |
| 6 | Released1500, momentary press2000 |
| 7 | Rolling field, often+1500 modulo4096; occasional identical original packets |

Do not call field7 a proven servo channel or infer a failsafe meaning from it. RC1 increments it per transmitted packet, which the tested receiver accepted. An original cold-start all-zero payload was observed but is intentionally not reproduced as a throttle-safety measure; the receiver accepted safe initial control payloads.

Observed circular hop order:

```text
2,75,26,54,4,74,40,8,73,45,6,72,30,50,10,70,34,12,36,69,38,
13,68,58,14,66,18,28,52,62,20,61,29,60,22,46,24,44,56,42,76
```

Tracked successful adjacent hops were approximately9ms, with a41-slot cycle approximately369ms. Scanned phase gaps are not reliable dwell measurements. The control callback requests9000 microseconds; actual radio timing and packet delivery are not proven by software heartbeat logs alone.

The original pairing reconnects without a user bind action. A fresh-receiver bind sequence, independently selectable identity, return-link format, GPS failsafe rules and universal receiver compatibility remain unknown. Current source deliberately preserves the captured profile instead of inventing these features.

Core files: `FMSBenchCore.h` (packing/gates), `FMSBenchTX_cc2500.ino` (tested transport), `FMSBeaver_cc2500.ino` (independent entry), `_MyConfig.h` (release configuration), and upstream `XN297_EMU.ino` (actual encoder). Historical Bench names are retained to reuse the tested implementation, not to expose packet-dump control mode in RC1.
