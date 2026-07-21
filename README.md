# Global Sonic Pitch

Global Sonic Pitch is an NVDA add-on that adds a separate `Sonic pitch` control
to supported synthesizers. It changes speech pitch through Sonic audio
processing while leaving NVDA's normal native `Pitch` setting unchanged.

## Quick Start

1. Install `globalSonicPitch-<version>.nvda-addon` from
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. Restart NVDA.
3. Open NVDA Settings and choose `Global Sonic Pitch`.
4. Enable `Enable global Sonic pitch`.
5. Open Voice settings or the synth settings ring and adjust `Sonic pitch`.

## Features

- Adds a `Global Sonic Pitch` settings panel.
- Adds a separate `Sonic pitch` setting while global processing is enabled.
- Keeps NVDA's normal `Pitch` setting as the synthesizer's native pitch.
- Stores `Sonic pitch` separately for each supported synthesizer and selected
  voice.
- Provides an optional extended range of approximately `-20..+20` semitones.
- Provides optional better-quality Sonic processing. Fast mode remains the
  default.
- Supports main-process NVDA synth audio and standard `sapi5_32` / `sapi4_32`
  on 64-bit NVDA through bundled 32-bit host wrappers.
- Includes bundled 32-bit and 64-bit Sonic native libraries.
- Provides English, Polish, and Slovak add-on help.
- Provides Polish and Slovak interface translations.

## Documentation

- Full English help: [addon/doc/en/readme.md](addon/doc/en/readme.md)
- Polish help: [addon/doc/pl/readme.md](addon/doc/pl/readme.md)
- Slovak help: [addon/doc/sk/readme.md](addon/doc/sk/readme.md)
- Technical notes: [docs/technical-notes.md](docs/technical-notes.md)
- Manual testing checklist: [TESTING.md](TESTING.md)
- Translation template: [addon/locale/nvda.pot](addon/locale/nvda.pot)

## Changes

- 1.1: Added optional better-quality Sonic processing for supported processing
  paths. Fast mode remains the default.
- 1.0: Stable release replacing the withdrawn 1.0 build. Improves short audio
  block handling and hardens Voice settings dialog cleanup.
- 0.4.20: Added optional 20-semitone range and standard `sapi4_32` host
  support on 64-bit NVDA.
- 0.4.19: Cleaned and reorganized public documentation for NVDA Add-on Store
  review. No audio behavior changes.
- 0.4.18: Added per-voice `Sonic pitch` values and Polish/Slovak
  localization.
- 0.4.15: Stabilized rapid `Sonic pitch` changes for standard `sapi5_32` on
  64-bit NVDA.
- 0.4.13: Added support for standard `sapi5_32` on 64-bit NVDA through the
  bundled host wrapper.
- 0.4.10: Bundled Sonic native libraries for 32-bit and 64-bit NVDA.

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Source Code

- Main plugin: [addon/globalPlugins/globalSonicPitch.py](addon/globalPlugins/globalSonicPitch.py)
- 32-bit SAPI5 host wrapper: [addon/sapi32HostDrivers/sapi5.py](addon/sapi32HostDrivers/sapi5.py)
- 32-bit SAPI4 host wrapper: [addon/sapi32HostDrivers/sapi4.py](addon/sapi32HostDrivers/sapi4.py)
- Bundled Sonic library notes: [addon/globalPlugins/sonicPitchNative/README.txt](addon/globalPlugins/sonicPitchNative/README.txt)

## Install

1. Download the latest `.nvda-addon` file from
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. In NVDA, open Add-on Store or Add-on Manager and choose to install from file.
3. Select the downloaded add-on package.
4. Restart NVDA when prompted.

Latest packaged add-on:
[globalSonicPitch-1.1.nvda-addon](https://github.com/kazek5p-git/sonicpitch/releases/latest)

## License

Global Sonic Pitch is licensed under GNU GPL version 2 or later. Bundled Sonic
native binaries are Apache 2.0 third-party components.
