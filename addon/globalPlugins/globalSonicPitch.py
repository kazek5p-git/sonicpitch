# Global Sonic pitch processing for NVDA WavePlayer speech audio.

from __future__ import annotations

import ctypes
import json
import os
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
	"extendedPitchRange": "boolean(default=False)",
	"sonicQuality": "integer(default=0, min=0, max=1)",
	"debugLogging": "boolean(default=False)",
}

NEUTRAL_PITCH = 50
STANDARD_MAX_SEMITONES = 6.0
EXTENDED_MAX_SEMITONES = 20.0
SONIC_PITCH_SETTING_ID = "sonicPitch"
SONIC_PITCH_EXTENDED_RANGE_PARAM_ID = "_sonicPitchExtendedRange"
SONIC_QUALITY_PARAM_ID = "_sonicQuality"
SONIC_PITCH_HOST_SETTING_IDS = {SONIC_PITCH_SETTING_ID, SONIC_PITCH_EXTENDED_RANGE_PARAM_ID, SONIC_QUALITY_PARAM_ID}
SUPPORT_URL = "https://buycoffee.to/kazimierz-parzych"
LEGACY_PITCH_CONFIG_KEY = "pitch"
PITCH_BY_SYNTH_CONFIG_KEY = "pitchBySynth"
EXTENDED_PITCH_RANGE_CONFIG_KEY = "extendedPitchRange"
SONIC_QUALITY_CONFIG_KEY = "sonicQuality"
VOICE_KEY_SEPARATOR = "::voice::"

_ORIGINAL_FEED_ATTR = "_globalSonicPitchOriginalFeed"
_ORIGINAL_IDLE_ATTR = "_globalSonicPitchOriginalIdle"
_ORIGINAL_STOP_ATTR = "_globalSonicPitchOriginalStop"
_ORIGINAL_CLOSE_ATTR = "_globalSonicPitchOriginalClose"
_FEED_PATCHED_ATTR = "_globalSonicPitchFeedPatched"
_ORIGINAL_SET_SYNTH_ATTR = "_globalSonicPitchOriginalSetSynth"
_SET_SYNTH_PATCHED_ATTR = "_globalSonicPitchSetSynthPatched"
_ORIGINAL_SETTINGS_SET_SYNTH_ATTR = "_globalSonicPitchOriginalSettingsSetSynth"
_SETTINGS_SET_SYNTH_PATCHED_ATTR = "_globalSonicPitchSettingsSetSynthPatched"
_ORIGINAL_VOICE_PANEL_MAKE_SETTINGS_ATTR = "_globalSonicPitchOriginalVoicePanelMakeSettings"
_ORIGINAL_VOICE_PANEL_ON_SAVE_ATTR = "_globalSonicPitchOriginalVoicePanelOnSave"
_ORIGINAL_VOICE_PANEL_ON_DISCARD_ATTR = "_globalSonicPitchOriginalVoicePanelOnDiscard"
_VOICE_PANEL_PATCHED_ATTR = "_globalSonicPitchVoicePanelPatched"
_ORIGINAL_SUPPORTED_SETTINGS_ATTR = "_globalSonicPitchOriginalSupportedSettings"
_SONIC_PITCH_SETTING_PATCHED_ATTR = "_globalSonicPitchVoiceSettingPatched"
_BUNDLED_SONIC_DIR = "sonicPitchNative"
_BUNDLED_SONIC_32_DLL = "sonicPitchSonic32.dll"
_BUNDLED_SONIC_64_DLL = "sonicPitchSonic64.dll"
_SAPI32_HOST_DRIVER_DIR = "sapi32HostDrivers"
_ORIGINAL_SAPI32_HOST_PATH_ATTR = "_globalSonicPitchOriginalSynthDriver32Path"
_SAPI32_HOST_PATH_PATCHED_ATTR = "_globalSonicPitchHostPathPatched"

_sonicModule = None
_processingLogKeys: set[tuple[Any, ...]] = set()
_deferredPitchLogKeys: set[tuple[Any, ...]] = set()
_voiceSettingLogKeys: set[str] = set()
_sonicUnavailableReason: str | None = None
_sonicPitchDriverSetting: Any | None = None
_missingClassAttr = object()
_sonicPitchClassPatches: dict[type, Any] = {}
_voiceClassPatches: dict[type, Any] = {}
_configMigrated = False
_deferSynthPitchPatchDepth = 0
_noDestroySonicStreamLogged = False
_playerProcessors: dict[int, "_SonicStreamProcessor"] = {}
_playerUtterancePitches: dict[int, int] = {}
_playerUtteranceQualities: dict[int, int] = {}
_playerProcessorsLock = threading.RLock()
_FIRST_AUDIO_CHUNK_MIN_DURATION_MS = 50
_SHORT_AUDIO_CHUNK_MAX_DURATION_MS = 35
_sapi32HostReloading = False
_sapi32HostReloadRequested = False
_voiceDialogSessions: dict[int, dict[str, dict[str, int]]] = {}
_runtimeSonicPitchByKey: dict[str, tuple[int, bool, int]] = {}
_qualityLogKeys: set[tuple[Any, ...]] = set()


class _SonicStreamP(ctypes.c_void_p):
	pass


class _BundledSonicModule:
	def __init__(self, sonicLib: ctypes.CDLL, dllPath: str):
		self.sonicLib = sonicLib
		self.dllPath = dllPath
		self.isBundled = True


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
	if enabled:
		_installSapi32HostDriverPatch()
	_setConfigValue("enabled", bool(enabled))
	_resetAllPlayerProcessors()
	_patchCurrentSynthPitch()


def _isExtendedPitchRangeEnabled() -> bool:
	return bool(_getConfigValue(EXTENDED_PITCH_RANGE_CONFIG_KEY, False))


def _setExtendedPitchRangeEnabled(enabled: bool) -> None:
	enabled = bool(enabled)
	wasEnabled = _isExtendedPitchRangeEnabled()
	_setConfigValue(EXTENDED_PITCH_RANGE_CONFIG_KEY, enabled)
	if wasEnabled == enabled:
		return
	_resetAllPlayerProcessors()
	_runtimeSonicPitchByKey.clear()
	_patchCurrentSynthPitch()


def _openSupportPage() -> None:
	try:
		opened = webbrowser.open_new_tab(SUPPORT_URL)
	except Exception:
		opened = False
		log.debugWarning("globalSonicPitch: failed to open support page", exc_info=True)
	if opened:
		if ui is not None:
			# Translators: Spoken message after opening the support page.
			ui.message(_("Opening support page"))
		return
	if ui is not None:
		# Translators: Spoken error when the support page cannot be opened automatically.
		ui.message(_("Cannot open support page. Open this address manually: {url}").format(url=SUPPORT_URL))


def _clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def _clampPitch(value: int | float) -> int:
	try:
		numericValue = float(value)
	except Exception:
		numericValue = float(NEUTRAL_PITCH)
	return int(_clamp(numericValue, 0.0, 100.0))


def _clampQuality(value: Any) -> int:
	try:
		return 1 if int(value) == 1 else 0
	except Exception:
		return 0


def _getSonicQuality() -> int:
	return _clampQuality(_getConfigValue(SONIC_QUALITY_CONFIG_KEY, 0))


def _setSonicQuality(value: Any) -> None:
	quality = _clampQuality(value)
	oldQuality = _getSonicQuality()
	_setConfigValue(SONIC_QUALITY_CONFIG_KEY, quality)
	if oldQuality == quality:
		return
	_resetAllPlayerProcessors()
	_runtimeSonicPitchByKey.clear()
	_patchCurrentSynthPitch()
	log.info(f"globalSonicPitch: Sonic processing quality set to {quality} ({_getQualityLabel(quality)})")


def _getQualityLabel(quality: int) -> str:
	return "higher quality" if _clampQuality(quality) == 1 else "fast"


def _pitchPercentToSonicRatio(pitchPercent: int | float) -> float:
	pitchPercent = _clamp(float(pitchPercent), 0.0, 100.0)
	maxSemitones = EXTENDED_MAX_SEMITONES if _isExtendedPitchRangeEnabled() else STANDARD_MAX_SEMITONES
	semitones = ((pitchPercent - 50.0) / 50.0) * maxSemitones
	ratio = 2.0 ** (semitones / 12.0)
	minRatio = 2.0 ** (-maxSemitones / 12.0)
	maxRatio = 2.0 ** (maxSemitones / 12.0)
	return _clamp(ratio, minRatio, maxRatio)


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


def _getCurrentSynthDisplayName() -> str:
	# Translators: Fallback synthesizer name used in spoken status messages.
	return _getSynthName() or _("current synth")


def _isGlobalAudioSupportedSynth(synthName: str) -> bool:
	if synthName.startswith("sapi5SonicPitch"):
		return False
	return True


