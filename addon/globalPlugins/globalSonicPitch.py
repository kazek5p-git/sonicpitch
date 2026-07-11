# Global Sonic pitch processing for NVDA WavePlayer speech audio.

from __future__ import annotations

import ctypes
import types
from typing import Any, Callable

import addonHandler
import config
import globalPluginHandler
import gui
import nvwave
import wx
import gui.settingsDialogs as settingsDialogs
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log
from scriptHandler import script

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
	"debugLogging": "boolean(default=False)",
}

NEUTRAL_PITCH = 50
MAX_SEMITONES = 6.0
MIN_SONIC_PITCH_RATIO = 0.70
MAX_SONIC_PITCH_RATIO = 1.45

UNSUPPORTED_GLOBAL_SYNTHS = {
	# On 64-bit NVDA, sapi5_32 speaks in the separate 32-bit synth host.
	# This global plugin is loaded only in the main NVDA process.
	"sapi5_32",
}

_ORIGINAL_FEED_ATTR = "_globalSonicPitchOriginalFeed"
_FEED_PATCHED_ATTR = "_globalSonicPitchFeedPatched"
_ORIGINAL_SET_SYNTH_ATTR = "_globalSonicPitchOriginalSetSynth"
_SET_SYNTH_PATCHED_ATTR = "_globalSonicPitchSetSynthPatched"
_ORIGINAL_SETTINGS_SET_SYNTH_ATTR = "_globalSonicPitchOriginalSettingsSetSynth"
_SETTINGS_SET_SYNTH_PATCHED_ATTR = "_globalSonicPitchSettingsSetSynthPatched"
_ORIGINAL_SET_PITCH_ATTR = "_globalSonicPitchOriginalSetPitch"
_ORIGINAL_GET_PITCH_ATTR = "_globalSonicPitchOriginalGetPitch"
_PITCH_PATCHED_ATTR = "_globalSonicPitchPitchPatched"
_NEUTRALIZING_ATTR = "_globalSonicPitchNeutralizing"

_sonicModule = None
_processingLogKeys: set[tuple[Any, ...]] = set()
_pitchTakeoverLogKeys: set[tuple[Any, ...]] = set()
_unsupportedSynthLogKeys: set[str] = set()
_sonicUnavailableReason: str | None = None
_configMigrated = False


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
	wasEnabled = bool(_getConfigValue("enabled", False))
	_setConfigValue("enabled", bool(enabled))
	if enabled:
		_patchCurrentSynthPitch()
		_activatePitchTakeoverForCurrentSynth()
	elif wasEnabled:
		_restoreCurrentSynthNativePitch()


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def _clampPitch(value: int | float) -> int:
	return int(_clamp(float(value), 0.0, 100.0))


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


def _isGlobalAudioSupportedSynth(synthName: str) -> bool:
	if synthName in UNSUPPORTED_GLOBAL_SYNTHS:
		return False
	if synthName.startswith("sapi5SonicPitch"):
		return False
	return True


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


def _shouldProcess(player: nvwave.WavePlayer, rawSize: int) -> bool:
	if rawSize <= 0:
		return False
	if not bool(_getConfigValue("enabled", False)):
		return False
	if int(_getConfigValue("pitch", NEUTRAL_PITCH)) == NEUTRAL_PITCH:
		return False
	if not _isSpeechPlayer(player):
		return False
	synthName = _getSynthName()
	if not _isGlobalAudioSupportedSynth(synthName):
		return False
	return True


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
		return ctypes.string_at(ctypes.addressof(value), ctypes.sizeof(value))
	except Exception:
		return bytes(value)


