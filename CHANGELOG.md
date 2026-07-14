# Changelog

## 0.4.20

- Adds an optional extended Sonic pitch range of approximately `-20..+20`
  semitones.
- Adds Sonic pitch processing for standard `sapi4_32` on 64-bit NVDA through
  the bundled 32-bit host wrapper when NVDA's SAPI4 WASAPI path is active.
- Keeps remote 32-bit SAPI processing inside the 32-bit synth host to avoid
  accidental processing of unrelated main-process speech-purpose audio.
- Updates documentation and testing notes for the current SAPI4/SAPI5 host
  paths.

## 0.4.19

- Reorganizes public README files into a shorter add-on overview with links to
  detailed documentation.
- Cleans bundled add-on help so it describes the current Global Sonic Pitch
  add-on only.
- Rewrites technical notes and manual testing documentation around the current
  implementation.
- No audio behavior changes.

## 0.4.18

- Stores `Sonic pitch` separately for each supported synthesizer and selected
  voice.
- Refreshes the active runtime Sonic pitch after voice changes, including the
  standard `sapi5_32` host path on 64-bit NVDA.
- Adds Polish and Slovak UI translations, localized add-on manifest metadata,
  and bundled Slovak help documentation.
- Adds a gettext translation template at `addon/locale/nvda.pot`.

## 0.4.17

- Updates add-on author and store publisher metadata to list Kazimierz Parzych
  and DJ Graco.

## 0.4.15

- Stabilizes rapid `Sonic pitch` changes for standard `sapi5_32` on 64-bit
  NVDA.
- Serializes the 32-bit SAPI audio callback with host-side Sonic pitch changes.
- Replaces the host Sonic stream when the applied pitch changes.
- Recovers from host Sonic write or flush failures without leaving the speech
  path silent.

## 0.4.13

- Adds Sonic pitch control for standard `sapi5_32` on 64-bit NVDA through a
  bundled 32-bit host wrapper.
- Keeps the standard NVDA `sapi5_32` synthesizer entry.
- Makes Voice settings changes transactional: OK or Apply commits previewed
  values, while Escape or Cancel restores the previous value.

## 0.4.10

- Bundles local 32-bit and 64-bit Sonic native libraries with the add-on.
- Keeps a fallback to NVDA's internal Sonic module when available.
- Adds Apache 2.0 license metadata for the bundled Sonic native binaries.