def _getSynthPitchKey(synthName: str | None) -> str:
	key = str(synthName or "").strip()
	if key == "sapi5":
		return "sapi5_32" if _is32BitProcess() else "sapi5_64"
	if key == "sapi5_32":
		return "sapi5_32"
	return key


def _normalizePitchStorageKey(key: str | None) -> str:
	key = str(key or "").strip()
	if not key:
		return ""
	synthName, separator, voiceId = key.partition(VOICE_KEY_SEPARATOR)
	synthKey = _getSynthPitchKey(synthName)
	if not separator:
		return synthKey
	voiceId = str(voiceId or "").strip()
	if not synthKey or not voiceId:
		return synthKey
	return f"{synthKey}{VOICE_KEY_SEPARATOR}{voiceId}"


def _getBasePitchKeyFromStorageKey(key: str | None) -> str:
	key = _normalizePitchStorageKey(key)
	synthName, _, _voiceId = key.partition(VOICE_KEY_SEPARATOR)
	return _getSynthPitchKey(synthName)


def _stringifyVoiceIdentifier(value: Any) -> str:
	if value is None:
		return ""
	if isinstance(value, bytes):
		try:
			value = value.decode("utf-8", errors="replace")
		except Exception:
			value = repr(value)
	if not isinstance(value, str):
		for attr in ("id", "ID", "name", "displayName"):
			try:
				attrValue = getattr(value, attr, None)
			except Exception:
				attrValue = None
			if attrValue:
				return str(attrValue).strip()
	return str(value).strip()


def _getSynthVoiceId(synth: Any | None) -> str:
	if synth is None:
		return ""
	for attr in ("voice", "_voice"):
		try:
			voiceId = _stringifyVoiceIdentifier(getattr(synth, attr))
		except Exception:
			continue
		if voiceId and voiceId.lower() != "none":
			return voiceId
	return ""


def _getSonicPitchStorageKey(synthOrName: Any | None = None) -> str:
	if synthOrName is None:
		synthOrName = _getCurrentSynth()
	if isinstance(synthOrName, str):
		return _normalizePitchStorageKey(synthOrName)
	synthKey = _getSynthPitchKey(_getSynthName(synthOrName))
	if not synthKey:
		return ""
	voiceId = _getSynthVoiceId(synthOrName)
	if not voiceId:
		return synthKey
	return _normalizePitchStorageKey(f"{synthKey}{VOICE_KEY_SEPARATOR}{voiceId}")


def _isRemoteSapi32Synth(synthName: str | None) -> bool:
	return not _is32BitProcess() and str(synthName or "").strip() in {"sapi4_32", "sapi5_32"}


def _getSapi32HostDriverPath() -> str:
	return os.path.join(os.path.dirname(os.path.dirname(__file__)), _SAPI32_HOST_DRIVER_DIR)


def _installSapi32HostDriverPatch() -> bool:
	if _is32BitProcess():
		return False
	driverPath = _getSapi32HostDriverPath()
	if not os.path.isdir(driverPath):
		log.debugWarning(f"globalSonicPitch: 32-bit host driver path is missing: {driverPath}")
		return False
	patched = False
	try:
		for moduleName in ("sapi4_32", "sapi5_32"):
			try:
				module = __import__(f"synthDrivers.{moduleName}", fromlist=["SynthDriver"])
				synthClass = module.SynthDriver
				if not hasattr(synthClass, _ORIGINAL_SAPI32_HOST_PATH_ATTR):
					setattr(synthClass, _ORIGINAL_SAPI32_HOST_PATH_ATTR, getattr(synthClass, "synthDriver32Path", None))
				if getattr(synthClass, "synthDriver32Path", None) != driverPath:
					synthClass.synthDriver32Path = driverPath
					log.info(
						"globalSonicPitch: installed 32-bit host driver path; "
						f"synth={moduleName}; path={driverPath}",
					)
				setattr(synthClass, _SAPI32_HOST_PATH_PATCHED_ATTR, True)
				patched = True
			except Exception:
				log.debugWarning(f"globalSonicPitch: failed to install 32-bit host path for {moduleName}", exc_info=True)
		return patched
	except Exception:
		log.debugWarning("globalSonicPitch: failed to install 32-bit host driver path", exc_info=True)
		return False


def _restoreSapi32HostDriverPatch() -> None:
	if _is32BitProcess():
		return
	for moduleName in ("sapi4_32", "sapi5_32"):
		try:
			module = __import__(f"synthDrivers.{moduleName}", fromlist=["SynthDriver"])
			synthClass = module.SynthDriver
			if not getattr(synthClass, _SAPI32_HOST_PATH_PATCHED_ATTR, False):
				continue
			originalPath = getattr(synthClass, _ORIGINAL_SAPI32_HOST_PATH_ATTR, None)
			if originalPath:
				synthClass.synthDriver32Path = originalPath
			for attr in (_ORIGINAL_SAPI32_HOST_PATH_ATTR, _SAPI32_HOST_PATH_PATCHED_ATTR):
				try:
					delattr(synthClass, attr)
				except Exception:
					pass
			log.info(f"globalSonicPitch: restored 32-bit host driver path; synth={moduleName}")
		except Exception:
			log.debugWarning(f"globalSonicPitch: failed to restore 32-bit host path for {moduleName}", exc_info=True)


def _getRemoteService(synth: Any | None) -> Any | None:
	if synth is None:
		return None
	return getattr(synth, "_remoteService", None)


def _remoteSapi32SupportsSonicPitch(synth: Any | None) -> bool:
	if not _isRemoteSapi32Synth(_getSynthName(synth)):
		return False
	return _hasSonicPitchSetting(getattr(synth, "supportedSettings", ()))


def _reloadCurrentRemoteSapi32Synth() -> None:
	global _sapi32HostReloading, _sapi32HostReloadRequested
	if synthDriverHandler is None or _sapi32HostReloading:
		return
	synthName = _getSynthName()
	if not _isRemoteSapi32Synth(synthName):
		return
	_sapi32HostReloading = True
	try:
		log.info(f"globalSonicPitch: reloading 32-bit synth to enable host Sonic pitch support; synth={synthName}")
		synthDriverHandler.setSynth(synthName)
	finally:
		_sapi32HostReloading = False
		_sapi32HostReloadRequested = False


def _requestRemoteSapi32SynthReload() -> None:
	global _sapi32HostReloadRequested
	if _sapi32HostReloadRequested or not _installSapi32HostDriverPatch():
		return
	if not _isRemoteSapi32Synth(_getSynthName()):
		return
	_sapi32HostReloadRequested = True
	try:
		wx.CallAfter(_reloadCurrentRemoteSapi32Synth)
	except Exception:
		_reloadCurrentRemoteSapi32Synth()


def _setRemoteSapi32SonicPitch(synth: Any | None, pitch: int | float) -> bool:
	if not _isRemoteSapi32Synth(_getSynthName(synth)):
		return False
	service = _getRemoteService(synth)
	if service is None:
		return False
	pitch = _clampPitch(pitch)
	quality = _getSonicQuality()
	try:
		service.setParam(SONIC_PITCH_EXTENDED_RANGE_PARAM_ID, 1 if _isExtendedPitchRangeEnabled() else 0)
	except Exception:
		log.debugWarning(
			"globalSonicPitch: failed to apply remote 32-bit Sonic pitch range",
			exc_info=True,
		)
	try:
		service.setParam(SONIC_QUALITY_PARAM_ID, quality)
	except Exception:
		log.debugWarning(
			"globalSonicPitch: failed to apply remote 32-bit Sonic quality; remote host will use fast mode",
			exc_info=True,
		)
	try:
		service.setParam(SONIC_PITCH_SETTING_ID, pitch)
		log.info(
			"globalSonicPitch: applied remote 32-bit Sonic pitch; "
			f"synth={_getSynthName(synth)}; sonicPitch={pitch}; "
			f"extendedRange={_isExtendedPitchRangeEnabled()}; quality={quality} ({_getQualityLabel(quality)})",
		)
		return True
	except Exception:
		log.debugWarning("globalSonicPitch: failed to apply remote 32-bit Sonic pitch", exc_info=True)
		return False


def _applyRuntimeSonicPitch(synth: Any | None, pitch: int | float) -> None:
	if not _isRemoteSapi32Synth(_getSynthName(synth)):
		return
	key = _getSonicPitchStorageKey(synth) or _getSynthName(synth)
	pitch = _clampPitch(pitch)
	state = (pitch, _isExtendedPitchRangeEnabled(), _getSonicQuality())
	if key and _runtimeSonicPitchByKey.get(key) == state:
		return
	if _setRemoteSapi32SonicPitch(synth, pitch):
		if key:
			_runtimeSonicPitchByKey[key] = state
	else:
		_requestRemoteSapi32SynthReload()