def _processPcm16Block(raw: bytes, channels: int, sampleRate: int, pitchPercent: int) -> bytes | None:
	frameSize = channels * 2
	if len(raw) < frameSize or len(raw) % frameSize:
		return None
	sonic = _getSonicModule()
	if sonic is None:
		return None
	frameCount = len(raw) // frameSize
	sampleCount = frameCount * channels
	inputSamples = (ctypes.c_short * sampleCount).from_buffer_copy(raw)
	stream = sonic.SonicStream(sampleRate, channels)
	stream.pitch = _pitchPercentToSonicRatio(pitchPercent)
	stream.writeShort(inputSamples, frameCount)
	stream.flush()
	processedSamples = stream.readShort()
	if not processedSamples:
		return None
	processed = _ctypesArrayToBytes(processedSamples)
	return processed or None


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
		if raw is not None and _shouldProcess(self, len(raw)):
			waveFormat = _getWaveFormat(self)
			if waveFormat is not None:
				channels, sampleRate, bitsPerSample = waveFormat
				if bitsPerSample == 16:
					pitch = int(_getConfigValue("pitch", NEUTRAL_PITCH))
					processed = _processPcm16Block(raw, channels, sampleRate, pitch)
					if processed:
						_logProcessedOnce(
							_getSynthName(),
							channels,
							sampleRate,
							pitch,
							len(raw),
							len(processed),
						)
						return originalFeed(self, processed, len(processed), onDone)
				elif _isDebugLoggingEnabled():
					log.debug(f"globalSonicPitch: bypassing non-16-bit audio: {bitsPerSample}")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to process WavePlayer feed; bypassing", exc_info=True)
	return originalFeed(self, data, size, onDone)


def installWavePlayerHook() -> None:
	if getattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, False):
		return
	setattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR, nvwave.WavePlayer.feed)
	nvwave.WavePlayer.feed = _patchedFeed
	setattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, True)
	log.info("globalSonicPitch: installed WavePlayer speech feed hook")


def uninstallWavePlayerHook() -> None:
	if not getattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, False):
		return
	originalFeed = getattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR, None)
	if originalFeed is not None and nvwave.WavePlayer.feed is _patchedFeed:
		nvwave.WavePlayer.feed = originalFeed
	try:
		delattr(nvwave.WavePlayer, _ORIGINAL_FEED_ATTR)
	except Exception:
		pass
	setattr(nvwave.WavePlayer, _FEED_PATCHED_ATTR, False)
	log.info("globalSonicPitch: removed WavePlayer speech feed hook")


def _getOriginalSetPitch(synth: Any) -> Callable[[int], None] | None:
	return getattr(synth, _ORIGINAL_SET_PITCH_ATTR, None)


def _getOriginalGetPitch(synth: Any) -> Callable[[], int] | None:
	return getattr(synth, _ORIGINAL_GET_PITCH_ATTR, None)


def _isPitchTakeoverSupported(synth: Any | None) -> bool:
	if synth is None:
		return False
	synthName = _getSynthName(synth)
	if not _isGlobalAudioSupportedSynth(synthName):
		return False
	return callable(getattr(synth, "_set_pitch", None)) and callable(getattr(synth, "_get_pitch", None))


def _logUnsupportedPitchTakeover(synthName: str) -> None:
	if synthName in _unsupportedSynthLogKeys and not _isDebugLoggingEnabled():
		return
	_unsupportedSynthLogKeys.add(synthName)
	log.info(f"globalSonicPitch: pitch takeover not available for synth={synthName or 'unknown'}")


def _logPitchTakeoverOnce(synthName: str, sonicPitch: int, nativePitch: int | None = None) -> None:
	key = (synthName, sonicPitch, nativePitch)
	if key in _pitchTakeoverLogKeys and not _isDebugLoggingEnabled():
		return
	_pitchTakeoverLogKeys.add(key)
	log.info(
		"globalSonicPitch: pitch takeover active; "
		f"synth={synthName or 'unknown'}; sonicPitch={sonicPitch}; "
		f"nativePitch={NEUTRAL_PITCH}"
		+ (f"; previousNativePitch={nativePitch}" if nativePitch is not None else ""),
	)


def _nativeGetPitch(synth: Any) -> int | None:
	originalGetPitch = _getOriginalGetPitch(synth) or getattr(synth, "_get_pitch", None)
	if not callable(originalGetPitch):
		return None
	try:
		return _clampPitch(originalGetPitch())
	except Exception:
		return None


