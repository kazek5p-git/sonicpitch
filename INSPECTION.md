# Local NVDA Inspection

Inspection was performed on this machine from `C:\Program Files\NVDA`.

- Installed NVDA version data: `2026.2beta5`, build `56710`.
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
- The built-in `sapi5_32` host path is deliberately excluded from pitch
  takeover in the main process.
- Runtime pitch takeover is done by patching the active synth instance's
  `_set_pitch` and `_get_pitch` methods, then restoring those methods when the
  plugin terminates.

Private internals used:

- `synthDriverHandler.setSynth`
- synth driver `_set_pitch` and `_get_pitch`
- `synthDrivers._sonic.SonicStream.pitch`
- `nvwave.WavePlayer.feed`
- `nvwave.AudioPurpose.SPEECH`