def _getActiveVoiceDialogSession() -> dict[str, dict[str, int]] | None:
	if not _voiceDialogSessions:
		return None
	try:
		return next(reversed(_voiceDialogSessions.values()))
	except Exception:
		return None


def _getVoiceDialogPendingPitch(key: str) -> int | None:
	for session in reversed(tuple(_voiceDialogSessions.values())):
		pending = session.get("pending", {})
		if key in pending:
			return _clampPitch(pending[key])
	return None


def _captureVoiceDialogBaseline(session: dict[str, dict[str, int]], synthOrName: Any | None) -> str:
	key = _getSonicPitchStorageKey(synthOrName)
	if not key:
		return ""
	snapshots = session.setdefault("snapshots", {})
	if key not in snapshots:
		snapshots[key] = _getStoredSonicPitchForKey(key)
	return key


def _setVoiceDialogPendingSonicPitch(synth: Any | None, pitch: int | float) -> bool:
	session = _getActiveVoiceDialogSession()
	if session is None:
		return False
	synthName = _getSynthName(synth)
	if not _isGlobalAudioSupportedSynth(synthName):
		return False
	key = _captureVoiceDialogBaseline(session, synth)
	if not key:
		return False
	pitch = _clampPitch(pitch)
	pending = session.setdefault("pending", {})
	snapshotPitch = session.setdefault("snapshots", {}).get(key, NEUTRAL_PITCH)
	if key not in pending and pitch == snapshotPitch:
		return True
	pending[key] = pitch
	_clearIdlePlayerUtterancePitches()
	_applyRuntimeSonicPitch(synth, pitch)
	log.info(
		"globalSonicPitch: captured temporary Sonic pitch setting; "
		f"synth={synthName}; key={key}; pendingPitch={pitch}",
	)
	return True


def _commitVoiceDialogSession(panelId: int) -> None:
	session = _voiceDialogSessions.get(panelId)
	if not session:
		return
	pending = dict(session.get("pending", {}))
	session["pending"] = {}
	for key, pitch in pending.items():
		_setSonicPitchForKey(key, pitch)
	currentSynth = _getCurrentSynth()
	currentKey = _getSonicPitchStorageKey(currentSynth)
	if currentKey in pending:
		_applyRuntimeSonicPitch(currentSynth, pending[currentKey])
	snapshots = session.setdefault("snapshots", {})
	for key in set(snapshots) | set(pending):
		snapshots[key] = _getStoredSonicPitchForKey(key)
	if pending:
		log.info(
			"globalSonicPitch: committed Sonic pitch changes from Voice settings; "
			f"keys={','.join(sorted(pending))}",
		)


def _restoreVoiceDialogSession(panelId: int) -> None:
	session = _voiceDialogSessions.get(panelId)
	if not session:
		return
	pending = dict(session.get("pending", {}))
	snapshots = dict(session.get("snapshots", {}))
	session["pending"] = {}
	if not pending:
		return
	_clearIdlePlayerUtterancePitches()
	for key, pitch in snapshots.items():
		_setSonicPitchForKey(key, pitch)
	currentSynth = _getCurrentSynth()
	currentKey = _getSonicPitchStorageKey(currentSynth)
	if currentKey in snapshots:
		_applyRuntimeSonicPitch(currentSynth, snapshots[currentKey])
	log.info(
		"globalSonicPitch: restored Sonic pitch after Voice settings discard; "
		f"keys={','.join(sorted(pending))}",
	)


def _ensureVoiceDialogSession(panel: Any) -> None:
	panelId = id(panel)
	if panelId not in _voiceDialogSessions:
		_voiceDialogSessions[panelId] = {"snapshots": {}, "pending": {}}
	_captureVoiceDialogBaseline(_voiceDialogSessions[panelId], _getCurrentSynth())
	if getattr(panel, "_globalSonicPitchVoiceSessionDestroyBound", False):
		return

	def _onDestroy(evt):
		try:
			if evt.GetEventObject() is panel:
				try:
					_restoreVoiceDialogSession(panelId)
				except Exception:
					log.debugWarning("globalSonicPitch: failed to restore Voice settings on destroy", exc_info=True)
				finally:
					_voiceDialogSessions.pop(panelId, None)
		finally:
			evt.Skip()

	try:
		panel.Bind(wx.EVT_WINDOW_DESTROY, _onDestroy)
		setattr(panel, "_globalSonicPitchVoiceSessionDestroyBound", True)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to bind Voice settings destroy handler", exc_info=True)


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
		key = _normalizePitchStorageKey(str(synthName))
		if key:
			pitches[key] = _clampPitch(pitch)
	return pitches


def _saveSynthPitchMap(pitches: dict[str, int]) -> None:
	serializable = {
		_normalizePitchStorageKey(synthName): _clampPitch(pitch)
		for synthName, pitch in pitches.items()
		if _normalizePitchStorageKey(synthName)
	}
	_setConfigValue(
		PITCH_BY_SYNTH_CONFIG_KEY,
		json.dumps(serializable, sort_keys=True, separators=(",", ":")),
	)


def _getStoredSonicPitchForKey(key: str | None) -> int:
	key = _normalizePitchStorageKey(key)
	if not key:
		return NEUTRAL_PITCH
	pitches = _loadSynthPitchMap()
	if key in pitches:
		return pitches[key]
	baseKey = _getBasePitchKeyFromStorageKey(key)
	if key != baseKey and baseKey in pitches:
		pitch = pitches.pop(baseKey)
		pitches[key] = pitch
		_saveSynthPitchMap(pitches)
		log.info(
			"globalSonicPitch: migrated per-synth Sonic pitch to current voice; "
			f"synth={baseKey}; key={key}; sonicPitch={pitch}",
		)
		return pitch
	return NEUTRAL_PITCH


def _migrateLegacyGlobalPitchToKey(key: str) -> None:
	legacyPitch = _clampPitch(_getConfigValue(LEGACY_PITCH_CONFIG_KEY, NEUTRAL_PITCH))
	if legacyPitch == NEUTRAL_PITCH:
		return
	key = _normalizePitchStorageKey(key)
	baseKey = _getBasePitchKeyFromStorageKey(key)
	if not key or not _isGlobalAudioSupportedSynth(baseKey):
		return
	pitches = _loadSynthPitchMap()
	if not pitches:
		pitches[key] = legacyPitch
		_saveSynthPitchMap(pitches)
		log.info(
			"globalSonicPitch: migrated global Sonic pitch to current synth; "
			f"key={key}; sonicPitch={legacyPitch}",
		)
	_setConfigValue(LEGACY_PITCH_CONFIG_KEY, NEUTRAL_PITCH)


def _setSonicPitchForKey(key: str | None, pitch: int | float) -> int | None:
	key = _normalizePitchStorageKey(key)
	baseKey = _getBasePitchKeyFromStorageKey(key)
	if not key or not _isGlobalAudioSupportedSynth(baseKey):
		return None
	pitch = _clampPitch(pitch)
	pitches = _loadSynthPitchMap()
	oldPitch = pitches.get(key, NEUTRAL_PITCH)
	pitches[key] = pitch
	_saveSynthPitchMap(pitches)
	_setConfigValue(LEGACY_PITCH_CONFIG_KEY, NEUTRAL_PITCH)
	if pitch != oldPitch:
		_clearIdlePlayerUtterancePitches()
		log.info(
			"globalSonicPitch: stored Sonic pitch for next safe audio boundary; "
			f"key={key}; oldPitch={oldPitch}; pendingPitch={pitch}",
		)
	return pitch


def _getSonicPitchForSynth(synthOrName: Any | None = None) -> int:
	key = _getSonicPitchStorageKey(synthOrName)
	if not key:
		return NEUTRAL_PITCH
	pendingPitch = _getVoiceDialogPendingPitch(key)
	if pendingPitch is not None:
		return pendingPitch
	_migrateLegacyGlobalPitchToKey(key)
	return _getStoredSonicPitchForKey(key)


def _setSonicPitchForSynth(synthOrName: Any | None, pitch: int | float) -> int | None:
	return _setSonicPitchForKey(_getSonicPitchStorageKey(synthOrName), pitch)


def _setCurrentSynthSonicPitch(pitch: int | float) -> int | None:
	synth = _getCurrentSynth()
	if _setVoiceDialogPendingSonicPitch(synth, pitch):
		return _clampPitch(pitch)
	pitch = _setSonicPitchForSynth(synth, pitch)
	if pitch is not None:
		_applyRuntimeSonicPitch(synth, pitch)
	return pitch


def _changeCurrentSynthSonicPitch(delta: int) -> int | None:
	return _setCurrentSynthSonicPitch(_getSonicPitchForSynth(_getCurrentSynth()) + delta)


