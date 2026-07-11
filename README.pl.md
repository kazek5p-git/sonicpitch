# Global Sonic Pitch

Global Sonic Pitch to dodatek do NVDA, który przejmuje normalne ustawienie
wysokości mowy NVDA i stosuje je przez przetwarzanie audio Sonic. Dodatek działa
globalnie dla syntezatorów, których audio mowy przechodzi przez główny proces
NVDA.

Dokumentacja angielska: [README.md](README.md)

## Najważniejsze Informacje

- Dodatek nie dodaje nowych syntezatorów do okna wyboru syntezatora.
- Po włączeniu trybu globalnego zwykły suwak `Wysokość` NVDA steruje Sonic.
- Natywna wysokość aktywnego syntezatora jest utrzymywana neutralnie na `50`,
  jeśli dany sterownik pozwala ją przejąć.
- Audio mowy jest filtrowane przez Sonic w głównym `WavePlayer` NVDA.
- Standardowy `sapi5_32` na 64-bitowym NVDA jest celowo pomijany, bo działa w
  osobnym 32-bitowym hoście.

## Dla Kogo Jest Ten Dodatek

Użyj Global Sonic Pitch, jeśli chcesz mieć jedną metodę zmiany wysokości mowy
dla różnych syntezatorów NVDA, szczególnie wtedy, gdy natywna regulacja
wysokości danego głosu brzmi gorzej albo zachowuje się niespójnie.

Dodatek był testowany lokalnie z:

- RHVoice;
- eSpeak NG;
- OneCore;
- SAPI5 64-bit;
- standardowym SAPI5 32-bit jako ścieżką ładowaną, ale nieprzetwarzaną globalnie.

## Wymagania

- NVDA 2025.1 lub nowsze.
- Windows.
- Nowoczesna ścieżka audio NVDA z dostępnym Sonic.
- Syntezator wysyłający 16-bitowe PCM mowy przez główny `WavePlayer` NVDA.

Ostatnio testowana lokalnie konfiguracja: NVDA 2026.2 beta, 64-bit.

## Instalacja

