# Technical Notes

This document records the implementation details for Global Sonic Pitch.

## Design Goal

The add-on must provide Sonic-based pitch adjustment without changing NVDA's
installed files or adding replacement synthesizer drivers.

Version 0.3.0 changed the add-on identity from `sapi5SonicPitch` to
`globalSonicPitch` and removes the previous custom SAPI5 synth drivers from the
package. The current package contains a global plugin, documentation, and
bundled native Sonic libraries.

Version 0.4.0 adds a dynamic `sonicPitch` driver setting so NVDA's standard
Voice dialog and synth settings ring can expose the add-on pitch without
changing NVDA's installed files.

Version 0.4.1 stops taking over NVDA's normal `pitch` setting. Native `pitch`
and add-on `sonicPitch` are independent controls.

Version 0.4.2 makes the dynamic `sonicPitch` Voice dialog/ring setting visible
only while global Sonic pitch is enabled.

Version 0.4.3 adds a voluntary support link. The URL is kept in `SUPPORT_URL`
in both the global plugin and `installTasks.py`. The settings button, Input
Gesture script, and optional install-time prompt open it through Python's
`webbrowser` module. The add-on does not handle payments or store payment data.
The same version also defers dynamic setting patching after synth changes
initiated from `gui.settingsDialogs.setSynth` through `wx.CallAfter` to avoid
racing NVDA's own Voice dialog refresh.

Version 0.4.4 fixes freezes seen with some SAPI5 voices, including eSpeak-NG
SAPI, while lowering `sonicPitch` during active speech. Version 0.4.3 tried to
keep the active `SonicStream` and update `stream.pitch` in place. That was good
for continuity but unsafe with some SAPI callback timing. Version 0.4.4 stopped
retuning a native stream in place. Current versions defer pitch changes during
active speech, apply them at a safe boundary, and protect the processor map with
an `RLock`.

Version 0.4.5 shortens the scope of the global processor-map lock. The map lock
now protects only lookup, insertion, removal, and reset. Each
`_SonicStreamProcessor` has its own lock for `SonicStream.writeShort`,
`readShort`, and `flush`. This keeps one stream serialized while avoiding a
global lock around expensive Sonic processing, which matters for fast SAPI5
voices such as eSpeak-NG SAPI at rate 100.

Versions 0.4.6 and 0.4.7 briefly experimented with SAPI voice-list
compatibility hooks for eSpeak-NG SAPI and `sapi5_32`. Those hooks were removed
in version 0.4.10. Current versions do not patch SAPI voice enumeration, do not
write registry voice tokens, and do not modify NVDA files on disk.

Version 0.4.8 changes `sonicPitch` from one global pitch value to a per-synth
value. The add-on settings panel now only enables/disables processing and debug
logging. The dynamic Voice dialog/ring setting and Input Gesture scripts read
and write the active supported synth's own `sonicPitch` value.

Version 0.4.9 makes Sonic pitch application utterance-scoped. Changing
`sonicPitch` stores the new value immediately, but an already active speech
`WavePlayer` continues using the pitch value captured at the start of that
utterance. The new value is used by the next utterance. This avoids resetting or
replacing a native `SonicStream` while SAPI or another synth is feeding audio
callbacks.

Version 0.4.10 bundles local 32-bit and 64-bit Sonic native DLLs and prefers
them over NVDA's internal Sonic module. If the bundled DLL cannot be loaded, the
add-on falls back to NVDA's internal `synthDrivers._sonic` module. On 32-bit
NVDA processes, the add-on avoids calling native `sonicDestroyStream` to work
around a reproduced native heap crash on NVDA 2025.3.3 x86 with SAPI5.

Version 0.4.11 improves short setting feedback after repeated PageUp/PageDown
changes. Empty `WavePlayer.feed` markers are treated as safe utterance
boundaries, and a changed `sonicPitch` creates a fresh Sonic stream at the next
safe boundary instead of retuning an already-used native stream in place.

Version 0.4.12 prepares the project for NVDA Add-on Store submission. It updates
stable-channel metadata, adds root licensing and third-party notice files, and
records the store submission checklist in `docs/addon-store-submission.md`.

Version 0.4.13 adds support for the standard `sapi5_32` synth on 64-bit NVDA.
Because that synth speaks in NVDA's separate 32-bit synth host, the main global
plugin cannot process its audio through the main-process `WavePlayer` hook. The
add-on instead patches the in-memory `sapi5_32.SynthDriver.synthDriver32Path`
to point at a bundled 32-bit host wrapper. The wrapper imports NVDA's original
32-bit SAPI5 driver, exposes a hidden remote `sonicPitch` parameter, and applies
that value to the host-side Sonic stream. This still uses the standard NVDA
`sapi5_32` synth entry and does not modify NVDA files on disk.