def _getProcessingContext(player: nvwave.WavePlayer, rawSize: int) -> tuple[str, int, int] | None:
	if rawSize <= 0:
		return None
	if not bool(_getConfigValue("enabled", False)):
		return None
	if not _isSpeechPlayer(player):
		return None
	synth = _getCurrentSynth()
	synthName = _getSynthName(synth)
	if not _isGlobalAudioSupportedSynth(synthName):
		return None
	if _isRemoteSapi32Synth(synthName):
		return None
	pitch = _getSonicPitchForSynth(synth)
	utterancePitch = _getOrCreatePlayerUtterancePitch(player, pitch)
	quality = _getSonicQuality()
	utteranceQuality = _getOrCreatePlayerUtteranceQuality(player, quality)
	if utterancePitch != pitch:
		_logDeferredPitchOnce(synthName, utterancePitch, pitch)
	if utteranceQuality != quality:
		_logDeferredQualityOnce(synthName, utteranceQuality, quality)
	if utterancePitch == NEUTRAL_PITCH:
		_clearPlayerUtterancePitch(player)
		return None
	return synthName, utterancePitch, utteranceQuality


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


def _configureSonicLibrary(sonicLib: ctypes.CDLL) -> None:
	sonicLib.sonicCreateStream.restype = _SonicStreamP
	sonicLib.sonicCreateStream.argtypes = [ctypes.c_int, ctypes.c_int]
	sonicLib.sonicDestroyStream.restype = None
	sonicLib.sonicDestroyStream.argtypes = [_SonicStreamP]
	sonicLib.sonicWriteFloatToStream.restype = ctypes.c_int
	sonicLib.sonicWriteFloatToStream.argtypes = [_SonicStreamP, ctypes.c_void_p, ctypes.c_int]
	sonicLib.sonicWriteShortToStream.restype = ctypes.c_int
	sonicLib.sonicWriteShortToStream.argtypes = [_SonicStreamP, ctypes.c_void_p, ctypes.c_int]
	sonicLib.sonicWriteUnsignedCharToStream.restype = ctypes.c_int
	sonicLib.sonicWriteUnsignedCharToStream.argtypes = [_SonicStreamP, ctypes.c_void_p, ctypes.c_int]
	sonicLib.sonicReadFloatFromStream.restype = ctypes.c_int
	sonicLib.sonicReadFloatFromStream.argtypes = [_SonicStreamP, ctypes.c_void_p, ctypes.c_int]
	sonicLib.sonicReadShortFromStream.restype = ctypes.c_int
	sonicLib.sonicReadShortFromStream.argtypes = [_SonicStreamP, ctypes.c_void_p, ctypes.c_int]
	sonicLib.sonicReadUnsignedCharFromStream.restype = ctypes.c_int
	sonicLib.sonicReadUnsignedCharFromStream.argtypes = [_SonicStreamP, ctypes.c_void_p, ctypes.c_int]
	sonicLib.sonicFlushStream.restype = ctypes.c_int
	sonicLib.sonicFlushStream.argtypes = [_SonicStreamP]
	sonicLib.sonicSamplesAvailable.restype = ctypes.c_int
	sonicLib.sonicSamplesAvailable.argtypes = [_SonicStreamP]
	sonicLib.sonicGetSpeed.restype = ctypes.c_float
	sonicLib.sonicGetSpeed.argtypes = [_SonicStreamP]
	sonicLib.sonicSetSpeed.restype = None
	sonicLib.sonicSetSpeed.argtypes = [_SonicStreamP, ctypes.c_float]
	sonicLib.sonicGetPitch.restype = ctypes.c_float
	sonicLib.sonicGetPitch.argtypes = [_SonicStreamP]
	sonicLib.sonicSetPitch.restype = None
	sonicLib.sonicSetPitch.argtypes = [_SonicStreamP, ctypes.c_float]
	sonicLib.sonicGetRate.restype = ctypes.c_float
	sonicLib.sonicGetRate.argtypes = [_SonicStreamP]
	sonicLib.sonicSetRate.restype = None
	sonicLib.sonicSetRate.argtypes = [_SonicStreamP, ctypes.c_float]
	sonicLib.sonicGetVolume.restype = ctypes.c_float
	sonicLib.sonicGetVolume.argtypes = [_SonicStreamP]
	sonicLib.sonicSetVolume.restype = None
	sonicLib.sonicSetVolume.argtypes = [_SonicStreamP, ctypes.c_float]
	sonicLib.sonicGetQuality.restype = ctypes.c_int
	sonicLib.sonicGetQuality.argtypes = [_SonicStreamP]
	sonicLib.sonicSetQuality.restype = None
	sonicLib.sonicSetQuality.argtypes = [_SonicStreamP, ctypes.c_int]
	sonicLib.sonicGetSampleRate.restype = ctypes.c_int
	sonicLib.sonicGetSampleRate.argtypes = [_SonicStreamP]
	sonicLib.sonicSetSampleRate.restype = None
	sonicLib.sonicSetSampleRate.argtypes = [_SonicStreamP, ctypes.c_int]
	sonicLib.sonicGetNumChannels.restype = ctypes.c_int
	sonicLib.sonicGetNumChannels.argtypes = [_SonicStreamP]
	sonicLib.sonicSetNumChannels.restype = None
	sonicLib.sonicSetNumChannels.argtypes = [_SonicStreamP, ctypes.c_int]


def _getBundledSonicPath() -> str:
	dllName = _BUNDLED_SONIC_32_DLL if _is32BitProcess() else _BUNDLED_SONIC_64_DLL
	return os.path.join(os.path.dirname(__file__), _BUNDLED_SONIC_DIR, dllName)


def _loadBundledSonicModule() -> _BundledSonicModule | None:
	dllPath = _getBundledSonicPath()
	if not os.path.isfile(dllPath):
		return None
	sonicLib = ctypes.CDLL(dllPath)
	_configureSonicLibrary(sonicLib)
	log.info(f"globalSonicPitch: loaded bundled Sonic library; path={dllPath}")
	return _BundledSonicModule(sonicLib, dllPath)


def _getSonicModule():
	global _sonicModule, _sonicUnavailableReason
	if _sonicModule is not None:
		return _sonicModule
	bundledError = None
	try:
		_sonicModule = _loadBundledSonicModule()
		if _sonicModule is not None:
			_sonicUnavailableReason = None
			return _sonicModule
	except Exception as exc:
		bundledError = f"{type(exc).__name__}: {exc}"
		if _isDebugLoggingEnabled():
			log.debugWarning("globalSonicPitch: bundled Sonic is unavailable", exc_info=True)
	try:
		from synthDrivers import _sonic

		_sonic.initialize()
		_sonicModule = _sonic
		_sonicUnavailableReason = None
	except Exception as exc:
		nvdaError = f"{type(exc).__name__}: {exc}"
		if bundledError:
			_sonicUnavailableReason = f"bundled Sonic: {bundledError}; NVDA Sonic: {nvdaError}"
		else:
			_sonicUnavailableReason = f"NVDA Sonic: {nvdaError}"
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


def _is32BitProcess() -> bool:
	return ctypes.sizeof(ctypes.c_void_p) == 4


class _NoDestroySonicStream:
	"""Sonic stream wrapper that avoids unstable native destruction in 32-bit NVDA."""

	def __init__(self, sonicModule: Any, sampleRate: int, channels: int):
		self._sonicModule = sonicModule
		self.channels = channels
		self.stream = sonicModule.sonicLib.sonicCreateStream(sampleRate, channels)
		if not self.stream:
			raise MemoryError()

	def writeShort(self, data: Any, numSamples: int) -> None:
		if not self._sonicModule.sonicLib.sonicWriteShortToStream(self.stream, data, numSamples):
			raise MemoryError()

	def readShort(self) -> Any:
		samples = self.samplesAvailable
		buffer = (ctypes.c_short * (samples * self.channels))()
		self._sonicModule.sonicLib.sonicReadShortFromStream(self.stream, buffer, samples)
		return buffer

	def flush(self) -> None:
		if not self._sonicModule.sonicLib.sonicFlushStream(self.stream):
			raise MemoryError()

	@property
	def samplesAvailable(self) -> int:
		return self._sonicModule.sonicLib.sonicSamplesAvailable(self.stream)

	@property
	def pitch(self) -> float:
		return self._sonicModule.sonicLib.sonicGetPitch(self.stream)

	@pitch.setter
	def pitch(self, value: float) -> None:
		self._sonicModule.sonicLib.sonicSetPitch(self.stream, value)

	@property
	def quality(self) -> int:
		return self._sonicModule.sonicLib.sonicGetQuality(self.stream)

	@quality.setter
	def quality(self, value: int) -> None:
		self._sonicModule.sonicLib.sonicSetQuality(self.stream, _clampQuality(value))


