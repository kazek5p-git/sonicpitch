Bundled Sonic native library
============================

This directory contains local Windows builds of the Sonic library used by
Global Sonic Pitch when processing NVDA speech audio.

Source: https://github.com/waywardgeek/sonic
Commit used for these builds: b93885dcb70aae50c6f76b0fe4e0868f029a077e
License: Apache License 2.0, included in LICENSE-Sonic.txt.

The source was built without local source modifications. The DLLs export the
standard Sonic C API symbols used by NVDA's _sonic wrapper.

Files:
- sonicPitchSonic32.dll: 32-bit Windows build for 32-bit NVDA processes.
- sonicPitchSonic64.dll: 64-bit Windows build for 64-bit NVDA processes.
