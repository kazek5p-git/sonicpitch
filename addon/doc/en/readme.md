# Global Sonic Pitch

Global Sonic Pitch adds a separate `Sonic pitch` control and applies it through
Sonic. NVDA's normal `Pitch` setting remains the active synth's native pitch
control. The add-on works globally for synthesizers whose speech audio reaches
NVDA's main process, and it supports standard `sapi5_32` on 64-bit NVDA through
a small 32-bit host wrapper.

## What It Does

- Adds a `Global Sonic Pitch` settings panel.
- Does not add synthesizers to NVDA's synthesizer dialog.
- Adds a `Sonic pitch` setting to standard Voice settings and the synth
  settings ring while global Sonic pitch is enabled and the active synth is
  supported.
- NVDA's normal `Pitch` setting continues to control the synth's native pitch.
- `Sonic pitch` is a separate Sonic control.
- `Sonic pitch` is stored separately for each supported synthesizer.
- Processes speech audio through Sonic.
- Supports standard `sapi5_32` on 64-bit NVDA without adding a new synthesizer.
- Includes an optional external support link.
- May ask during installation whether to open the support page.

## Quick Start

1. Select a normal NVDA synth, such as RHVoice, eSpeak, OneCore, 64-bit SAPI5,
   or standard `sapi5_32`.
2. Open NVDA Settings.
3. Choose `Global Sonic Pitch`.
4. Enable `Enable global Sonic pitch`.
5. Change Sonic processing from the `Sonic pitch` voice setting, the synth
   settings ring, or an assigned Input Gesture.
6. Change native pitch from NVDA's normal `Pitch` setting if you want to use
   both controls together.

`Sonic pitch` `50` is neutral. Values below `50` lower speech through Sonic,
and values above `50` raise speech through Sonic. Each supported synthesizer
keeps its own `Sonic pitch` value.

## Settings

- `Enable global Sonic pitch` - enables global Sonic pitch processing.
- `Enable debug logging` - writes detailed entries to the NVDA log.
- `Support the author` - opens the external BuyCoffee support page.

NVDA's normal `Pitch` setting remains the synth's native pitch. `Sonic pitch`
is a separate add-on setting stored per supported synthesizer.

The add-on panel is always available. The separate `Sonic pitch` slider is added
to NVDA's Voice dialog and synth settings ring only while `Enable global Sonic
pitch` is enabled. It is removed from those Voice controls when global Sonic
pitch is disabled. If `Synth ring settings selector` is installed, `sonicPitch`
is added to its settings list.

There is intentionally no `Sonic pitch` slider in the add-on's global settings
panel. The global panel enables the audio processor; the `Sonic pitch` value is
changed from Voice settings, the synth settings ring, or assigned gestures for
the current supported synthesizer.

In Input Gestures, the `Global Sonic Pitch` category lets you assign gestures
for toggling, reporting status, opening the support page, increasing,
decreasing, and resetting Sonic pitch for the current supported synthesizer.

## Support

The `Support the author` button and the `Open support page` Input Gesture
command open:

```text
https://buycoffee.to/kazimierz-parzych
```

This is voluntary external support. The add-on does not process payments, store
payment data, or unlock features based on support.

During installation or update, Sonic Pitch may show a small optional support
message. `Yes` opens the same page in the default browser. `No` continues
installation without changing add-on behavior.

## Compatibility

The add-on is expected to work with RHVoice, eSpeak, OneCore, 64-bit SAPI5,
standard `sapi5_32` on 64-bit NVDA, eSpeak-NG SAPI through SAPI5, and similar
synths when their 16-bit PCM speech audio reaches NVDA's main `WavePlayer` or
NVDA's 32-bit SAPI5 synth host.

Third-party eSpeak-NG SAPI voices must be configured in the eSpeak-NG SAPI
configuration tool before they appear in SAPI. Current versions of this add-on
do not patch SAPI voice enumeration, do not modify NVDA files, and do not write
registry voice tokens.

Standard `sapi5_32` on 64-bit NVDA runs in a separate 32-bit synth host. Current
versions load a bundled wrapper in that host so the standard NVDA `sapi5_32`
synth can receive the same `Sonic pitch` value. This does not modify NVDA files,
does not change the SAPI voice list, and does not add a separate synthesizer.

## Migration From The Old Add-on

The old `sapi5SonicPitch` add-on added separate SAPI5 Sonic Pitch synths. The
current `globalSonicPitch` add-on does not add synths. If `SAPI5 32-bit Sonic
Pitch` or `SAPI5 64-bit Sonic Pitch` still appears in the synthesizer dialog,
remove the old `sapi5SonicPitch` add-on and restart NVDA.

## Verifying Behavior

Enable `Enable debug logging`, restart NVDA, and check `%TEMP%\nvda.log`.

Useful entries:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: loaded bundled Sonic library`
- `globalSonicPitch: processed speech audio`