class _DestroySonicStream(_NoDestroySonicStream):
	def __del__(self):
		stream = getattr(self, "stream", None)
		if not stream:
			return
		try:
			self._sonicModule.sonicLib.sonicDestroyStream(stream)
		except Exception:
			pass
		self.stream = None


def _createSonicStream(sonicModule: Any, sampleRate: int, channels: int) -> Any:
	global _noDestroySonicStreamLogged
	if _is32BitProcess():
		if not _noDestroySonicStreamLogged:
			_noDestroySonicStreamLogged = True
			log.info("globalSonicPitch: using no-destroy Sonic stream wrapper for 32-bit NVDA stability")
		return _NoDestroySonicStream(sonicModule, sampleRate, channels)
	if getattr(sonicModule, "isBundled", False):
		return _DestroySonicStream(sonicModule, sampleRate, channels)
	return sonicModule.SonicStream(sampleRate, channels)


def _applySonicQualityToStream(stream: Any, quality: int, source: str, sampleRate: int, channels: int) -> int:
	quality = _clampQuality(quality)
	try:
		stream.quality = quality
	except Exception:
		key = (source, "fallback", quality)
		if key not in _qualityLogKeys:
			_qualityLogKeys.add(key)
			log.debugWarning(
				"globalSonicPitch: failed to set Sonic quality; using stream default fast mode; "
				f"source={source}; requestedQuality={quality}",
				exc_info=True,
			)
		return quality
	key = (source, sampleRate, channels, quality)
	if key not in _qualityLogKeys or _isDebugLoggingEnabled():
		_qualityLogKeys.add(key)
		log.info(
			"globalSonicPitch: applied Sonic quality to new stream; "
			f"source={source}; quality={quality} ({_getQualityLabel(quality)}); "
			f"sampleRate={sampleRate}; channels={channels}",
		)
	return quality


class _SonicStreamProcessor:
	def __init__(self, sonicModule: Any, channels: int, sampleRate: int, pitchPercent: int, quality: int):
		self.channels = channels
		self.sampleRate = sampleRate
		self.stream = _createSonicStream(sonicModule, sampleRate, channels)
		self.pitchPercent = _clampPitch(pitchPercent)
		self.quality = _applySonicQualityToStream(self.stream, quality, "main", sampleRate, channels)
		self.stream.pitch = _pitchPercentToSonicRatio(self.pitchPercent)
		self.isFirstAudioChunk = True
		self.isActive = False
		self._pendingInputFrames = 0
		self._pendingOnDoneCallbacks: list[Callable[..., Any]] = []
		self._lock = threading.RLock()

	def formatMatches(self, channels: int, sampleRate: int, quality: int) -> bool:
		return self.channels == channels and self.sampleRate == sampleRate and self.quality == _clampQuality(quality)

	def isIdleForPitchChange(self) -> bool:
		with self._lock:
			if self.isActive:
				return False
			try:
				return self.isFirstAudioChunk and self.stream.samplesAvailable <= 0
			except Exception:
				return False

	def _readAvailable(self) -> bytes:
		if self.stream.samplesAvailable <= 0:
			return b""
		return _ctypesArrayToBytes(self.stream.readShort())

	def deferOnDone(self, callback: Callable[..., Any] | None) -> None:
		if not callable(callback):
			return
		with self._lock:
			self._pendingOnDoneCallbacks.append(callback)

	def takeOnDone(self, callback: Callable[..., Any] | None = None) -> Callable[..., None] | None:
		with self._lock:
			callbacks = self._pendingOnDoneCallbacks
			self._pendingOnDoneCallbacks = []
		if callable(callback):
			callbacks.append(callback)
		if not callbacks:
			return None

		def _onDone(*args, **kwargs):
			for pendingCallback in callbacks:
				try:
					pendingCallback()
				except Exception:
					log.debugWarning("globalSonicPitch: failed to run deferred WavePlayer callback", exc_info=True)

		return _onDone

	def completePendingOnDone(self) -> None:
		onDone = self.takeOnDone()
		if onDone is not None:
			onDone()

	def process(self, raw: bytes, flush: bool = False) -> bytes:
		with self._lock:
			frameSize = self.channels * 2
			if raw:
				self.isActive = True
				frameCount = len(raw) // frameSize
				self._pendingInputFrames += frameCount
				sampleCount = frameCount * self.channels
				inputSamples = (ctypes.c_short * sampleCount).from_buffer_copy(raw)
				self.stream.writeShort(inputSamples, frameCount)
			if flush:
				self.stream.flush()
				self.isFirstAudioChunk = False
			elif (
				self.isFirstAudioChunk
				and self.stream.samplesAvailable < self.sampleRate * _FIRST_AUDIO_CHUNK_MIN_DURATION_MS // 1000
				and self._pendingInputFrames > self.sampleRate * _SHORT_AUDIO_CHUNK_MAX_DURATION_MS // 1000
			):
				return b""
			self.isFirstAudioChunk = False
			processed = self._readAvailable()
			if processed or flush:
				self._pendingInputFrames = 0
			return processed

	def finish(self) -> bytes:
		try:
			return self.process(b"", flush=True)
		finally:
			with self._lock:
				self.isFirstAudioChunk = True
				self.isActive = False
				self._pendingInputFrames = 0


def _getPlayerProcessorKey(player: nvwave.WavePlayer) -> int:
	return id(player)


def _finishProcessorSafely(processor: "_SonicStreamProcessor" | None) -> bytes:
	if processor is None:
		return b""
	try:
		return processor.finish()
	except Exception:
		log.debugWarning("globalSonicPitch: failed to finish retired Sonic stream", exc_info=True)
		return b""


def _finishPlayerProcessor(player: nvwave.WavePlayer) -> tuple[bytes, Callable[..., None] | None]:
	with _playerProcessorsLock:
		processor = _playerProcessors.get(_getPlayerProcessorKey(player))
	if processor is None:
		return b"", None
	return _finishProcessorSafely(processor), processor.takeOnDone()


def _resetPlayerProcessor(player: nvwave.WavePlayer) -> None:
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		processor = _playerProcessors.pop(processorKey, None)
		_playerUtterancePitches.pop(processorKey, None)
		_playerUtteranceQualities.pop(processorKey, None)
	if processor is not None:
		processor.completePendingOnDone()


def _resetAllPlayerProcessors() -> None:
	with _playerProcessorsLock:
		processors = list(_playerProcessors.values())
		_playerProcessors.clear()
		_playerUtterancePitches.clear()
		_playerUtteranceQualities.clear()
	for processor in processors:
		_finishProcessorSafely(processor)
		processor.completePendingOnDone()


def _getOrCreatePlayerUtterancePitch(player: nvwave.WavePlayer, pitch: int) -> int:
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		if processorKey not in _playerUtterancePitches:
			_playerUtterancePitches[processorKey] = _clampPitch(pitch)
		return _playerUtterancePitches[processorKey]


def _getOrCreatePlayerUtteranceQuality(player: nvwave.WavePlayer, quality: int) -> int:
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		if processorKey not in _playerUtteranceQualities:
			_playerUtteranceQualities[processorKey] = _clampQuality(quality)
		return _playerUtteranceQualities[processorKey]


def _clearPlayerUtterancePitch(player: nvwave.WavePlayer) -> None:
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		_playerUtterancePitches.pop(processorKey, None)
		_playerUtteranceQualities.pop(processorKey, None)


def _clearIdlePlayerUtterancePitches() -> None:
	with _playerProcessorsLock:
		for processorKey in list(_playerUtterancePitches):
			processor = _playerProcessors.get(processorKey)
			if processor is None or processor.isIdleForPitchChange():
				_playerUtterancePitches.pop(processorKey, None)
				_playerUtteranceQualities.pop(processorKey, None)
		for processorKey in list(_playerUtteranceQualities):
			if processorKey not in _playerUtterancePitches:
				_playerUtteranceQualities.pop(processorKey, None)


def _logDeferredPitchOnce(synthName: str, activePitch: int, pendingPitch: int) -> None:
	key = (synthName, activePitch, pendingPitch)
	if key in _deferredPitchLogKeys and not _isDebugLoggingEnabled():
		return
	_deferredPitchLogKeys.add(key)
	log.info(
		"globalSonicPitch: deferring Sonic pitch change until next utterance; "
		f"synth={synthName or 'unknown'}; activePitch={activePitch}; pendingPitch={pendingPitch}",
	)


