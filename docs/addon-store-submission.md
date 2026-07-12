# NVDA Add-on Store Submission Notes

This document keeps the information needed to submit Global Sonic Pitch to the
NVDA Add-on Store.

## Current Store Readiness

Status: mostly ready after version 0.4.15.

Completed:

- Add-on name is unique: `globalSonicPitch`.
- Package version uses `major.minor.patch`: `0.4.15`.
- Manifest uses HTTPS project URL.
- Manifest declares stable compatibility:
  - `minimumNVDAVersion = 2025.1.0`
  - `lastTestedNVDAVersion = 2026.1.1`
- Root repository license file exists.
- Bundled Sonic native binaries include Apache 2.0 license metadata.
- The add-on does not patch NVDA files on disk.
- The add-on does not write SAPI voice tokens to the registry.
- Old SAPI voice-enumeration experiments were removed.
- Standard `sapi5_32` on 64-bit NVDA is supported through a bundled host
  wrapper that is loaded at runtime and does not replace NVDA files.
- Rapid `sapi5_32` Sonic pitch changes on 64-bit NVDA are deferred to safe
  32-bit host speech boundaries.
- Voice dialog style `sapi5_32` stress on 64-bit NVDA is handled by replacing
  host Sonic streams on applied pitch changes.
- Voice dialog Sonic pitch changes now follow normal settings behavior: OK or
  Apply commits, while Escape or Cancel restores the previous value.
- Current GitHub Release contains one `.nvda-addon` asset.
- User documentation exists in English and Polish.
- Store submission metadata draft is recorded below.

Before submitting:

- Run one final smoke test on the exact stable NVDA version named in the
  manifest if the local machine is not already on that version.
- Confirm the GitHub Release download URL points to the newest package.
- Confirm old unstable GitHub Releases have been deleted.

## Store Metadata Draft

Use this as the basis for the add-on store submission issue or JSON metadata.

```json
{
  "addonId": "globalSonicPitch",
  "displayName": "Global Sonic Pitch",
  "URL": "https://github.com/kazek5p-git/sonicpitch",
  "description": "Adds optional global Sonic pitch processing for NVDA speech audio.",
  "sha256": "0A6F4DDA1FF321E57043989BA8E7618BE5E39BEC4E5C13FEAA1339CE8467C902",
  "addonVersionName": "0.4.15",
  "channel": "stable",
  "publisher": "Kazek",
  "sourceURL": "https://github.com/kazek5p-git/sonicpitch",
  "license": "GPL v2 or later",
  "licenseURL": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt",
  "homepage": "https://github.com/kazek5p-git/sonicpitch",
  "downloadURL": "https://github.com/kazek5p-git/sonicpitch/releases/download/v0.4.15/globalSonicPitch-0.4.15.nvda-addon",
  "minimumNVDAVersion": "2025.1.0",
  "lastTestedNVDAVersion": "2026.1.1",
  "reviewURL": "https://github.com/kazek5p-git/sonicpitch/releases/tag/v0.4.15"
}
```

## Public Description

Global Sonic Pitch adds a separate `Sonic pitch` control to supported NVDA
synthesizers. It changes pitch through Sonic audio processing while leaving
NVDA's normal native `Pitch` setting unchanged.

The add-on works as a global plugin. It processes speech audio that reaches
NVDA's main `WavePlayer`, and it controls standard `sapi5_32` on 64-bit NVDA
through a small 32-bit host wrapper instead of replacing SAPI5 or any other
synthesizer driver.

Key points:

- `Sonic pitch` is stored separately per supported synthesizer.
- The normal NVDA `Pitch` setting remains the synth's own native pitch.
- The `Sonic pitch` slider appears only while global processing is enabled.
- The add-on uses bundled 32-bit and 64-bit Sonic native libraries.
- Standard `sapi5_32` on 64-bit NVDA uses a bundled 32-bit host wrapper and
  remains the normal NVDA `sapi5_32` synthesizer.
- It avoids changing already-used native Sonic streams in place.
- It does not modify NVDA files, write registry voice tokens, or add SAPI voice
  list entries.

## Compatibility Notes

Supported when speech audio reaches the main NVDA `WavePlayer` as 16-bit PCM:

- RHVoice.
- eSpeak NG in the NVDA main process.
- OneCore in the NVDA main process.
- 64-bit SAPI5 voices using NVDA's standard audio path.
- Standard `sapi5_32` on 64-bit NVDA through the bundled 32-bit host wrapper.

Known limitation:

- Third-party SAPI voices, including eSpeak-NG SAPI, must already be configured
  and visible to NVDA's standard SAPI voice list. The add-on does not add or
  repair SAPI voice registrations.

## Release Safety Policy

Only stable releases should be kept visible on GitHub Releases.

If a release can freeze or crash NVDA, delete the GitHub Release entry after a
fixed release is available. Keep git tags unless there is a separate reason to
remove them; tags preserve source history without encouraging users to install
old assets.

## Verification Checklist

Before each store-facing release:

1. Run syntax check:

   ```powershell
   python -m py_compile addon\globalPlugins\globalSonicPitch.py addon\sapi32HostDrivers\sapi5.py addon\installTasks.py
   ```

2. Build the package from the contents of `addon`.

3. Verify the archive contains:

   - `manifest.ini`
   - `globalPlugins/globalSonicPitch.py`
   - `sapi32HostDrivers/sapi5.py`
   - `globalPlugins/sonicPitchNative/sonicPitchSonic32.dll`
   - `globalPlugins/sonicPitchNative/sonicPitchSonic64.dll`
   - `doc/en/readme.md`
   - `doc/pl/readme.md`

4. Verify the archive does not contain `__pycache__`.

5. Run at least:

   - Stable NVDA x64 smoke test with SAPI5.
   - Stable NVDA x64 smoke test with standard `sapi5_32`.
   - NVDA 2025.3.3 x86 portable crash-regression test with SAPI5 at rate 100.
   - Voice dialog Escape/Cancel rollback test for `Sonic pitch`.
   - Slider feedback test covering repeated PageUp/PageDown changes.

6. Confirm the log contains no Global Sonic Pitch exceptions:

   - `globalSonicPitch: failed`
   - `failed to process WavePlayer feed`
   - `failed to finish retired Sonic stream`
   - `OSError: exception: access violation`

7. Publish one GitHub Release with exactly one `.nvda-addon` asset.

8. Update the `sha256` field in the metadata draft.
