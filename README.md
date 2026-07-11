# Global Sonic Pitch

Global Sonic Pitch is an NVDA add-on that captures NVDA's normal speech pitch
setting and applies it through Sonic audio processing. It works globally for
synthesizers whose speech audio is played through NVDA's main process.

Polish documentation: [README.pl.md](README.pl.md)

## Key Points

- The add-on does not add synthesizers to NVDA's synthesizer dialog.
- When global mode is enabled, NVDA's normal `Pitch` setting controls Sonic.
- The active synth's native pitch is held at neutral `50` where the driver
  allows pitch takeover.
- Speech audio is filtered through Sonic in NVDA's main `WavePlayer`.
- Standard `sapi5_32` on 64-bit NVDA is deliberately skipped because it speaks
  in a separate 32-bit synth host.

## Who This Is For

Use Global Sonic Pitch when you want one Sonic-based pitch method across several
NVDA synthesizers, especially when a voice's native pitch control sounds poor or
behaves inconsistently.

Tested locally with:

- RHVoice;
- eSpeak NG;
- OneCore;
- 64-bit SAPI5;
- standard 32-bit SAPI5 as a loadable but intentionally unprocessed path.

## Requirements

- NVDA 2025.1 or newer.
- Windows.
- A modern NVDA audio path with Sonic available.
- A synthesizer that feeds 16-bit PCM speech audio through NVDA's main
  `WavePlayer`.

Latest local test target: NVDA 2026.2 beta, 64-bit.

## Installation

1. Download the latest `.nvda-addon` file from
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. If the older `SAPI5 Sonic Pitch` / `sapi5SonicPitch` add-on is installed,
   remove it first and restart NVDA.
3. Open `globalSonicPitch-<version>.nvda-addon` with NVDA.
4. Confirm installation.
5. Restart NVDA.
6. Open NVDA Settings and choose `Global Sonic Pitch`.
7. Enable `Enable global Sonic pitch`.

## Quick Start

1. Select a normal NVDA synth, such as RHVoice, eSpeak, OneCore, or 64-bit
   SAPI5.
2. Enable `Global Sonic Pitch` in NVDA settings.
3. Change pitch with NVDA's normal voice setting.
4. Treat pitch `50` as neutral.
5. If the result sounds wrong, return to `50` or disable global mode.

## Settings

The `Global Sonic Pitch` panel contains:

- `Enable global Sonic pitch` - turns global pitch takeover on or off.
- `Sonic pitch` - sets the pitch value used by Sonic.
- `Enable debug logging` - writes detailed diagnostic entries to the NVDA log.

When the add-on is enabled, NVDA's normal voice settings ring changes the same
value as the `Sonic pitch` slider.

## Pitch Behavior

NVDA exposes pitch from `0` to `100`.

- `50` is neutral.
- `0..49` lowers speech.
- `51..100` raises speech.
- The full range maps to roughly `-6..+6` semitones.
- The Sonic ratio is clamped to `0.70..1.45` to avoid extreme distortion.

When global mode is enabled, the add-on captures the pitch change, stores it in
its own configuration, and sets the native synth pitch to `50`. This prevents
double pitch shifting by the synth and Sonic at the same time.

## Synth Compatibility

| Synth | Expected behavior |
| --- | --- |
| RHVoice | Supported when audio reaches the main `WavePlayer`. |
| eSpeak NG | Supported in NVDA's main process. |
| OneCore | Supported in NVDA's main process. |
| 64-bit SAPI5 | Supported when it uses NVDA's audio path. |
| 32-bit SAPI5 on 64-bit NVDA | Loads normally, but global Sonic does not process it. |
| Other synths | May work if they feed 16-bit PCM through the main `WavePlayer`. |

## Important 32-bit SAPI5 Limitation

Standard `sapi5_32` on 64-bit NVDA speaks through a separate 32-bit synth host.
This add-on's global plugin is loaded in the main NVDA process, not in that
host. Therefore, the add-on does not take over `sapi5_32` pitch and does not
process its audio through Sonic.

This is intentional. It keeps standard `sapi5_32` loading normally and avoids
neutralizing native pitch when Sonic cannot process that audio path.

## Migration From SAPI5 Sonic Pitch

Versions 0.1.x and 0.2.x used the add-on id `sapi5SonicPitch` and added custom
SAPI5 Sonic Pitch synthesizers. The current add-on works differently:

- the new add-on id is `globalSonicPitch`;
- it does not add anything to the synthesizer dialog;
- the old `sapi5SonicPitch` folder should be removed;
- settings from the experimental `[sapi5SonicPitchGlobal]` section are migrated
  at startup.

If `SAPI5 32-bit Sonic Pitch` or `SAPI5 64-bit Sonic Pitch` still appears in
the synthesizer dialog, the old add-on is still installed.

## Verifying That It Works

1. Enable `Enable debug logging` in the `Global Sonic Pitch` settings panel.
2. Restart NVDA.
3. Select RHVoice, eSpeak, OneCore, or 64-bit SAPI5.
4. Set pitch to something other than `50`, such as `75`.
5. Open the current NVDA log at `%TEMP%\nvda.log`.

Expected log entries:

```text
globalSonicPitch: installed WavePlayer speech feed hook
globalSonicPitch: installed synth pitch takeover hook
globalSonicPitch: pitch takeover active; synth=RHVoice; sonicPitch=75; nativePitch=50
globalSonicPitch: processed speech audio; synth=RHVoice; pitch=75
```

For `sapi5_32`, the expected entry is:

```text
globalSonicPitch: pitch takeover not available for synth=sapi5_32
```

## Troubleshooting

### Pitch Does Not Change

Check that global mode is enabled and pitch is not `50`. Then check the NVDA
log for `processed speech audio`. If that entry is missing, the selected synth
probably does not feed audio through NVDA's main `WavePlayer`.

### The Synth Still Changes Its Native Pitch

Enable debug logging and look for `pitch takeover active`. If the entry is
missing, the add-on could not take over that driver's pitch setting. Sonic may
still process audio, but the synth's native pitch might not be locked.

### Audio Has Small Gaps Or Artifacts

Since version 0.3.1, the add-on keeps a continuous Sonic stream for the active
`WavePlayer` and avoids flushing every small block. If gaps remain, check CPU
load, extreme pitch values, and whether the issue happens with more than one
synth.

### Standard 32-bit SAPI5 Has No Global Sonic Pitch

This is a known limitation. `sapi5_32` runs in a separate host and is not
globally filtered by this add-on.

### Old Sonic Pitch Synths Still Appear

Remove the old `sapi5SonicPitch` add-on from NVDA's add-on manager or delete
`%APPDATA%\nvda\addons\sapi5SonicPitch`, then restart NVDA.

## Log Files

- Current log: `%TEMP%\nvda.log`
- Previous log: `%TEMP%\nvda-old.log`
- 32-bit synth host logs: `%TEMP%\nvda_synthDriverHost.*.log`

Useful search terms:

- `globalSonicPitch`
- `pitch takeover active`
- `captured NVDA pitch`
- `processed speech audio`
- `pitch takeover not available`
- `Sonic is unavailable`

## Technical Summary

The add-on runs only at NVDA runtime. It does not modify NVDA's installed files.

It uses:

- an NVDA global plugin;
- a hook on `nvwave.WavePlayer.feed`;
- hooks on `WavePlayer.idle`, `stop`, and `close` to finish or discard Sonic
  stream state;
- runtime takeover of the active synth's `_set_pitch` and `_get_pitch` methods;
- NVDA's internal `synthDrivers._sonic.SonicStream`.

Sonic is kept as a continuous stream per `WavePlayer`. This is important for
audio quality because repeatedly creating a stream and flushing every small
block can cause micro-gaps.

## Build From Source

The add-on package root is `addon`.

Manual build:

1. Zip the contents of `addon`, not the outer project directory.
2. Rename the archive to `globalSonicPitch-<version>.nvda-addon`.

PowerShell example:

```powershell
New-Item -ItemType Directory -Path .\dist -Force | Out-Null
Compress-Archive -Path .\addon\* -DestinationPath .\dist\globalSonicPitch.zip -Force
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.3.2.nvda-addon -Force
```

Syntax check:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py
```

## Repository Layout

- `addon/manifest.ini` - NVDA add-on manifest.
- `addon/globalPlugins/globalSonicPitch.py` - main plugin.
- `addon/doc/en/readme.md` - English add-on help.
- `addon/doc/pl/readme.md` - Polish add-on help.
- `docs/technical-notes.md` - maintenance notes.
- `TESTING.md` - test matrix.
- `CHANGELOG.md` - release history.
