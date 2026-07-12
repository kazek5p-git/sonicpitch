# Global Sonic pitch processing for NVDA WavePlayer speech audio.

from __future__ import annotations

import ctypes
import json
import locale
import sys
import threading
import webbrowser
from typing import Any, Callable

import addonHandler
import config
import globalPluginHandler
import gui
import nvwave
import wx
import gui.settingsDialogs as settingsDialogs
try:
	import globalVars
except Exception:
	globalVars = None
try:
	import versionInfo
except Exception:
	versionInfo = None
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log
from scriptHandler import script

try:
	from autoSettingsUtils.driverSetting import NumericDriverSetting
except Exception:
	NumericDriverSetting = None

try:
	import synthDriverHandler
	import ui
except Exception:
	synthDriverHandler = None
	ui = None

try:
	addonHandler.initTranslation()
except Exception:
	pass

try:
	_
except NameError:
	_ = lambda message: message


CONFIG_SECTION = "globalSonicPitch"
OLD_CONFIG_SECTION = "sapi5SonicPitchGlobal"
CONFIG_SPEC = {
	"enabled": "boolean(default=False)",
	"pitch": "integer(default=50, min=0, max=100)",
	"pitchBySynth": "string(default='{}')",
	"debugLogging": "boolean(default=False)",
}

NEUTRAL_PITCH = 50
MAX_SEMITONES = 6.0
MIN_SONIC_PITCH_RATIO = 0.70
MAX_SONIC_PITCH_RATIO = 1.45
SONIC_PITCH_SETTING_ID = "sonicPitch"
SUPPORT_URL = "https://buycoffee.to/kazimierz-parzych"
LEGACY_PITCH_CONFIG_KEY = "pitch"
PITCH_BY_SYNTH_CONFIG_KEY = "pitchBySynth"
SAPI5_32BIT_NVDA_MIN_SAFE_VERSION = (2026, 1)

UNSUPPORTED_GLOBAL_SYNTHS = {
	# On 64-bit NVDA, sapi5_32 speaks in the separate 32-bit synth host.
	# This global plugin is loaded only in the main NVDA process.
	"sapi5_32",
}

_ORIGINAL_FEED_ATTR = "_globalSonicPitchOriginalFeed"
_ORIGINAL_IDLE_ATTR = "_globalSonicPitchOriginalIdle"
_ORIGINAL_STOP_ATTR = "_globalSonicPitchOriginalStop"
_ORIGINAL_CLOSE_ATTR = "_globalSonicPitchOriginalClose"
_FEED_PATCHED_ATTR = "_globalSonicPitchFeedPatched"
_ORIGINAL_SET_SYNTH_ATTR = "_globalSonicPitchOriginalSetSynth"
_SET_SYNTH_PATCHED_ATTR = "_globalSonicPitchSetSynthPatched"
_ORIGINAL_SETTINGS_SET_SYNTH_ATTR = "_globalSonicPitchOriginalSettingsSetSynth"
_SETTINGS_SET_SYNTH_PATCHED_ATTR = "_globalSonicPitchSettingsSetSynthPatched"
_ORIGINAL_SUPPORTED_SETTINGS_ATTR = "_globalSonicPitchOriginalSupportedSettings"
_SONIC_PITCH_SETTING_PATCHED_ATTR = "_globalSonicPitchVoiceSettingPatched"
_ORIGINAL_SAPI5_GET_VOICE_TOKENS_ATTR = "_globalSonicPitchOriginalGetVoiceTokens"
_ORIGINAL_SAPI5_32_GET_AVAILABLE_VOICES_ATTR = "_globalSonicPitchOriginalGetAvailableVoices"
_SAPI5_VOICE_ENUM_PATCHED_ATTR = "_globalSonicPitchVoiceEnumPatched"
_SAPI5_32_VOICE_ENUM_PATCHED_ATTR = "_globalSonicPitch32VoiceEnumPatched"
_ESPEAK_NG_SAPI_TOKEN_ENUM_PART = "\\Speech\\Voices\\TokenEnums\\eSpeak-NG\\"

_sonicModule = None
_processingLogKeys: set[tuple[Any, ...]] = set()
_voiceSettingLogKeys: set[str] = set()
_unsupportedSynthLogKeys: set[tuple[str, str]] = set()
_sapi5VoiceEnumLogKeys: set[str] = set()
_sonicUnavailableReason: str | None = None
_sonicPitchDriverSetting: Any | None = None
_missingClassAttr = object()
_sonicPitchClassPatches: dict[type, Any] = {}
_configMigrated = False
_deferSynthPitchPatchDepth = 0
_playerProcessors: dict[int, "_SonicStreamProcessor"] = {}
_playerProcessorsLock = threading.RLock()
_FIRST_AUDIO_CHUNK_MIN_DURATION_MS = 50


def _ensureConfigSpec() -> None:
	config.conf.spec[CONFIG_SECTION] = CONFIG_SPEC
	global _configMigrated
	if not _configMigrated:
		_migrateOldConfigSection()
		_configMigrated = True


def _migrateOldConfigSection() -> None:
	try:
		if OLD_CONFIG_SECTION not in config.conf:
			return
		oldConf = config.conf[OLD_CONFIG_SECTION]
		newConf = config.conf[CONFIG_SECTION]
	except Exception:
		return
	for key in ("enabled", "pitch", "debugLogging"):
		try:
			if key in oldConf:
				newConf[key] = oldConf[key]
		except Exception:
			continue


def _getConfigValue(key: str, default: Any) -> Any:
	try:
		_ensureConfigSpec()
		return config.conf[CONFIG_SECTION].get(key, default)
	except Exception:
		return default


def _setConfigValue(key: str, value: Any) -> None:
	_ensureConfigSpec()
	config.conf[CONFIG_SECTION][key] = value


def _setGlobalEnabled(enabled: bool) -> None:
	_setConfigValue("enabled", bool(enabled))
	_resetAllPlayerProcessors()
	_patchCurrentSynthPitch()


def _openSupportPage() -> None:
	try:
		opened = webbrowser.open_new_tab(SUPPORT_URL)
	except Exception:
		opened = False
		log.debugWarning("globalSonicPitch: failed to open support page", exc_info=True)
	if opened:
		if ui is not None:
			ui.message(_("Opening support page"))
		return
	if ui is not None:
		ui.message(_("Cannot open support page. Open this address manually: {url}").format(url=SUPPORT_URL))


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


