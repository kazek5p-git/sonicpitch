# Local NVDA Inspection

Inspection was performed on this machine from `C:\Program Files\NVDA`.

- Installed NVDA version data: `2026.2beta5`, build `56710`.
- NVDA Python runtime found in the install: Python 3.13 DLLs.
- Current shell Python used for static tooling: Python 3.14.3, 64-bit.
- Current installed NVDA architecture: 64-bit.
- 64-bit SAPI5 base module detected: `synthDrivers.sapi5` from `library.zip`.
- 64-bit base description detected from bytecode constants: `Microsoft Speech API version 5 (64 bit)`.
- Runtime compatibility is not gated on this description because it may be translated.
- 32-bit SAPI5 proxy module detected: `synthDrivers.sapi5_32` from `library.zip`.
- 32-bit proxy description detected from bytecode constants: `Microsoft Speech API version 5 (32 bit)`.
- 32-bit in-host base module detected: `C:\Program Files\NVDA\_synthDrivers32\sapi5.py`.
- 32-bit in-host base imports `._sapi5.SynthDriver`.
- 32-bit in-host `_sapi5.SynthDriver` source keeps the base description `Microsoft Speech API version 5 (64 bit)`.
- For this reason, the add-on validates 32-bit host compatibility by process bitness and module path, not by that internal description.
- 32-bit in-host Sonic wrapper detected: `C:\Program Files\NVDA\_synthDrivers32\_sonic.py`.
- Sonic wrapper exposes `SonicStream.pitch` as a property with a setter.
- Base SAPI5 class exposes `sonicStream`.
- Base SAPI5 class exposes `_initWasapiAudio`.
- Built-in rate boost uses `sonicStream.speed`; this prototype only sets `sonicStream.pitch`.

Detected separation:

- 64-bit SAPI5 path: `synthDrivers.sapi5.SynthDriver`.
- 32-bit SAPI5 path on 64-bit NVDA: `SynthDriverProxy32` points to a host module by path and name.
- 32-bit SAPI5 path inside the host: host imports `synthDrivers.sapi5`, which resolves to the 32-bit host driver.

Private internals used:

- `synthDrivers.sapi5.SynthDriver`.
- `_bridge.clients.synthDriverHost32.synthDriver.SynthDriverProxy32`.
- `SynthDriverProxy32.synthDriver32Path`.
- `SynthDriverProxy32.synthDriver32Name`.
- `SynthDriver._initWasapiAudio`.
- `SynthDriver.sonicStream`.
- `SonicStream.pitch`.
