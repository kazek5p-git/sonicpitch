# Changelog

## 0.4.4

- Fixes freezes with some SAPI5 voices, including eSpeak-NG SAPI, when Sonic
  pitch is lowered rapidly during active speech.
- Reverts the 0.4.3 in-place `SonicStream.pitch` update path. Pitch changes now
  reset the active Sonic processor and start a fresh stream on the next audio
  block instead of mutating the stream currently being fed by SAPI callbacks.
- Avoids flushing and feeding the old Sonic stream tail when pitch changes
  mid-utterance, reducing the chance of re-entrant SAPI/WavePlayer callbacks.
- Adds locking around the per-player Sonic processor map and resets processors
  when global mode or the Sonic pitch value changes.
- Confirms standard SAPI5 still loads normally after testing with a configured
  eSpeak-NG SAPI profile and the built-in SAPI5 voice.

## 0.4.3

- Adds a `Support the author` button to the add-on settings panel.
- Adds an assignable `Open support page` Input Gesture command.
- Adds an optional install-time support prompt that can open the same BuyCoffee
  page.
- Keeps the active Sonic stream when only `Sonic pitch` changes, reducing empty
  output blocks and dropouts during rapid pitch changes.
- Defers Voice dialog setting injection after synth changes made from NVDA
  settings, reducing refresh races with some SAPI5 voices.
- Documents the external BuyCoffee support link and clarifies that the add-on
  does not process payments, store payment data, or unlock features based on
  support.

## 0.4.2

- Shows the dynamic `Sonic pitch` setting in NVDA Voice settings and the synth
  settings ring only while `Enable global Sonic pitch` is enabled.
- Removes the `Sonic pitch` voice setting again when global Sonic pitch is
  disabled, leaving NVDA's normal voice settings uncluttered.
- Updates documentation to clarify that the add-on settings panel is always
  available, while the Voice dialog/ring setting is conditional.

## 0.4.1

- Changes global mode so NVDA's normal `Pitch` setting remains the synth's
  native pitch control even when Sonic pitch processing is enabled.
- Keeps `Sonic pitch` as the separate add-on-controlled Sonic processing value
  exposed in the add-on panel, Voice settings, synth settings ring, and
  assignable Input Gestures.
- Updates Polish and English documentation to describe the two independent pitch
  controls.

## 0.4.0

- Adds a dynamic `Sonic pitch` numeric setting to supported synths, so NVDA's
  standard Voice dialog and synth settings ring can expose the global Sonic
  pitch value without modifying NVDA itself.
- Integrates with `Synth ring settings selector` by adding `sonicPitch` to its
  available settings list when that add-on is present or loaded later.
- Adds assignable Input Gestures for increasing, decreasing, and resetting
  global Sonic pitch.
- Updates Polish and English documentation for the new Voice dialog/ring
  control path.

## 0.3.2

- Expands Polish and English user documentation with quick start, settings,
  compatibility, migration, verification, troubleshooting, logs, and build
  sections.
- Rewrites the packaged NVDA help files in Polish and English so the installed
  add-on includes practical usage and diagnostic guidance.
- No runtime behavior changes from 0.3.1.

## 0.3.1

- Changes project links to the renamed GitHub repository `sonicpitch`.
- Reworks global Sonic audio processing to keep a continuous `SonicStream` per
  speech `WavePlayer` instead of creating and flushing a new stream for every
  audio block.
- Adds a small first-chunk buffer, matching NVDA's SAPI5 Sonic strategy, to
  reduce underruns and micro-gaps while speech starts.
- Flushes the remaining Sonic stream tail at `WavePlayer.idle()` and resets it
  on stop/close.

## 0.3.0

- Renames the add-on identity to `globalSonicPitch` with the display name
  `Global Sonic Pitch`.
- Removes the previous custom SAPI5 synth drivers from the package, so the
  add-on no longer adds synthesizer choices.
- Adds runtime pitch takeover for supported synth drivers: NVDA pitch is stored
  as the Sonic pitch, while the native synth pitch is held at neutral `50`.
- Migrates enabled state, pitch, and debug logging from the old
  `[sapi5SonicPitchGlobal]` config section.
- Keeps built-in `sapi5_32` excluded from global takeover on 64-bit NVDA because
  its audio is produced in the separate 32-bit synth host.
- Updates English and Polish documentation for the global-only add-on design.

## 0.2.0

- Adds an experimental global Sonic pitch processor.
- Installs a global plugin that can hook `nvwave.WavePlayer.feed` for speech
  audio only.
- Adds an NVDA settings panel for enabling global processing, setting global
  Sonic pitch, enabling debug logs, and optionally processing the add-on's own
  SAPI5 Sonic Pitch synthesizers.
- Keeps global Sonic processing disabled by default.
- Keeps the existing `SAPI5 32-bit Sonic Pitch` and `SAPI5 64-bit Sonic Pitch`
  synthesizers.
- Leaves NVDA's built-in synthesizer drivers unmodified.

## 0.1.9

- Documentation-focused release.
- Expands the GitHub README with installation, usage, troubleshooting, build,
  and repository layout sections.
- Adds a Polish GitHub README.
- Expands the English and Polish add-on help included in the `.nvda-addon`
  package.
- Adds technical maintenance notes for the 32-bit host path, Sonic pitch mapping,
  and NVDA private API usage.
- No synthesizer behavior changes from 0.1.8.

## 0.1.8

- Provides separate `SAPI5 32-bit Sonic Pitch` and `SAPI5 64-bit Sonic Pitch`
  synthesizers.
- Applies NVDA's global pitch setting through Sonic instead of SAPI XML pitch.
- Keeps standard NVDA `sapi5` and `sapi5_32` synthesizers untouched.
- Removes the experimental global repair plugin used in earlier development
  builds.
- Synchronizes Sonic stream access to avoid crashes while lowering pitch during
  active speech.
- Recreates the WASAPI/Sonic stream when pitch changes while the SAPI5 path is
  active.
- Includes Polish and English add-on help.