def _logDeferredQualityOnce(synthName: str, activeQuality: int, pendingQuality: int) -> None:
	key = ("quality", synthName, activeQuality, pendingQuality)
	if key in _deferredPitchLogKeys and not _isDebugLoggingEnabled():
		return
	_deferredPitchLogKeys.add(key)
	log.info(
		"globalSonicPitch: deferring Sonic quality change until next utterance; "
		f"synth={synthName or 'unknown'}; activeQuality={activeQuality} ({_getQualityLabel(activeQuality)}); "
		f"pendingQuality={pendingQuality} ({_getQualityLabel(pendingQuality)})",
	)


def _getOrCreatePlayerProcessor(
	player: nvwave.WavePlayer,
	channels: int,
	sampleRate: int,
	pitchPercent: int,
	quality: int,
) -> tuple[_SonicStreamProcessor | None, bytes]:
	retiredProcessor = None
	with _playerProcessorsLock:
		processorKey = _getPlayerProcessorKey(player)
		processor = _playerProcessors.get(processorKey)
		if processor is not None:
			if (
				processor.formatMatches(channels, sampleRate, quality)
				and processor.pitchPercent == _clampPitch(pitchPercent)
			):
				return processor, b""
			retiredProcessor = _playerProcessors.pop(processorKey, None)
			log.info(
				"globalSonicPitch: recreating Sonic processor for new parameters; "
				f"pitch={_clampPitch(pitchPercent)}; quality={_clampQuality(quality)} ({_getQualityLabel(quality)})",
			)
		sonic = _getSonicModule()
		if sonic is None:
			return None, b""
		processor = _SonicStreamProcessor(sonic, channels, sampleRate, pitchPercent, quality)
		_playerProcessors[processorKey] = processor
	tail = _finishProcessorSafely(retiredProcessor)
	if retiredProcessor is not None:
		retiredProcessor.completePendingOnDone()
	return processor, tail


def _processPcm16Block(
	player: nvwave.WavePlayer,
	raw: bytes,
	channels: int,
	sampleRate: int,
	pitchPercent: int,
	quality: int,
) -> tuple[bytes, _SonicStreamProcessor] | None:
	frameSize = channels * 2
	if len(raw) < frameSize or len(raw) % frameSize:
		return None
	processor, tail = _getOrCreatePlayerProcessor(player, channels, sampleRate, pitchPercent, quality)
	if processor is None:
		return None
	processed = processor.process(raw)
	return (tail + processed, processor)