1. Pobierz najnowszy plik `.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. Jeśli masz stary dodatek `SAPI5 Sonic Pitch` / `sapi5SonicPitch`, usuń go
   przed instalacją i zrestartuj NVDA.
3. Otwórz pobrany plik `globalSonicPitch-<wersja>.nvda-addon` w NVDA.
4. Potwierdź instalację.
5. Zrestartuj NVDA.
6. Otwórz ustawienia NVDA i przejdź do kategorii `Global Sonic Pitch`.
7. Włącz opcję `Enable global Sonic pitch`.

## Szybki Start

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore albo
   SAPI5 64-bit.
2. W ustawieniach NVDA włącz `Global Sonic Pitch`.
3. Zmieniaj wysokość normalnym ustawieniem głosu NVDA.
4. Ustawienie `50` traktuj jako neutralne.
5. Jeśli coś brzmi źle, wróć do `50` albo wyłącz globalny tryb w panelu dodatku.

## Ustawienia

Panel `Global Sonic Pitch` zawiera:

- `Enable global Sonic pitch` - włącza lub wyłącza globalne przejęcie wysokości.
- `Sonic pitch` - ustawia wartość wysokości używaną przez Sonic.
- `Enable debug logging` - dodaje szczegółowe wpisy do logu NVDA.

Po włączeniu dodatku normalne ustawienie `Wysokość` w pierścieniu ustawień
syntezatora zmienia tę samą wartość co suwak `Sonic pitch`.

## Jak Działa Wysokość

NVDA używa skali od `0` do `100`.

- `50` jest neutralne.
- `0..49` obniża głos.
- `51..100` podwyższa głos.
- Pełny zakres odpowiada mniej więcej `-6..+6` półtonom.
- Współczynnik Sonic jest ograniczony do `0.70..1.45`, żeby uniknąć skrajnych
  zniekształceń.

Gdy globalny tryb jest włączony, dodatek przechwytuje zmianę wysokości, zapisuje
ją w swojej konfiguracji, a natywną wysokość syntezatora ustawia na `50`. Dzięki
temu nie dochodzi do podwójnej zmiany wysokości: raz przez syntezator i drugi
raz przez Sonic.

## Zgodność Syntezatorów

| Syntezator | Oczekiwane działanie |
| --- | --- |
| RHVoice | Obsługiwany, jeśli audio trafia do głównego `WavePlayer`. |
| eSpeak NG | Obsługiwany w głównym procesie NVDA. |
| OneCore | Obsługiwany w głównym procesie NVDA. |
| SAPI5 64-bit | Obsługiwany, gdy używa ścieżki audio NVDA. |
| SAPI5 32-bit na 64-bitowym NVDA | Ładuje się normalnie, ale globalny Sonic go nie przetwarza. |
| Dodatkowe syntezatory | Mogą działać, jeśli wysyłają 16-bitowe PCM przez główny `WavePlayer`. |

## Ważne Ograniczenie SAPI5 32-bit

Standardowy `sapi5_32` działa na 64-bitowym NVDA przez osobny 32-bitowy host
syntezatorów. Globalny plugin dodatku jest ładowany w głównym procesie NVDA, a
nie w tym hoście. Z tego powodu dodatek nie przejmuje wysokości dla `sapi5_32` i
nie filtruje jego audio przez Sonic.

To zachowanie jest celowe. Dzięki temu standardowy `sapi5_32` nadal ładuje się
normalnie i nie jest neutralizowany bez faktycznego przetwarzania Sonic.

## Migracja Ze Starego SAPI5 Sonic Pitch

Wersje 0.1.x i 0.2.x dodatku używały nazwy `sapi5SonicPitch` i dodawały własne
syntezatory SAPI5 Sonic Pitch. Aktualna wersja działa inaczej:

- nowy identyfikator dodatku to `globalSonicPitch`;
- dodatek nie dodaje żadnych pozycji do okna wyboru syntezatora;
- stary folder `sapi5SonicPitch` powinien być usunięty;
- ustawienia z eksperymentalnej sekcji `[sapi5SonicPitchGlobal]` są migrowane
  przy starcie.

Jeśli w wyborze syntezatora nadal widzisz `SAPI5 32-bit Sonic Pitch` albo
`SAPI5 64-bit Sonic Pitch`, stary dodatek nadal jest zainstalowany.

## Jak Sprawdzić Czy Dodatek Działa

1. Włącz `Enable debug logging` w panelu `Global Sonic Pitch`.
2. Zrestartuj NVDA.
3. Ustaw syntezator na RHVoice, eSpeak, OneCore albo SAPI5 64-bit.
4. Ustaw wysokość inną niż `50`, na przykład `75`.
5. Otwórz aktualny log NVDA: `%TEMP%\nvda.log`.

W logu powinny pojawić się wpisy podobne do:

```text
globalSonicPitch: installed WavePlayer speech feed hook
globalSonicPitch: installed synth pitch takeover hook
globalSonicPitch: pitch takeover active; synth=RHVoice; sonicPitch=75; nativePitch=50
globalSonicPitch: processed speech audio; synth=RHVoice; pitch=75
```

Jeśli wybrany jest `sapi5_32`, oczekiwany wpis to:

```text
globalSonicPitch: pitch takeover not available for synth=sapi5_32
```

## Rozwiązywanie Problemów

### Wysokość się nie zmienia

Sprawdź, czy globalny tryb jest włączony i czy wartość pitch nie wynosi `50`.
Sprawdź też log NVDA pod kątem `processed speech audio`. Jeśli tego wpisu nie
ma, audio danego syntezatora prawdopodobnie nie przechodzi przez główny
`WavePlayer`.

### Syntezator zmienia swoją natywną wysokość

Włącz debug logging i poszukaj `pitch takeover active`. Jeśli wpisu nie ma,
dodatek nie mógł przejąć ustawienia pitch tego sterownika. W takim przypadku
Sonic może nadal przetwarzać audio, ale natywna wysokość syntezatora nie musi
być zablokowana.

### Słychać drobne przerwy albo artefakty

Od wersji 0.3.1 dodatek utrzymuje ciągły strumień Sonic dla aktywnego
`WavePlayer` i nie wykonuje `flush()` po każdym małym bloku audio. Jeśli nadal
słychać przerwy, sprawdź czy nie masz bardzo dużego obciążenia CPU, bardzo
agresywnego pitch oraz czy problem występuje na więcej niż jednym syntezatorze.

### Standardowy SAPI5 32-bit nie ma globalnego Sonic pitch

To jest znane ograniczenie. `sapi5_32` działa w osobnym hoście i nie jest
globalnie filtrowany przez ten dodatek.

### Stare syntezatory Sonic Pitch nadal są na liście

Usuń stary dodatek `sapi5SonicPitch` z menedżera dodatków NVDA albo z katalogu
`%APPDATA%\nvda\addons\sapi5SonicPitch`, a potem zrestartuj NVDA.

## Pliki Logów

- Aktualny log: `%TEMP%\nvda.log`
- Poprzedni log: `%TEMP%\nvda-old.log`
- Logi 32-bitowego hosta syntezatorów: `%TEMP%\nvda_synthDriverHost.*.log`

Najważniejsze frazy:

- `globalSonicPitch`
- `pitch takeover active`
- `captured NVDA pitch`
- `processed speech audio`
- `pitch takeover not available`
- `Sonic is unavailable`

## Szczegóły Techniczne

Dodatek działa tylko w czasie działania NVDA. Nie modyfikuje plików
zainstalowanego NVDA.

Mechanizmy używane przez dodatek:

- globalny plugin NVDA;
- hook `nvwave.WavePlayer.feed`;
- hook `WavePlayer.idle`, `stop` i `close` do obsługi końca strumienia;
- przejęcie metod `_set_pitch` i `_get_pitch` aktywnego syntezatora;
- wewnętrzny `synthDrivers._sonic.SonicStream`.

Sonic działa na ciągłym strumieniu audio per `WavePlayer`. Taki model jest
ważny dla jakości, bo częste tworzenie nowego strumienia i flushowanie każdego
małego bloku może powodować mikroprzerwy.

## Budowanie Ze Źródeł

Katalogiem głównym paczki dodatku jest `addon`.

Ręczne budowanie:

1. Spakuj zawartość katalogu `addon`, nie zewnętrzny katalog projektu.
2. Zmień nazwę archiwum na `globalSonicPitch-<wersja>.nvda-addon`.

Przykład PowerShell:

```powershell
New-Item -ItemType Directory -Path .\dist -Force | Out-Null
Compress-Archive -Path .\addon\* -DestinationPath .\dist\globalSonicPitch.zip -Force
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.3.2.nvda-addon -Force
```

Sprawdzenie składni:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py
```

## Układ Repozytorium

- `addon/manifest.ini` - manifest dodatku NVDA.
- `addon/globalPlugins/globalSonicPitch.py` - główny plugin.
- `addon/doc/en/readme.md` - angielska pomoc dodatku.
- `addon/doc/pl/readme.md` - polska pomoc dodatku.
- `docs/technical-notes.md` - notatki techniczne dla utrzymania.
- `TESTING.md` - macierz testów.
- `CHANGELOG.md` - historia zmian.
