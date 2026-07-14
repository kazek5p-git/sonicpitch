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
SONIC_PITCH_EXTENDED_RANGE_PARAM_ID = "_sonicPitchExtendedRange"
SONIC_PITCH_HOST_SETTING_IDS = {SONIC_PITCH_SETTING_ID, SONIC_PITCH_EXTENDED_RANGE_PARAM_ID}
NEUTRAL_PITCH = 50
STANDARD_MAX_SEMITONES = 6.0
EXTENDED_MAX_SEMITONES = 20.0


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def _clampPitch(value: int | float) -> int:
	try:
		numericValue = float(value)
	except Exception:
		numericValue = float(NEUTRAL_PITCH)
	return int(_clamp(numericValue, 0.0, 100.0))


def _pitchPercentToSonicRatio(pitchPercent: int | float, extendedRange: bool = False) -> float:
	pitchPercent = _clamp(float(pitchPercent), 0.0, 100.0)
	maxSemitones = EXTENDED_MAX_SEMITONES if extendedRange else STANDARD_MAX_SEMITONES
	semitones = ((pitchPercent - 50.0) / 50.0) * maxSemitones
	ratio = 2.0 ** (semitones / 12.0)
	minRatio = 2.0 ** (-maxSemitones / 12.0)
	maxRatio = 2.0 ** (maxSemitones / 12.0)
	return _clamp(ratio, minRatio, maxRatio)


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


def _createSonicPitchExtendedRangeSetting():
	if NumericDriverSetting is None:
		return None
	try:
		return NumericDriverSetting(
			SONIC_PITCH_EXTENDED_RANGE_PARAM_ID,
			"Sonic pitch extended range",
			availableInSettingsRing=False,
			defaultVal=0,
			minVal=0,
			maxVal=1,
			minStep=1,
			normalStep=1,
			largeStep=1,
			displayName="Sonic pitch extended range",
			useConfig=False,
		)
	except TypeError:
		return NumericDriverSetting(
			SONIC_PITCH_EXTENDED_RANGE_PARAM_ID,
			"Sonic pitch extended range",
			False,
			0,
			0,
			1,
			1,
			1,
			1,
			"Sonic pitch extended range",
			False,
		)


_SONIC_PITCH_EXTENDED_RANGE_SETTING = _createSonicPitchExtendedRangeSetting()


class _LockedSonicStream:
	def __init__(self, stream, lock, sampleRate: int | None = None, channels: int | None = None):
		self._stream = stream
		self._lock = lock
		self._sampleRate = sampleRate
		self._channels = channels
		if self._sampleRate is None:
			try:
				self._sampleRate = int(stream.sampleRate)
			except Exception:
				self._sampleRate = None
		if self._channels is None:
			try:
				self._channels = int(stream.channels)
			except Exception:
				self._channels = None

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
			try:
				self._sampleRate = int(self._stream.sampleRate)
			except Exception:
				if self._sampleRate is None:
					raise
			return self._sampleRate

	@property
	def channels(self) -> int:
		with self._lock:
			try:
				self._channels = int(self._stream.channels)
			except Exception:
				if self._channels is None:
					raise
			return self._channels

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


_ORIGINAL_REMOTE_WRITE = _sapi5.SynthDriverAudioStream.ISequentialStream_RemoteWrite


def _globalSonicPitchRemoteWrite(self, this, pv, cb, pcbWritten):
	synth = self.synthRef()
	lock = getattr(synth, "_sonicPitchLock", None)
	if lock is None:
		return _ORIGINAL_REMOTE_WRITE(self, this, pv, cb, pcbWritten)
	with lock:
		try:
			return _ORIGINAL_REMOTE_WRITE(self, this, pv, cb, pcbWritten)
		except Exception:
			if pcbWritten:
				pcbWritten[0] = cb
			handler = getattr(synth, "_handleSonicStreamFailure", None)
			if handler is not None:
				handler("RemoteWrite")
			_logWarning("globalSonicPitch sapi5_32 host: recovered after Sonic RemoteWrite failure")
			return _sapi5.hresult.S_OK


if getattr(_sapi5.SynthDriverAudioStream, "_globalSonicPitchRemoteWritePatched", False) is False:
	_sapi5.SynthDriverAudioStream.ISequentialStream_RemoteWrite = _globalSonicPitchRemoteWrite
	_sapi5.SynthDriverAudioStream._globalSonicPitchRemoteWritePatched = True


