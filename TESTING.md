# Manual Testing

Test matrix:

1. NVDA 2025.1 32-bit, if available.
2. Latest NVDA 2025.x 32-bit, if available.
3. NVDA 2026.1 or newer 64-bit.
4. Windows 10 and Windows 11.
5. SAPI5 32-bit Sonic Pitch.
6. SAPI5 64-bit Sonic Pitch, where available.
7. At least one 32-bit SAPI5 voice.
8. At least one 64-bit SAPI5 voice, where available.
9. Pitch 25, 50, and 75.
10. Rate boost off and on.
11. Voice switching.
12. Cancel/interruption by quickly navigating text.
13. Say-all / continuous reading.
14. Add-on disable/re-enable.
15. NVDA restart after selecting each custom synth.
16. Error log check after each scenario.
17. Standard SAPI5 32-bit still loads after enabling the add-on.
18. Standard SAPI5 64-bit still loads after enabling the add-on.
19. Add-on help opens in English and Polish locales.
20. Global Sonic processing disabled: eSpeak, RHVoice, OneCore, SAPI5 32-bit,
    and SAPI5 64-bit load normally.
21. Global Sonic processing enabled: eSpeak, RHVoice, OneCore, SAPI5 32-bit,
    and SAPI5 64-bit still load and produce speech.
22. Global Sonic processing enabled: logs show `sapi5SonicPitchGlobal:
    processed speech audio` for PCM synths in the main NVDA process.
23. Global Sonic processing enabled: NVDA sound effects are not processed as
    speech audio.
24. Global Sonic processing enabled: `sapi5SonicPitch32` and
    `sapi5SonicPitch64` are skipped by default to avoid double processing.
25. Global Sonic processing enabled: standard `sapi5_32` still loads, but is not
    expected to be globally filtered on 64-bit NVDA because it runs in the
    separate 32-bit synth host.

Expected results:

- NVDA loads with no startup errors.
- One add-on package installs both driver modules.
- `SAPI5 32-bit Sonic Pitch` appears when the 32-bit SAPI5 base path is available and compatible.
- `SAPI5 64-bit Sonic Pitch` appears when the 64-bit SAPI5 base path is available and compatible.
- On 64-bit NVDA, both drivers appear as separate synthesizers if both base paths are available.
- On 32-bit NVDA, the 64-bit driver does not appear or fails cleanly.
- Each custom driver exposes the same voices as its corresponding base SAPI5 driver.
- Pitch 50 sounds neutral.
- Pitch below 50 sounds lower.
- Pitch above 50 sounds higher.
- Rate boost still works independently.
- Voice switching reapplies Sonic pitch.
- Speech cancellation remains responsive.
- Say-all does not obviously regress.
- Missing base modules or missing Sonic internals are handled gracefully.
- Standard NVDA `sapi5` and `sapi5_32` drivers are not modified by the add-on.
- The installed add-on package contains `globalPlugins` only for the optional
  global WavePlayer hook and settings panel.
- Global Sonic processing is disabled by default.
- Standard `sapi5_32` is not patched by the global processor; use
  `sapi5SonicPitch32` for 32-bit SAPI5 Sonic pitch.

Packaging:

Zip the contents of the `addon` directory, not the outer project directory, and use the `.nvda-addon` extension.
