# Manual Testing

## Test Matrix

1. NVDA 2025.1 or newer.
2. NVDA 2026.1 or newer 64-bit.
3. Windows 10 and Windows 11.
4. Add-on install, disable, re-enable, and restart.
5. Add-on help opens in English, Polish, and Slovak locales.
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
17. eSpeak-NG SAPI is configured in its own configurator and appears as a
    normal SAPI5 voice.
18. Confirm the add-on does not create or supplement SAPI voice-list entries.
19. eSpeak-NG SAPI through SAPI5 speaks with global Sonic enabled when the
    voice is already visible in NVDA's standard SAPI5 voice list.
20. While eSpeak-NG SAPI is speaking, quickly lower `Sonic pitch` through 45,
    40, 35, 30, 25, 20, 15, 10, 5, and 0, confirming NVDA does not freeze.
21. Repeat the eSpeak-NG SAPI test with SAPI5 rate set to 100. For stress
    testing, use repeated pitch changes about every 40 ms while speech is
    active.
22. NVDA 2025.3.3 x86 portable with SAPI5 at rate 100 completes repeated
    downward `Sonic pitch` changes without a native crash.
23. Latest stable NVDA x64 with SAPI5 loads the bundled 64-bit Sonic library
    and completes a smoke test without Global Sonic Pitch errors.
24. If a newer beta is available, run an additional beta smoke test, but do not
    set stable-channel `lastTestedNVDAVersion` to a beta API target.
25. Pitch 25, 50, and 75 through the normal NVDA pitch setting, confirming it
    remains the synth's native pitch control.
26. Confirm the Global Sonic Pitch panel has no `Sonic pitch` slider; it only
    enables processing, debug logging, and the support button.
27. Pitch 25, 50, and 75 through the `Sonic pitch` setting in the Voice dialog
    or synth settings ring when it is exposed.
28. Set different `Sonic pitch` values for two supported synths, switch between
    them, and confirm each synth restores its own value.
29. In one synth with more than one voice, such as SAPI5 Paulina and eSpeak-NG
    SAPI, set different `Sonic pitch` values per voice and confirm switching
    voices restores the correct value.
30. While SAPI5 is speaking, quickly decrease `Sonic pitch` several steps and
    confirm NVDA does not crash or report repeated empty processed blocks.
31. While any supported synth is speaking, change `Sonic pitch` and confirm the
    log reports that the change is deferred until the next utterance.
32. Confirm the next utterance uses the newly selected `Sonic pitch`.
33. In Voice settings or the synth settings ring, repeatedly change `Sonic
    pitch` with PageUp/PageDown and confirm each short feedback message uses
    the latest non-neutral value without needing extra slider movement.
34. With global Sonic disabled, confirm `Sonic pitch` is not exposed in the
    Voice dialog or synth settings ring.
35. With global Sonic enabled, confirm `Sonic pitch` is exposed in the Voice
    dialog or synth settings ring for supported synths.
36. In the Voice dialog, change `Sonic pitch`, press Escape or Cancel, reopen
    Voice settings, and confirm the previous value and spoken pitch are
    restored.
37. In the Voice dialog, change `Sonic pitch`, press OK or Apply, reopen Voice
    settings, and confirm the new value is stored.
38. On 64-bit NVDA, test standard `sapi5_32` with global Sonic enabled and
    confirm the Sonic pitch slider appears and changes the 32-bit host output.
39. On 64-bit NVDA, with standard `sapi5_32` speaking, change `Sonic pitch`
    rapidly about every 40 ms and confirm speech continues. The 32-bit host log
    should show deferred updates during active speech and a final applied value
    at a speech boundary.
40. On 64-bit NVDA, repeat a Voice dialog style stress pattern on standard
    `sapi5_32`: cancel current speech, change `sonicPitch`, and speak the new
    value every 150 to 200 ms. Confirm the test finishes and the 32-bit host log
    contains no `access violation`, `RemoteWrite` failure, or `error speaking`.
41. On 64-bit NVDA, set different values for standard `sapi5`/SAPI64 and
    `sapi5_32`/SAPI32, then confirm the config stores separate `sapi5_64` and
    `sapi5_32` entries.
42. On 32-bit NVDA, test standard `sapi5` and confirm its value maps to the
    `sapi5_32` key.
