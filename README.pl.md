# Global Sonic Pitch

Global Sonic Pitch to dodatek do NVDA, który dodaje osobną regulację `Sonic
pitch` dla obsługiwanych syntezatorów. Zmienia wysokość mowy przez
przetwarzanie Sonic, a zwykłe ustawienie NVDA `Wysokość` nadal steruje natywną
wysokością syntezatora.

## Szybki Start

1. Zainstaluj `globalSonicPitch-<wersja>.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. Zrestartuj NVDA.
3. Otwórz ustawienia NVDA i wybierz `Global Sonic Pitch`.
4. Włącz `Enable global Sonic pitch`.
5. Otwórz ustawienia głosu albo pierścień ustawień syntezatora i zmień
   `Sonic pitch`.

## Funkcje

- Dodaje panel ustawień `Global Sonic Pitch`.
- Dodaje osobne ustawienie `Sonic pitch`, gdy globalne przetwarzanie jest
  włączone.
- Zostawia zwykłą `Wysokość` NVDA jako natywną wysokość syntezatora.
- Zapisuje `Sonic pitch` osobno dla każdego obsługiwanego syntezatora i
  wybranego głosu.
- Udostępnia opcjonalny rozszerzony zakres około `-20..+20` półtonów.
- Obsługuje audio syntezatorów działających w głównym procesie NVDA oraz
  standardowe `sapi5_32` / `sapi4_32` na 64-bitowym NVDA przez dołączone
  wrappery hosta 32-bitowego.
- Zawiera dołączone natywne biblioteki Sonic 32-bit i 64-bit.
- Zawiera pomoc dodatku po angielsku, polsku i słowacku.
- Zawiera polskie i słowackie tłumaczenie interfejsu.

## Dokumentacja

- Pełna pomoc angielska: [addon/doc/en/readme.md](addon/doc/en/readme.md)
- Pomoc polska: [addon/doc/pl/readme.md](addon/doc/pl/readme.md)
- Pomoc słowacka: [addon/doc/sk/readme.md](addon/doc/sk/readme.md)
- Notatki techniczne: [docs/technical-notes.md](docs/technical-notes.md)
- Lista testów ręcznych: [TESTING.md](TESTING.md)
- Szablon tłumaczeń: [addon/locale/nvda.pot](addon/locale/nvda.pot)

## Zmiany

- 1.0: Stabilne wydanie zastępujące wycofaną kompilację 1.0. Poprawia
  obsługę krótkich bloków audio i wzmacnia sprzątanie okna ustawień głosu.
- 0.4.20: Dodano opcjonalny zakres 20 półtonów i obsługę standardowego
  `sapi4_32` przez host 32-bitowy w 64-bitowym NVDA.
- 0.4.19: Uporządkowana dokumentacja publiczna pod recenzję w NVDA Add-on
  Store. Bez zmian w działaniu audio.
- 0.4.18: Dodano wartości `Sonic pitch` per głos oraz polską i słowacką
  lokalizację.
- 0.4.15: Ustabilizowano szybkie zmiany `Sonic pitch` dla standardowego
  `sapi5_32` na 64-bitowym NVDA.
- 0.4.13: Dodano obsługę standardowego `sapi5_32` na 64-bitowym NVDA przez
  dołączony wrapper hosta.
- 0.4.10: Dołączono natywne biblioteki Sonic dla 32-bitowego i 64-bitowego
  NVDA.

Historia wydań jest w [CHANGELOG.md](CHANGELOG.md).

## Kod Źródłowy

- Główny plugin: [addon/globalPlugins/globalSonicPitch.py](addon/globalPlugins/globalSonicPitch.py)
- Wrapper hosta SAPI5 32-bit: [addon/sapi32HostDrivers/sapi5.py](addon/sapi32HostDrivers/sapi5.py)
- Wrapper hosta SAPI4 32-bit: [addon/sapi32HostDrivers/sapi4.py](addon/sapi32HostDrivers/sapi4.py)
- Notatki o dołączonej bibliotece Sonic: [addon/globalPlugins/sonicPitchNative/README.txt](addon/globalPlugins/sonicPitchNative/README.txt)

## Instalacja

1. Pobierz najnowszy plik `.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. W NVDA otwórz sklep dodatków albo menedżer dodatków i wybierz instalację z
   pliku.
3. Wskaż pobrany pakiet dodatku.
4. Zrestartuj NVDA po komunikacie.

Najnowszy pakiet:
[globalSonicPitch-1.0.nvda-addon](https://github.com/kazek5p-git/sonicpitch/releases/latest)

## Licencja

Global Sonic Pitch jest licencjonowany na GNU GPL w wersji 2 lub nowszej.
Dołączone natywne biblioteki Sonic są zewnętrznymi komponentami na licencji
Apache 2.0.
