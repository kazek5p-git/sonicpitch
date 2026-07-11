# Manual Testing

## Test Matrix

1. NVDA 2025.1 or newer.
2. NVDA 2026.1 or newer 64-bit.
3. Windows 10 and Windows 11.
4. Add-on install, disable, re-enable, and restart.
5. Add-on help opens in English and Polish locales.
6. Synthesizer dialog does not show any add-on-provided Sonic synth.
7. Standard eSpeak loads with global Sonic disabled.
8. Standard eSpeak loads with global Sonic enabled.
9. RHVoice loads with global Sonic disabled.
10. RHVoice loads with global Sonic enabled.
11. OneCore loads with global Sonic disabled.
12. OneCore loads with global Sonic enabled.
13. Standard SAPI5 64-bit loads with global Sonic disabled.
14. Standard SAPI5 64-bit loads with global Sonic enabled.
15. Standard SAPI5 32-bit loads with global Sonic disabled.
16. Standard SAPI5 32-bit loads with global Sonic enabled.
17. Pitch 25, 50, and 75 through the normal NVDA pitch setting.
18. Pitch 25, 50, and 75 through the Global Sonic Pitch panel.
19. Rate, volume, voice switching, and cancellation still behave normally.
20. Say-all / continuous reading does not obviously regress.
21. NVDA sound effects are not processed as speech audio.
22. Error log check after each scenario.

## Expected Results

- NVDA loads with no startup errors.
- The package contains `globalPlugins` and documentation only; it does not
  contain `synthDrivers`.
- `SAPI5 32-bit Sonic Pitch` and `SAPI5 64-bit Sonic Pitch` do not appear in the
  synthesizer dialog after the old `sapi5SonicPitch` add-on is removed.
- Global Sonic processing is disabled by default.
- When global Sonic is disabled, native synth pitch behaves normally.
- When global Sonic is enabled for supported main-process synths, logs show:
  - `globalSonicPitch: patched pitch setting`
  - `globalSonicPitch: pitch takeover active`
  - `globalSonicPitch: processed speech audio`
- While global Sonic is enabled, changing NVDA pitch logs
  `globalSonicPitch: captured NVDA pitch`, and the native synth pitch is kept at
  neutral `50`.
- Standard `sapi5_32` still loads. On 64-bit NVDA it is not globally processed
  and pitch takeover is not applied, because it runs in the separate 32-bit
  synth host.
- Missing Sonic internals or unsupported audio formats are handled by bypassing
  the original audio block rather than breaking speech.

## Packaging

Zip the contents of the `addon` directory, not the outer project directory, and
use the `.nvda-addon` extension.

Expected package name for version 0.3.0:

```text
globalSonicPitch-0.3.0.nvda-addon
```
