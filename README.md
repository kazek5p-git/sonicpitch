# Global Sonic Pitch

Global Sonic Pitch is an NVDA add-on that adds a separate `Sonic pitch` control
and applies it through Sonic audio processing. NVDA's normal `Pitch` setting
remains the active synth's native pitch control. The add-on works globally for
synthesizers whose speech audio is played through NVDA's main process.

Polish documentation: [README.pl.md](README.pl.md)

## Key Points

- The add-on does not add synthesizers to NVDA's synthesizer dialog.
- NVDA's normal `Pitch` setting continues to control the synth's native pitch.
- When global mode is enabled, the add-on adds its own `Sonic pitch` setting to
  Voice settings and the synth settings ring for supported synthesizers.
- `Sonic pitch` is a separate Sonic control and does not replace native `Pitch`.
- `Sonic pitch` is stored separately for each supported synthesizer.
- Speech audio is filtered through Sonic in NVDA's main `WavePlayer`.
- Standard `sapi5_32` on 64-bit NVDA is deliberately skipped because it speaks
  in a separate 32-bit synth host.
- The add-on includes an optional support link that opens BuyCoffee in the
  default browser.
- During installation, the add-on may ask whether to open the support page.

## Who This Is For

Use Global Sonic Pitch when you want an additional, independent Sonic-based
pitch control across several NVDA synthesizers, especially when a voice's native
pitch control sounds poor or behaves inconsistently.

Tested locally with:

- RHVoice;
- eSpeak NG;
- eSpeak-NG SAPI through SAPI5;
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
3. Change Sonic processing with the `Sonic pitch` voice setting, the synth
   settings ring, or an assigned Input Gesture. If `Sonic pitch` is not in Voice
   settings yet, enable global mode in the add-on panel and reopen Voice
   settings.
4. Change native synth pitch with NVDA's normal `Pitch` setting if you want to
   use both controls together.
5. Treat `Sonic pitch` value `50` as neutral. Each supported synthesizer keeps
   its own `Sonic pitch` value.
6. If the result sounds wrong, return to `50` or disable global mode.

## Settings

The `Global Sonic Pitch` panel contains:

- `Enable global Sonic pitch` - turns global Sonic pitch processing on or off.
- `Enable debug logging` - writes detailed diagnostic entries to the NVDA log.
- `Support the author` - opens the external BuyCoffee support page.

NVDA's normal `Pitch` setting remains the active synth's native pitch setting.
`Sonic pitch` is a separate add-on setting stored per supported synthesizer.

The add-on panel is always available in NVDA Settings so the feature can be
enabled or disabled.

While `Enable global Sonic pitch` is enabled, the add-on also tries to add a
separate `Sonic pitch` setting to NVDA's standard Voice dialog and synth
settings ring. This setting is injected dynamically into the active synth
without modifying NVDA itself. When global Sonic pitch is disabled, the setting
is removed from Voice settings and the synth settings ring.

There is intentionally no `Sonic pitch` slider in the add-on's global settings
panel. The global panel enables the audio processor; the `Sonic pitch` value is
changed from Voice settings, the synth settings ring, or assigned gestures for
the current supported synthesizer.

If `Synth ring settings selector` is installed, `sonicPitch` is added to its
available settings list so it can appear in the ring while global mode is on.

The `Global Sonic Pitch` category in Input Gestures contains:

- `Toggle global Sonic pitch`;
- `Report global Sonic pitch status`;
- `Open support page`;
- `Increase Sonic pitch for the current synthesizer`;
- `Decrease Sonic pitch for the current synthesizer`;
- `Reset Sonic pitch for the current synthesizer`.

These commands have no default gestures, so you can assign your own shortcuts.

## Support

The `Support the author` button in the settings panel, and the `Open support
page` Input Gesture command, open:

```text
https://buycoffee.to/kazimierz-parzych
```

This is a voluntary external support link. The add-on does not process payments,
store payment data, or unlock any features based on support.

During installation or update, Sonic Pitch also shows a small optional support
message. Choosing `Yes` opens the same page in the default browser. Choosing
`No` continues installation without changing add-on behavior.

## Pitch Behavior

NVDA exposes pitch from `0` to `100`.

- `50` is neutral.
- `0..49` lowers speech.
- `51..100` raises speech.
- The full range maps to roughly `-6..+6` semitones.
- The Sonic ratio is clamped to `0.70..1.45` to avoid extreme distortion.

When global mode is enabled, the add-on processes speech audio through Sonic
using the active synthesizer's own `Sonic pitch` value. NVDA's normal `Pitch`
setting still changes the synth's native pitch. If both sliders are away from
`50`, you will hear the combined result.

Starting with version 0.4.9, `Sonic pitch` changes are applied at utterance
boundaries. Moving the `Sonic pitch` control saves the new value immediately,
but an already speaking Sonic stream keeps its current value until that
utterance ends. The next utterance uses the new value. This avoids replacing
native Sonic processing objects inside active speech callbacks.

## Synth Compatibility

| Synth | Expected behavior |
| --- | --- |
| RHVoice | Supported when audio reaches the main `WavePlayer`. |
| eSpeak NG | Supported in NVDA's main process. |
| eSpeak-NG SAPI through SAPI5 | Supported as a SAPI5 voice after it is configured in the eSpeak-NG SAPI configurator. Version 0.4.6 and newer help NVDA list these dynamic voices in standard `sapi5`; version 0.4.7 and newer also supplement the standard `sapi5_32` voice list. |
| OneCore | Supported in NVDA's main process. |
| 64-bit SAPI5 | Supported when it uses NVDA's audio path. |
| 32-bit SAPI5 on 64-bit NVDA | Loads normally, but global Sonic does not process it. |
| Other synths | May work if they feed 16-bit PCM through the main `WavePlayer`. |

