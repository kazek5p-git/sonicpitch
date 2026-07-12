# 32-bit SAPI5 host wrapper for Global Sonic Pitch.

from __future__ import annotations

import os
import sys
import threading

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

from . import _sapi5  # noqa: E402
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


class _LockedSonicStream:
	def __init__(self, stream, lock):
		self._stream = stream
		self._lock = lock

	def __getattr__(self, name: str):
		return getattr(self._stream, name)

	def writeShort(self, *args, **kwargs):
		with self._lock:
			return self._stream.writeShort(*args, **kwargs)

	def readShort(self, *args, **kwargs):
		with self._lock:
			return self._stream.readShort(*args, **kwargs)

	def flush(self, *args, **kwargs):
		with self._lock:
			return self._stream.flush(*args, **kwargs)

	@property
	def samplesAvailable(self) -> int:
		with self._lock:
			return self._stream.samplesAvailable

	@property
	def sampleRate(self) -> int:
		with self._lock:
			return self._stream.sampleRate

	@property
	def channels(self) -> int:
		with self._lock:
			return self._stream.channels

	@property
	def speed(self) -> float:
		with self._lock:
			return self._stream.speed

	@speed.setter
	def speed(self, value: float) -> None:
		with self._lock:
			self._stream.speed = value

	@property
	def pitch(self) -> float:
		with self._lock:
			return self._stream.pitch

	@pitch.setter
	def pitch(self, value: float) -> None:
		with self._lock:
			self._stream.pitch = value


class SynthDriver(_BaseSynthDriver):
	if _SONIC_PITCH_SETTING is None:
		supportedSettings = _BaseSynthDriver.supportedSettings
	else:
		supportedSettings = tuple(
			setting for setting in _BaseSynthDriver.supportedSettings if getattr(setting, "id", "") != SONIC_PITCH_SETTING_ID
		) + (_SONIC_PITCH_SETTING,)

	def __init__(self, *args, **kwargs):
		self._sonicPitchLock = threading.RLock()
		self._sonicPitch = NEUTRAL_PITCH
		self._lastAppliedSonicPitch: int | None = None
		super().__init__(*args, **kwargs)
		_logInfo(
			"globalSonicPitch sapi5_32 host: initialized Sonic pitch wrapper; "
			f"originalPath={_ORIGINAL_SYNTH_DRIVERS_32_PATH}",
		)

	def _get_sonicPitch(self) -> int:
		return _clampPitch(getattr(self, "_sonicPitch", NEUTRAL_PITCH))

	def _set_sonicPitch(self, value: int | float) -> None:
		self._sonicPitch = _clampPitch(value)
		self._applySonicPitchIfSafe()

	def _isSonicPitchApplySafe(self) -> bool:
		return not (
			getattr(self, "_isSpeaking", False)
			or getattr(self, "_isCancelling", False)
			or bool(getattr(self, "_speakRequests", ()))
		)

	def _applySonicPitchIfSafe(self) -> bool:
		if not self._isSonicPitchApplySafe():
			_logInfo(
				"globalSonicPitch sapi5_32 host: deferred Sonic pitch until safe boundary; "
				f"sonicPitch={self._sonicPitch}",
			)
			return False
		return self._applySonicPitch(force=True)

	def _applySonicPitch(self, force: bool = False) -> bool:
		if not force and not self._isSonicPitchApplySafe():
			return False
		stream = getattr(self, "sonicStream", None)
		if stream is None:
			return False
		sonicPitch = _clampPitch(self._sonicPitch)
		if self._lastAppliedSonicPitch == sonicPitch:
			return True
		ratio = _pitchPercentToSonicRatio(sonicPitch)
		with self._sonicPitchLock:
			stream.pitch = ratio
			self._lastAppliedSonicPitch = sonicPitch
			_logInfo(
				"globalSonicPitch sapi5_32 host: set Sonic pitch; "
				f"sonicPitch={sonicPitch}; ratio={ratio:.4f}",
			)
		return True

	def _initWasapiAudio(self):
		super()._initWasapiAudio()
		if self.sonicStream is not None and not isinstance(self.sonicStream, _LockedSonicStream):
			self.sonicStream = _LockedSonicStream(self.sonicStream, self._sonicPitchLock)
		self._lastAppliedSonicPitch = None
		self._applySonicPitch(force=True)

	def _onEndStream(self) -> None:
		super()._onEndStream()
		self._applySonicPitch(force=True)

	def _speakThread(self):
		request = None
		while not self._isStoppingThread:
			with self._threadCond:
				self._threadCond.wait_for(self._requestsAvailable)
				if self._speakRequests:
					request = self._speakRequests.popleft()
					self._isCancelling = False
					self._isCompleted = False
			if request is not None:
				text, bookmarks = request
				self._bookmarkLists.append(bookmarks)
				try:
					self._applySonicPitch(force=True)
					self.tts.Speak(
						text,
						_sapi5.SpeechVoiceSpeakFlags.IsXML | _sapi5.SpeechVoiceSpeakFlags.Async,
					)
					with self._threadCond:
						self._threadCond.wait_for(self._requestCompleted)
					if not self._isCancelling:
						self.sonicStream.flush()
						audioData = self.sonicStream.readShort()
						self.player.feed(audioData, len(audioData) * 2)
						self._onEndStream()
				except Exception:
					self._bookmarkLists.pop()
					_logWarning("globalSonicPitch sapi5_32 host: error speaking")
				request = None
				if not self._requestsAvailable():
					self.player.idle()
			if self._isCancelling:
				self.tts.Speak(
					None,
					_sapi5.SpeechVoiceSpeakFlags.Async | _sapi5.SpeechVoiceSpeakFlags.PurgeBeforeSpeak,
				)
				self._bookmarkLists.clear()
				if self.sonicStream:
					self.sonicStream.flush()
					self.sonicStream.readShort()
				self._isCancelling = False
				self._applySonicPitch(force=True)


__all__ = ["SynthDriver"]
