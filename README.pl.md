# SAPI5 Sonic Pitch

SAPI5 Sonic Pitch to dodatek do NVDA, który dodaje osobne syntezatory Microsoft
SAPI5 z korekcją wysokości realizowaną przez wewnętrzny strumień Sonic w NVDA.

Dokumentacja angielska: [README.md](README.md)

## Co Dodaje Dodatek

Dodatek dodaje dwa wybory w oknie syntezatorów NVDA:

- `SAPI5 32-bit Sonic Pitch`
- `SAPI5 64-bit Sonic Pitch`

To są osobne syntezatory. Dodatek nie zastępuje, nie podmienia i nie łata
wbudowanych syntezatorów NVDA `sapi5` oraz `sapi5_32`. Po wyłączeniu dodatku
standardowe SAPI5 powinno działać tak samo jak wcześniej.

## Kiedy Tego Używać

Dodatek jest przydatny dla głosów SAPI5, które ignorują normalne ustawienie
wysokości w NVDA albo zmieniają wysokość słabo przez standardowy mechanizm SAPI
XML.

Dodatek dotyczy tylko głosów SAPI5. Nie wpływa na OneCore, eSpeak, RHVoice,
Vocalizer ani inne syntezatory NVDA.

## Wymagania

- NVDA 2025.1 lub nowsze.
- Windows z co najmniej jednym głosem SAPI5.
- Ścieżka audio NVDA udostępniająca wewnętrzny strumień Sonic.
- Dla 32-bitowych głosów SAPI5 na 64-bitowym NVDA potrzebny jest działający
  wbudowany 32-bitowy host syntezatorów NVDA.

Aktualny release był testowany lokalnie na NVDA 2026.2 beta, 64-bit.

## Instalacja

1. Pobierz najnowszy plik `.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sapi5-sonic-pitch/releases/latest).
2. Otwórz pobrany plik za pomocą NVDA.
3. Potwierdź instalację.
4. Uruchom NVDA ponownie, gdy NVDA o to poprosi.
5. Otwórz okno wyboru syntezatora i wybierz `SAPI5 32-bit Sonic Pitch` albo
   `SAPI5 64-bit Sonic Pitch`.

## Używanie Wysokości

Po wybraniu jednego z syntezatorów Sonic Pitch zmieniaj wysokość zwykłym
ustawieniem głosu w NVDA.

- Wysokość `50` jest neutralna.
- Wartości poniżej `50` obniżają głos.
- Wartości powyżej `50` podwyższają głos.
- Pełny zakres NVDA odpowiada mniej więcej `-6` do `+6` półtonom.
- Współczynnik Sonic jest ograniczony do `0.70..1.45`, żeby uniknąć skrajnych
  wartości.

Tempo, głośność, wybór głosu i rate boost nadal obsługuje standardowa logika
sterownika SAPI5 w NVDA. Sonic Pitch zmienia tylko sposób stosowania globalnej
wysokości.

## SAPI5 32-bit I 64-bit

Głosy SAPI5 są rejestrowane osobno dla aplikacji 32-bitowych i 64-bitowych.
Dlatego dodatek pokazuje dwa osobne syntezatory.

`SAPI5 64-bit Sonic Pitch` używa normalnej 64-bitowej ścieżki SAPI5 w 64-bitowym
NVDA.

`SAPI5 32-bit Sonic Pitch` używa 32-bitowego hosta syntezatorów NVDA, gdy NVDA
działa jako aplikacja 64-bitowa. Dzięki temu 32-bitowe głosy SAPI5 mogą działać,
a zmiana wysokości jest wykonywana wewnątrz procesu 32-bitowego hosta.

Każdy z tych syntezatorów pokazuje tylko głosy dostępne dla swojej bitowości
SAPI5.

## Rozwiązywanie Problemów

Jeśli syntezatory dodatku nie pojawiają się na liście, sprawdź wersję NVDA i to,
czy odpowiednia ścieżka SAPI5 jest dostępna.

Jeśli nie ładuje się `SAPI5 32-bit Sonic Pitch`, najpierw sprawdź wbudowany
syntezator NVDA `Microsoft Speech API version 5 (32 bit)`. Jeżeli wbudowany
syntezator też nie działa, problem jest poza tym dodatkiem.

Jeśli zwykły `sapi5` albo `sapi5_32` przestaje działać tylko wtedy, gdy dodatek
jest włączony, upewnij się, że używasz wersji `0.1.8` lub nowszej. Starsze
wersje robocze przez krótki czas zawierały globalny moduł naprawczy. Aktualne
wydania nie instalują żadnego globalnego pluginu.

Przydatne logi NVDA:

- bieżący log: `%TEMP%\nvda.log`
- poprzedni log: `%TEMP%\nvda-old.log`
- logi 32-bitowego hosta: `%TEMP%\nvda_synthDriverHost.*.log`

W logach warto szukać:

- `sapi5SonicPitch`
- `sapi5SonicPitch32`
- `sapi5SonicPitch64`
- `Sonic pitch unavailable`

## Znane Ograniczenia

- Dodatek używa prywatnych wewnętrznych mechanizmów NVDA związanych z WASAPI i
  Sonic.
- Jeśli NVDA zmieni `sonicStream`, `_initWasapiAudio` albo 32-bitowy host
  syntezatorów, dodatek może wymagać aktualizacji.
- Starsze ścieżki audio bez WASAPI nie udostępniają strumienia Sonic, więc Sonic
  Pitch nie może tam działać.
- Osadzone komendy zmiany wysokości w sekwencji mowy mogą zostać zneutralizowane,
  ponieważ dodatek utrzymuje SAPI XML pitch w pozycji neutralnej, żeby uniknąć
  podwójnego przetwarzania wysokości.

## Budowanie Ze Źródeł

Katalogiem głównym paczki dodatku jest `addon`.

Ręczne budowanie:

1. Spakuj zawartość katalogu `addon`, nie cały katalog projektu.
2. Zmień nazwę archiwum na `sapi5SonicPitch-<wersja>.nvda-addon`.

Przykład w PowerShellu:

```powershell
Compress-Archive -Path .\addon\* -DestinationPath .\dist\sapi5SonicPitch.zip -Force
Move-Item .\dist\sapi5SonicPitch.zip .\dist\sapi5SonicPitch-0.1.9.nvda-addon -Force
```

Przed publikacją paczki warto wykonać kontrolę składni:

```powershell
python -m py_compile `
  addon\synthDrivers\_sapi5SonicPitch32Host.py `
  addon\synthDrivers\_sapi5SonicPitchCommon.py `
  addon\synthDrivers\sapi5SonicPitch32.py `
  addon\synthDrivers\sapi5SonicPitch64.py
```

## Struktura Repozytorium

- `addon/manifest.ini` - manifest dodatku NVDA.
- `addon/synthDrivers/` - sterowniki syntezatorów Sonic Pitch.
- `addon/doc/en/readme.md` - angielska pomoc dodatku.
- `addon/doc/pl/readme.md` - polska pomoc dodatku.
- `INSPECTION.md` - notatki z lokalnej inspekcji NVDA.
- `TESTING.md` - lista testów ręcznych.
- `docs/technical-notes.md` - notatki techniczne.