def _logProcessedOnce(
	synthName: str,
	channels: int,
	sampleRate: int,
	pitch: int,
	quality: int,
	inSize: int,
	outSize: int,
) -> None:
	key = (synthName, channels, sampleRate, pitch, quality)
	if key in _processingLogKeys and not _isDebugLoggingEnabled():
		return
	_processingLogKeys.add(key)
	log.info(
		"globalSonicPitch: processed speech audio; "
		f"synth={synthName or 'unknown'}; pitch={pitch}; "
		f"quality={quality} ({_getQualityLabel(quality)}); "
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
			tail, pendingOnDone = _finishPlayerProcessor(self)
			if tail:
				originalFeed(self, tail, len(tail), pendingOnDone)
			elif pendingOnDone is not None:
				originalFeed(self, None, 0, pendingOnDone)
			_clearPlayerUtterancePitch(self)
			return originalFeed(self, data, size, onDone)
		processingContext = _getProcessingContext(self, len(raw)) if raw is not None else None
		if raw is not None and processingContext is not None:
			synthName, pitch, quality = processingContext
			waveFormat = _getWaveFormat(self)
			if waveFormat is not None:
				channels, sampleRate, bitsPerSample = waveFormat
				if bitsPerSample == 16:
					processedResult = _processPcm16Block(self, raw, channels, sampleRate, pitch, quality)
					if processedResult is not None:
						processed, processor = processedResult
						_logProcessedOnce(
							synthName,
							channels,
							sampleRate,
							pitch,
							quality,
							len(raw),
							len(processed),
						)
						if processed:
							return originalFeed(self, processed, len(processed), processor.takeOnDone(onDone))
						if onDone is not None:
							processor.deferOnDone(onDone)
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
		tail, onDone = _finishPlayerProcessor(player)
		if tail:
			originalFeed(player, tail, len(tail), onDone)
		elif onDone is not None:
			originalFeed(player, None, 0, onDone)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to flush Sonic stream tail", exc_info=True)
		_resetPlayerProcessor(player)
	finally:
		_clearPlayerUtterancePitch(player)


def _patchedIdle(self, *args, **kwargs):
	_feedProcessorTail(self)
	originalIdle = getattr(nvwave.WavePlayer, _ORIGINAL_IDLE_ATTR)
	return originalIdle(self, *args, **kwargs)


def _patchedStop(self, *args, **kwargs):
	_resetPlayerProcessor(self)
	_clearPlayerUtterancePitch(self)
	originalStop = getattr(nvwave.WavePlayer, _ORIGINAL_STOP_ATTR)
	return originalStop(self, *args, **kwargs)


def _patchedClose(self, *args, **kwargs):
	_resetPlayerProcessor(self)
	_clearPlayerUtterancePitch(self)
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
			# Translators: Name of the add-on pitch setting in NVDA Voice settings.
			_("Sonic pitch"),
			availableInSettingsRing=True,
			defaultVal=NEUTRAL_PITCH,
			minVal=0,
			maxVal=100,
			minStep=1,
			normalStep=5,
			largeStep=10,
			# Translators: Display name of the add-on pitch setting in the synth settings ring.
			displayName=_("Sonic pitch"),
			useConfig=False,
		)
	except TypeError:
		try:
			_sonicPitchDriverSetting = NumericDriverSetting(
				SONIC_PITCH_SETTING_ID,
				# Translators: Name of the add-on pitch setting in NVDA Voice settings.
				_("Sonic pitch"),
				True,
				NEUTRAL_PITCH,
				0,
				100,
				1,
				5,
				10,
				# Translators: Display name of the add-on pitch setting in the synth settings ring.
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


def _settingId(setting: Any) -> str:
	return str(getattr(setting, "id", "") or "")


def _hasSonicPitchSetting(settings: Any) -> bool:
	try:
		return any(_settingId(setting) == SONIC_PITCH_SETTING_ID for setting in settings)
	except Exception:
		return False


def _withoutSonicPitchSettings(settings: Any) -> tuple[Any, ...]:
	try:
		return tuple(setting for setting in settings if _settingId(setting) not in SONIC_PITCH_HOST_SETTING_IDS)
	except Exception:
		return tuple(settings or ())


def _stripSonicPitchSetting(synth: Any | None) -> None:
	if synth is None:
		return
	try:
		supportedSettings = tuple(getattr(synth, "supportedSettings", ()))
		filteredSettings = _withoutSonicPitchSettings(supportedSettings)
		if len(filteredSettings) == len(supportedSettings):
			return
		synth.supportedSettings = filteredSettings
		_updateSynthSettingsRing(synth)
		log.info(f"globalSonicPitch: hid Sonic pitch voice setting; synth={_getSynthName(synth)}")
	except Exception:
		log.debugWarning("globalSonicPitch: failed to hide Sonic pitch voice setting", exc_info=True)


def _patchedGetSonicPitchSetting(self):
	pitch = _getSonicPitchForSynth(self)
	if bool(_getConfigValue("enabled", False)):
		_applyRuntimeSonicPitch(self, pitch)
	return pitch


def _patchedSetSonicPitchSetting(self, value):
	synthName = _getSynthName(self)
	if _setVoiceDialogPendingSonicPitch(self, value):
		return None
	pitch = _setSonicPitchForSynth(self, value)
	if pitch is None:
		return None
	_applyRuntimeSonicPitch(self, pitch)
	log.info(
		"globalSonicPitch: captured Sonic pitch setting; "
		f"synth={synthName}; key={_getSonicPitchStorageKey(self)}; sonicPitch={pitch}",
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


def _refreshSonicPitchAfterVoiceChange(synth: Any | None) -> None:
	if synth is None or not bool(_getConfigValue("enabled", False)):
		return
	synthName = _getSynthName(synth)
	if not _isGlobalAudioSupportedSynth(synthName):
		return
	try:
		pitch = _getSonicPitchForSynth(synth)
		_clearIdlePlayerUtterancePitches()
		_applyRuntimeSonicPitch(synth, pitch)
		log.info(
			"globalSonicPitch: refreshed Sonic pitch after voice change; "
			f"synth={synthName}; key={_getSonicPitchStorageKey(synth)}; sonicPitch={pitch}",
		)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to refresh Sonic pitch after voice change", exc_info=True)


def _patchSynthVoiceProperty(synth: Any) -> None:
	synthClass = synth.__class__
	if synthClass in _voiceClassPatches:
		return
	originalValue = getattr(synthClass, "voice", _missingClassAttr)
	if not isinstance(originalValue, property) or originalValue.fset is None:
		return

	def _getVoice(instance):
		if originalValue.fget is None:
			raise AttributeError("voice")
		return originalValue.fget(instance)

	def _setVoice(instance, value):
		originalValue.fset(instance, value)
		_refreshSonicPitchAfterVoiceChange(instance)

	_voiceClassPatches[synthClass] = originalValue
	setattr(
		synthClass,
		"voice",
		property(
			_getVoice,
			_setVoice,
			originalValue.fdel,
			originalValue.__doc__,
		),
	)


def _restoreSynthVoiceProperty(synthClass: type) -> None:
	if synthClass not in _voiceClassPatches:
		return
	originalValue = _voiceClassPatches.pop(synthClass)
	try:
		setattr(synthClass, "voice", originalValue)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to restore synth voice class property", exc_info=True)


def _restoreAllSynthVoiceProperties() -> None:
	for synthClass in list(_voiceClassPatches):
		_restoreSynthVoiceProperty(synthClass)


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


def _logVoiceSettingOnce(synth: Any, value: int | None = None) -> None:
	synthName = _getSynthName(synth)
	key = _getSonicPitchStorageKey(synth) or synthName
	if key in _voiceSettingLogKeys and not _isDebugLoggingEnabled():
		return
	_voiceSettingLogKeys.add(key)
	log.info(
		"globalSonicPitch: added Sonic pitch voice setting; "
		f"synth={synthName or 'unknown'}"
		+ (f"; key={key}" if key else "")
		+ (f"; value={value}" if value is not None else ""),
	)


def _patchSynthSonicPitchSetting(synth: Any | None) -> None:
	if synth is None:
		return
	if not bool(_getConfigValue("enabled", False)):
		_unpatchSynthSonicPitchSetting(synth)
		return
	synthName = _getSynthName(synth)
	if not _isGlobalAudioSupportedSynth(synthName):
		return
	if _isRemoteSapi32Synth(synthName):
		_installSapi32HostDriverPatch()
		if not _remoteSapi32SupportsSonicPitch(synth):
			_stripSonicPitchSetting(synth)
			_requestRemoteSapi32SynthReload()
			return
	setting = _getSonicPitchDriverSetting()
	if setting is None:
		return
	try:
		_patchSonicPitchClassProperty(synth)
		_patchSynthVoiceProperty(synth)
		supportedSettings = _withoutSonicPitchSettings(tuple(getattr(synth, "supportedSettings", ())))
		if not getattr(synth, _SONIC_PITCH_SETTING_PATCHED_ATTR, False):
			setattr(synth, _ORIGINAL_SUPPORTED_SETTINGS_ATTR, supportedSettings)
			synth.supportedSettings = supportedSettings + (setting,)
			setattr(synth, _SONIC_PITCH_SETTING_PATCHED_ATTR, True)
		elif not _hasSonicPitchSetting(supportedSettings):
			synth.supportedSettings = supportedSettings + (setting,)
		settingValue = _getReadableSonicPitchSettingValue(synth)
		if settingValue is None:
			_unpatchSynthSonicPitchSetting(synth)
			return
		_applyRuntimeSonicPitch(synth, settingValue)
		_ensureSynthRingSettingsSelectorIncludesSonicPitch()
		_updateSynthSettingsRing(synth)
		_logVoiceSettingOnce(synth, settingValue)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to add Sonic pitch voice setting", exc_info=True)


def _unpatchSynthSonicPitchSetting(synth: Any | None) -> None:
	if synth is None:
		return
	if not getattr(synth, _SONIC_PITCH_SETTING_PATCHED_ATTR, False):
		if _isRemoteSapi32Synth(_getSynthName(synth)):
			_stripSonicPitchSetting(synth)
		return
	try:
		originalSupportedSettings = getattr(synth, _ORIGINAL_SUPPORTED_SETTINGS_ATTR, None)
		if originalSupportedSettings is not None:
			synth.supportedSettings = _withoutSonicPitchSettings(originalSupportedSettings)
		for attr in (
			_ORIGINAL_SUPPORTED_SETTINGS_ATTR,
			_SONIC_PITCH_SETTING_PATCHED_ATTR,
		):
			try:
				delattr(synth, attr)
			except Exception:
				pass
		_restoreSonicPitchClassProperty(synth.__class__)
		_restoreSynthVoiceProperty(synth.__class__)
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
		_restoreAllSynthVoiceProperties()


def _safePatchCurrentSynthPitch() -> None:
	try:
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
	_resetAllPlayerProcessors()
	_runtimeSonicPitchByKey.clear()
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
			_safePatchCurrentSynthPitch()


def _patchedVoicePanelMakeSettings(self, *args, **kwargs):
	_ensureVoiceDialogSession(self)
	originalMakeSettings = getattr(settingsDialogs.VoiceSettingsPanel, _ORIGINAL_VOICE_PANEL_MAKE_SETTINGS_ATTR)
	return originalMakeSettings(self, *args, **kwargs)


def _patchedVoicePanelOnSave(self, *args, **kwargs):
	originalOnSave = getattr(settingsDialogs.VoiceSettingsPanel, _ORIGINAL_VOICE_PANEL_ON_SAVE_ATTR)
	result = originalOnSave(self, *args, **kwargs)
	panelId = id(self)
	try:
		_commitVoiceDialogSession(panelId)
	except Exception:
		log.debugWarning("globalSonicPitch: failed to commit Voice settings Sonic pitch transaction", exc_info=True)
	finally:
		_voiceDialogSessions.pop(panelId, None)
	return result


def _patchedVoicePanelOnDiscard(self, *args, **kwargs):
	originalOnDiscard = getattr(settingsDialogs.VoiceSettingsPanel, _ORIGINAL_VOICE_PANEL_ON_DISCARD_ATTR)
	try:
		return originalOnDiscard(self, *args, **kwargs)
	finally:
		panelId = id(self)
		try:
			_restoreVoiceDialogSession(panelId)
		except Exception:
			log.debugWarning("globalSonicPitch: failed to discard Voice settings Sonic pitch transaction", exc_info=True)
		finally:
			_voiceDialogSessions.pop(panelId, None)


def installVoiceSettingsDialogHook() -> None:
	voicePanelClass = getattr(settingsDialogs, "VoiceSettingsPanel", None)
	if voicePanelClass is None:
		return
	if getattr(voicePanelClass, _VOICE_PANEL_PATCHED_ATTR, False):
		return
	setattr(voicePanelClass, _ORIGINAL_VOICE_PANEL_MAKE_SETTINGS_ATTR, voicePanelClass.makeSettings)
	setattr(voicePanelClass, _ORIGINAL_VOICE_PANEL_ON_SAVE_ATTR, voicePanelClass.onSave)
	setattr(voicePanelClass, _ORIGINAL_VOICE_PANEL_ON_DISCARD_ATTR, voicePanelClass.onDiscard)
	voicePanelClass.makeSettings = _patchedVoicePanelMakeSettings
	voicePanelClass.onSave = _patchedVoicePanelOnSave
	voicePanelClass.onDiscard = _patchedVoicePanelOnDiscard
	setattr(voicePanelClass, _VOICE_PANEL_PATCHED_ATTR, True)
	log.info("globalSonicPitch: installed Voice settings Sonic pitch transaction hook")


def uninstallVoiceSettingsDialogHook() -> None:
	voicePanelClass = getattr(settingsDialogs, "VoiceSettingsPanel", None)
	if voicePanelClass is None:
		return
	for panelId in list(_voiceDialogSessions):
		try:
			_restoreVoiceDialogSession(panelId)
		except Exception:
			log.debugWarning("globalSonicPitch: failed to restore Voice settings while uninstalling hook", exc_info=True)
		finally:
			_voiceDialogSessions.pop(panelId, None)
	if not getattr(voicePanelClass, _VOICE_PANEL_PATCHED_ATTR, False):
		return
	originalMakeSettings = getattr(voicePanelClass, _ORIGINAL_VOICE_PANEL_MAKE_SETTINGS_ATTR, None)
	originalOnSave = getattr(voicePanelClass, _ORIGINAL_VOICE_PANEL_ON_SAVE_ATTR, None)
	originalOnDiscard = getattr(voicePanelClass, _ORIGINAL_VOICE_PANEL_ON_DISCARD_ATTR, None)
	if originalMakeSettings is not None and voicePanelClass.makeSettings is _patchedVoicePanelMakeSettings:
		voicePanelClass.makeSettings = originalMakeSettings
	if originalOnSave is not None and voicePanelClass.onSave is _patchedVoicePanelOnSave:
		voicePanelClass.onSave = originalOnSave
	if originalOnDiscard is not None and voicePanelClass.onDiscard is _patchedVoicePanelOnDiscard:
		voicePanelClass.onDiscard = originalOnDiscard
	for attr in (
		_ORIGINAL_VOICE_PANEL_MAKE_SETTINGS_ATTR,
		_ORIGINAL_VOICE_PANEL_ON_SAVE_ATTR,
		_ORIGINAL_VOICE_PANEL_ON_DISCARD_ATTR,
	):
		try:
			delattr(voicePanelClass, attr)
		except Exception:
			pass
	setattr(voicePanelClass, _VOICE_PANEL_PATCHED_ATTR, False)
	log.info("globalSonicPitch: removed Voice settings Sonic pitch transaction hook")


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
	_runtimeSonicPitchByKey.clear()
	_restoreAllSonicPitchClassProperties()
	_restoreAllSynthVoiceProperties()
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
	# Translators: Title of the add-on settings panel in NVDA preferences.
	title = _("Global Sonic Pitch")

	def makeSettings(self, settingsSizer):
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		conf = config.conf[CONFIG_SECTION]
		self.enableCheckbox = helper.addItem(
			# Translators: Checkbox enabling or disabling Sonic pitch processing.
			wx.CheckBox(self, label=_("Enable global Sonic pitch")),
		)
		self.enableCheckbox.SetValue(bool(conf["enabled"]))
		self.extendedRangeCheckbox = helper.addItem(
			# Translators: Checkbox increasing the Sonic pitch control range from 6 to 20 semitones.
			wx.CheckBox(self, label=_("Increase Sonic pitch range to 20 semitones")),
		)
		self.extendedRangeCheckbox.SetValue(bool(conf[EXTENDED_PITCH_RANGE_CONFIG_KEY]))
		self.qualityCheckbox = helper.addItem(
			# Translators: Checkbox enabling Sonic's better-quality processing mode.
			wx.CheckBox(self, label=_("Use better-quality Sonic processing")),
		)
		self.qualityCheckbox.SetValue(_getSonicQuality() == 1)
		self.qualityDescription = helper.addItem(
			wx.StaticText(
				self,
				# Translators: Help text for Sonic's better-quality processing mode.
				label=_(
					"Better quality may improve Sonic pitch processing for some voices, but can use more CPU. "
					"It does not change the pitch range."
				),
			),
		)
		self.debugCheckbox = helper.addItem(
			# Translators: Checkbox enabling debug log messages for this add-on.
			wx.CheckBox(self, label=_("Enable debug logging")),
		)
		self.debugCheckbox.SetValue(bool(conf["debugLogging"]))
		self.supportButton = helper.addItem(
			# Translators: Button opening the author's support page.
			wx.Button(self, label=_("Support the author")),
		)
		self.enableCheckbox.Bind(wx.EVT_CHECKBOX, self._updateControlState)
		self.supportButton.Bind(wx.EVT_BUTTON, self._onSupport)
		self._updateControlState()

	def _updateControlState(self, event=None):
		enabled = self.enableCheckbox.IsChecked()
		self.extendedRangeCheckbox.Enable(enabled)
		self.qualityCheckbox.Enable(enabled)
		self.qualityDescription.Enable(enabled)
		self.debugCheckbox.Enable(enabled)

	def _onSupport(self, event):
		_openSupportPage()

	def onSave(self):
		_setConfigValue("debugLogging", self.debugCheckbox.IsChecked())
		_setSonicQuality(1 if self.qualityCheckbox.IsChecked() else 0)
		_setExtendedPitchRangeEnabled(self.extendedRangeCheckbox.IsChecked())
		_setGlobalEnabled(self.enableCheckbox.IsChecked())
		config.conf.save()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Translators: Input Gestures category for this add-on.
	scriptCategory = _("Global Sonic Pitch")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		_ensureConfigSpec()
		_installSapi32HostDriverPatch()
		installWavePlayerHook()
		installSynthPitchHook()
		installVoiceSettingsDialogHook()
		if GlobalSonicPitchSettingsPanel not in NVDASettingsDialog.categoryClasses:
			NVDASettingsDialog.categoryClasses.append(GlobalSonicPitchSettingsPanel)

	def terminate(self):
		try:
			if GlobalSonicPitchSettingsPanel in NVDASettingsDialog.categoryClasses:
				NVDASettingsDialog.categoryClasses.remove(GlobalSonicPitchSettingsPanel)
		finally:
			uninstallVoiceSettingsDialogHook()
			uninstallSynthPitchHook()
			uninstallWavePlayerHook()
			_restoreSapi32HostDriverPatch()
			super().terminate()

	@script(
		# Translators: Input gesture description for toggling the add-on.
		description=_("Toggle global Sonic pitch"),
		category=scriptCategory,
	)
	def script_toggleGlobalSonicPitch(self, gesture):
		enabled = not bool(_getConfigValue("enabled", False))
		_setGlobalEnabled(enabled)
		config.conf.save()
		if ui is not None:
			# Translators: Spoken status when global Sonic pitch has been enabled or disabled.
			ui.message(_("Global Sonic pitch on") if enabled else _("Global Sonic pitch off"))

	@script(
		# Translators: Input gesture description for reporting the add-on status.
		description=_("Report global Sonic pitch status"),
		category=scriptCategory,
	)
	def script_reportGlobalSonicPitch(self, gesture):
		enabled = bool(_getConfigValue("enabled", False))
		synth = _getCurrentSynth()
		synthName = _getSynthName(synth)
		if enabled and _isGlobalAudioSupportedSynth(synthName):
			pitch = _getSonicPitchForSynth(synth)
			# Translators: Spoken status. {synth} is a synthesizer name, {pitch} is a number from 0 to 100.
			message = _("Global Sonic pitch on, {synth} Sonic pitch {pitch}").format(
				synth=synthName or _getCurrentSynthDisplayName(),
				pitch=pitch,
			)
		elif enabled:
			# Translators: Spoken status when the current synth cannot be processed by Sonic. {synth} is a synth name.
			message = _("Global Sonic pitch on, Sonic pitch is unavailable for {synth}").format(
				synth=synthName or _getCurrentSynthDisplayName(),
			)
		else:
			# Translators: Spoken status when global Sonic pitch is disabled.
			message = _("Global Sonic pitch off")
		if _sonicUnavailableReason:
			message = f"{message}. Sonic unavailable: {_sonicUnavailableReason}"
		if ui is not None:
			ui.message(message)

	@script(
		# Translators: Input gesture description for opening the author's support page.
		description=_("Open support page"),
		category=scriptCategory,
	)
	def script_openSupportPage(self, gesture):
		_openSupportPage()

	@script(
		# Translators: Input gesture description for increasing Sonic pitch for the current synth.
		description=_("Increase Sonic pitch for the current synthesizer"),
		category=scriptCategory,
	)
	def script_increaseGlobalSonicPitch(self, gesture):
		pitch = _changeCurrentSynthSonicPitch(5)
		config.conf.save()
		if ui is not None:
			if pitch is None:
				# Translators: Spoken message when Sonic pitch is unavailable. {synth} is a synth name.
				ui.message(_("Sonic pitch is unavailable for {synth}").format(synth=_getCurrentSynthDisplayName()))
			else:
				# Translators: Spoken message after changing Sonic pitch. {pitch} is a number from 0 to 100.
				ui.message(_("Sonic pitch {pitch}").format(pitch=pitch))

	@script(
		# Translators: Input gesture description for decreasing Sonic pitch for the current synth.
		description=_("Decrease Sonic pitch for the current synthesizer"),
		category=scriptCategory,
	)
	def script_decreaseGlobalSonicPitch(self, gesture):
		pitch = _changeCurrentSynthSonicPitch(-5)
		config.conf.save()
		if ui is not None:
			if pitch is None:
				# Translators: Spoken message when Sonic pitch is unavailable. {synth} is a synth name.
				ui.message(_("Sonic pitch is unavailable for {synth}").format(synth=_getCurrentSynthDisplayName()))
			else:
				# Translators: Spoken message after changing Sonic pitch. {pitch} is a number from 0 to 100.
				ui.message(_("Sonic pitch {pitch}").format(pitch=pitch))

	@script(
		# Translators: Input gesture description for resetting Sonic pitch for the current synth.
		description=_("Reset Sonic pitch for the current synthesizer"),
		category=scriptCategory,
	)
	def script_resetGlobalSonicPitch(self, gesture):
		pitch = _setCurrentSynthSonicPitch(NEUTRAL_PITCH)
		config.conf.save()
		if ui is not None:
			if pitch is None:
				# Translators: Spoken message when Sonic pitch is unavailable. {synth} is a synth name.
				ui.message(_("Sonic pitch is unavailable for {synth}").format(synth=_getCurrentSynthDisplayName()))
			else:
				# Translators: Spoken message after changing Sonic pitch. {pitch} is a number from 0 to 100.
				ui.message(_("Sonic pitch {pitch}").format(pitch=pitch))
