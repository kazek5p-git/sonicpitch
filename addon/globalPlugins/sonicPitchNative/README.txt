Bundled Sonic native library
============================

This directory contains unmodified Windows builds of the Sonic library taken
from the official NV Access alpha snapshot:

nvda_snapshot_alpha-55934,102a54ea

Global Sonic Pitch bundles these binaries as separate add-on-local libraries
so that it can use its own Sonic library instance instead of sharing NVDA's
already loaded Sonic module. This keeps the add-on's Sonic stream lifetime
independent from NVDA's internal Sonic usage.

Upstream source:
https://github.com/waywardgeek/sonic

NVDA source:
https://github.com/nvaccess/nvda

Sonic source revision used by this NVDA build:
b93885dcb70aae50c6f76b0fe4e0868f029a077e

License:
Apache License 2.0, included in LICENSE-Sonic.txt.

The binary contents are redistributed unchanged from the official NVDA build.
Only the file names used inside the add-on have been changed.

Files:

- sonic32.dll
  32-bit x86 Sonic binary.
  Original NVDA file: _synthDrivers32\sonic.dll
  SHA-256:
  4be05ee9824c985da10ead3d1e73f3363de57e2f652905f2001e5fe94c273257

- sonic64.dll
  64-bit x64 Sonic binary.
  Original NVDA file: synthDrivers\sonic.dll
  SHA-256:
  67aeb94831616c599d45600724e464384c97c6173a4b42b7af990f489fc6c60e

The DLLs export the standard Sonic C API. Global Sonic Pitch uses the subset
required by NVDA's _sonic-compatible processing wrapper.

If the bundled library cannot be loaded, Global Sonic Pitch retains its
fallback to NVDA's internal Sonic module.