class SynthDriver(_BaseSynthDriver):
	_hostSettings = tuple(
		setting
		for setting in (_SONIC_PITCH_SETTING, _SONIC_PITCH_EXTENDED_RANGE_SETTING)
		if setting is not None
	)
	supportedSettings = tuple(
		setting
		for setting in _BaseSynthDriver.supportedSettings
		if getattr(setting, "id", "") not in SONIC_PITCH_HOST_SETTING_IDS
	) + _hostSettings

	def __init__(self, *args, **kwargs):
		self._sonicPitchLock = threading.RLock()
		self._sonicPitch = NEUTRAL_PITCH
		self._sonicPitchExtendedRange = False
		self._lastAppliedSonicPitch: int | None = None
		self._sonicSampleRate: int | None = None
		self._sonicChannels: int | None = None
		self._retiredSonicStreams = []
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

	def _get_sonicPitchExtendedRange(self) -> bool:
		return bool(getattr(self, "_sonicPitchExtendedRange", False))

	def _set_sonicPitchExtendedRange(self, value) -> None:
		enabled = bool(value)
		if bool(getattr(self, "_sonicPitchExtendedRange", False)) == enabled:
			return
		self._sonicPitchExtendedRange = enabled
		self._lastAppliedSonicPitch = None
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
		ratio = _pitchPercentToSonicRatio(sonicPitch, self._get_sonicPitchExtendedRange())
		with self._sonicPitchLock:
			if self._lastAppliedSonicPitch is not None:
				return self._replaceSonicStream(sonicPitch, "pitch change")
			stream.pitch = ratio
			self._lastAppliedSonicPitch = sonicPitch
			_logInfo(
				"globalSonicPitch sapi5_32 host: set Sonic pitch; "
				f"sonicPitch={sonicPitch}; ratio={ratio:.4f}; extendedRange={self._get_sonicPitchExtendedRange()}",
			)
		return True

	def _wrapSonicStream(self, stream):
		if isinstance(stream, _LockedSonicStream):
			self._sonicSampleRate = stream.sampleRate
			self._sonicChannels = stream.channels
			return stream
		lockedStream = _LockedSonicStream(stream, self._sonicPitchLock)
		self._sonicSampleRate = lockedStream.sampleRate
		self._sonicChannels = lockedStream.channels
		return lockedStream

	def _retireSonicStream(self, stream) -> None:
		if stream is not None:
			self._retiredSonicStreams.append(stream)

	def _replaceSonicStream(self, sonicPitch: int | None = None, reason: str = "") -> bool:
		sampleRate = self._sonicSampleRate
		channels = self._sonicChannels
		if not sampleRate or not channels:
			stream = getattr(self, "sonicStream", None)
			try:
				sampleRate = int(stream.sampleRate)
				channels = int(stream.channels)
			except Exception:
				return False
		sonicPitch = _clampPitch(self._sonicPitch if sonicPitch is None else sonicPitch)
		ratio = _pitchPercentToSonicRatio(sonicPitch, self._get_sonicPitchExtendedRange())
		oldStream = getattr(self, "sonicStream", None)
		newStream = _LockedSonicStream(_sapi5.SonicStream(sampleRate, channels), self._sonicPitchLock, sampleRate, channels)
		if getattr(self, "_rateBoost", False):
			newStream.speed = self._percentToParam(getattr(self, "_rate", 50), 0.5, 6.0)
		else:
			newStream.speed = 1
		newStream.pitch = ratio
		self._retireSonicStream(oldStream)
		self.sonicStream = newStream
		self._sonicSampleRate = sampleRate
		self._sonicChannels = channels
		self._lastAppliedSonicPitch = sonicPitch
		self._isFirstAudioChunk = True
		_logInfo(
			"globalSonicPitch sapi5_32 host: replaced Sonic stream; "
			f"reason={reason}; sonicPitch={sonicPitch}; ratio={ratio:.4f}; "
			f"extendedRange={self._get_sonicPitchExtendedRange()}",
		)
		return True

	def _handleSonicStreamFailure(self, reason: str) -> None:
		with self._sonicPitchLock:
			self._lastAppliedSonicPitch = None
			if not self._replaceSonicStream(self._sonicPitch, reason):
				_logWarning(f"globalSonicPitch sapi5_32 host: failed to replace Sonic stream; reason={reason}")

	def _flushAndReadSonicStream(self, reason: str):
		with self._sonicPitchLock:
			try:
				self.sonicStream.flush()
				return self.sonicStream.readShort()
			except Exception:
				self._handleSonicStreamFailure(reason)
				_logWarning(f"globalSonicPitch sapi5_32 host: recovered after Sonic flush/read failure; reason={reason}")
				return None

	def _initWasapiAudio(self):
		super()._initWasapiAudio()
		if self.sonicStream is not None:
			self.sonicStream = self._wrapSonicStream(self.sonicStream)
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
						audioData = self._flushAndReadSonicStream("end stream")
						if audioData is not None:
							self.player.feed(audioData, len(audioData) * 2)
						self._onEndStream()
				except Exception:
					if self._bookmarkLists:
						self._bookmarkLists.pop()
					self._handleSonicStreamFailure("speak exception")
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
					self._flushAndReadSonicStream("cancel")
				self._isCancelling = False
				self._applySonicPitch(force=True)


__all__ = ["SynthDriver"]