def _isDebugLoggingEnabled() -> bool:
	return bool(_getConfigValue("debugLogging", False))


def _getCurrentSynth() -> Any | None:
	if synthDriverHandler is None:
		return None
	try:
		return synthDriverHandler.getSynth()
	except Exception:
		return None


def _getSynthName(synth: Any | None = None) -> str:
	if synth is None:
		synth = _getCurrentSynth()
	return str(getattr(synth, "name", "") or "")


def _getNvdaVersionTuple() -> tuple[int, int]:
	if versionInfo is None:
		return (0, 0)
	try:
		year = int(getattr(versionInfo, "version_year", 0) or 0)
		major = int(getattr(versionInfo, "version_major", 0) or 0)
		if year:
			return year, major
	except Exception:
		pass
	try:
		versionText = str(getattr(versionInfo, "version", "") or "")
		parts = []
		for part in versionText.split("."):
			if not part.isdigit():
				break
			parts.append(int(part))
		if parts:
			return parts[0], parts[1] if len(parts) > 1 else 0
	except Exception:
		pass
	return (0, 0)


def _is32BitNvdaProcess() -> bool:
	return sys.maxsize <= 2**32


def _isLegacy32BitNvdaSapi5(synthName: str) -> bool:
	nvdaVersion = _getNvdaVersionTuple()
	return (
		synthName == "sapi5"
		and _is32BitNvdaProcess()
		and nvdaVersion != (0, 0)
		and nvdaVersion < SAPI5_32BIT_NVDA_MIN_SAFE_VERSION
	)


def _getUnsupportedGlobalAudioReason(synthName: str) -> str | None:
	if synthName in UNSUPPORTED_GLOBAL_SYNTHS:
		return _("the synth speaks through a separate 32-bit synth host")
	if synthName.startswith("sapi5SonicPitch"):
		return _("old SAPI5 Sonic Pitch synth paths are not processed by the global add-on")
	if _isLegacy32BitNvdaSapi5(synthName):
		return _(
			"SAPI5 global Sonic processing is disabled on 32-bit NVDA before 2026.1 "
			"to avoid native heap crashes",
		)
	return None


def _isGlobalAudioSupportedSynth(synthName: str) -> bool:
	return _getUnsupportedGlobalAudioReason(synthName) is None


def _logUnsupportedSynthOnce(synthName: str, reason: str) -> None:
	key = (synthName, reason)
	if key in _unsupportedSynthLogKeys and not _isDebugLoggingEnabled():
		return
	_unsupportedSynthLogKeys.add(key)
	log.info(
		"globalSonicPitch: not adding Sonic pitch voice setting; "
		f"synth={synthName or 'unknown'}; reason={reason}",
	)


def _getSynthPitchKey(synthName: str | None) -> str:
	return str(synthName or "").strip()


def _loadSynthPitchMap() -> dict[str, int]:
	value = _getConfigValue(PITCH_BY_SYNTH_CONFIG_KEY, "{}")
	if isinstance(value, dict):
		data = value
	else:
		try:
			data = json.loads(str(value or "{}"))
		except Exception:
			if _isDebugLoggingEnabled():
				log.debugWarning("globalSonicPitch: failed to parse per-synth pitch config", exc_info=True)
			return {}
	if not isinstance(data, dict):
		return {}
	pitches: dict[str, int] = {}
	for synthName, pitch in data.items():
		key = _getSynthPitchKey(str(synthName))
		if key:
			pitches[key] = _clampPitch(pitch)
	return pitches


def _saveSynthPitchMap(pitches: dict[str, int]) -> None:
	serializable = {
		_getSynthPitchKey(synthName): _clampPitch(pitch)
		for synthName, pitch in pitches.items()
		if _getSynthPitchKey(synthName)
	}
	_setConfigValue(
		PITCH_BY_SYNTH_CONFIG_KEY,
		json.dumps(serializable, sort_keys=True, separators=(",", ":")),
	)


def _migrateLegacyGlobalPitchToSynth(synthName: str) -> None:
	legacyPitch = _clampPitch(_getConfigValue(LEGACY_PITCH_CONFIG_KEY, NEUTRAL_PITCH))
	if legacyPitch == NEUTRAL_PITCH:
		return
	key = _getSynthPitchKey(synthName)
	if not key or not _isGlobalAudioSupportedSynth(key):
		return
	pitches = _loadSynthPitchMap()
	if not pitches:
		pitches[key] = legacyPitch
		_saveSynthPitchMap(pitches)
		log.info(
			"globalSonicPitch: migrated global Sonic pitch to current synth; "
			f"synth={key}; sonicPitch={legacyPitch}",
		)
	_setConfigValue(LEGACY_PITCH_CONFIG_KEY, NEUTRAL_PITCH)


def _getSonicPitchForSynth(synthName: str | None = None) -> int:
	if synthName is None:
		synthName = _getSynthName()
	key = _getSynthPitchKey(synthName)
	if not key:
		return NEUTRAL_PITCH
	_migrateLegacyGlobalPitchToSynth(key)
	return _loadSynthPitchMap().get(key, NEUTRAL_PITCH)


def _setSonicPitchForSynth(synthName: str | None, pitch: int | float) -> int | None:
	key = _getSynthPitchKey(synthName)
	if not key or not _isGlobalAudioSupportedSynth(key):
		return None
	pitch = _clampPitch(pitch)
	pitches = _loadSynthPitchMap()
	oldPitch = pitches.get(key, NEUTRAL_PITCH)
	pitches[key] = pitch
	_saveSynthPitchMap(pitches)
	_setConfigValue(LEGACY_PITCH_CONFIG_KEY, NEUTRAL_PITCH)
	if pitch != oldPitch:
		_resetAllPlayerProcessors()
	return pitch


def _setCurrentSynthSonicPitch(pitch: int | float) -> int | None:
	return _setSonicPitchForSynth(_getSynthName(), pitch)


def _changeCurrentSynthSonicPitch(delta: int) -> int | None:
	return _setCurrentSynthSonicPitch(_getSonicPitchForSynth() + delta)