The same release makes Voice dialog changes transactional. While the dialog is
open, `sonicPitch` writes are stored as a temporary preview and applied to the
current runtime path. OK or Apply commits the values to
`[globalSonicPitch] pitchBySynth`; Escape, Cancel, or dialog destruction
restores the captured values.

Version 0.4.14 stabilizes fast `sonicPitch` changes for standard `sapi5_32` on
64-bit NVDA. The 32-bit host no longer mutates `sonicStream.pitch` while SAPI is
actively speaking or cancelling. Instead, it records the latest requested value,
defers the host-side Sonic pitch update until a safe speech boundary, and
serializes host Sonic stream operations with a reentrant lock. This fixes a
failure mode where NVDA 2026.1.1 x64 kept running but the remote `sapi5_32`
speech path went silent until the synth was reloaded.

## Config

Current config section:

```ini
[globalSonicPitch]
enabled = boolean(default=False)
pitch = integer(default=50, min=0, max=100)
pitchBySynth = string(default='{}')
debugLogging = boolean(default=False)
```

`pitch` is kept as a legacy migration key. Current per-synth values are stored
as JSON in `pitchBySynth`, for example:

```json
{"RHVoice":45,"sapi5_64":38,"sapi5_32":44,"vocalizer":52}
```

The plugin migrates values from the old `[sapi5SonicPitchGlobal]` section once
at startup. If a legacy global `pitch` value exists and no per-synth values are
stored yet, the value is moved lazily to the current supported synth and the
legacy `pitch` key is reset to neutral `50`.

## Sonic Pitch Mapping

The add-on exposes `Sonic pitch` as a value from `0` to `100`, matching NVDA's
usual pitch scale.

For Sonic processing, the add-on treats `50` as neutral and maps the full range
to approximately `-6..+6` semitones:

```text
semitones = ((pitchPercent - 50) / 50) * 6
ratio = 2 ** (semitones / 12)
```

The final Sonic pitch ratio is clamped to `0.70..1.45`.

## Native Pitch And Sonic Pitch

The add-on intentionally does not patch the active synth instance's `_set_pitch`
or `_get_pitch` methods in version 0.4.1 and newer.

NVDA's normal `pitch` setting remains native synth pitch. The add-on's
`sonicPitch` setting is a separate value stored per synth in
`[globalSonicPitch] pitchBySynth`. If both are away from neutral `50`, the user
hears the combined native synth pitch and Sonic processing.

The add-on still wraps `synthDriverHandler.setSynth` so it can inject or remove
the dynamic `sonicPitch` setting after synth changes.

For SAPI5, the add-on normalizes pitch storage keys by process architecture:

- `sapi5` in a 64-bit NVDA process is stored as `sapi5_64`.
- `sapi5` in a 32-bit NVDA process is stored as `sapi5_32`.
- Explicit `sapi5_32` in 64-bit NVDA is stored as `sapi5_32`.

This lets 64-bit NVDA keep separate Sonic pitch values for its standard SAPI5
64-bit path and the standard `sapi5_32` remote-host path. Current versions do
not add eSpeak-NG SAPI voices to `sapi5_32` or any other SAPI voice list.

## Dynamic Voice Setting

For supported main-process synths and for the 64-bit NVDA `sapi5_32` proxy
after the host wrapper is active, while `[globalSonicPitch] enabled` is true,
the plugin adds a `NumericDriverSetting` with id `sonicPitch` to the active
synth instance's `supportedSettings`.

When `[globalSonicPitch] enabled` is false, the plugin removes that dynamic
setting again. This keeps NVDA's standard Voice dialog and synth settings ring
native-only while the add-on processing is disabled. The add-on's own settings
panel remains available so the user can turn the feature back on.

The setting is not stored in the synth's own config. At runtime, the plugin adds
a class-level Python `property` named `sonicPitch` to the active synth class.
That property reads and writes the active synth's entry in
`[globalSonicPitch] pitchBySynth`.

In version 0.4.9 and newer, writes to that property no longer call
`_resetAllPlayerProcessors()`. The processor for the current utterance keeps its
captured pitch until `WavePlayer.idle()`, `stop()`, `close()`, an end-of-stream
empty feed, or a synth change clears the per-player utterance state. Version
0.4.11 also clears idle utterance state when the stored pitch changes, which
lets short setting feedback messages pick up the latest value without unsafe
mid-stream retuning.

In version 0.4.13 and newer, while a Voice settings panel is open, writes to
the dynamic property are treated as dialog preview state. They are applied to
runtime audio immediately, but they are not written to config until the panel's
`onSave`. The panel's `onDiscard` and destroy handler restore the captured
value.

An earlier prototype tried to attach `_get_sonicPitch` and `_set_sonicPitch` to
the synth instance. That does not work reliably because NVDA's
`AutoPropertyType` creates descriptor properties from `_get_*` methods when the
class is created, not when methods are later added to an instance.

