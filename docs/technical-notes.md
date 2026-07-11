# Technical Notes

This document records the implementation details that are easiest to forget
while maintaining SAPI5 Sonic Pitch.

## Design Goal

The add-on must provide Sonic-based pitch adjustment without changing NVDA's
built-in `sapi5` or `sapi5_32` synthesizers.

Current releases expose only separate synth drivers:

- `sapi5SonicPitch64`
- `sapi5SonicPitch32`

There is no `globalPlugins` package in the add-on. That is intentional.

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

Any NVDA release that changes those APIs may require add-on changes.