def _getProcessingContext(player: nvwave.WavePlayer, rawSize: int) -> tuple[str, int] | None:
	if rawSize <= 0:
		return None
	if not bool(_getConfigValue("enabled", False)):
		return None
	if not _isSpeechPlayer(player):
		return None
	synthName = _getSynthName()
	if not _isGlobalAudioSupportedSynth(synthName):
		return None
	pitch = _getSonicPitchForSynth(synthName)
	if pitch == NEUTRAL_PITCH:
		return None
	return synthName, pitch


def _isSpeechPlayer(player: nvwave.WavePlayer) -> bool:
	try:
		return getattr(player, "_purpose", None) == nvwave.AudioPurpose.SPEECH
	except Exception:
		return False


def _getWaveFormat(player: nvwave.WavePlayer) -> tuple[int, int, int] | None:
	try:
		waveFormat = player._format
		channels = int(waveFormat.nChannels)
		sampleRate = int(waveFormat.nSamplesPerSec)
		bitsPerSample = int(waveFormat.wBitsPerSample)
	except Exception:
		return None
	if channels <= 0 or sampleRate <= 0:
		return None
	return channels, sampleRate, bitsPerSample


def _getRawBytes(data: Any, size: int | None) -> bytes | None:
	try:
		if size is not None:
			size = int(size)
			if size < 0:
				return None
			if isinstance(data, (bytes, bytearray, memoryview)):
				return bytes(data)[:size]
			return ctypes.string_at(data, size)
		if isinstance(data, bytes):
			return data
		if isinstance(data, (bytearray, memoryview)):
			return bytes(data)
		return bytes(data)
	except Exception:
		return None


def _getSonicModule():
	global _sonicModule, _sonicUnavailableReason
	if _sonicModule is not None:
		return _sonicModule
	try:
		from synthDrivers import _sonic

		_sonic.initialize()
		_sonicModule = _sonic
		_sonicUnavailableReason = None
	except Exception as exc:
		_sonicUnavailableReason = f"{type(exc).__name__}: {exc}"
		if _isDebugLoggingEnabled():
			log.debugWarning("globalSonicPitch: Sonic is unavailable", exc_info=True)
		return None
	return _sonicModule


def _ctypesArrayToBytes(value: Any) -> bytes:
	try:
		if not value:
			return b""
		return ctypes.string_at(ctypes.addressof(value), ctypes.sizeof(value))
	except Exception:
		return bytes(value)


class _SonicStreamProcessor:
	def __init__(self, sonicModule: Any, channels: int, sampleRate: int, pitchPercent: int):
		self.channels = channels
		self.sampleRate = sampleRate
		self.stream = sonicModule.SonicStream(sampleRate, channels)
		self.pitchPercent = _clampPitch(pitchPercent)
		self.stream.pitch = _pitchPercentToSonicRatio(self.pitchPercent)
		self.isFirstAudioChunk = True
		self._lock = threading.RLock()

	def matches(self, channels: int, sampleRate: int, pitchPercent: int) -> bool:
		return (
			self.channels == channels
			and self.sampleRate == sampleRate
			and self.pitchPercent == _clampPitch(pitchPercent)
		)

	def _readAvailable(self) -> bytes:
		if self.stream.samplesAvailable <= 0:
			return b""
		return _ctypesArrayToBytes(self.stream.readShort())

	def process(self, raw: bytes, flush: bool = False) -> bytes:
		with self._lock:
			frameSize = self.channels * 2
			if raw:
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
				return b""
			self.isFirstAudioChunk = False
			return self._readAvailable()

	def drain(self) -> bytes:
		with self._lock:
			return self._readAvailable()

	def finish(self) -> bytes:
		return self.process(b"", flush=True)


def _getPlayerProcessorKey(player: nvwave.WavePlayer) -> int:
	return id(player)


def _popPlayerProcessor(player: nvwave.WavePlayer) -> _SonicStreamProcessor | None:
	with _playerProcessorsLock:
		return _playerProcessors.pop(_getPlayerProcessorKey(player), None)


def _drainPlayerProcessor(player: nvwave.WavePlayer) -> bytes:
	with _playerProcessorsLock:
		processor = _playerProcessors.get(_getPlayerProcessorKey(player))
	if processor is None:
		return b""
	return processor.drain()


def _finishPlayerProcessor(player: nvwave.WavePlayer) -> bytes:
	with _playerProcessorsLock:
		processor = _playerProcessors.pop(_getPlayerProcessorKey(player), None)
	if processor is None:
		return b""
	return processor.finish()


def _resetPlayerProcessor(player: nvwave.WavePlayer) -> None:
	_popPlayerProcessor(player)


def _resetAllPlayerProcessors() -> None:
	with _playerProcessorsLock:
		_playerProcessors.clear()


def _getOrCreatePlayerProcessor(
	player: nvwave.WavePlayer,
	channels: int,
	sampleRate: int,
	pitchPercent: int,
) -> tuple[_SonicStreamProcessor | None, bytes]:
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		processor = _playerProcessors.get(processorKey)
		if processor is not None and not processor.matches(channels, sampleRate, pitchPercent):
			_playerProcessors.pop(processorKey, None)
			processor = None
		if processor is not None:
			return processor, b""
		sonic = _getSonicModule()
		if sonic is None:
			return None, b""
		processor = _SonicStreamProcessor(sonic, channels, sampleRate, pitchPercent)
		_playerProcessors[processorKey] = processor
		return processor, b""


def _processPcm16Block(
	player: nvwave.WavePlayer,
	raw: bytes,
	channels: int,
	sampleRate: int,
	pitchPercent: int,
) -> bytes | None:
	frameSize = channels * 2
	if len(raw) < frameSize or len(raw) % frameSize:
		return None
	processor, tail = _getOrCreatePlayerProcessor(player, channels, sampleRate, pitchPercent)
	if processor is None:
		return tail or None
	processed = processor.process(raw)
	return (tail + processed) or b""


