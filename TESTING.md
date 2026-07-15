# Manual Testing

This checklist focuses on the current Global Sonic Pitch add-on.

## Core Matrix

1. NVDA 2025.1 or newer starts without Global Sonic Pitch errors.
2. NVDA 2026.1 or newer 64-bit starts without Global Sonic Pitch errors.
3. Global Sonic processing is disabled by default on a fresh config.
4. The synthesizer dialog does not show add-on-provided replacement synths.
5. The `Global Sonic Pitch` settings panel appears in NVDA Settings.
6. With global processing disabled, `Sonic pitch` is not shown in Voice
   settings or the synth settings ring.
7. With global processing enabled, `Sonic pitch` appears for supported synths.
8. NVDA's normal `Pitch` setting still controls native synth pitch.
9. The separate `Sonic pitch` setting controls Sonic processing.
10. `Sonic pitch` value `50` is neutral.
11. Lower values lower speech.
12. Higher values raise speech.
13. With extended range disabled, the audible range is the normal range.
14. With `Increase Sonic pitch range to 20 semitones` enabled, the same slider
    covers the extended range and remains neutral at `50`.
15. Different supported synthesizers keep different `Sonic pitch` values.
16. Different voices inside the same supported synth keep different
    `Sonic pitch` values.
17. Switching back to a voice restores that voice's stored value.
18. Changes made in Voice settings are previewed live.
19. Escape or Cancel restores the previous Voice settings value.
20. OK or Apply commits the new Voice settings value.
21. Changes made through the synth settings ring are committed immediately.
22. Input Gesture scripts appear in the `Global Sonic Pitch` category.

## Synth Paths

1. RHVoice works when speech audio reaches NVDA's main audio path.
2. eSpeak NG works in NVDA's main process.
3. OneCore works in NVDA's main process.
4. Standard 64-bit SAPI5 works when it uses NVDA's normal audio path.
5. Standard `sapi5_32` works on 64-bit NVDA through the bundled host wrapper.
6. Standard `sapi4_32` works on 64-bit NVDA through the bundled host wrapper
   when NVDA's SAPI4 WASAPI path is active.
7. eSpeak-NG SAPI works through SAPI5 after it is configured in its own
   configuration tool and visible in NVDA's normal SAPI5 voice list.
8. The add-on does not add SAPI voice-list entries.
9. The add-on does not write SAPI registry voice tokens.

## Stress Tests

1. Change `Sonic pitch` rapidly with PageUp/PageDown in Voice settings.
2. Repeat rapid downward changes while SAPI5 is speaking.
3. Repeat rapid downward changes with eSpeak-NG SAPI at high rate.
4. On 64-bit NVDA, repeat rapid changes with standard `sapi5_32`.
5. On 64-bit NVDA, repeat rapid changes with standard `sapi4_32`.
6. Confirm speech continues and NVDA does not freeze.
7. Confirm the 32-bit host log does not show access violations.
8. Confirm the next utterance uses the latest selected `Sonic pitch`.
9. Confirm say-all or continuous reading does not obviously regress.

## Localization

1. English add-on help opens.
2. Polish add-on help opens.
3. Slovak add-on help opens.
4. Polish interface strings load in a Polish NVDA locale.
5. Slovak interface strings load in a Slovak NVDA locale.
6. `addon/locale/nvda.pot` contains all UI `msgid` entries from the shipped
   `.po` files.

## Support Prompt

1. During install or update, the optional support prompt appears outside NVDA
   minimal mode.
2. Choosing `No` continues installation.
3. Choosing `Yes` opens `https://buycoffee.to/kazimierz-parzych` in the default
   browser.
4. The settings panel `Support the author` button opens the same page.
5. The `Open support page` Input Gesture command opens the same page.

## Logs

Expected useful entries when debug logging is enabled:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: processed speech audio`
- `globalSonicPitch: applied remote 32-bit Sonic pitch`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`
- `globalSonicPitch sapi4_32 host: processed SAPI4 audio`

## Packaging

Zip the contents of the `addon` directory, not the outer project directory, and
use the `.nvda-addon` extension.

Expected package name for version 1.0:

```text
globalSonicPitch-1.0.nvda-addon
```

Before release:

1. Confirm `addon/manifest.ini` has the release version.
2. Confirm the package contains English, Polish, and Slovak help.
3. Confirm the package contains Polish and Slovak locale files.
4. Confirm the package does not contain `__pycache__`.
5. Confirm SHA256 is recorded in release notes and store submission notes.
