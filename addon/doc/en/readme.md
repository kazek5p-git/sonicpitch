# Global Sonic Pitch

Global Sonic Pitch applies NVDA speech pitch through Sonic audio processing in
the main NVDA process.

## What It Does

The add-on adds a settings panel named Global Sonic Pitch. It does not add any
new synthesizers to NVDA's synthesizer dialog.

When enabled, the add-on captures NVDA's normal pitch setting, keeps the active
synth's native pitch at neutral 50 where possible, and applies the pitch change
to speech audio through Sonic.

## Use

1. Open NVDA Settings.
2. Choose Global Sonic Pitch.
3. Enable global Sonic pitch.
4. Change pitch from NVDA's normal voice settings or synth settings ring.

The Sonic pitch slider in the add-on panel changes the same add-on pitch value.

Pitch 50 is neutral. Values below 50 lower the voice. Values above 50 raise the
voice. The range maps to roughly -6 to +6 semitones.

## Notes

The add-on works only for speech audio that reaches the main NVDA WavePlayer as
16-bit PCM. The standard 32-bit SAPI5 synth on 64-bit NVDA runs in a separate
32-bit synth host, so this global plugin does not process that audio and does
not take over its pitch.

If old SAPI5 Sonic Pitch synthesizers still appear in the synthesizer list,
remove the older sapi5SonicPitch add-on and restart NVDA.

Useful log entries include globalSonicPitch, pitch takeover active, captured
NVDA pitch, and processed speech audio.