The plugin updates `globalVars.settingsRing` after inserting or removing the
setting. If the `Synth ring settings selector` add-on is present or loaded
later, the plugin adds `sonicPitch` to that add-on's `availableSettings` list so
the selector does not hide it from the ring while global mode is enabled.

On plugin termination, the original `supportedSettings` tuple is restored for
the current synth.

## 32-bit SAPI5 Host Wrapper

The 64-bit NVDA `sapi5_32` driver talks to a 32-bit host process. To support
that path without replacing NVDA's synth in the synthesizer dialog, the add-on
temporarily points `sapi5_32.SynthDriver.synthDriver32Path` at
`addon/sapi32HostDrivers` while the add-on is loaded.

`addon/sapi32HostDrivers/sapi5.py` is loaded inside the 32-bit host. It:

- locates NVDA's original `_synthDrivers32` directory;
- appends that directory to `synthDrivers.__path__`;
- imports NVDA's original `_sapi5.SynthDriver`;
- adds a host-side `sonicPitch` numeric setting with `useConfig=False`;
- maps `0..100` to the same Sonic pitch ratio as the main plugin;
- applies the ratio to the host's `sonicStream.pitch` at safe speech
  boundaries;
- serializes host Sonic stream reads, writes, flushes, and pitch changes;
- reapplies the value after the host recreates WASAPI/Sonic audio.

The main plugin verifies remote support by checking whether the remote proxy's
`supportedSettings` contains `sonicPitch`. If the currently loaded `sapi5_32`
host does not expose that setting, the plugin strips the local UI setting,
schedules a reload of `sapi5_32`, and tries again after the host starts through
the wrapper. This avoids probing `getParam("sonicPitch")` on an old host and
keeps the 32-bit host log clean.

The host wrapper deliberately does not enumerate voices, add registry tokens,
or modify NVDA's installed `_synthDrivers32` files. It only adds the remote
pitch parameter and reuses NVDA's original 32-bit SAPI5 implementation.

## Global WavePlayer Path

`globalPlugins/globalSonicPitch.py` hooks `nvwave.WavePlayer.feed` at runtime.
It does not patch files on disk.

The hook is intentionally narrow:

- it only processes `WavePlayer` instances whose `_purpose` is
  `nvwave.AudioPurpose.SPEECH`;
- it only processes 16-bit PCM blocks;
- it keeps one Sonic stream per speech `WavePlayer` while speech is active;
- it captures `Sonic pitch` at the start of an utterance and keeps that value
  until the utterance ends;
- it recreates that stream when the audio format or captured pitch changes at a
  safe boundary;
- it buffers the first chunk until about 50 ms of processed audio is available;
- it avoids `SonicStream.flush()` in the middle of ordinary audio blocks;
- it does not replace the active stream when Sonic pitch changes during active
  speech;
- it flushes the remaining Sonic stream tail before `WavePlayer.idle()`;
- it uses a global lock only for the processor map and a per-stream lock around
  Sonic calls;
- it bypasses non-speech sounds;
- it leaves remote-host audio such as `sapi5_32` to the host wrapper path;
- it falls back to the original `WavePlayer.feed` call on any exception.

The continuous stream is important for audio quality. Flushing Sonic after every
small block can create tiny gaps and artifacts because Sonic loses its internal
analysis window at block boundaries.

The bundled native path uses `ctypes` signatures for the Sonic C API. In 32-bit
NVDA processes, `_NoDestroySonicStream` intentionally leaks the small native
Sonic stream objects for process lifetime instead of calling
`sonicDestroyStream`, because local testing reproduced native heap corruption
when destroying those streams under NVDA 2025.3.3 x86.

## Logs

The most useful logs while debugging are:

- `%TEMP%\nvda.log`
- `%TEMP%\nvda-old.log`
- `%TEMP%\nvda_synthDriverHost.*.log`

Look for:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: applied remote SAPI5 32-bit Sonic pitch`
- `globalSonicPitch sapi5_32 host: deferred Sonic pitch until safe boundary`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`
- `globalSonicPitch: processed speech audio`
- `globalSonicPitch: Sonic is unavailable`

## Maintenance Warnings

This add-on relies on private NVDA internals:

- `synthDriverHandler.setSynth`
- `autoSettingsUtils.driverSetting.NumericDriverSetting`
- `globalVars.settingsRing.updateSupportedSettings`
- synth driver `supportedSettings`
- `synthDrivers.sapi5_32.SynthDriver.synthDriver32Path`
- `synthDrivers._sonic.SonicStream` as a fallback Sonic path
- `nvwave.WavePlayer.feed`
- `nvwave.WavePlayer.idle`
- `nvwave.WavePlayer.stop`
- `nvwave.WavePlayer.close`
- `nvwave.AudioPurpose.SPEECH`

Any NVDA release that changes those APIs may require add-on changes.
