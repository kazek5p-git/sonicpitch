# Global Sonic Pitch

Global Sonic Pitch adds a separate `Sonic pitch` control and applies it through
Sonic. NVDA's normal `Pitch` setting remains the active synth's native pitch
control. The add-on works globally for synthesizers whose speech audio reaches
NVDA's main process.

## What It Does

- Adds a `Global Sonic Pitch` settings panel.
- Does not add synthesizers to NVDA's synthesizer dialog.
- Adds a `Sonic pitch` setting to standard Voice settings and the synth
  settings ring while global Sonic pitch is enabled and the active synth is
  supported.
- NVDA's normal `Pitch` setting continues to control the synth's native pitch.
- `Sonic pitch` is a separate Sonic control.
- Processes speech audio through Sonic.
- Includes an optional external support link.
- May ask during installation whether to open the support page.

## Quick Start

1. Select a normal NVDA synth, such as RHVoice, eSpeak, OneCore, or 64-bit
   SAPI5.
2. Open NVDA Settings.
3. Choose `Global Sonic Pitch`.
4. Enable `Enable global Sonic pitch`.
5. Change Sonic processing from the `Sonic pitch` voice setting or the add-on
   panel's `Sonic pitch` slider.
6. Change native pitch from NVDA's normal `Pitch` setting if you want to use
   both controls together.

`Sonic pitch` `50` is neutral. Values below `50` lower speech through Sonic,
and values above `50` raise speech through Sonic.

## Settings

- `Enable global Sonic pitch` - enables global Sonic pitch processing.
- `Sonic pitch` - sets the pitch used by Sonic.
- `Enable debug logging` - writes detailed entries to the NVDA log.
- `Support the author` - opens the external BuyCoffee support page.

NVDA's normal `Pitch` setting remains the synth's native pitch. `Sonic pitch`
is a separate add-on setting.

The add-on panel is always available. The separate `Sonic pitch` slider is added
to NVDA's Voice dialog and synth settings ring only while `Enable global Sonic
pitch` is enabled. It is removed from those Voice controls when global Sonic
pitch is disabled. If `Synth ring settings selector` is installed, `sonicPitch`
is added to its settings list.

In Input Gestures, the `Global Sonic Pitch` category lets you assign gestures
for toggling, reporting status, opening the support page, increasing,
decreasing, and resetting Sonic pitch.

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
eSpeak-NG SAPI through SAPI5, and similar synths when their 16-bit PCM speech
audio reaches NVDA's main `WavePlayer`.

Third-party eSpeak-NG SAPI voices must be configured in the eSpeak-NG SAPI
configuration tool before they appear in the normal SAPI5 voice list.

Standard `sapi5_32` on 64-bit NVDA is deliberately skipped. It runs in a
separate 32-bit synth host, so this global plugin cannot process that audio.

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
- `globalSonicPitch: processed speech audio`

For standard `sapi5_32`, the expected entry is:

```text
Loaded synthDriver sapi5_32
```

## Troubleshooting

If `Sonic pitch` is not in Voice settings, enable `Enable global Sonic pitch` in
the `Global Sonic Pitch` settings panel, then reopen Voice settings or switch
synthesizers.

If `Sonic pitch` does not change, make sure global mode is enabled and `Sonic
pitch` is not `50`. Also check whether `processed speech audio` appears in the
log.

If you hear the synth's native pitch change, that is expected. NVDA's normal
`Pitch` setting controls native pitch, while `Sonic pitch` controls only Sonic
processing.

If small audio gaps remain, check CPU load, less extreme `Sonic pitch` values,
and more than one synth. Since version 0.3.1, the add-on uses a continuous
Sonic stream to reduce micro-gaps between audio blocks. Since version 0.4.4,
pitch changes during active speech reset the Sonic processor instead of
changing the active stream in place, avoiding freezes seen with some SAPI5
voices during rapid downward pitch changes.

## Logs

- Current log: `%TEMP%\nvda.log`
- Previous log: `%TEMP%\nvda-old.log`
- 32-bit host logs: `%TEMP%\nvda_synthDriverHost.*.log`