## Important 32-bit SAPI5 Limitation

Standard `sapi5_32` on 64-bit NVDA speaks through a separate 32-bit synth host.
This add-on's global plugin is loaded in the main NVDA process, not in that
host. Therefore, the add-on does not process `sapi5_32` audio through Sonic and
does not add the separate `Sonic pitch` setting to that synth.

Version 0.4.7 and newer can still add configured eSpeak-NG SAPI dynamic voices
to NVDA's standard `sapi5_32` voice list at runtime. This only affects voice
visibility and selection; it does not make `sapi5_32` globally Sonic-processed.

This is intentional. It keeps standard `sapi5_32` loading normally and avoids
altering native pitch when Sonic cannot process that audio path.

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
4. Set `Sonic pitch` to something other than `50`, such as `75`.
5. Open the current NVDA log at `%TEMP%\nvda.log`.

Expected log entries:

```text
globalSonicPitch: installed WavePlayer speech feed hook
globalSonicPitch: installed synth Sonic pitch setting hook
globalSonicPitch: added Sonic pitch voice setting; synth=RHVoice
globalSonicPitch: processed speech audio; synth=RHVoice; pitch=75
```

For `sapi5_32`, the expected entry is:

```text
Loaded synthDriver sapi5_32
```

## Troubleshooting

### Sonic Pitch Is Not In Voice Settings

Enable `Enable global Sonic pitch` in the `Global Sonic Pitch` settings panel,
then reopen Voice settings or switch synthesizers. The add-on hides the
`Sonic pitch` voice setting while global Sonic pitch is disabled.

### Sonic Pitch Does Not Change

Check that global mode is enabled and `Sonic pitch` is not `50`. Then check the
NVDA log for `processed speech audio`. If that entry is missing, the selected
synth probably does not feed audio through NVDA's main `WavePlayer`.

If switching synthesizers seems to reset `Sonic pitch`, that is expected until
you change it for that synthesizer. Values are stored separately for each
supported synthesizer.

### The Synth Still Changes Its Native Pitch

This is now expected. NVDA's normal `Pitch` setting controls the synth's native
pitch, while `Sonic pitch` controls only Sonic processing.

### Audio Has Small Gaps Or Artifacts

Since version 0.3.1, the add-on keeps a continuous Sonic stream for the active
`WavePlayer` and avoids flushing every small block. If gaps remain, check CPU
load, extreme `Sonic pitch` values, and whether the issue happens with more than
one synth.

Version 0.4.4 also avoids changing the active Sonic stream's pitch in place.
When `Sonic pitch` changes during speech, the old processor is discarded and a
fresh processor starts on the next audio block. This is slightly more
conservative, but it avoids freezes seen with some SAPI5 voices during rapid
downward pitch changes.

Version 0.4.5 further reduces lock contention while Sonic processes fast SAPI5
voices, including eSpeak-NG SAPI at rate 100.

Version 0.4.9 makes pitch changes apply from the next utterance instead of
replacing the active Sonic processor during speech. If you move `Sonic pitch`
while NVDA is already speaking, the audible change may wait until the next
spoken phrase. This is intentional and favors stability over instant mid-word
retuning.

### eSpeak-NG SAPI Does Not Appear In SAPI5

The third-party eSpeak-NG SAPI voice must be configured with its own
configuration tool before it appears in SAPI5. After creating or enabling a
voice profile there, restart NVDA and choose the voice from the normal SAPI5
voice list.

NVDA 2026.2 reads standard SAPI5 voice tokens directly from the registry path
used by ordinary voices. eSpeak-NG SAPI exposes configured voices through a
dynamic SAPI token enumerator instead. Since version 0.4.6, this add-on appends
only those eSpeak-NG SAPI dynamic tokens to NVDA's standard `sapi5` voice list
at runtime. Since version 0.4.7, it also supplements NVDA's standard `sapi5_32`
voice list with those configured eSpeak-NG SAPI dynamic tokens. It does not
modify NVDA files or write registry voice tokens.

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
- `added Sonic pitch voice setting`
- `captured Sonic pitch setting`
- `processed speech audio`
- `Sonic is unavailable`

## Technical Summary

The add-on runs only at NVDA runtime. It does not modify NVDA's installed files.

It uses:

- an NVDA global plugin;
- a hook on `nvwave.WavePlayer.feed`;
- hooks on `WavePlayer.idle`, `stop`, and `close` to finish or discard Sonic
  stream state;
- dynamic insertion of a `sonicPitch` setting into the active synth's
  `supportedSettings`;
- runtime addition of configured eSpeak-NG SAPI dynamic tokens to NVDA's
  standard `sapi5` and `sapi5_32` voice lists;
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
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.4.9.nvda-addon -Force
```

Syntax check:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py addon\installTasks.py
```

## Repository Layout

- `addon/manifest.ini` - NVDA add-on manifest.
- `addon/installTasks.py` - install-time optional support prompt.
- `addon/globalPlugins/globalSonicPitch.py` - main plugin.
- `addon/doc/en/readme.md` - English add-on help.
- `addon/doc/pl/readme.md` - Polish add-on help.
- `docs/technical-notes.md` - maintenance notes.
- `TESTING.md` - test matrix.
- `CHANGELOG.md` - release history.
