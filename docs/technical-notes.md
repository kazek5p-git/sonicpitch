# Technical Notes

This document records the implementation details that are easiest to forget
while maintaining SAPI5 Sonic Pitch.

## Design Goal

The add-on must provide Sonic-based pitch adjustment without changing NVDA's
installed files or built-in synth driver modules.

The add-on exposes separate synth drivers:

- `sapi5SonicPitch64`
- `sapi5SonicPitch32`

Version 0.2.0 also installs `globalPlugins/sapi5SonicPitchGlobal.py`, which is a
runtime-only global WavePlayer hook. It must remain optional and disabled by
default.

## Pitch Mapping

NVDA exposes pitch as a value from `0` to `100`.

The add-on treats `50` as neutral and maps the full range to approximately
`-6..+6` semitones:

```text
semitones = ((pitchPercent - 50) / 50) * 6
ratio = 2 ** (semitones / 12)
```

The final Sonic pitch ratio is clamped to `0.70..1.45`.

SAPI XML pitch is neutralized by returning `0` from `_percentToPitch`. This
prevents double pitch processing: SAPI should not shift pitch while Sonic is
also shifting pitch.

The global processor uses the same mapping, but it uses its own add-on setting
instead of modifying the selected synth's native pitch. For clean testing, the
selected synth's own pitch should be set to neutral.

## 64-bit Path

`sapi5SonicPitch64.py` imports NVDA's normal `synthDrivers.sapi5` module and
subclasses its `SynthDriver` together with `Sapi5SonicPitchMixin`.

The driver is unavailable under 32-bit Python/NVDA.

## 32-bit Path On 64-bit NVDA

`sapi5SonicPitch32.py` uses NVDA's private `SynthDriverProxy32`. The proxy starts
NVDA's 32-bit synth host and loads `_sapi5SonicPitch32Host.py` inside that host.

The host-side module appends NVDA's built-in `_synthDrivers32` path to
`synthDrivers.__path__`, then imports the 32-bit `synthDrivers.sapi5` module.
Pitch is applied inside the 32-bit host process, where the 32-bit SAPI5 voice
actually runs.

## Global WavePlayer Path

`globalPlugins/sapi5SonicPitchGlobal.py` hooks `nvwave.WavePlayer.feed` at
runtime. It does not patch files on disk.

The hook is intentionally narrow:

- it only processes `WavePlayer` instances whose `_purpose` is
  `nvwave.AudioPurpose.SPEECH`;
- it only processes 16-bit PCM blocks;
- it processes one incoming block into one outgoing block, preserving the same
  `onDone` callback;
- it bypasses non-speech sounds;
- it bypasses this add-on's own `sapi5SonicPitch32` and `sapi5SonicPitch64`
  synths by default;
- it falls back to the original `WavePlayer.feed` call on any exception.

The one-block-in, one-block-out design is less sophisticated than a long-lived
Sonic stream, but it avoids buffering speech indexes across callback boundaries.
That makes it safer as a global add-on hook.

The built-in `sapi5_32` proxy on 64-bit NVDA is not globally filtered by this
hook. Its audio is produced in NVDA's separate 32-bit synth host, which does not
load this global plugin. Do not patch the standard proxy to force this behavior;
that was the class of change that previously broke ordinary `sapi5_32` loading.
Use `sapi5SonicPitch32` for 32-bit SAPI5 Sonic pitch.

## Sonic Stream Access

The mixin applies pitch after `_initWasapiAudio` and after settings are loaded.

Changing `SonicStream.pitch` while audio is being processed can race with the
SAPI5 audio callback. `SynchronizedSonicStream` wraps the Sonic stream and uses a
re-entrant lock for stream reads, writes, and property updates.

When pitch changes while WASAPI and SAPI are active, the mixin cancels current
speech and reassigns the current voice. This recreates the WASAPI/Sonic stream
instead of mutating the live native stream in the most fragile moment.

## Compatibility Checks

The drivers check for:

- expected Python bitness;
- the base SAPI5 `SynthDriver`;
- `_set_pitch`;
- `_percentToPitch`;
- `_initWasapiAudio`;
- a writable `SonicStream.pitch` property;
- the built-in 32-bit SAPI5 and Sonic host files when using the 32-bit proxy.

Checks log the reason for unavailability rather than making the synthesizer list
fail noisily.

## Logs

The most useful logs while debugging are:

- `%TEMP%\nvda.log`
- `%TEMP%\nvda-old.log`
- `%TEMP%\nvda_synthDriverHost.*.log`

Look for:

- `applied Sonic pitch`
- `sapi5SonicPitchGlobal: installed WavePlayer speech feed hook`
- `sapi5SonicPitchGlobal: processed speech audio`
- `pitch setting changed`
- `recreating WASAPI/Sonic stream`
- `Sonic pitch unavailable`
- `32-bit synth driver host check failed`

## Maintenance Warnings

This add-on relies on private NVDA internals:

- `_bridge.clients.synthDriverHost32.synthDriver.SynthDriverProxy32`
- `SynthDriverProxy32.synthDriver32Path`
- `SynthDriverProxy32.synthDriver32Name`
- `synthDrivers.sapi5.SynthDriver._initWasapiAudio`
- `SynthDriver.sonicStream`
- `synthDrivers._sonic.SonicStream.pitch`
- `nvwave.WavePlayer.feed`
- `nvwave.AudioPurpose.SPEECH`

Any NVDA release that changes those APIs may require add-on changes.