def _nativeSetPitch(synth: Any, pitch: int) -> bool:
	originalSetPitch = _getOriginalSetPitch(synth) or getattr(synth, "_set_pitch", None)
	if not callable(originalSetPitch):
		return False
	try:
		setattr(synth, _NEUTRALIZING_ATTR, True)
		originalSetPitch(_clampPitch(pitch))
		return True
	except Exception:
		log.debugWarning("globalSonicPitch: failed to set native synth pitch", exc_info=True)
		return False
	finally:
		try:
			setattr(synth, _NEUTRALIZING_ATTR, False)
		except Exception:
			pass


def _activatePitchTakeoverForSynth(synth: Any | None) -> None:
	if not bool(_getConfigValue("enabled", False)):
		return
	if not _isPitchTakeoverSupported(synth):
		_logUnsupportedPitchTakeover(_getSynthName(synth))
		return
	nativePitch = _nativeGetPitch(synth)
	sonicPitch = _clampPitch(_getConfigValue("pitch", NEUTRAL_PITCH))
	if sonicPitch == NEUTRAL_PITCH and nativePitch not in (None, NEUTRAL_PITCH):
		sonicPitch = nativePitch
		_setConfigValue("pitch", sonicPitch)
	if _nativeSetPitch(synth, NEUTRAL_PITCH):
		_logPitchTakeoverOnce(_getSynthName(synth), sonicPitch, nativePitch)


def _activatePitchTakeoverForCurrentSynth() -> None:
	_activatePitchTakeoverForSynth(_getCurrentSynth())


def _restoreCurrentSynthNativePitch() -> None:
	synth = _getCurrentSynth()
	if not _isPitchTakeoverSupported(synth):
		return
	pitch = _clampPitch(_getConfigValue("pitch", NEUTRAL_PITCH))
	if _nativeSetPitch(synth, pitch):
		log.info(f"globalSonicPitch: restored native pitch; synth={_getSynthName(synth)}; pitch={pitch}")


def _patchedSetPitch(self, value):
	originalSetPitch = _getOriginalSetPitch(self)
	if not callable(originalSetPitch):
		return None
	if getattr(self, _NEUTRALIZING_ATTR, False):
		return originalSetPitch(value)
	if bool(_getConfigValue("enabled", False)):
		sonicPitch = _clampPitch(value)
		_setConfigValue("pitch", sonicPitch)
		_nativeSetPitch(self, NEUTRAL_PITCH)
		log.info(
			"globalSonicPitch: captured NVDA pitch; "
			f"synth={_getSynthName(self)}; sonicPitch={sonicPitch}; nativePitch={NEUTRAL_PITCH}",
		)
		return None
	return originalSetPitch(value)


def _patchedGetPitch(self):
	if bool(_getConfigValue("enabled", False)):
		return _clampPitch(_getConfigValue("pitch", NEUTRAL_PITCH))
	originalGetPitch = _getOriginalGetPitch(self)
	if callable(originalGetPitch):
		return originalGetPitch()
	return NEUTRAL_PITCH


def _patchSynthPitch(synth: Any | None) -> None:
	if synth is None:
		return
	if getattr(synth, _PITCH_PATCHED_ATTR, False):
		if bool(_getConfigValue("enabled", False)):
			_activatePitchTakeoverForSynth(synth)
		return
	if not _isPitchTakeoverSupported(synth):
		if bool(_getConfigValue("enabled", False)):
			_logUnsupportedPitchTakeover(_getSynthName(synth))
		return
	try:
		setattr(synth, _ORIGINAL_SET_PITCH_ATTR, getattr(synth, "_set_pitch"))
		setattr(synth, _ORIGINAL_GET_PITCH_ATTR, getattr(synth, "_get_pitch"))
		synth._set_pitch = types.MethodType(_patchedSetPitch, synth)
		synth._get_pitch = types.MethodType(_patchedGetPitch, synth)
		setattr(synth, _PITCH_PATCHED_ATTR, True)
		log.info(f"globalSonicPitch: patched pitch setting; synth={_getSynthName(synth)}")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to patch synth pitch setting", exc_info=True)
		return
	if bool(_getConfigValue("enabled", False)):
		_activatePitchTakeoverForSynth(synth)