def _logProcessedOnce(synthName: str, channels: int, sampleRate: int, pitch: int, inSize: int, outSize: int) -> None:
	key = (synthName, channels, sampleRate, pitch)
	if key in _processingLogKeys and not _isDebugLoggingEnabled():
		return
	_processingLogKeys.add(key)
	log.info(
		"globalSonicPitch: processed speech audio; "
		f"synth={synthName or 'unknown'}; pitch={pitch}; "
		f"channels={channels}; sampleRate={sampleRate}; bytes={inSize}->{outSize}",
	)


def _patchedFeed(self, data, size=None, onDone=None):
	originalFeed = getattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR)
	if callable(size) and onDone is None:
		onDone = size
		size = None
	raw = _getRawBytes(data, size)
	try:
		if raw is not None and len(raw) == 0:
			tail = _finishPlayerProcessor(self) if onDone is None else _drainPlayerProcessor(self)
			if tail:
				originalFeed(self, tail, len(tail), None)
			return originalFeed(self, data, size, onDone)
		processingContext = _getProcessingContext(self, len(raw)) if raw is not None else None
		if raw is not None and processingContext is not None:
			synthName, pitch = processingContext
			waveFormat = _getWaveFormat(self)
			if waveFormat is not None:
				channels, sampleRate, bitsPerSample = waveFormat
				if bitsPerSample == 16:
					processed = _processPcm16Block(self, raw, channels, sampleRate, pitch)
					if processed is not None:
						_logProcessedOnce(
							synthName,
							channels,
							sampleRate,
							pitch,
							len(raw),
							len(processed),
						)
						if processed:
							return originalFeed(self, processed, len(processed), onDone)
						if onDone is not None:
							return originalFeed(self, None, 0, onDone)
						return None
				elif _isDebugLoggingEnabled():
					log.debug(f"globalSonicPitch: bypassing non-16-bit audio: {bitsPerSample}")
		elif raw is not None:
			_resetPlayerProcessor(self)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to process WavePlayer feed; bypassing", exc_info=True)
		_resetPlayerProcessor(self)
	return originalFeed(self, data, size, onDone)


def _feedProcessorTail(player: nvwave.WavePlayer) -> None:
	originalFeed = getattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR)
	try:
		tail = _finishPlayerProcessor(player)
		if tail:
			originalFeed(player, tail, len(tail), None)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to flush Sonic stream tail", exc_info=True)
		_resetPlayerProcessor(player)


def _patchedIdle(self, *args, **kwargs):
	_feedProcessorTail(self)
	originalIdle = getattr(nvwave.WavePlayer, _ORIGINAL_IDLE_ATTR)
	return originalIdle(self, *args, **kwargs)


def _patchedStop(self, *args, **kwargs):
	_resetPlayerProcessor(self)
	originalStop = getattr(nvwave.WavePlayer, _ORIGINAL_STOP_ATTR)
	return originalStop(self, *args, **kwargs)


def _patchedClose(self, *args, **kwargs):
	_resetPlayerProcessor(self)
	originalClose = getattr(nvwave.WavePlayer, _ORIGINAL_CLOSE_ATTR)
	return originalClose(self, *args, **kwargs)


def installWavePlayerHook() -> None:
	if getattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, False):
		return
	setattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR, nvwave.WavePlayer.feed)
	nvwave.WavePlayer.feed = _patchedFeed
	if callable(getattr(nvwave.WavePlayer, "idle", None)):
		setattr(nvwave.WavePlayer, _ORIGINAL_IDLE_ATTR, nvwave.WavePlayer.idle)
		nvwave.WavePlayer.idle = _patchedIdle
	if callable(getattr(nvwave.WavePlayer, "stop", None)):
		setattr(nvwave.WavePlayer, _ORIGINAL_STOP_ATTR, nvwave.WavePlayer.stop)
		nvwave.WavePlayer.stop = _patchedStop
	if callable(getattr(nvwave.WavePlayer, "close", None)):
		setattr(nvwave.WavePlayer, _ORIGINAL_CLOSE_ATTR, nvwave.WavePlayer.close)
		nvwave.WavePlayer.close = _patchedClose
	setattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, True)
	log.info("globalSonicPitch: installed WavePlayer speech feed hook")


def uninstallWavePlayerHook() -> None:
	if not getattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, False):
		return
	originalFeed = getattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR, None)
	if originalFeed is not None and nvwave.WavePlayer.feed is _patchedFeed:
		nvwave.WavePlayer.feed = originalFeed
	originalIdle = getattr(nvwave.WavePlayer, _ORIGINAL_IDLE_ATTR, None)
	if originalIdle is not None and getattr(nvwave.WavePlayer, "idle", None) is _patchedIdle:
		nvwave.WavePlayer.idle = originalIdle
	originalStop = getattr(nvwave.WavePlayer, _ORIGINAL_STOP_ATTR, None)
	if originalStop is not None and getattr(nvwave.WavePlayer, "stop", None) is _patchedStop:
		nvwave.WavePlayer.stop = originalStop
	originalClose = getattr(nvwave.WavePlayer, _ORIGINAL_CLOSE_ATTR, None)
	if originalClose is not None and getattr(nvwave.WavePlayer, "close", None) is _patchedClose:
		nvwave.WavePlayer.close = originalClose
	try:
		delattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR)
	except Exception:
		pass
	for attr in (_ORIGINAL_IDLE_ATTR, _ORIGINAL_STOP_ATTR, _ORIGINAL_CLOSE_ATTR):
		try:
			delattr(nvwave.WavePlayer, attr)
		except Exception:
			pass
	_resetAllPlayerProcessors()
	setattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, False)
	log.info("globalSonicPitch: removed WavePlayer speech feed hook")


