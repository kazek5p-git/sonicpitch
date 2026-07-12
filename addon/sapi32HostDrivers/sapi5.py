# 32-bit SAPI5 host wrapper for Global Sonic Pitch.

from __future__ import annotations

import os
import sys

try:
	from logHandler import log
except Exception:
	log = None

try:
	_
except NameError:
	_ = lambda message: message


SONIC_PITCH_SETTING_ID = "sonicPitch"
NEUTRAL_PITCH = 50
MAX_SEMITONES = 6.0
MIN_SONIC_PITCH_RATIO = 0.70
MAX_SONIC_PITCH_RATIO = 1.45


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def _clampPitch(value: int | float) -> int:
	try:
		numericValue = float(value)
	except Exception:
		numericValue = float(NEUTRAL_PITCH)
	return int(_clamp(numericValue, 0.0, 100.0))


def _pitchPercentToSonicRatio(pitchPercent: int | float) -> float:
	pitchPercent = _clamp(float(pitchPercent), 0.0, 100.0)
	semitones = ((pitchPercent - 50.0) / 50.0) * MAX_SEMITONES
	ratio = 2.0 ** (semitones / 12.0)
	return _clamp(ratio, MIN_SONIC_PITCH_RATIO, MAX_SONIC_PITCH_RATIO)


def _logInfo(message: str) -> None:
	if log is not None:
		log.info(message)


def _logWarning(message: str) -> None:
	if log is not None:
		log.debugWarning(message, exc_info=True)


def _candidateAppDirs() -> list[str]:
	candidates: list[str] = []
	try:
		import globalVars

		appDir = getattr(globalVars, "appDir", None)
		if appDir:
			candidates.append(str(appDir))
	except Exception:
		pass
	try:
		import NVDAState

		readPaths = getattr(NVDAState, "ReadPaths", None)
		for attr in ("appDir", "appDirPath"):
			appDir = getattr(readPaths, attr, None)
			if appDir:
				candidates.append(str(appDir))
	except Exception:
		pass
	if getattr(sys, "executable", ""):
		candidates.append(os.path.abspath(os.path.join(os.path.dirname(sys.executable), "..", "..", "..", "..")))
	for path in list(sys.path):
		if path:
			candidates.append(os.path.abspath(path))
	seen: set[str] = set()
	unique: list[str] = []
	for path in candidates:
		path = os.path.abspath(path)
		key = os.path.normcase(path)
		if key in seen:
			continue
		seen.add(key)
		unique.append(path)
	return unique


def _findOriginalSynthDrivers32Path() -> str:
	thisDir = os.path.abspath(os.path.dirname(__file__))
	for appDir in _candidateAppDirs():
		for candidate in (
			os.path.join(appDir, "_synthDrivers32"),
			appDir if os.path.basename(appDir).lower() == "_synthdrivers32" else "",
		):
			if not candidate:
				continue
			candidate = os.path.abspath(candidate)
			if os.path.normcase(candidate) == os.path.normcase(thisDir):
				continue
			if os.path.isfile(os.path.join(candidate, "_sapi5.py")) and os.path.isfile(
				os.path.join(candidate, "sapi5.py"),
			):
				return candidate
	raise RuntimeError("Could not locate NVDA _synthDrivers32 directory")


_ORIGINAL_SYNTH_DRIVERS_32_PATH = _findOriginalSynthDrivers32Path()

try:
	import synthDrivers

	if _ORIGINAL_SYNTH_DRIVERS_32_PATH not in synthDrivers.__path__:
		synthDrivers.__path__.append(_ORIGINAL_SYNTH_DRIVERS_32_PATH)
except Exception:
	_logWarning("globalSonicPitch sapi5_32 host: failed to append original synth driver path")
	raise

import comtypes.client

sys.modules["comInterfaces.SpeechLib"] = comtypes.client.GetModule(
	r"c:\windows\system32\speech\common\sapi.dll",
)

from . import _sonic  # noqa: E402

_sonic.SONIC_DLL_PATH = os.path.join(_ORIGINAL_SYNTH_DRIVERS_32_PATH, "sonic.dll")

from ._sapi5 import SynthDriver as _BaseSynthDriver  # noqa: E402

try:
	from autoSettingsUtils.driverSetting import NumericDriverSetting
except Exception:
	NumericDriverSetting = None


def _createSonicPitchSetting():
	if NumericDriverSetting is None:
		return None
	try:
		return NumericDriverSetting(
			SONIC_PITCH_SETTING_ID,
			_("Sonic pitch"),
			availableInSettingsRing=False,
			defaultVal=NEUTRAL_PITCH,
			minVal=0,
			maxVal=100,
			minStep=1,
			normalStep=5,
			largeStep=10,
			displayName=_("Sonic pitch"),
			useConfig=False,
		)
	except TypeError:
		return NumericDriverSetting(
			SONIC_PITCH_SETTING_ID,
			_("Sonic pitch"),
			False,
			NEUTRAL_PITCH,
			0,
			100,
			1,
			5,
			10,
			_("Sonic pitch"),
			False,
		)


_SONIC_PITCH_SETTING = _createSonicPitchSetting()


class SynthDriver(_BaseSynthDriver):
	if _SONIC_PITCH_SETTING is None:
		supportedSettings = _BaseSynthDriver.supportedSettings
	else:
		supportedSettings = tuple(
			setting for setting in _BaseSynthDriver.supportedSettings if getattr(setting, "id", "") != SONIC_PITCH_SETTING_ID
		) + (_SONIC_PITCH_SETTING,)

	def __init__(self, *args, **kwargs):
		self._sonicPitch = NEUTRAL_PITCH
		super().__init__(*args, **kwargs)
		self._applySonicPitch()
		_logInfo(
			"globalSonicPitch sapi5_32 host: initialized Sonic pitch wrapper; "
			f"originalPath={_ORIGINAL_SYNTH_DRIVERS_32_PATH}",
		)

	def _get_sonicPitch(self) -> int:
		return _clampPitch(getattr(self, "_sonicPitch", NEUTRAL_PITCH))

	def _set_sonicPitch(self, value: int | float) -> None:
		self._sonicPitch = _clampPitch(value)
		self._applySonicPitch()

	def _applySonicPitch(self) -> None:
		stream = getattr(self, "sonicStream", None)
		if stream is None:
			return
		ratio = _pitchPercentToSonicRatio(self._sonicPitch)
		stream.pitch = ratio
		_logInfo(
			"globalSonicPitch sapi5_32 host: set Sonic pitch; "
			f"sonicPitch={self._sonicPitch}; ratio={ratio:.4f}",
		)

	def _initWasapiAudio(self):
		super()._initWasapiAudio()
		self._applySonicPitch()


__all__ = ["SynthDriver"]