43. Input Gesture scripts for opening the support page, increasing,
    decreasing, and resetting Sonic pitch for the current synth appear in the
    `Global Sonic Pitch` category.
44. During installation or update, the optional support prompt appears outside
    minimal mode. `No` continues installation. `Yes` opens
    `https://buycoffee.to/kazimierz-parzych` in the default browser.
45. Rate, volume, voice switching, and cancellation still behave normally.
46. Say-all / continuous reading does not obviously regress.
47. NVDA sound effects are not processed as speech audio.
48. The repository contains root license documentation and third-party notices.
49. `docs/addon-store-submission.md` has the current package version, download
    URL, and SHA256 before submitting to the NVDA Add-on Store.
50. Error log check after each scenario.

## Expected Results

- NVDA loads with no startup errors.
- The package contains `globalPlugins`, `sapi32HostDrivers`, `installTasks.py`,
  documentation, and `globalPlugins/sonicPitchNative`; it does not contain
  replacement synthesizers shown in NVDA's synthesizer dialog.
- `SAPI5 32-bit Sonic Pitch` and `SAPI5 64-bit Sonic Pitch` do not appear in the
  synthesizer dialog after the old `sapi5SonicPitch` add-on is removed.
- Global Sonic processing is disabled by default.
- When global Sonic is disabled, native synth pitch behaves normally.
- When global Sonic is disabled, the dynamic `Sonic pitch` setting is not added
  to Voice settings or the synth settings ring.
- When global Sonic is enabled for supported main-process synths, logs show:
  - `globalSonicPitch: added Sonic pitch voice setting`
  - `globalSonicPitch: loaded bundled Sonic library`
  - `globalSonicPitch: processed speech audio`
- When global Sonic is disabled again, the dynamic `Sonic pitch` Voice setting
  is removed.
- While global Sonic is enabled, changing NVDA's normal `Pitch` setting changes
  only the synth's native pitch. It should not change the stored `sonicPitch`
  value for the current synth.
- Changing the dynamic `Sonic pitch` setting logs
  `globalSonicPitch: captured Sonic pitch setting` and changes the current
  supported synth's Sonic pitch value.
- Different supported synths can keep different `Sonic pitch` values.
- Different supported voices inside the same synth can keep different `Sonic
  pitch` values.
- Standard 64-bit SAPI5 and standard `sapi5_32` on 64-bit NVDA keep separate
  `sapi5_64` and `sapi5_32` values.
- Changes made from the Voice dialog are previewed live; Escape or Cancel
  restores the previous value, while OK or Apply commits the new value.
- Changing `Sonic pitch` during active speech does not reset the current Sonic
  processor. The active utterance keeps its starting value, and the next
  utterance uses the new value.
- Standard `sapi5_32` still loads. On 64-bit NVDA it is controlled through the
  bundled 32-bit host wrapper, and logs show:
  - `globalSonicPitch: applied remote SAPI5 32-bit Sonic pitch`
  - `globalSonicPitch sapi5_32 host: set Sonic pitch`
- During rapid `sapi5_32` changes on 64-bit NVDA, the host log may show
  `globalSonicPitch sapi5_32 host: deferred Sonic pitch until safe boundary`;
  the final selected value should then be applied at a speech boundary and
  speech should continue.
- During Voice dialog style `sapi5_32` stress on 64-bit NVDA, the host log
  should show `globalSonicPitch sapi5_32 host: replaced Sonic stream` for
  applied pitch changes and should not log `access violation`.
- eSpeak-NG SAPI can be tested only after its own configurator enables at least
  one SAPI voice profile.
- The add-on does not add eSpeak-NG SAPI dynamic voices to NVDA's SAPI voice
  lists. If such voices are missing, fix eSpeak-NG SAPI configuration first.
- Rapid downward Sonic pitch changes while eSpeak-NG SAPI is speaking complete
  without NVDA freezing or logging access violations.
- The same rapid-change scenario at SAPI5 rate 100 completes without NVDA
  freezing or logging access violations.
- On 32-bit NVDA, the log shows `using no-destroy Sonic stream wrapper` once
  Sonic processing starts.
- Missing Sonic internals or unsupported audio formats are handled by bypassing
  the original audio block rather than breaking speech.

## Packaging

Zip the contents of the `addon` directory, not the outer project directory, and
use the `.nvda-addon` extension.

Expected package name for version 0.4.18:

```text
globalSonicPitch-0.4.18.nvda-addon
```
