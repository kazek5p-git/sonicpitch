# Third-Party Notices

Global Sonic Pitch bundles native Sonic libraries for 32-bit and 64-bit NVDA.

## Sonic

The bundled DLLs are unmodified Sonic binaries distributed with the official
NV Access alpha snapshot `nvda_snapshot_alpha-55934,102a54ea`.

Upstream project:
https://github.com/waywardgeek/sonic

NVDA source:
https://github.com/nvaccess/nvda

Sonic source revision:
`b93885dcb70aae50c6f76b0fe4e0868f029a077e`

Bundled files:

- `addon/globalPlugins/sonicPitchNative/sonic32.dll`
- `addon/globalPlugins/sonicPitchNative/sonic64.dll`

The binary contents are redistributed unchanged from the NVDA build. Only
their file names inside the add-on have been changed.

License: Apache License 2.0.

The bundled license text is included at:

- `addon/globalPlugins/sonicPitchNative/LICENSE-Sonic.txt`

Global Sonic Pitch keeps these copies separate from NVDA's loaded Sonic module
so that the add-on manages its own Sonic stream lifetime independently.

The add-on also retains a fallback to NVDA's internal Sonic module if the
bundled library cannot be loaded.
