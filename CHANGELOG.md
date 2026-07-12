# Changelog

## 0.4.16

- Updates add-on author metadata to include both `Kazek` and `DJ Graco`.
- No audio processing behavior changes from 0.4.15.

## 0.4.15

- Further stabilizes standard `sapi5_32` on 64-bit NVDA during rapid Voice
  dialog `Sonic pitch` changes.
- Serializes the entire 32-bit SAPI `RemoteWrite` audio callback with
  host-side Sonic pitch changes, instead of locking only individual Sonic calls.
- Replaces the host Sonic stream when the applied `sonicPitch` changes, keeping
  retired streams alive for the host process instead of retuning a previously
  used native stream.
- Recovers from host Sonic write or flush failures by replacing the stream and
  dropping the damaged audio block, preventing the remote SAPI path from going
  silent until the synth is reloaded.

## 0.4.14

- Stabilizes rapid `Sonic pitch` changes for standard `sapi5_32` on 64-bit
  NVDA.
- Defers host-side `sonicPitch` updates until a safe 32-bit SAPI speech
  boundary instead of retuning the host Sonic stream during active speech.
- Serializes host-side Sonic stream reads, writes, flushes, and pitch updates
  through a reentrant lock.
- Fixes a case where 64-bit NVDA 2026.1.1 could keep running while the
  `sapi5_32` speech path stopped talking after quick pitch changes.
- Keeps the standard NVDA `sapi5_32` synthesizer entry and still does not
  modify NVDA files on disk.

## 0.4.13

- Adds Sonic pitch control for standard `sapi5_32` on 64-bit NVDA through a
  bundled 32-bit host wrapper.
- Keeps the standard NVDA `sapi5_32` synthesizer entry; the add-on still does
  not add replacement synthesizers or modify NVDA files on disk.
- Stores SAPI5 Sonic pitch values with architecture-aware keys: `sapi5_64` for
  the 64-bit SAPI5 path and `sapi5_32` for 32-bit SAPI5.
- Makes Voice dialog changes transactional. `Sonic pitch` changes are previewed
  live, OK or Apply commits them, and Escape or Cancel restores the previous
  value.
- Applies remote `sapi5_32` pitch changes immediately through the 32-bit host
  service and logs the host-side `sonicPitch` application.
- Updates English and Polish documentation, technical notes, and manual testing
  instructions for the new SAPI5 architecture behavior.

## 0.4.12

- Prepares the package for NVDA Add-on Store submission.
- Sets `lastTestedNVDAVersion` to the latest stable target `2026.1.1` instead
  of the locally tested 2026.2 beta target.
- Adds root licensing documentation for the add-on source and third-party Sonic
  native binaries.
- Adds store submission notes, metadata draft, and a release verification
  checklist.
- Adds translator comments for visible UI strings and gesture descriptions.
- No audio processing behavior changes from 0.4.11.

## 0.4.11

- Improves `Sonic pitch` slider responsiveness for rapid PageUp/PageDown
  changes in NVDA Voice settings and the synth settings ring.
- Treats empty WavePlayer feed markers with callbacks as utterance boundaries,
  so the next short feedback message uses the latest stored Sonic pitch.
- Avoids keeping a neutral `Sonic pitch` value pinned to the player, preventing
  later non-neutral changes from being skipped until another movement.
- Applies a changed `Sonic pitch` by creating a fresh Sonic stream at the next
  safe boundary instead of retuning an already-used native stream in place.
- Keeps the 0.4.10 32-bit no-destroy Sonic stream workaround intact.

## 0.4.10

- Bundles local 32-bit and 64-bit Sonic native libraries with the add-on and
  prefers them over NVDA's internal `sonic.dll`.
- Keeps a fallback to NVDA's internal Sonic library if the bundled library is
  missing or cannot be loaded.
- Avoids native `sonicDestroyStream` for 32-bit NVDA processes and reuses the
  active Sonic stream after stop/idle/reset events, preventing a reproduced
  `0xc0000374` native heap crash on NVDA 2025.3.3 x86 with SAPI5.
- Removes the unused eSpeak-NG SAPI voice-enumeration compatibility hook so the
  add-on no longer modifies SAPI5 or `sapi5_32` voice lists.
- Adds Apache 2.0 license metadata for the bundled Sonic native binaries.

## 0.4.9

- Changes Sonic pitch application to be utterance-scoped for all supported
  synthesizers.
- `Sonic pitch` values are still saved immediately, but active Sonic streams are
  no longer reset or replaced in the middle of speech.
- New values start with the next utterance, reducing the chance of native Sonic
  or SAPI callback instability during rapid pitch changes.
- Keeps SAPI5 support enabled; this is a stability workaround, not a synth
  compatibility block.
- Clears per-utterance Sonic state on idle, stop, close, and synth changes.

## 0.4.8

- Changes `Sonic pitch` from one shared global value to a value stored
  separately for each supported synthesizer.
- Removes the `Sonic pitch` slider from the `Global Sonic Pitch` settings
  panel. The panel now only controls global enablement, debug logging, and the
  support button.
- Keeps the dynamic `Sonic pitch` control in NVDA Voice settings and the synth
  settings ring while global Sonic pitch is enabled and the active synth is
  supported.
- Updates Input Gesture scripts so increase, decrease, reset, and status report
  operate on the current supported synthesizer's Sonic pitch value.
- Migrates an existing legacy global `pitch` value to the current supported
  synth on first use, then resets the legacy key to neutral.

## 0.4.7

- Extends the eSpeak-NG SAPI dynamic voice compatibility hook to NVDA's
  standard `sapi5_32` proxy voice list.
- Keeps `sapi5_32` as a native NVDA synth path: the add-on only supplements the
  visible voice list and still does not process the separate 32-bit synth host
  audio through Sonic.
- Verified locally that `sapi5_32` lists `Polish (sandro)` and `Polish klatt6`
  from `Speech\Voices\TokenEnums\eSpeak-NG`.
- Verified locally that `sapi5_32` accepts the `Polish (sandro)` eSpeak-NG SAPI
  token without a voice-load error.

## 0.4.6

- Adds a runtime compatibility hook for eSpeak-NG SAPI dynamic voice tokens.
- NVDA 2026.2 reads SAPI5 voices directly from the standard
  `Speech\Voices\Tokens` registry path, while eSpeak-NG SAPI exposes configured
  voices through `Speech\Voices\TokenEnums\eSpeak-NG`.
- The add-on now appends only eSpeak-NG SAPI dynamic tokens returned by the
  Windows SAPI enumerator to NVDA's standard `sapi5` voice list.
- Does not modify NVDA files or write registry voice tokens.
- Verified locally that NVDA's `sapi5` voice list includes configured
  `Polish (sandro)` and `Polish klatt6` eSpeak-NG SAPI voices.

## 0.4.5

- Reduces lock contention during Sonic processing for fast SAPI5 voices.
- Moves expensive Sonic `writeShort`, `readShort`, and `flush` calls out of the
  global player-processor map lock.
- Adds a per-stream lock so one Sonic stream is still protected from concurrent
  feed, drain, and finish calls.
- Hardens the eSpeak-NG SAPI case where rate is set to 100 and pitch is lowered
  rapidly during active speech.
- Validated locally with eSpeak-NG SAPI through SAPI5 at rate 100 using an
  aggressive 20-run pitch-change stress test.

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
