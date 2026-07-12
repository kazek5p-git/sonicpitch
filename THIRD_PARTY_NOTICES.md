# Third-Party Notices

Global Sonic Pitch bundles native Sonic libraries so the add-on can use a known
Sonic build on both 32-bit and 64-bit NVDA.

## Sonic

Files:

- `addon/globalPlugins/sonicPitchNative/sonicPitchSonic32.dll`
- `addon/globalPlugins/sonicPitchNative/sonicPitchSonic64.dll`

License: Apache License 2.0.

The bundled license text is included at:

- `addon/globalPlugins/sonicPitchNative/LICENSE-Sonic.txt`

The add-on also keeps a fallback to NVDA's internal Sonic module if the bundled
library cannot be loaded.
