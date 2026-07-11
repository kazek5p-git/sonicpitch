# SAPI5 Sonic Pitch

This NVDA add-on provides separate SAPI5 synth drivers for Sonic-based
pitch post-processing:

- SAPI5 32-bit Sonic Pitch
- SAPI5 64-bit Sonic Pitch

It is intended for SAPI5 voices that ignore NVDA pitch or implement pitch poorly.
It does not affect OneCore, eSpeak, RHVoice, Vocalizer, or other synth drivers.

The add-on requires NVDA 2025.1 or newer. It was tested on NVDA 2026.2 beta,
Python 3.13, 64-bit.

## How Pitch Works

Pitch 50 is neutral. The full NVDA pitch range maps to approximately -6 to +6
semitones, then to a Sonic pitch ratio. The ratio is clamped to 0.70..1.45.

The driver keeps SAPI XML pitch neutral by returning 0 from `_percentToPitch`.
This avoids double pitch processing, but dynamic embedded pitch commands may be
neutralized.

## 32-bit and 64-bit Separation

On 64-bit NVDA, the 64-bit driver subclasses `synthDrivers.sapi5.SynthDriver`.
The 32-bit driver uses NVDA's `SynthDriverProxy32` and a private host-side module
so Sonic pitch is applied inside the 32-bit SAPI5 host process.

On 32-bit NVDA, the 32-bit driver subclasses local `synthDrivers.sapi5.SynthDriver`.
The 64-bit driver refuses to load.

Each driver exposes only the voices available through its own SAPI5 bitness.

## Limitations

- No custom Sonic DLLs or native binaries are bundled.
- WASAPI/Sonic internals are private NVDA implementation details.
- If Sonic or `_initWasapiAudio` changes in NVDA, this add-on may need updates.
- Legacy non-WASAPI output does not expose `sonicStream`, so Sonic pitch cannot be applied there.
