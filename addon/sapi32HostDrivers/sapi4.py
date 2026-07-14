# 32-bit SAPI4 host wrapper for Global Sonic Pitch.

from __future__ import annotations

import ctypes
import importlib.util
import os
import sys
import threading
from typing import Any

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
_FIRST_AUDIO_CHUNK_MIN_DURATION_MS = 50

_processingLogKeys: set[tuple[Any, ...]] = set()
_playerProcessors: dict[int, "_SonicStreamProcessor"] = {}
_playerProcessorsLock = threading.RLock()
_retiredProcessors: list["_SonicStreamProcessor"] = []
_activePitchLock = threading.RLock()
_activeSonicPitch = NEUTRAL_PITCH
_activeExtendedRange = False


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
			if os.path.isfile(os.path.join(candidate, "_sapi4.py")) and os.path.isfile(
				os.path.join(candidate, "sapi4.py"),
			):
				return candidate
	raise RuntimeError("Could not locate NVDA _synthDrivers32 directory")


_ORIGINAL_SYNTH_DRIVERS_32_PATH = _findOriginalSynthDrivers32Path()

try:
	import synthDrivers

	if _ORIGINAL_SYNTH_DRIVERS_32_PATH not in synthDrivers.__path__:
		synthDrivers.__path__.append(_ORIGINAL_SYNTH_DRIVERS_32_PATH)
except Exception:
	_logWarning("globalSonicPitch sapi4_32 host: failed to append original synth driver path")
	raise

from . import _sonic  # noqa: E402

_sonic.SONIC_DLL_PATH = os.path.join(_ORIGINAL_SYNTH_DRIVERS_32_PATH, "sonic.dll")


def _loadOriginalSapi4Module():
	moduleName = "synthDrivers._globalSonicPitchOriginalSapi4"
	if moduleName in sys.modules:
		return sys.modules[moduleName]
	modulePath = os.path.join(_ORIGINAL_SYNTH_DRIVERS_32_PATH, "sapi4.py")
	spec = importlib.util.spec_from_file_location(moduleName, modulePath)
	if spec is None or spec.loader is None:
		raise RuntimeError(f"Could not load original SAPI4 driver: {modulePath}")
	module = importlib.util.module_from_spec(spec)
	sys.modules[moduleName] = module
	spec.loader.exec_module(module)
	return module


_originalSapi4 = _loadOriginalSapi4Module()
_BaseSynthDriver = _originalSapi4.SynthDriver
_BaseSynthDriverAudio = _originalSapi4.SynthDriverAudio
_AudioState = _originalSapi4._AudioState

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


def _setActiveSonicPitch(pitch: int | float) -> None:
	global _activeSonicPitch
	with _activePitchLock:
		_activeSonicPitch = _clampPitch(pitch)


def _getActiveSonicPitch() -> int:
	with _activePitchLock:
		return _clampPitch(_activeSonicPitch)


def _setActiveExtendedRange(enabled: bool) -> None:
	global _activeExtendedRange
	with _activePitchLock:
		enabled = bool(enabled)
		if _activeExtendedRange == enabled:
			return
		_activeExtendedRange = enabled
	_resetAllPlayerProcessors()


def _getActiveExtendedRange() -> bool:
	with _activePitchLock:
		return bool(_activeExtendedRange)


def _ctypesArrayToBytes(value: Any) -> bytes:
	try:
		if not value:
			return b""
		return ctypes.string_at(ctypes.addressof(value), ctypes.sizeof(value))
	except Exception:
		return bytes(value)


def _ensureSonicInitialized() -> bool:
	try:
		_sonic.initialize()
		return True
	except Exception:
		_logWarning("globalSonicPitch sapi4_32 host: Sonic is unavailable")
		return False


