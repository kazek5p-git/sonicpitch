# Technical Notes

This document records the implementation details for Global Sonic Pitch.

## Design Goal

The add-on must provide Sonic-based pitch adjustment without changing NVDA's
installed files or adding replacement synthesizer drivers.

Version 0.3.0 changed the add-on identity from `sapi5SonicPitch` to
`globalSonicPitch` and removes the previous custom SAPI5 synth drivers from the
package. The current package contains only a global plugin and documentation.

## Config

Current config section:

```ini
[globalSonicPitch]
enabled = boolean(default=False)
pitch = integer(default=50, min=0, max=100)
debugLogging = boolean(default=False)
```

The plugin migrates values from the old `[sapi5SonicPitchGlobal]` section once
at startup so users testing version 0.2.0 keep their enabled state and pitch.

## Pitch Mapping

NVDA exposes pitch as a value from `0` to `100`.

The add-on treats `50` as neutral and maps the full range to approximately
`-6..+6` semitones:

```text
semitones = ((pitchPercent - 50) / 50) * 6
ratio = 2 ** (semitones / 12)
```

The final Sonic pitch ratio is clamped to `0.70..1.45`.

## Pitch Takeover

Filtering audio alone is not enough. If the selected synth receives NVDA's
native pitch change, the user hears the synth's own pitch plus any Sonic shift.

When global Sonic pitch is enabled, the plugin patches the active synth
instance's `_set_pitch` and `_get_pitch` methods at runtime:

- `_set_pitch(value)` stores `value` in `[globalSonicPitch] pitch`;
- the synth's original `_set_pitch` is called with neutral `50`;
- `_get_pitch()` returns the add-on pitch while the global mode is enabled;
- when the mode is disabled, the add-on restores the stored pitch to the native
  synth.

The patch is applied to the current synth on startup and after
`synthDriverHandler.setSynth` completes. It is removed when the global plugin is
terminated.

The built-in `sapi5_32` synth is excluded because its speech is produced in the
separate 32-bit host on 64-bit NVDA. Taking over its pitch in the main process
would neutralize native pitch without Sonic being able to process the audio.

## Global WavePlayer Path

`globalPlugins/globalSonicPitch.py` hooks `nvwave.WavePlayer.feed` at runtime.
It does not patch files on disk.

The hook is intentionally narrow:

- it only processes `WavePlayer` instances whose `_purpose` is
  `nvwave.AudioPurpose.SPEECH`;
- it only processes 16-bit PCM blocks;
- it keeps one Sonic stream per speech `WavePlayer` while speech is active;
- it buffers the first chunk until about 50 ms of processed audio is available;
- it avoids `SonicStream.flush()` in the middle of ordinary audio blocks;
- it flushes the remaining Sonic stream tail before `WavePlayer.idle()`;
- it bypasses non-speech sounds;
- it bypasses unsupported host paths such as `sapi5_32`;
- it falls back to the original `WavePlayer.feed` call on any exception.

The continuous stream is important for audio quality. Flushing Sonic after every
small block can create tiny gaps and artifacts because Sonic loses its internal
analysis window at block boundaries.

## Logs

The most useful logs while debugging are:

- `%TEMP%\nvda.log`
- `%TEMP%\nvda-old.log`
- `%TEMP%\nvda_synthDriverHost.*.log`

Look for:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth pitch takeover hook`
- `globalSonicPitch: patched pitch setting`
- `globalSonicPitch: pitch takeover active`
- `globalSonicPitch: captured NVDA pitch`
- `globalSonicPitch: processed speech audio`
- `globalSonicPitch: Sonic is unavailable`

## Maintenance Warnings

This add-on relies on private NVDA internals:

- `synthDriverHandler.setSynth`
- synth driver `_set_pitch` and `_get_pitch`
- `synthDrivers._sonic.SonicStream.pitch`
- `nvwave.WavePlayer.feed`
- `nvwave.WavePlayer.idle`
- `nvwave.WavePlayer.stop`
- `nvwave.WavePlayer.close`
- `nvwave.AudioPurpose.SPEECH`

Any NVDA release that changes those APIs may require add-on changes.
