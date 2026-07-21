# Technical Notes

This document records the current implementation details for Global Sonic
Pitch. It is intended for maintainers and reviewers.

## Design Goal

Global Sonic Pitch provides Sonic-based pitch adjustment without changing NVDA's
installed files and without adding replacement synthesizer entries to NVDA's
synthesizer dialog.

The add-on works in two paths:

- main-process speech audio processed through `nvwave.WavePlayer`;
- standard `sapi5_32` and `sapi4_32` on 64-bit NVDA controlled through bundled
  32-bit host wrappers.

## Configuration

Current config section:

```ini
[globalSonicPitch]
enabled = boolean(default=False)
pitch = integer(default=50, min=0, max=100)
pitchBySynth = string(default='{}')
extendedPitchRange = boolean(default=False)
sonicQuality = integer(default=0, min=0, max=1)
debugLogging = boolean(default=False)
```

`enabled` controls whether Sonic pitch processing is active.

`debugLogging` enables detailed diagnostic logging.

`extendedPitchRange` changes the pitch mapping from the standard 6-semitone
range to the optional 20-semitone range. It is disabled by default.

`sonicQuality` controls Sonic's native analysis quality. `0` is Sonic's fast
default mode and `1` enables Sonic's higher-quality analysis. The value is
clamped to `0` or `1`; no migration is needed for older configs because the
default remains `0`.

`pitchBySynth` stores current Sonic pitch values as JSON. Values are keyed by
the supported synthesizer and, when available, the selected voice:

```json
{
  "RHVoice::voice::Magda": 45,
  "sapi5_64::voice::Paulina": 38,
  "sapi5_32::voice::eSpeak-NG Polish": 44,
  "sapi4_32::voice::{C0123C20-8BCC-11D2-9B00-C0E1DF000000}": 75
}
```

`pitch` is kept only as a neutral legacy compatibility key for older configs.
New values are written to `pitchBySynth`.

## Pitch Scale

The add-on exposes `Sonic pitch` as a value from `0` to `100`, matching NVDA's
usual pitch scale.

`50` is neutral. By default, the full range maps to approximately `-6..+6`
semitones:

```text
maxSemitones = 6
semitones = ((pitchPercent - 50) / 50) * maxSemitones
ratio = 2 ** (semitones / 12)
```

When `extendedPitchRange` is enabled, `maxSemitones` is `20`, giving
approximately `-20..+20` semitones. The final Sonic pitch ratio is clamped to
the mathematically matching range for the selected mode.

## Native Pitch And Sonic Pitch

NVDA's normal `pitch` setting remains native synthesizer pitch.

The add-on's `sonicPitch` setting is a separate value. If both values are away
from neutral `50`, the user hears the combined native synthesizer pitch and
Sonic pitch processing.

The add-on does not patch synth `_get_pitch` or `_set_pitch` methods.

## Dynamic Voice Setting

While `[globalSonicPitch] enabled` is true, the plugin adds a
`NumericDriverSetting` with id `sonicPitch` to the active supported synth's
`supportedSettings`.

When global processing is disabled, the setting is removed again. This keeps
NVDA's normal Voice dialog and synth settings ring native-only while the add-on
is off.

The setting is not stored in the synth's own config. At runtime, the plugin
adds a class-level Python property named `sonicPitch` to the active synth class.
That property reads and writes the active synth and voice entry in
`[globalSonicPitch] pitchBySynth`.

When a writable `voice` property is available on the synth class, the add-on
wraps it so the current runtime Sonic pitch value is refreshed after NVDA
changes the selected voice.

The add-on updates `globalVars.settingsRing` after inserting or removing the
dynamic setting. If the `Synth ring settings selector` add-on is present, the
add-on adds `sonicPitch` to its `availableSettings` list.

## Main WavePlayer Path

The plugin hooks `nvwave.WavePlayer.feed` at runtime.

The hook is intentionally narrow:

- it only processes `WavePlayer` instances whose `_purpose` is
  `nvwave.AudioPurpose.SPEECH`;
- it only processes compatible speech audio blocks;
- it keeps one Sonic stream per speech `WavePlayer` while speech is active;
- it captures `Sonic pitch` and Sonic quality at the start of an utterance and
  keeps those values until the utterance ends;
- it recreates the stream when the audio format, captured pitch, or captured
  quality changes at a safe boundary;
- it applies Sonic quality to newly created streams before processing PCM;
- it buffers the first chunk until enough processed audio is available;
- it avoids `SonicStream.flush()` in the middle of ordinary audio blocks;
- it bypasses non-speech sounds;
- it falls back to the original `WavePlayer.feed` call on any exception.
- it ignores remote 32-bit SAPI synths in the main process because those paths
  are processed in the 32-bit synth host.