For standard `sapi5_32`, the expected entry is:

```text
Loaded synthDriver sapi5_32
globalSonicPitch: applied remote SAPI5 32-bit Sonic pitch
```

The host log `%TEMP%\nvda_synthDriverHost.*.log` should also contain:

```text
globalSonicPitch sapi5_32 host: set Sonic pitch
```

## Troubleshooting

If `Sonic pitch` is not in Voice settings, enable `Enable global Sonic pitch` in
the `Global Sonic Pitch` settings panel, then reopen Voice settings or switch
synthesizers.

If `Sonic pitch` does not change, make sure global mode is enabled and `Sonic
pitch` is not `50`. For main-process synths, check whether `processed speech
audio` appears in the log. For `sapi5_32`, check for `applied remote SAPI5
32-bit Sonic pitch` in `%TEMP%\nvda.log` and `globalSonicPitch sapi5_32 host:
set Sonic pitch` in `%TEMP%\nvda_synthDriverHost.*.log`.

If switching synthesizers seems to reset `Sonic pitch`, that is expected until
you change it for that synthesizer. Values are stored separately for each
supported synthesizer.

If you hear the synth's native pitch change, that is expected. NVDA's normal
`Pitch` setting controls native pitch, while `Sonic pitch` controls only Sonic
processing.

If small audio gaps remain, check CPU load, less extreme `Sonic pitch` values,
and more than one synth. Since version 0.3.1, the add-on reuses a continuous
Sonic stream while the audio format and selected pitch stay the same. Current
versions do not retune an already-used Sonic stream in place; changes during
active speech are applied from the next safe utterance boundary with a fresh
stream. This avoids freezes seen with some SAPI5 voices during rapid downward
pitch changes. Since version 0.4.5, the add-on also reduces lock contention
while processing fast SAPI5 voices such as eSpeak-NG SAPI at rate 100.

Since version 0.4.10, the add-on uses bundled 32-bit and 64-bit Sonic native
libraries. In 32-bit NVDA processes, Sonic streams are kept alive instead of
being passed to native `sonicDestroyStream`, which works around a reproduced
native heap crash on NVDA 2025.3.3 x86 with SAPI5.

Since version 0.4.11, short feedback messages after repeated PageUp/PageDown
changes use the latest `Sonic pitch` value more reliably.

Since version 0.4.12, repository documentation includes license files,
third-party Sonic notices, and NVDA Add-on Store submission notes.

Since version 0.4.13, standard `sapi5_32` on 64-bit NVDA is controlled through
the bundled 32-bit host wrapper. The same version also makes Voice dialog Sonic
pitch changes transactional: OK or Apply commits the previewed value, while
Escape or Cancel restores the previous value.

## License

Global Sonic Pitch source code is licensed under the GNU GPL version 2 or
later. Bundled Sonic native binaries are Apache 2.0 third-party components.

## Logs

- Current log: `%TEMP%\nvda.log`
- Previous log: `%TEMP%\nvda-old.log`
- 32-bit host logs: `%TEMP%\nvda_synthDriverHost.*.log`