class _SonicStreamProcessor:
	def __init__(self, channels: int, sampleRate: int, pitchPercent: int, extendedRange: bool):
		self.channels = channels
		self.sampleRate = sampleRate
		self.pitchPercent = _clampPitch(pitchPercent)
		self.extendedRange = bool(extendedRange)
		self.stream = _sonic.SonicStream(sampleRate, channels)
		self.stream.pitch = _pitchPercentToSonicRatio(self.pitchPercent, self.extendedRange)
		self.isFirstAudioChunk = True
		self.pendingInputBytes = 0
		self._lock = threading.RLock()

	def matches(self, channels: int, sampleRate: int, pitchPercent: int, extendedRange: bool) -> bool:
		return (
			self.channels == channels
			and self.sampleRate == sampleRate
			and self.pitchPercent == _clampPitch(pitchPercent)
			and self.extendedRange == bool(extendedRange)
		)

	def _readAvailable(self) -> bytes:
		if self.stream.samplesAvailable <= 0:
			return b""
		return _ctypesArrayToBytes(self.stream.readShort())

	def process(self, raw: bytes, flush: bool = False) -> tuple[bytes, int]:
		with self._lock:
			frameSize = self.channels * 2
			if raw:
				self.pendingInputBytes += len(raw)
				frameCount = len(raw) // frameSize
				sampleCount = frameCount * self.channels
				inputSamples = (ctypes.c_short * sampleCount).from_buffer_copy(raw)
				self.stream.writeShort(inputSamples, frameCount)
			if flush:
				self.stream.flush()
				self.isFirstAudioChunk = False
			elif (
				self.isFirstAudioChunk
				and self.stream.samplesAvailable < self.sampleRate * _FIRST_AUDIO_CHUNK_MIN_DURATION_MS // 1000
			):
				return b"", 0
			self.isFirstAudioChunk = False
			processed = self._readAvailable()
			if not processed:
				return b"", 0
			doneBytes = self.pendingInputBytes
			self.pendingInputBytes = 0
			return processed, doneBytes

	def finish(self) -> tuple[bytes, int]:
		with self._lock:
			processed, doneBytes = self.process(b"", flush=True)
			if self.pendingInputBytes:
				doneBytes += self.pendingInputBytes
				self.pendingInputBytes = 0
			self.isFirstAudioChunk = True
			return processed, doneBytes


def _retireProcessor(processor: "_SonicStreamProcessor" | None) -> None:
	if processor is not None:
		_retiredProcessors.append(processor)
		if len(_retiredProcessors) > 32:
			del _retiredProcessors[: len(_retiredProcessors) - 32]


def _getPlayerProcessorKey(player: Any) -> int:
	return id(player)


def _finishPlayerProcessor(player: Any) -> tuple[bytes, int]:
	with _playerProcessorsLock:
		processor = _playerProcessors.get(_getPlayerProcessorKey(player))
	if processor is None:
		return b"", 0
	try:
		return processor.finish()
	except Exception:
		_logWarning("globalSonicPitch sapi4_32 host: failed to finish Sonic stream")
		return b"", 0


def _resetPlayerProcessor(player: Any) -> None:
	with _playerProcessorsLock:
		processor = _playerProcessors.pop(_getPlayerProcessorKey(player), None)
	_retireProcessor(processor)


def _resetAllPlayerProcessors() -> None:
	with _playerProcessorsLock:
		processors = list(_playerProcessors.values())
		_playerProcessors.clear()
	for processor in processors:
		_retireProcessor(processor)


def _getOrCreatePlayerProcessor(
	player: Any,
	channels: int,
	sampleRate: int,
	pitchPercent: int,
	extendedRange: bool,
) -> _SonicStreamProcessor | None:
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		processor = _playerProcessors.get(processorKey)
		if processor is not None:
			if processor.matches(channels, sampleRate, pitchPercent, extendedRange):
				return processor
			_playerProcessors.pop(processorKey, None)
			_retireProcessor(processor)
		if not _ensureSonicInitialized():
			return None
		processor = _SonicStreamProcessor(channels, sampleRate, pitchPercent, extendedRange)
		_playerProcessors[processorKey] = processor
		return processor


def _logProcessedOnce(channels: int, sampleRate: int, pitch: int, extendedRange: bool, inSize: int, outSize: int) -> None:
	key = (channels, sampleRate, pitch, extendedRange)
	if key in _processingLogKeys:
		return
	_processingLogKeys.add(key)
	_logInfo(
		"globalSonicPitch sapi4_32 host: processed SAPI4 audio; "
		f"sonicPitch={pitch}; extendedRange={extendedRange}; "
		f"channels={channels}; sampleRate={sampleRate}; bytes={inSize}->{outSize}",
	)


def _processPcm16Block(audio: Any, raw: bytes, channels: int, sampleRate: int) -> tuple[bytes | None, int]:
	pitch = _getActiveSonicPitch()
	if pitch == NEUTRAL_PITCH:
		_resetPlayerProcessor(audio._player)
		return None, 0
	extendedRange = _getActiveExtendedRange()
	frameSize = channels * 2
	if len(raw) < frameSize or len(raw) % frameSize:
		return None, 0
	processor = _getOrCreatePlayerProcessor(audio._player, channels, sampleRate, pitch, extendedRange)
	if processor is None:
		return None, 0
	processed, doneBytes = processor.process(raw)
	if processed is not None:
		_logProcessedOnce(channels, sampleRate, pitch, extendedRange, len(raw), len(processed))
	return processed, doneBytes