def _unpatchSynthPitch(synth: Any | None) -> None:
	if synth is None or not getattr(synth, _PITCH_PATCHED_ATTR, False):
		return
	originalSetPitch = _getOriginalSetPitch(synth)
	originalGetPitch = _getOriginalGetPitch(synth)
	try:
		if callable(originalSetPitch):
			synth._set_pitch = originalSetPitch
		if callable(originalGetPitch):
			synth._get_pitch = originalGetPitch
		for attr in (
			_ORIGINAL_SET_PITCH_ATTR,
			_ORIGINAL_GET_PITCH_ATTR,
			_PITCH_PATCHED_ATTR,
			_NEUTRALIZING_ATTR,
		):
			try:
				delattr(synth, attr)
			except Exception:
				pass
		log.info(f"globalSonicPitch: restored pitch setting hook; synth={_getSynthName(synth)}")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to restore synth pitch setting", exc_info=True)


def _patchCurrentSynthPitch() -> None:
	_patchSynthPitch(_getCurrentSynth())


def _callSetSynthAndPatch(originalSetSynth: Callable[..., Any], *args, **kwargs):
	result = originalSetSynth(*args, **kwargs)
	try:
		_patchCurrentSynthPitch()
	except Exception:
		log.debugWarning("globalSonicPitch: failed after synth switch", exc_info=True)
	return result


def _patchedSetSynth(*args, **kwargs):
	originalSetSynth = getattr(synthDriverHandler, _ORIGINAL_SET_SYNTH_ATTR)
	return _callSetSynthAndPatch(originalSetSynth, *args, **kwargs)


def _patchedSettingsSetSynth(*args, **kwargs):
	originalSetSynth = getattr(settingsDialogs, _ORIGINAL_SETTINGS_SET_SYNTH_ATTR)
	return _callSetSynthAndPatch(originalSetSynth, *args, **kwargs)


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
	log.info("globalSonicPitch: installed synth pitch takeover hook")


def uninstallSynthPitchHook() -> None:
	if synthDriverHandler is None:
		return
	_unpatchSynthPitch(_getCurrentSynth())
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
	log.info("globalSonicPitch: removed synth pitch takeover hook")


class GlobalSonicPitchSettingsPanel(SettingsPanel):
	title = _("Global Sonic Pitch")

	def makeSettings(self, settingsSizer):
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = config.conf[CONFIG_SECTION]
		self.enableCheckbox = helper.addItem(
			wx.CheckBox(self, label=_("Enable global Sonic pitch")),
		)
		self.enableCheckbox.SetValue(bool(conf["enabled"]))
		self.pitchSlider = helper.addLabeledControl(
			_("Sonic pitch"),
			wx.Slider,
			minValue=0,
			maxValue=100,
			style=wx.SL_HORIZONTAL | wx.SL_LABELS,
		)
		self.pitchSlider.SetValue(int(conf["pitch"]))
		self.debugCheckbox = helper.addItem(
			wx.CheckBox(self, label=_("Enable debug logging")),
		)
		self.debugCheckbox.SetValue(bool(conf["debugLogging"]))
		self.enableCheckbox.Bind(wx.EVT_CHECKBOX, self._updateControlState)
		self._updateControlState()

	def _updateControlState(self, event=None):
		enabled = self.enableCheckbox.IsChecked()
		self.pitchSlider.Enable(enabled)
		self.debugCheckbox.Enable(enabled)

	def onSave(self):
		_setConfigValue("pitch", self.pitchSlider.GetValue())
		_setConfigValue("debugLogging", self.debugCheckbox.IsChecked())
		_setGlobalEnabled(self.enableCheckbox.IsChecked())
		config.conf.save()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Global Sonic Pitch")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		_ensureConfigSpec()
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
		pitch = int(_getConfigValue("pitch", NEUTRAL_PITCH))
		message = _("Global Sonic pitch on, pitch {pitch}").format(pitch=pitch) if enabled else _(
			"Global Sonic pitch off",
		)
		if _sonicUnavailableReason:
			message = f"{message}. Sonic unavailable: {_sonicUnavailableReason}"
		if ui is not None:
			ui.message(message)
