# Local NVDA Inspection

Inspection was performed on this machine from `C:\Program Files\NVDA`.

- Installed NVDA version data observed during local testing: `2026.2beta6`,
  64-bit.
- NVDA Python runtime found in the install: Python 3.13 DLLs.
- Current shell Python used for static tooling: Python 3.14.3, 64-bit.
- Current installed NVDA architecture: 64-bit.
- The installed NVDA build contains `synthDrivers._sonic` in `library.zip`.
- The 32-bit synth host contains `_synthDrivers32\_sonic.py`.
- The installed NVDA build exposes `nvwave.WavePlayer`.
- Speech audio purpose is available as `nvwave.AudioPurpose.SPEECH`.
- Built-in `sapi5_32` still runs through a separate 32-bit synth host on
  64-bit NVDA.

Current add-on implications:

- The add-on must package only a global plugin and documentation.
- The add-on must not ship `addon/synthDrivers`, because that would add custom
  synth choices to NVDA's synthesizer dialog.
- Global audio processing can only cover speech audio that reaches the main
  NVDA process.
- The built-in `sapi5_32` host path is deliberately excluded from global Sonic
  audio processing in the main process.
- The add-on does not patch the active synth's native `pitch` setting in
  version 0.4.1 and newer.
- Runtime integration with the Voice dialog and synth settings ring is done by
  injecting a separate `sonicPitch` setting into the active synth's
  `supportedSettings` while global Sonic pitch is enabled.
- When global Sonic pitch is disabled, `sonicPitch` is removed from the active
  synth's Voice settings and synth settings ring.
- The `sonicPitch` setting is backed by a runtime class-level Python property
  on the active synth class and stores its value in `[globalSonicPitch] pitch`.
- NVDA's normal `pitch` setting remains native synth pitch.

Private internals used:

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