def _getSonicPitchDriverSetting() -> Any | None:
	global _sonicPitchDriverSetting
	if NumericDriverSetting is None:
		return None
	if _sonicPitchDriverSetting is not None:
		return _sonicPitchDriverSetting
	try:
		_sonicPitchDriverSetting = NumericDriverSetting(
			SONIC_PITCH_SETTING_ID,
			_("Sonic pitch"),
			availableInSettingsRing=True,
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
		try:
			_sonicPitchDriverSetting = NumericDriverSetting(
				SONIC_PITCH_SETTING_ID,
				_("Sonic pitch"),
				True,
				NEUTRAL_PITCH,
				0,
				100,
				1,
				5,
				10,
				_("Sonic pitch"),
				False,
			)
		except Exception:
			log.debugWarning("globalSonicPitch: failed to create Sonic pitch voice setting", exc_info=True)
			return None
	except Exception:
		log.debugWarning("globalSonicPitch: failed to create Sonic pitch voice setting", exc_info=True)
		return None
	return _sonicPitchDriverSetting


def _isEspeakNgSapiTokenId(tokenId: str) -> bool:
	return _ESPEAK_NG_SAPI_TOKEN_ENUM_PART.lower() in str(tokenId).lower()


def _tokenId(token: Any) -> str | None:
	try:
		return str(token.Id)
	except Exception:
		return None


def _patchedSapi5GetVoiceTokens(self):
	originalGetVoiceTokens = getattr(self.__class__, _ORIGINAL_SAPI5_GET_VOICE_TOKENS_ATTR)
	tokens = list(originalGetVoiceTokens(self))
	seen = {tokenId for tokenId in (_tokenId(token) for token in tokens) if tokenId}
	try:
		dynamicTokens = self.tts.GetVoices("", "")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to enumerate SAPI5 dynamic voices", exc_info=True)
		return tokens
	added = 0
	try:
		tokenCount = len(dynamicTokens)
	except Exception:
		tokenCount = 0
	for index in range(tokenCount):
		try:
			token = dynamicTokens[index]
		except Exception:
			continue
		tokenId = _tokenId(token)
		if not tokenId or tokenId in seen or not _isEspeakNgSapiTokenId(tokenId):
			continue
		tokens.append(token)
		seen.add(tokenId)
		added += 1
	if added:
		key = f"added:{added}"
		if key not in _sapi5VoiceEnumLogKeys:
			_sapi5VoiceEnumLogKeys.add(key)
			log.info(f"globalSonicPitch: added {added} eSpeak-NG SAPI dynamic voices to NVDA sapi5 voice list")
	return tokens


def _getSapiTokenLanguage(token: Any) -> str | None:
	try:
		languageId = int(token.getattribute("language").split(";")[0], 16)
		return locale.windows_locale.get(languageId)
	except Exception:
		return None


def _getEspeakNgSapiVoiceInfos() -> dict[str, Any]:
	try:
		import comtypes.client
	except Exception:
		return {}
	try:
		voice = comtypes.client.CreateObject("SAPI.SpVoice")
		tokens = voice.GetVoices("", "")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to enumerate SAPI voices for eSpeak-NG compatibility", exc_info=True)
		return {}
	voiceInfos: dict[str, Any] = {}
	try:
		tokenCount = len(tokens)
	except Exception:
		tokenCount = 0
	for index in range(tokenCount):
		try:
			token = tokens[index]
			tokenId = _tokenId(token)
			if not tokenId or not _isEspeakNgSapiTokenId(tokenId):
				continue
			voiceInfos[tokenId] = synthDriverHandler.VoiceInfo(
				tokenId,
				token.GetDescription(),
				_getSapiTokenLanguage(token),
			)
		except Exception:
			continue
	return voiceInfos


def _addEspeakNgSapiVoiceInfos(voices: Any, source: str) -> int:
	if voices is None:
		return 0
	added = 0
	try:
		for voiceId, voiceInfo in _getEspeakNgSapiVoiceInfos().items():
			if voiceId in voices:
				continue
			voices[voiceId] = voiceInfo
			added += 1
	except Exception:
		log.debugWarning(f"globalSonicPitch: failed to add eSpeak-NG SAPI voices to {source}", exc_info=True)
		return added
	if added:
		key = f"{source}:{added}"
		if key not in _sapi5VoiceEnumLogKeys:
			_sapi5VoiceEnumLogKeys.add(key)
			log.info(f"globalSonicPitch: added {added} eSpeak-NG SAPI dynamic voices to NVDA {source} voice list")
	return added


def _patchedSapi532GetAvailableVoices(self):
	originalGetAvailableVoices = getattr(self.__class__, _ORIGINAL_SAPI5_32_GET_AVAILABLE_VOICES_ATTR)
	voices = originalGetAvailableVoices(self)
	_addEspeakNgSapiVoiceInfos(voices, "sapi5_32")
	return voices


def _patchCurrentSapi532AvailableVoices() -> None:
	synth = _getCurrentSynth()
	if _getSynthName(synth) != "sapi5_32":
		return
	try:
		voices = getattr(synth, "availableVoices", None)
		if _addEspeakNgSapiVoiceInfos(voices, "sapi5_32 current"):
			try:
				synth._availableVoices = voices
			except Exception:
				pass
			_updateSynthSettingsRing(synth)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to patch current sapi5_32 voices", exc_info=True)


def installSapi5VoiceEnumerationHook() -> None:
	try:
		import synthDrivers.sapi5 as sapi5
	except Exception:
		log.debugWarning("globalSonicPitch: failed to import sapi5 for voice enumeration hook", exc_info=True)
	else:
		synthClass = getattr(sapi5, "SynthDriver", None)
		if synthClass is not None and not getattr(synthClass, _SAPI5_VOICE_ENUM_PATCHED_ATTR, False):
			originalGetVoiceTokens = getattr(synthClass, "_getVoiceTokens", None)
			if callable(originalGetVoiceTokens):
				setattr(synthClass, _ORIGINAL_SAPI5_GET_VOICE_TOKENS_ATTR, originalGetVoiceTokens)
				synthClass._getVoiceTokens = _patchedSapi5GetVoiceTokens
				setattr(synthClass, _SAPI5_VOICE_ENUM_PATCHED_ATTR, True)
				log.info("globalSonicPitch: installed eSpeak-NG SAPI sapi5 voice enumeration hook")
	try:
		import synthDrivers.sapi5_32 as sapi5_32
	except Exception:
		log.debugWarning("globalSonicPitch: failed to import sapi5_32 for voice enumeration hook", exc_info=True)
	else:
		synthClass = getattr(sapi5_32, "SynthDriver", None)
		if synthClass is not None and not getattr(synthClass, _SAPI5_32_VOICE_ENUM_PATCHED_ATTR, False):
			originalGetAvailableVoices = getattr(synthClass, "_getAvailableVoices", None)
			if callable(originalGetAvailableVoices):
				setattr(synthClass, _ORIGINAL_SAPI5_32_GET_AVAILABLE_VOICES_ATTR, originalGetAvailableVoices)
				synthClass._getAvailableVoices = _patchedSapi532GetAvailableVoices
				setattr(synthClass, _SAPI5_32_VOICE_ENUM_PATCHED_ATTR, True)
				log.info("globalSonicPitch: installed eSpeak-NG SAPI sapi5_32 voice enumeration hook")
	_patchCurrentSapi532AvailableVoices()


def uninstallSapi5VoiceEnumerationHook() -> None:
	try:
		import synthDrivers.sapi5 as sapi5
	except Exception:
		pass
	else:
		synthClass = getattr(sapi5, "SynthDriver", None)
		if synthClass is not None and getattr(synthClass, _SAPI5_VOICE_ENUM_PATCHED_ATTR, False):
			originalGetVoiceTokens = getattr(synthClass, _ORIGINAL_SAPI5_GET_VOICE_TOKENS_ATTR, None)
			if originalGetVoiceTokens is not None and getattr(synthClass, "_getVoiceTokens", None) is _patchedSapi5GetVoiceTokens:
				synthClass._getVoiceTokens = originalGetVoiceTokens
			try:
				delattr(synthClass, _ORIGINAL_SAPI5_GET_VOICE_TOKENS_ATTR)
			except Exception:
				pass
			setattr(synthClass, _SAPI5_VOICE_ENUM_PATCHED_ATTR, False)
			log.info("globalSonicPitch: removed eSpeak-NG SAPI sapi5 voice enumeration hook")
	try:
		import synthDrivers.sapi5_32 as sapi5_32
	except Exception:
		return
	synthClass = getattr(sapi5_32, "SynthDriver", None)
	if synthClass is None or not getattr(synthClass, _SAPI5_32_VOICE_ENUM_PATCHED_ATTR, False):
		return
	originalGetAvailableVoices = getattr(synthClass, _ORIGINAL_SAPI5_32_GET_AVAILABLE_VOICES_ATTR, None)
	if originalGetAvailableVoices is not None and getattr(synthClass, "_getAvailableVoices", None) is _patchedSapi532GetAvailableVoices:
		synthClass._getAvailableVoices = originalGetAvailableVoices
	try:
		delattr(synthClass, _ORIGINAL_SAPI5_32_GET_AVAILABLE_VOICES_ATTR)
	except Exception:
		pass
	setattr(synthClass, _SAPI5_32_VOICE_ENUM_PATCHED_ATTR, False)
	log.info("globalSonicPitch: removed eSpeak-NG SAPI sapi5_32 voice enumeration hook")


def _settingId(setting: Any) -> str:
	return str(getattr(setting, "id", "") or "")


def _hasSonicPitchSetting(settings: Any) -> bool:
	try:
		return any(_settingId(setting) == SONIC_PITCH_SETTING_ID for setting in settings)
	except Exception:
		return False


def _patchedGetSonicPitchSetting(self):
	return _getSonicPitchForSynth(_getSynthName(self))


def _patchedSetSonicPitchSetting(self, value):
	synthName = _getSynthName(self)
	pitch = _setSonicPitchForSynth(synthName, value)
	if pitch is None:
		return None
	log.info(
		"globalSonicPitch: captured Sonic pitch setting; "
		f"synth={synthName}; sonicPitch={pitch}",
	)
	return None


def _patchSonicPitchClassProperty(synth: Any) -> None:
	synthClass = synth.__class__
	if synthClass not in _sonicPitchClassPatches:
		_sonicPitchClassPatches[synthClass] = getattr(synthClass, SONIC_PITCH_SETTING_ID, _missingClassAttr)
	setattr(
		synthClass,
		SONIC_PITCH_SETTING_ID,
		property(_patchedGetSonicPitchSetting, _patchedSetSonicPitchSetting),
	)


def _restoreSonicPitchClassProperty(synthClass: type) -> None:
	if synthClass not in _sonicPitchClassPatches:
		return
	originalValue = _sonicPitchClassPatches.pop(synthClass)
	try:
		if originalValue is _missingClassAttr:
			delattr(synthClass, SONIC_PITCH_SETTING_ID)
		else:
			setattr(synthClass, SONIC_PITCH_SETTING_ID, originalValue)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to restore synth Sonic pitch class property", exc_info=True)


def _restoreAllSonicPitchClassProperties() -> None:
	for synthClass in list(_sonicPitchClassPatches):
		_restoreSonicPitchClassProperty(synthClass)


def _ensureSynthRingSettingsSelectorIncludesSonicPitch() -> None:
	try:
		if "synthRingSettingsSelector" not in config.conf.spec:
			config.conf.spec["synthRingSettingsSelector"] = {
				"availableSettings": (
					"string_list(default=list('language', 'voice', 'variant', 'rate', "
					"'rateBoost', 'volume', 'pitch', 'inflection', 'sonicPitch'))"
				),
			}
		selectorConfig = config.conf["synthRingSettingsSelector"]
		availableSettings = list(selectorConfig.get("availableSettings", []))
		if SONIC_PITCH_SETTING_ID in availableSettings:
			return
		availableSettings.append(SONIC_PITCH_SETTING_ID)
		selectorConfig["availableSettings"] = availableSettings
		log.info("globalSonicPitch: added Sonic pitch to synthRingSettingsSelector settings list")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to update synthRingSettingsSelector integration", exc_info=True)


def _updateSynthSettingsRing(synth: Any | None) -> None:
	if synth is None or globalVars is None:
		return
	settingsRing = getattr(globalVars, "settingsRing", None)
	if settingsRing is None:
		return
	try:
		settingsRing.updateSupportedSettings(synth)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to update synth settings ring", exc_info=True)


def _getReadableSonicPitchSettingValue(synth: Any) -> int | None:
	try:
		return _clampPitch(getattr(synth, SONIC_PITCH_SETTING_ID))
	except Exception:
		log.debugWarning("globalSonicPitch: Sonic pitch voice setting is not readable", exc_info=True)
		return None


def _logVoiceSettingOnce(synthName: str, value: int | None = None) -> None:
	if synthName in _voiceSettingLogKeys and not _isDebugLoggingEnabled():
		return
	_voiceSettingLogKeys.add(synthName)
	log.info(
		"globalSonicPitch: added Sonic pitch voice setting; "
		f"synth={synthName or 'unknown'}"
		+ (f"; value={value}" if value is not None else ""),
	)


def _patchSynthSonicPitchSetting(synth: Any | None) -> None:
	if synth is None:
		return
	if not bool(_getConfigValue("enabled", False)):
		_unpatchSynthSonicPitchSetting(synth)
		return
	synthName = _getSynthName(synth)
	unsupportedReason = _getUnsupportedGlobalAudioReason(synthName)
	if unsupportedReason is not None:
		_logUnsupportedSynthOnce(synthName, unsupportedReason)
		return
	setting = _getSonicPitchDriverSetting()
	if setting is None:
		return
	try:
		_patchSonicPitchClassProperty(synth)
		supportedSettings = tuple(getattr(synth, "supportedSettings", ()))
		if not getattr(synth, _SONIC_PITCH_SETTING_PATCHED_ATTR, False):
			setattr(synth, _ORIGINAL_SUPPORTED_SETTINGS_ATTR, supportedSettings)
			if not _hasSonicPitchSetting(supportedSettings):
				synth.supportedSettings = supportedSettings + (setting,)
			setattr(synth, _SONIC_PITCH_SETTING_PATCHED_ATTR, True)
		elif not _hasSonicPitchSetting(supportedSettings):
			synth.supportedSettings = supportedSettings + (setting,)
		settingValue = _getReadableSonicPitchSettingValue(synth)
		if settingValue is None:
			_unpatchSynthSonicPitchSetting(synth)
			return
		_ensureSynthRingSettingsSelectorIncludesSonicPitch()
		_updateSynthSettingsRing(synth)
		_logVoiceSettingOnce(synthName, settingValue)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to add Sonic pitch voice setting", exc_info=True)


def _unpatchSynthSonicPitchSetting(synth: Any | None) -> None:
	if synth is None or not getattr(synth, _SONIC_PITCH_SETTING_PATCHED_ATTR, False):
		return
	try:
		originalSupportedSettings = getattr(synth, _ORIGINAL_SUPPORTED_SETTINGS_ATTR, None)
		if originalSupportedSettings is not None:
			synth.supportedSettings = originalSupportedSettings
		for attr in (
			_ORIGINAL_SUPPORTED_SETTINGS_ATTR,
			_SONIC_PITCH_SETTING_PATCHED_ATTR,
		):
			try:
				delattr(synth, attr)
			except Exception:
				pass
		_restoreSonicPitchClassProperty(synth.__class__)
		_updateSynthSettingsRing(synth)
		log.info(f"globalSonicPitch: removed Sonic pitch voice setting; synth={_getSynthName(synth)}")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to remove Sonic pitch voice setting", exc_info=True)


def _patchCurrentSynthPitch() -> None:
	synth = _getCurrentSynth()
	if bool(_getConfigValue("enabled", False)):
		_patchSynthSonicPitchSetting(synth)
	else:
		_unpatchSynthSonicPitchSetting(synth)
		_restoreAllSonicPitchClassProperties()


def _safePatchCurrentSynthPitch() -> None:
	try:
		_patchCurrentSapi532AvailableVoices()
		_patchCurrentSynthPitch()
	except Exception:
		log.debugWarning("globalSonicPitch: failed after synth switch", exc_info=True)


def _schedulePatchCurrentSynthPitch() -> None:
	try:
		wx.CallAfter(_safePatchCurrentSynthPitch)
	except Exception:
		_safePatchCurrentSynthPitch()


def _callSetSynthAndPatch(originalSetSynth: Callable[..., Any], *args, **kwargs):
	result = originalSetSynth(*args, **kwargs)
	if not _deferSynthPitchPatchDepth:
		_safePatchCurrentSynthPitch()
	return result


def _patchedSetSynth(*args, **kwargs):
	originalSetSynth = getattr(synthDriverHandler, _ORIGINAL_SET_SYNTH_ATTR)
	return _callSetSynthAndPatch(originalSetSynth, *args, **kwargs)


def _patchedSettingsSetSynth(*args, **kwargs):
	global _deferSynthPitchPatchDepth
	originalSetSynth = getattr(settingsDialogs, _ORIGINAL_SETTINGS_SET_SYNTH_ATTR)
	_deferSynthPitchPatchDepth += 1
	try:
		return originalSetSynth(*args, **kwargs)
	finally:
		_deferSynthPitchPatchDepth = max(0, _deferSynthPitchPatchDepth - 1)
		if not _deferSynthPitchPatchDepth:
			_schedulePatchCurrentSynthPitch()


def installSynthPitchHook() -> None:
	if synthDriverHandler is None:
		return
	if getattr(synthDriverHandler, _SET_SYNTH_PATCHED_ATTR, False):
		_patchCurrentSynthPitch()
		return
	settingsSetSynth = getattr(settingsDialogs, "setSynth", None)
	setattr(synthDriverHandler, _ORIGINAL_SET_SYNTH_ATTR, synthDriverHandler.setSynth)
	synthDriverHandler.setSynth = _patchedSetSynth
	setattr(synthDriverHandler, _SET_SYNTH_PATCHED_ATTR, True)
	if callable(settingsSetSynth):
		setattr(settingsDialogs, _ORIGINAL_SETTINGS_SET_SYNTH_ATTR, settingsSetSynth)
		settingsDialogs.setSynth = _patchedSettingsSetSynth
		setattr(settingsDialogs, _SETTINGS_SET_SYNTH_PATCHED_ATTR, True)
	_patchCurrentSynthPitch()
	log.info("globalSonicPitch: installed synth Sonic pitch setting hook")


def uninstallSynthPitchHook() -> None:
	if synthDriverHandler is None:
		return
	_unpatchSynthSonicPitchSetting(_getCurrentSynth())
	_restoreAllSonicPitchClassProperties()
	if getattr(settingsDialogs, _SETTINGS_SET_SYNTH_PATCHED_ATTR, False):
		originalSettingsSetSynth = getattr(settingsDialogs, _ORIGINAL_SETTINGS_SET_SYNTH_ATTR, None)
		if originalSettingsSetSynth is not None and settingsDialogs.setSynth is _patchedSettingsSetSynth:
			settingsDialogs.setSynth = originalSettingsSetSynth
		try:
			delattr(settingsDialogs, _ORIGINAL_SETTINGS_SET_SYNTH_ATTR)
		except Exception:
			pass
		setattr(settingsDialogs, _SETTINGS_SET_SYNTH_PATCHED_ATTR, False)
	if not getattr(synthDriverHandler, _SET_SYNTH_PATCHED_ATTR, False):
		return
	originalSetSynth = getattr(synthDriverHandler, _ORIGINAL_SET_SYNTH_ATTR, None)
	if originalSetSynth is not None and synthDriverHandler.setSynth is _patchedSetSynth:
		synthDriverHandler.setSynth = originalSetSynth
	try:
		delattr(synthDriverHandler, _ORIGINAL_SET_SYNTH_ATTR)
	except Exception:
		pass
	setattr(synthDriverHandler, _SET_SYNTH_PATCHED_ATTR, False)
	log.info("globalSonicPitch: removed synth Sonic pitch setting hook")


class GlobalSonicPitchSettingsPanel(SettingsPanel):
	title = _("Global Sonic Pitch")

	def makeSettings(self, settingsSizer):
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = config.conf[CONFIG_SECTION]
		self.enableCheckbox = helper.addItem(
			wx.CheckBox(self, label=_("Enable global Sonic pitch")),
		)
		self.enableCheckbox.SetValue(bool(conf["enabled"]))
		self.debugCheckbox = helper.addItem(
			wx.CheckBox(self, label=_("Enable debug logging")),
		)
		self.debugCheckbox.SetValue(bool(conf["debugLogging"]))
		self.supportButton = helper.addItem(
			wx.Button(self, label=_("Support the author")),
		)
		self.enableCheckbox.Bind(wx.EVT_CHECKBOX, self._updateControlState)
		self.supportButton.Bind(wx.EVT_BUTTON, self._onSupport)
		self._updateControlState()

	def _updateControlState(self, event=None):
		enabled = self.enableCheckbox.IsChecked()
		self.debugCheckbox.Enable(enabled)

	def _onSupport(self, event):
		_openSupportPage()

	def onSave(self):
		_setConfigValue("debugLogging", self.debugCheckbox.IsChecked())
		_setGlobalEnabled(self.enableCheckbox.IsChecked())
		config.conf.save()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Global Sonic Pitch")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		_ensureConfigSpec()
		installSapi5VoiceEnumerationHook()
		installWavePlayerHook()
		installSynthPitchHook()
		if GlobalSonicPitchSettingsPanel not in NVDASettingsDialog.categoryClasses:
			NVDASettingsDialog.categoryClasses.append(GlobalSonicPitchSettingsPanel)

	def terminate(self):
		try:
			if GlobalSonicPitchSettingsPanel in NVDASettingsDialog.categoryClasses:
				NVDASettingsDialog.categoryClasses.remove(GlobalSonicPitchSettingsPanel)
		finally:
			uninstallSynthPitchHook()
			uninstallWavePlayerHook()
			uninstallSapi5VoiceEnumerationHook()
			super().terminate()

	@script(
		description=_("Toggle global Sonic pitch"),
		category=scriptCategory,
	)
	def script_toggleGlobalSonicPitch(self, gesture):
		enabled = not bool(_getConfigValue("enabled", False))
		_setGlobalEnabled(enabled)
		config.conf.save()
		if ui is not None:
			ui.message(_("Global Sonic pitch on") if enabled else _("Global Sonic pitch off"))

	@script(
		description=_("Report global Sonic pitch status"),
		category=scriptCategory,
	)
	def script_reportGlobalSonicPitch(self, gesture):
		enabled = bool(_getConfigValue("enabled", False))
		synthName = _getSynthName()
		if enabled and _isGlobalAudioSupportedSynth(synthName):
			pitch = _getSonicPitchForSynth(synthName)
			message = _("Global Sonic pitch on, {synth} Sonic pitch {pitch}").format(
				synth=synthName or _("current synth"),
				pitch=pitch,
			)
		elif enabled:
			reason = _getUnsupportedGlobalAudioReason(synthName)
			message = _("Global Sonic pitch on, Sonic pitch is unavailable for {synth}").format(
				synth=synthName or _("current synth"),
			)
			if reason:
				message = f"{message}. {reason}"
		else:
			message = _("Global Sonic pitch off")
		if _sonicUnavailableReason:
			message = f"{message}. Sonic unavailable: {_sonicUnavailableReason}"
		if ui is not None:
			ui.message(message)

	@script(
		description=_("Open support page"),
		category=scriptCategory,
	)
	def script_openSupportPage(self, gesture):
		_openSupportPage()

	@script(
		description=_("Increase Sonic pitch for the current synthesizer"),
		category=scriptCategory,
	)
	def script_increaseGlobalSonicPitch(self, gesture):
		pitch = _changeCurrentSynthSonicPitch(5)
		config.conf.save()
		if ui is not None:
			if pitch is None:
				ui.message(_("Sonic pitch is unavailable for {synth}").format(synth=_getSynthName() or _("current synth")))
			else:
				ui.message(_("Sonic pitch {pitch}").format(pitch=pitch))

	@script(
		description=_("Decrease Sonic pitch for the current synthesizer"),
		category=scriptCategory,
	)
	def script_decreaseGlobalSonicPitch(self, gesture):
		pitch = _changeCurrentSynthSonicPitch(-5)
		config.conf.save()
		if ui is not None:
			if pitch is None:
				ui.message(_("Sonic pitch is unavailable for {synth}").format(synth=_getSynthName() or _("current synth")))
			else:
				ui.message(_("Sonic pitch {pitch}").format(pitch=pitch))

	@script(
		description=_("Reset Sonic pitch for the current synthesizer"),
		category=scriptCategory,
	)
	def script_resetGlobalSonicPitch(self, gesture):
		pitch = _setCurrentSynthSonicPitch(NEUTRAL_PITCH)
		config.conf.save()
		if ui is not None:
			if pitch is None:
				ui.message(_("Sonic pitch is unavailable for {synth}").format(synth=_getSynthName() or _("current synth")))
			else:
				ui.message(_("Sonic pitch {pitch}").format(pitch=pitch))
