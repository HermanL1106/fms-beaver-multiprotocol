# Setup and control mapping

Remove the propeller. Turn the original F4 off. Keep the aircraft battery disconnected while configuring or flashing. Use only a compatible external STM32 module; never flash this application into the Pocket itself.

| Radio setting | Value |
|---|---|
| Internal RF | OFF |
| External RF | MULTI, output rangeCH1–16 |
| Protocol | FMSBeav, private numeric125 if name unavailable |
| Subtype | 0 |
| Receiver number | 5 (profile gate, not a new address) |
| Option | 42 (enable key, not tuning/channel) |
| Bind / Auto bind / Bind CH | Disabled / not used |
| Output order | AETR |

Changing protocol/subtype can reset option and receiver number. Recheck them afterwards. No EdgeTX model import is supplied; configure the outputs below yourself.

| Output | Meaning | Owner's control |
|---|---|---|
| CH1 | Aileron | Aileron stick |
| CH2 | Elevator | Elevator stick |
| CH3 | Throttle | Throttle stick |
| CH4 | Rudder, polarity corrected in code | Rudder stick |
| CH5 | -100 stabilized; 0 manual; +100 full self-level | SC |
| CH7 | -100 released; +100 momentary command | SE |
| CH8 | -100 motor locked; +100 unlock request | SD |
| CH16 | -100 RF disabled; +100 enable request | SA |

Names and mode labels were tested on one aircraft. Verify movement, neutrals and modes on your own hardware; a successful packet CRC does not establish correct flight-controller behavior. Do not inadvertently reverse rudder twice. Transmitter trims, rates and expo are not automatically set by this firmware; use conservative, verified model settings rather than assuming the original F4's feel is reproduced.

## Interlocks

Boot with CH16 and CH8 low, CH7 released and throttle minimum. RF requires CH16 OFF before ON. Once RF is active, motor unlock requires CH8 OFF before ON with throttle low. An unsuccessful high-throttle attempt consumes that request: lower throttle and repeat OFF → ON. Raw low-throttle threshold is220; tested radio minimum was approximately208–212. Motor command remains physical low1989 while locked.

RF gating uses raw CH16>1800; motor-request gating uses raw CH8>1800. Typical -100/+100 serial values are about205/1843. Input-gap detection clears arming; do not assume automatic reconnection will resume motor output. Test again after any model, firmware or switch-mapping change.

**RF OFF is not motor cut.** A receiver can execute its own lost-link/GPS behavior. Motor lock is a transmitted command, not a physical power disconnect and not a substitute for verified receiver failsafe. GPS-enabled lost-link/RTH is untested.

## Propeller-off ground check

1. Confirm correct outputs and low/off startup positions while the aircraft is disconnected.
2. Enable RF with motor locked and throttle low, then power the aircraft. Check link behavior and that the motor is stopped.
3. Verify aileron/elevator/rudder directions and neutrals, then the three mode positions. Correct mechanical setup before using transmitter compensation.
4. GPS-wait cancellation was observed with roughly a3-second momentary press; airborne RTH has not been verified.
5. Only with the propeller removed, clear of moving parts and throttle low, test motor unlock, low throttle and motor cut. Never deliberately perform these experiments in flight.
6. Lock the motor, lower throttle and disconnect aircraft power before RF/radio power-off.

No aircraft RSSI or authenticated link-alive sensor is supplied. A module version/status display only proves communication between the radio and the module.
