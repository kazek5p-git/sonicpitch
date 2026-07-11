# SAPI5 Sonic Pitch

SAPI5 Sonic Pitch adds separate SAPI5 synthesizers that apply NVDA pitch through
NVDA's internal Sonic audio processing. It also includes an experimental global
Sonic pitch processor for PCM speech audio.

## Added Synthesizers

- SAPI5 32-bit Sonic Pitch
- SAPI5 64-bit Sonic Pitch

These are separate synthesizers. The add-on does not modify NVDA's standard
SAPI5 32-bit or 64-bit synthesizers.

The global processor is disabled by default. It can be enabled in NVDA Settings,
category SAPI5 Sonic Pitch.

## Purpose

Some SAPI5 voices ignore NVDA's normal pitch setting, or implement it in a way
that sounds poor. This add-on keeps SAPI XML pitch neutral and applies the
global pitch setting through Sonic instead.

The add-on affects only its own Sonic Pitch synthesizers. It does not affect
OneCore, eSpeak, RHVoice, Vocalizer, or other synth drivers unless the optional
global processor is enabled.

## Requirements

- NVDA 2025.1 or newer.
- Windows with SAPI5 voices installed.
- NVDA audio output using the modern WASAPI/Sonic path.
- For 32-bit voices on 64-bit NVDA, NVDA's 32-bit synth host must be present.

## Usage

1. Open NVDA's synthesizer dialog.
2. Choose SAPI5 32-bit Sonic Pitch or SAPI5 64-bit Sonic Pitch.
3. Open NVDA voice settings.
4. Change pitch using the normal pitch setting.

Pitch 50 is neutral. Values below 50 lower the voice, and values above 50 raise
the voice. The full NVDA pitch range maps to about -6 to +6 semitones and is
limited to a Sonic ratio of 0.70..1.45.

Rate, volume, voice selection, and rate boost remain handled by NVDA's normal
SAPI5 driver behavior.

## Global Sonic Pitch

The global processor hooks NVDA's speech `WavePlayer` at runtime. It processes
16-bit PCM speech blocks with Sonic and falls back to original audio if
processing fails.

It skips this add-on's own SAPI5 Sonic Pitch synthesizers by default to avoid
double processing. For the cleanest test with eSpeak, RHVoice, OneCore, or
Vocalizer, keep the selected synth's native pitch neutral and use the global
pitch setting in the SAPI5 Sonic Pitch settings panel.

The standard SAPI5 32-bit synthesizer is not globally filtered on 64-bit NVDA
because it runs in NVDA's separate 32-bit synth host. Use SAPI5 32-bit Sonic
Pitch for 32-bit SAPI5 voices.

## 32-bit And 64-bit Voices

Windows stores 32-bit and 64-bit SAPI5 voices separately. A 32-bit voice may not
appear in the 64-bit synthesizer, and a 64-bit voice may not appear in the
32-bit synthesizer.

On 64-bit NVDA, the 32-bit Sonic Pitch synthesizer runs through NVDA's 32-bit
synth host. The 64-bit Sonic Pitch synthesizer runs directly in NVDA.

## Troubleshooting

If a Sonic Pitch synthesizer does not appear, check that the matching built-in
SAPI5 path is available in NVDA.

If the 32-bit Sonic Pitch synthesizer does not load, first test NVDA's built-in
Microsoft Speech API version 5 (32 bit) synthesizer. If the built-in
synthesizer also fails, the issue is not specific to this add-on.

If the standard SAPI5 synthesizers fail only while this add-on is enabled,
disable global Sonic processing in the SAPI5 Sonic Pitch settings panel and
check the NVDA log. The add-on must not patch the standard SAPI5 synth drivers.

Useful log files:

- %TEMP%\nvda.log
- %TEMP%\nvda-old.log
- %TEMP%\nvda_synthDriverHost.*.log

Search for sapi5SonicPitch, sapi5SonicPitch32, sapi5SonicPitch64,
sapi5SonicPitchGlobal, or Sonic pitch unavailable.

## Limitations

- The add-on uses private NVDA WASAPI/Sonic internals.
- The global processor hooks `nvwave.WavePlayer.feed` at runtime.
- Future NVDA changes may require add-on updates.
- Legacy audio paths without Sonic cannot use this pitch method.
- Embedded pitch commands may be neutralized to avoid double pitch processing.
