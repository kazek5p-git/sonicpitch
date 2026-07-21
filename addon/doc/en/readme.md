# Global Sonic Pitch

Global Sonic Pitch adds a separate `Sonic pitch` control to supported NVDA
synthesizers. It changes speech pitch through Sonic audio processing while
leaving NVDA's normal native `Pitch` setting unchanged.

## What It Adds

- A `Global Sonic Pitch` settings panel.
- A separate `Sonic pitch` voice setting while global processing is enabled.
- Per-synthesizer and per-voice Sonic pitch values.
- An optional extended range of approximately `-20..+20` semitones.
- Optional higher-quality Sonic analysis. Fast mode is the default.
- Processing for supported speech audio that reaches NVDA's main audio path.
- Support for standard `sapi5_32` and `sapi4_32` on 64-bit NVDA through
  bundled 32-bit host wrappers.
- Optional debug logging.
- An optional support link.

The add-on does not add a replacement synthesizer to NVDA's synthesizer dialog
and does not modify NVDA files on disk.

## Quick Start

1. Select a normal NVDA synthesizer, such as RHVoice, eSpeak, OneCore,
   64-bit SAPI5, standard `sapi5_32`, or standard `sapi4_32`.
2. Open NVDA Settings.
3. Choose `Global Sonic Pitch`.
4. Enable `Enable global Sonic pitch`.
5. Reopen Voice settings or use the synth settings ring.
6. Adjust `Sonic pitch`.

`Sonic pitch` value `50` is neutral. Lower values lower speech through Sonic.
Higher values raise speech through Sonic.

## Settings

- `Enable global Sonic pitch` enables or disables Sonic pitch processing.
- `Increase Sonic pitch range to 20 semitones` extends the `Sonic pitch`
  control from the normal `-6..+6` semitone range to approximately
  `-20..+20` semitones.
- `Use higher-quality Sonic analysis` makes Sonic use its more accurate
  pitch-period analysis. It may improve some voices, but can use more CPU. It
  does not change the pitch range or slider mapping, and the audible difference
  may be small for clean TTS voices or small pitch changes.
- `Enable debug logging` writes detailed add-on entries to the NVDA log.
- `Support the author` opens the external support page.

The add-on panel only controls global processing and diagnostics. The actual
`Sonic pitch` value is changed from Voice settings, the synth settings ring, or
assigned Input Gestures.

When global processing is disabled, the `Sonic pitch` voice setting is removed
from Voice settings and the synth settings ring.

## Native Pitch And Sonic Pitch

NVDA's normal `Pitch` setting remains the synthesizer's native pitch. `Sonic
pitch` is an additional processing value owned by this add-on.

If both controls are away from `50`, you hear the combined result:

- native synth pitch from NVDA's normal `Pitch` setting;
- Sonic processing from `Sonic pitch`.

## Per-Voice Values

`Sonic pitch` is stored separately for each supported synthesizer and selected
voice. For example, two voices inside SAPI5 can keep different Sonic pitch
values.

New voices start at `50` until you change them. Switching back to a voice
restores the value stored for that voice.

## Input Gestures

The `Global Sonic Pitch` category in Input Gestures contains commands for:

- toggling global Sonic pitch;
- reporting current status;
- opening the support page;
- increasing Sonic pitch for the current synthesizer and voice;
- decreasing Sonic pitch for the current synthesizer and voice;
- resetting Sonic pitch for the current synthesizer and voice.

No gestures are assigned by default.

## Compatibility

Expected supported paths:

- RHVoice when speech audio reaches NVDA's main `WavePlayer`.
- eSpeak NG in NVDA's main process.
- OneCore in NVDA's main process.
- 64-bit SAPI5 when it uses NVDA's normal audio path.
- Standard `sapi5_32` on 64-bit NVDA through the bundled 32-bit host wrapper.
- Standard `sapi4_32` on 64-bit NVDA through the bundled 32-bit host wrapper
  when NVDA's SAPI4 WASAPI audio path is active.
- Other synths that feed compatible speech audio through NVDA.

Third-party eSpeak-NG SAPI voices must be configured in their own configuration
tool before they appear in SAPI5. This add-on does not patch SAPI voice
enumeration, does not write registry voice tokens, and does not change the SAPI
voice list.

## Standard 32-bit SAPI On 64-bit NVDA

Standard `sapi5_32` and `sapi4_32` on 64-bit NVDA run in a separate 32-bit
synth host. Global Sonic Pitch loads bundled wrappers in that host so the
standard NVDA synth can receive the current `Sonic pitch` value.
The same host channel also receives the selected Sonic quality mode.

This keeps the normal NVDA synthesizer entries. It does not add a new
synthesizer and does not replace NVDA files. For SAPI4, Sonic processing is
available only through NVDA's WASAPI SAPI4 path. If NVDA is configured to use
the older SAPI4 `MMAudioDest` path, that audio bypasses NVDA's `WavePlayer` and
cannot be processed by this add-on.

## Support Link

The `Support the author` button and the `Open support page` Input Gesture open:

```text
https://buycoffee.to/kazimierz-parzych
```

Support is voluntary. The add-on does not process payments, store payment data,
or unlock features based on support.

During installation or update, the add-on may show a small optional support
prompt. Choosing `Yes` opens the same page in the default browser. Choosing
`No` continues installation without changing add-on behavior.

## Troubleshooting

If `Sonic pitch` is not in Voice settings, enable `Enable global Sonic pitch`,
then reopen Voice settings or switch synthesizers.

If changing `Sonic pitch` has no audible effect, make sure global processing is
enabled and the value is not `50`.

If switching synthesizers or voices appears to reset `Sonic pitch`, set a value
for that synthesizer and voice. Values are stored independently.

If standard `sapi5_32` or `sapi4_32` on 64-bit NVDA does not expose `Sonic
pitch`, restart NVDA or switch away from that synthesizer and back again.

If a third-party SAPI voice is missing, configure it in that voice package's own
configuration tool first, then restart NVDA.

## Logs

Useful log files:

- Current NVDA log: `%TEMP%\nvda.log`
- Previous NVDA log: `%TEMP%\nvda-old.log`
- 32-bit synth host logs: `%TEMP%\nvda_synthDriverHost.*.log`

Useful search terms:

- `globalSonicPitch`
- `added Sonic pitch voice setting`
- `captured Sonic pitch setting`
- `processed speech audio`
- `applied remote 32-bit Sonic pitch`
- `applied Sonic quality`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`
- `globalSonicPitch sapi4_32 host: processed SAPI4 audio`

## License

Global Sonic Pitch source code is licensed under GNU GPL version 2 or later.
Bundled Sonic native binaries are Apache 2.0 third-party components.
