# Changelog

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
