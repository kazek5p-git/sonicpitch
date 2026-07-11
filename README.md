# SAPI5 Sonic Pitch

NVDA add-on that provides separate SAPI5 synthesizer drivers with Sonic-based
pitch processing:

- `SAPI5 32-bit Sonic Pitch`
- `SAPI5 64-bit Sonic Pitch`

It is intended for SAPI5 voices that ignore NVDA's normal pitch setting or apply
it poorly. The add-on does not patch the standard NVDA `sapi5` or `sapi5_32`
drivers; it exposes separate synth choices instead.

## Requirements

- NVDA 2025.1 or newer.
- Windows with SAPI5 voices installed.
- NVDA audio path exposing the built-in Sonic stream.

## Install

Download the latest `.nvda-addon` package from Releases and open it with NVDA.
After installation, restart NVDA and choose one of the new synthesizers from the
NVDA synthesizer dialog.

## Build

The source package root is `addon`. To package manually, zip the contents of
`addon` and rename the archive to `sapi5SonicPitch-<version>.nvda-addon`.

The release package for version 0.1.8 is built as:

`dist/sapi5SonicPitch-0.1.8.nvda-addon`

## Notes

This add-on uses NVDA private WASAPI/Sonic internals. If those internals change
in a future NVDA release, the add-on may require updates.