The continuous stream matters for audio quality. Flushing Sonic after every
small audio block can create gaps because Sonic loses its internal analysis
window at block boundaries.

## Bundled Sonic Library

The add-on bundles native Sonic libraries for 32-bit and 64-bit NVDA. If the
bundled library is unavailable, the add-on falls back to NVDA's internal Sonic
module when possible.

The bundled libraries are documented in:

- `addon/globalPlugins/sonicPitchNative/README.txt`
- `addon/globalPlugins/sonicPitchNative/LICENSE-Sonic.txt`

## Standard 32-bit SAPI Host Paths

The 64-bit NVDA `sapi5_32` and `sapi4_32` drivers speak in a separate 32-bit
host process. The main-process WavePlayer hook cannot process that audio
directly.

To support this path without replacing NVDA's synth, the add-on temporarily
points the relevant `synthDriver32Path` values at `addon/sapi32HostDrivers`
while the add-on is loaded.

`addon/sapi32HostDrivers/sapi5.py` runs inside the 32-bit host. It:

- locates NVDA's original `_synthDrivers32` directory;
- imports NVDA's original 32-bit SAPI5 implementation;
- adds host-side `sonicPitch`, `_sonicPitchExtendedRange`, and `_sonicQuality`
  parameters;
- maps `0..100` to the same Sonic pitch ratio as the main plugin;
- applies Sonic quality before pitch on new or replaced Sonic streams;
- applies pitch and quality changes at safe speech boundaries;
- serializes the full SAPI audio callback with parameter changes;
- replaces the host Sonic stream when the applied pitch, range, or quality
  changes;
- recovers from host Sonic write or flush failures by replacing the stream.

`addon/sapi32HostDrivers/sapi4.py` also runs inside the 32-bit host. It:

- locates NVDA's original `_synthDrivers32` directory;
- imports NVDA's original 32-bit SAPI4 implementation;
- subclasses the original `SynthDriverAudio` WASAPI audio receiver;
- adds host-side `sonicPitch`, `_sonicPitchExtendedRange`, and `_sonicQuality`
  parameters;
- applies Sonic quality to newly created SAPI4 processing streams;
- processes 16-bit PCM blocks before they are fed to the host `WavePlayer`;
- flushes the Sonic stream at the SAPI4 unclaim boundary;
- leaves the original SAPI4 voice enumeration and COM driver selection intact.

SAPI4 has two NVDA audio paths. When
`config.conf["speech"]["useWASAPIForSAPI4"]` is true, SAPI4 audio goes through
`SynthDriverAudio` and `nvwave.WavePlayer`, which the host wrapper can process.
When that setting is false, NVDA uses SAPI4's older `MMAudioDest` path. That
path sends audio directly through the Microsoft multimedia destination and
bypasses NVDA's `WavePlayer`; SonicPitch cannot process that direct path
without replacing substantially more of the SAPI4 COM audio implementation.

The host wrappers do not enumerate voices, add registry tokens, or modify
NVDA's installed files.

## Logs

Useful log files:

- `%TEMP%\nvda.log`
- `%TEMP%\nvda-old.log`
- `%TEMP%\nvda_synthDriverHost.*.log`

Useful search terms:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: applied Sonic quality`
- `globalSonicPitch: processed speech audio`
- `globalSonicPitch: applied remote 32-bit Sonic pitch`
- `globalSonicPitch sapi5_32 host: applied Sonic quality`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`
- `globalSonicPitch sapi5_32 host: replaced Sonic stream`
- `globalSonicPitch sapi4_32 host: applied Sonic quality`
- `globalSonicPitch sapi4_32 host: processed SAPI4 audio`
- `globalSonicPitch: Sonic is unavailable`

## Maintenance Warnings

This add-on relies on NVDA runtime APIs and some private implementation details:

- `synthDriverHandler.setSynth`
- `gui.settingsDialogs.setSynth`
- `autoSettingsUtils.driverSetting.NumericDriverSetting`
- `globalVars.settingsRing.updateSupportedSettings`
- synth driver `supportedSettings`
- synth driver `voice` properties where available
- `synthDrivers.sapi5_32.SynthDriver.synthDriver32Path`
- `synthDrivers.sapi4_32.SynthDriver.synthDriver32Path`
- `synthDrivers._sonic.SonicStream` as a fallback Sonic path
- `nvwave.WavePlayer.feed`
- `nvwave.WavePlayer.idle`
- `nvwave.WavePlayer.stop`
- `nvwave.WavePlayer.close`
- `nvwave.AudioPurpose.SPEECH`

Any NVDA release that changes these APIs may require add-on changes.
