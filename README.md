# Global Sonic Pitch

Global Sonic Pitch is an NVDA add-on that can apply NVDA speech pitch through
Sonic audio processing in the main NVDA process.

Polish documentation: [README.pl.md](README.pl.md)

## What It Adds

The add-on adds a global plugin and an NVDA settings panel named
`Global Sonic Pitch`.

It does not add synthesizers to NVDA's synthesizer dialog. The standard
`sapi5`, `sapi5_32`, OneCore, eSpeak, RHVoice, Vocalizer, and other synth
choices remain the normal NVDA synth drivers.

When global pitch is enabled:

- NVDA's normal pitch setting is captured by the add-on.
- The selected synth's native pitch is held at neutral `50`, where supported.
- Sonic applies the configured pitch to the outgoing speech audio.
- Values below `50` lower speech and values above `50` raise speech.

## Requirements

- NVDA 2025.1 or newer.
- A modern NVDA audio path that exposes the internal Sonic stream.
- A synth driver that sends 16-bit PCM speech audio through NVDA's main
  `WavePlayer`.

The current release was tested locally on NVDA 2026.2 beta, 64-bit.

## Installation

1. Download the latest `.nvda-addon` file from
   [Releases](https://github.com/kazek5p-git/sapi5-sonic-pitch/releases/latest).
2. If `SAPI5 Sonic Pitch` / `sapi5SonicPitch` is installed, remove that older
   add-on first and restart NVDA.
3. Open the downloaded `globalSonicPitch-<version>.nvda-addon` file with NVDA.
4. Confirm installation and restart NVDA.
5. Open NVDA Settings, choose `Global Sonic Pitch`, and enable global Sonic
   pitch.

## Using Pitch

After global Sonic pitch is enabled, use NVDA's normal voice settings or synth
settings ring to change pitch. The add-on captures that value, keeps the synth's
native pitch neutral, and applies the change through Sonic.

The settings panel also exposes a `Sonic pitch` slider. It is useful when you
want to set the same value without going through the voice settings ring.

Pitch mapping:

- `50` is neutral.
- `0..49` lowers the voice.
- `51..100` raises the voice.
- The full range maps to roughly `-6..+6` semitones.
- The Sonic pitch ratio is clamped to `0.70..1.45`.

## Supported And Unsupported Paths

Global Sonic Pitch works in the main NVDA process. It is expected to work with
PCM synths such as eSpeak, RHVoice, OneCore, 64-bit SAPI5, and similar drivers
when their audio reaches NVDA's main `WavePlayer`.

The built-in `sapi5_32` synthesizer is a special case on 64-bit NVDA. It speaks
inside NVDA's separate 32-bit synth host, so this global plugin cannot process
that audio. For that synth, the add-on deliberately does not take over pitch; it
leaves native `sapi5_32` behavior alone.

## Troubleshooting

If old `SAPI5 32-bit Sonic Pitch` or `SAPI5 64-bit Sonic Pitch` entries still
appear in the synthesizer list, the old `sapi5SonicPitch` add-on is still
installed. Remove it and restart NVDA.

Useful NVDA log locations:

- Current log: `%TEMP%\nvda.log`
- Previous log: `%TEMP%\nvda-old.log`
- 32-bit synth host logs: `%TEMP%\nvda_synthDriverHost.*.log`

Search the logs for:

- `globalSonicPitch`
- `pitch takeover active`
- `captured NVDA pitch`
- `processed speech audio`
- `Sonic is unavailable`

## Known Limitations

- The add-on uses private NVDA Sonic and `WavePlayer` internals.
- It processes speech audio only in the main NVDA process.
- It processes 16-bit PCM speech blocks and bypasses anything else.
- Future NVDA changes to `nvwave.WavePlayer.feed`,
  `synthDrivers._sonic.SonicStream`, or synth pitch settings may require add-on
  updates.
- Embedded pitch commands inside a speech sequence may still be native to the
  synth. The add-on controls the normal NVDA pitch setting.

## Build From Source

The add-on package root is `addon`.

To build manually:

1. Zip the contents of `addon`, not the outer project directory.
2. Rename the archive to `globalSonicPitch-<version>.nvda-addon`.

PowerShell example:

```powershell
New-Item -ItemType Directory -Path .\dist -Force | Out-Null
Compress-Archive -Path .\addon\* -DestinationPath .\dist\globalSonicPitch.zip -Force
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.3.0.nvda-addon -Force
```

Before publishing a package, run a syntax check:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py
```

## Repository Layout

- `addon/manifest.ini` - NVDA add-on manifest.
- `addon/globalPlugins/` - global Sonic pitch processor and settings panel.
- `addon/doc/en/readme.md` - English add-on help.
- `addon/doc/pl/readme.md` - Polish add-on help.
- `INSPECTION.md` - local NVDA runtime inspection notes.
- `TESTING.md` - manual test matrix.
- `docs/technical-notes.md` - implementation notes.
