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
17. Pitch 25, 50, and 75 through the normal NVDA pitch setting, confirming it
    remains the synth's native pitch control.
18. Pitch 25, 50, and 75 through the Global Sonic Pitch panel.
19. Pitch 25, 50, and 75 through the `Sonic pitch` setting in the Voice dialog
    or synth settings ring when it is exposed.
20. With global Sonic disabled, confirm `Sonic pitch` is not exposed in the
    Voice dialog or synth settings ring.
21. With global Sonic enabled, confirm `Sonic pitch` is exposed in the Voice
    dialog or synth settings ring for supported synths.
22. Input Gesture scripts for increasing, decreasing, and resetting Sonic pitch
    appear in the `Global Sonic Pitch` category.
23. Rate, volume, voice switching, and cancellation still behave normally.
24. Say-all / continuous reading does not obviously regress.
25. NVDA sound effects are not processed as speech audio.
26. Error log check after each scenario.

## Expected Results

- NVDA loads with no startup errors.
- The package contains `globalPlugins` and documentation only; it does not
  contain `synthDrivers`.
- `SAPI5 32-bit Sonic Pitch` and `SAPI5 64-bit Sonic Pitch` do not appear in the
  synthesizer dialog after the old `sapi5SonicPitch` add-on is removed.
- Global Sonic processing is disabled by default.
- When global Sonic is disabled, native synth pitch behaves normally.
- When global Sonic is disabled, the dynamic `Sonic pitch` setting is not added
  to Voice settings or the synth settings ring.
- When global Sonic is enabled for supported main-process synths, logs show:
  - `globalSonicPitch: added Sonic pitch voice setting`
  - `globalSonicPitch: processed speech audio`
- When global Sonic is disabled again, the dynamic `Sonic pitch` Voice setting
  is removed.
- While global Sonic is enabled, changing NVDA pitch does not log
  `globalSonicPitch: captured NVDA pitch`; it should remain native synth pitch.
- Changing the dynamic `Sonic pitch` setting logs
  `globalSonicPitch: captured Sonic pitch setting` and changes the same global
  Sonic pitch value.
- Standard `sapi5_32` still loads. On 64-bit NVDA it is not globally processed
  because it runs in the separate 32-bit synth host.
- Missing Sonic internals or unsupported audio formats are handled by bypassing
  the original audio block rather than breaking speech.

## Packaging

Zip the contents of the `addon` directory, not the outer project directory, and
use the `.nvda-addon` extension.

Expected package name for version 0.4.2:

```text
globalSonicPitch-0.4.2.nvda-addon
```
