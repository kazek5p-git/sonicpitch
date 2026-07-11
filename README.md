# SAPI5 Sonic Pitch

SAPI5 Sonic Pitch is an NVDA add-on that adds separate Microsoft SAPI5
synthesizers with pitch correction handled through NVDA's Sonic audio stream.

Polish documentation: [README.pl.md](README.pl.md)

## What It Adds

The add-on adds two synthesizer choices:

- `SAPI5 32-bit Sonic Pitch`
- `SAPI5 64-bit Sonic Pitch`

These are separate synthesizers. The add-on does not replace, patch, or modify
NVDA's built-in `sapi5` and `sapi5_32` synthesizers. If the add-on is disabled,
the standard SAPI5 synthesizers should behave exactly as they did before.

## When To Use It

Use this add-on when a SAPI5 voice ignores NVDA's normal pitch setting or changes
pitch poorly through the standard SAPI XML mechanism.

The add-on is only for SAPI5 voices. It does not affect OneCore, eSpeak,
RHVoice, Vocalizer, or any other NVDA synthesizer.

## Requirements

- NVDA 2025.1 or newer.
- Windows with at least one SAPI5 voice installed.
- A recent NVDA audio path that exposes the internal Sonic stream.
- For 32-bit SAPI5 voices on 64-bit NVDA, NVDA's built-in 32-bit synth host must
  be present and working.

The current release was tested locally on NVDA 2026.2 beta, 64-bit.

## Installation

1. Download the latest `.nvda-addon` file from
   [Releases](https://github.com/kazek5p-git/sapi5-sonic-pitch/releases/latest).
2. Open the downloaded file with NVDA.
3. Confirm installation.
4. Restart NVDA when prompted.
5. Open NVDA's synthesizer dialog and choose `SAPI5 32-bit Sonic Pitch` or
   `SAPI5 64-bit Sonic Pitch`.

## Using Pitch

After selecting one of the Sonic Pitch synthesizers, use NVDA's normal voice
settings to change pitch.

- Pitch `50` is neutral.
- Values below `50` lower the voice.
- Values above `50` raise the voice.
- The full NVDA pitch range maps to roughly `-6` to `+6` semitones.
- The Sonic pitch ratio is clamped to `0.70..1.45` to avoid extreme values.

Rate, volume, voice selection, and rate boost are still handled by NVDA's normal
SAPI5 driver behavior. Sonic Pitch only changes how the global pitch setting is
applied.

## 32-bit And 64-bit SAPI5

SAPI5 voices are registered separately for 32-bit and 64-bit applications. This
is why the add-on exposes two synthesizers.

`SAPI5 64-bit Sonic Pitch` uses the normal 64-bit SAPI5 path in 64-bit NVDA.

`SAPI5 32-bit Sonic Pitch` uses NVDA's 32-bit synth host when running under
64-bit NVDA. This allows 32-bit SAPI5 voices to keep working while the pitch
change is applied inside the 32-bit host process.

Each synthesizer shows only the voices available to its own SAPI5 bitness.

## Troubleshooting

If the add-on does not appear in the synthesizer list, check that the installed
NVDA version is new enough and that the matching SAPI5 path is available.

If the 32-bit Sonic Pitch synthesizer does not load, first test NVDA's built-in
`Microsoft Speech API version 5 (32 bit)` synthesizer. If the built-in
synthesizer also fails, the problem is outside this add-on.

If the standard `sapi5` or `sapi5_32` synthesizer fails only while this add-on is
enabled, check that you are using version `0.1.8` or newer. Older development
builds briefly included a global repair plugin. Current releases do not install
any global plugin.

Useful NVDA log locations:

- Current log: `%TEMP%\nvda.log`
- Previous log: `%TEMP%\nvda-old.log`
- 32-bit synth host logs: `%TEMP%\nvda_synthDriverHost.*.log`

Search the logs for:

- `sapi5SonicPitch`
- `sapi5SonicPitch32`
- `sapi5SonicPitch64`
- `Sonic pitch unavailable`

## Known Limitations

- The add-on uses private NVDA WASAPI/Sonic internals.
- Future NVDA changes to `sonicStream`, `_initWasapiAudio`, or the 32-bit synth
  host may require add-on updates.
- Legacy non-WASAPI audio paths do not expose the Sonic stream, so Sonic Pitch
  cannot work there.
- Embedded pitch commands inside a speech sequence may be neutralized because the
  add-on keeps SAPI XML pitch at neutral to avoid double pitch processing.

## Build From Source

The add-on package root is `addon`.

To build manually:

1. Zip the contents of `addon`, not the outer project directory.
2. Rename the archive to `sapi5SonicPitch-<version>.nvda-addon`.

PowerShell example:

```powershell
Compress-Archive -Path .\addon\* -DestinationPath .\dist\sapi5SonicPitch.zip -Force
Move-Item .\dist\sapi5SonicPitch.zip .\dist\sapi5SonicPitch-0.1.9.nvda-addon -Force
```

Before publishing a package, run a syntax check:

```powershell
python -m py_compile `
  addon\synthDrivers\_sapi5SonicPitch32Host.py `
  addon\synthDrivers\_sapi5SonicPitchCommon.py `
  addon\synthDrivers\sapi5SonicPitch32.py `
  addon\synthDrivers\sapi5SonicPitch64.py
```

## Repository Layout

- `addon/manifest.ini` - NVDA add-on manifest.
- `addon/synthDrivers/` - Sonic Pitch synthesizer drivers.
- `addon/doc/en/readme.md` - English add-on help.
- `addon/doc/pl/readme.md` - Polish add-on help.
- `INSPECTION.md` - local NVDA runtime inspection notes.
- `TESTING.md` - manual test matrix.
- `docs/technical-notes.md` - implementation notes.