class SonicPitchSynthDriverAudio(_BaseSynthDriverAudio):
	def terminate(self):
		_resetPlayerProcessor(getattr(self, "_player", None))
		return super().terminate()

	def IAudio_Flush(self) -> None:
		_resetPlayerProcessor(getattr(self, "_player", None))
		return super().IAudio_Flush()

	def _audioThreadFunc(self):
		while not self._audioStopped:
			with self._audioCond:
				self._checkBookmarksAndState()
				deviceState = self._deviceState
				if deviceState not in (
					_AudioState.STARTED,
					_AudioState.UNCLAIMING,
					_AudioState.RECLAIMING,
				):
					self._audioCond.wait()
					continue
				if not self._audioQueue:
					self._audioCond.wait(0.01)
				item = self._audioQueue.popleft() if self._audioQueue else None
			if item:
				size = len(item)
				feedData = item
				doneBytes = size
				try:
					waveFormat = self._waveFormat
					if waveFormat and waveFormat.wBitsPerSample == 16:
						processed, processedDoneBytes = _processPcm16Block(
							self,
							item,
							waveFormat.nChannels,
							waveFormat.nSamplesPerSec,
						)
						if processed is not None:
							feedData = processed
							doneBytes = processedDoneBytes
					elif waveFormat and waveFormat.wBitsPerSample != 16:
						_resetPlayerProcessor(self._player)
				except Exception:
					_logWarning("globalSonicPitch sapi4_32 host: failed to process SAPI4 audio")
					_resetPlayerProcessor(self._player)
					feedData = item
					doneBytes = size
				if feedData:
					self._player.feed(feedData, len(feedData), lambda size=doneBytes: self._onChunkFinished(size))
				elif doneBytes:
					self._onChunkFinished(doneBytes)
				else:
					self._player.feed(None, 0, None)
			else:
				if deviceState == _AudioState.UNCLAIMING:
					try:
						tail, doneBytes = _finishPlayerProcessor(self._player)
						if tail:
							self._player.feed(tail, len(tail), lambda size=doneBytes: self._onChunkFinished(size))
						elif doneBytes:
							self._onChunkFinished(doneBytes)
					except Exception:
						_logWarning("globalSonicPitch sapi4_32 host: failed to flush Sonic stream")
					finally:
						_resetPlayerProcessor(self._player)
				self._player.feed(None, 0, None)


_originalSapi4.SynthDriverAudio = SonicPitchSynthDriverAudio


class SynthDriver(_BaseSynthDriver):
	def __init__(self, *args, **kwargs):
		self._sonicPitch = NEUTRAL_PITCH
		self._sonicPitchExtendedRange = False
		_setActiveSonicPitch(self._sonicPitch)
		_setActiveExtendedRange(self._sonicPitchExtendedRange)
		super().__init__(*args, **kwargs)
		self._ensureSonicPitchSetting()
		_logInfo(
			"globalSonicPitch sapi4_32 host: initialized Sonic pitch wrapper; "
			f"originalPath={_ORIGINAL_SYNTH_DRIVERS_32_PATH}",
		)

	def terminate(self):
		_resetAllPlayerProcessors()
		return super().terminate()

	def _ensureSonicPitchSetting(self) -> None:
		settings = [
			setting
			for setting in list(getattr(self, "supportedSettings", ()))
			if getattr(setting, "id", "") not in SONIC_PITCH_HOST_SETTING_IDS
		]
		settings.extend(
			setting
			for setting in (_SONIC_PITCH_SETTING, _SONIC_PITCH_EXTENDED_RANGE_SETTING)
			if setting is not None
		)
		self.supportedSettings = settings

	def _set_voice(self, val):
		result = super()._set_voice(val)
		self._ensureSonicPitchSetting()
		return result

	def _get_sonicPitch(self) -> int:
		return _clampPitch(getattr(self, "_sonicPitch", NEUTRAL_PITCH))

	def _set_sonicPitch(self, value: int | float) -> None:
		self._sonicPitch = _clampPitch(value)
		_setActiveSonicPitch(self._sonicPitch)

	def _get_sonicPitchExtendedRange(self) -> bool:
		return bool(getattr(self, "_sonicPitchExtendedRange", False))

	def _set_sonicPitchExtendedRange(self, value) -> None:
		self._sonicPitchExtendedRange = bool(value)
		_setActiveExtendedRange(self._sonicPitchExtendedRange)


__all__ = ["SynthDriver"]
