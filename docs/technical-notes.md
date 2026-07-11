# Technical Notes

This document records the implementation details for Global Sonic Pitch.

## Design Goal

The add-on must provide Sonic-based pitch adjustment without changing NVDA's
installed files or adding replacement synthesizer drivers.

Version 0.3.0 changed the add-on identity from `sapi5SonicPitch` to
`globalSonicPitch` and removes the previous custom SAPI5 synth drivers from the
package. The current package contains only a global plugin and documentation.

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
for continuity but unsafe with some SAPI callback timing. The current behavior
recreates the per-player Sonic processor when pitch or audio format changes,
discards the old processor without flushing its tail on mid-utterance pitch
changes, and protects the processor map with an `RLock`.

Version 0.4.5 shortens the scope of the global processor-map lock. The map lock
now protects only lookup, insertion, removal, and reset. Each
`_SonicStreamProcessor` has its own lock for `SonicStream.writeShort`,
`readShort`, and `flush`. This keeps one stream serialized while avoiding a
global lock around expensive Sonic processing, which matters for fast SAPI5
voices such as eSpeak-NG SAPI at rate 100.

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
`sonicPitch` setting is a separate value stored in `[globalSonicPitch] pitch`.
If both are away from neutral `50`, the user hears the combined native synth
pitch and Sonic processing.

The add-on still wraps `synthDriverHandler.setSynth` so it can inject or remove
the dynamic `sonicPitch` setting after synth changes.

The built-in `sapi5_32` synth is excluded from Sonic processing because its
speech is produced in the separate 32-bit host on 64-bit NVDA. The main-process
global plugin cannot process that host's audio, so `sapi5_32` is left as a
normal native synth path.

## Dynamic Voice Setting

For supported main-process synths, while `[globalSonicPitch] enabled` is true,
the plugin adds a `NumericDriverSetting` with id `sonicPitch` to the active
synth instance's `supportedSettings`.

When `[globalSonicPitch] enabled` is false, the plugin removes that dynamic
setting again. This keeps NVDA's standard Voice dialog and synth settings ring
native-only while the add-on processing is disabled. The add-on's own settings
panel remains available so the user can turn the feature back on.

The setting is not stored in the synth's own config. At runtime, the plugin adds
a class-level Python `property` named `sonicPitch` to the active synth class.
That property reads and writes `[globalSonicPitch] pitch`.

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

## Global WavePlayer Path

`globalPlugins/globalSonicPitch.py` hooks `nvwave.WavePlayer.feed` at runtime.
It does not patch files on disk.

The hook is intentionally narrow:

- it only processes `WavePlayer` instances whose `_purpose` is
  `nvwave.AudioPurpose.SPEECH`;
- it only processes 16-bit PCM blocks;
- it keeps one Sonic stream per speech `WavePlayer` while speech is active;
- it recreates that stream when the audio format or `Sonic pitch` value changes;
- it buffers the first chunk until about 50 ms of processed audio is available;
- it avoids `SonicStream.flush()` in the middle of ordinary audio blocks;
- it discards the old stream rather than flushing a tail when Sonic pitch changes
  during active speech;
- it flushes the remaining Sonic stream tail before `WavePlayer.idle()`;
- it uses a global lock only for the processor map and a per-stream lock around
  Sonic calls;
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
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: processed speech audio`
- `globalSonicPitch: Sonic is unavailable`

## Maintenance Warnings

This add-on relies on private NVDA internals:

- `synthDriverHandler.setSynth`
- `autoSettingsUtils.driverSetting.NumericDriverSetting`
- `globalVars.settingsRing.updateSupportedSettings`
- synth driver `supportedSettings`
- `synthDrivers._sonic.SonicStream.pitch`
- `nvwave.WavePlayer.feed`
- `nvwave.WavePlayer.idle`
- `nvwave.WavePlayer.stop`
- `nvwave.WavePlayer.close`
- `nvwave.AudioPurpose.SPEECH`

Any NVDA release that changes those APIs may require add-on changes.
