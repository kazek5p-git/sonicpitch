# Global Sonic Pitch

Global Sonic Pitch to dodatek do NVDA, który może stosować wysokość mowy przez
przetwarzanie audio Sonic w głównym procesie NVDA.

## Co Dodaje

Dodatek dodaje globalny plugin i panel ustawień NVDA o nazwie
`Global Sonic Pitch`.

Nie dodaje żadnych syntezatorów do okna wyboru syntezatora. Standardowe pozycje
`sapi5`, `sapi5_32`, OneCore, eSpeak, RHVoice, Vocalizer i inne pozostają
zwykłymi sterownikami NVDA.

Po włączeniu globalnej wysokości:

- normalne ustawienie wysokości NVDA jest przejmowane przez dodatek;
- natywna wysokość aktywnego syntezatora jest utrzymywana neutralnie na `50`,
  jeśli dany sterownik to obsługuje;
- Sonic stosuje wybraną wysokość na wyjściowym audio mowy;
- wartości poniżej `50` obniżają głos, a powyżej `50` go podwyższają.

## Wymagania

- NVDA 2025.1 lub nowsze.
- Nowoczesna ścieżka audio NVDA z wewnętrznym strumieniem Sonic.
- Syntezator, którego 16-bitowe audio PCM mowy przechodzi przez główny
  `WavePlayer` NVDA.

Aktualna wersja była testowana lokalnie na NVDA 2026.2 beta, 64-bit.

## Instalacja

1. Pobierz najnowszy plik `.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sapi5-sonic-pitch/releases/latest).
2. Jeśli masz zainstalowany stary dodatek `SAPI5 Sonic Pitch` /
   `sapi5SonicPitch`, usuń go najpierw i zrestartuj NVDA.
3. Otwórz pobrany plik `globalSonicPitch-<wersja>.nvda-addon` w NVDA.
4. Potwierdź instalację i zrestartuj NVDA.
5. Otwórz ustawienia NVDA, wybierz `Global Sonic Pitch` i włącz globalną
   wysokość Sonic.

## Użycie Wysokości

Po włączeniu globalnej wysokości Sonic zmieniaj wysokość zwykłymi ustawieniami
głosu NVDA albo pierścieniem ustawień syntezatora. Dodatek przechwytuje tę
wartość, trzyma natywną wysokość syntezatora neutralnie i stosuje zmianę przez
Sonic.

Panel ustawień ma też suwak `Sonic pitch`. Jest przydatny, gdy chcesz ustawić
tę samą wartość bez przechodzenia przez pierścień ustawień głosu.

Mapowanie:

- `50` jest neutralne.
- `0..49` obniża głos.
- `51..100` podwyższa głos.
- Pełny zakres odpowiada mniej więcej `-6..+6` półtonom.
- Współczynnik Sonic jest ograniczony do `0.70..1.45`.

## Obsługiwane I Nieobsługiwane Ścieżki

Global Sonic Pitch działa w głównym procesie NVDA. Powinien działać z
syntezatorami PCM takimi jak eSpeak, RHVoice, OneCore, SAPI5 64-bit i podobnymi
sterownikami, jeśli ich audio trafia do głównego `WavePlayer` NVDA.

Wbudowany syntezator `sapi5_32` jest szczególnym przypadkiem na 64-bitowym NVDA.
Mówi w osobnym 32-bitowym hoście syntezatorów, więc ten globalny plugin nie może
przetwarzać jego audio. Dla tego syntezatora dodatek celowo nie przejmuje
wysokości i zostawia natywne zachowanie `sapi5_32`.

## Rozwiązywanie Problemów

Jeśli w oknie wyboru syntezatora nadal widzisz stare pozycje
`SAPI5 32-bit Sonic Pitch` albo `SAPI5 64-bit Sonic Pitch`, stary dodatek
`sapi5SonicPitch` nadal jest zainstalowany. Usuń go i zrestartuj NVDA.

Przydatne logi NVDA:

- `%TEMP%\nvda.log`
- `%TEMP%\nvda-old.log`
- `%TEMP%\nvda_synthDriverHost.*.log`

W logach szukaj:

- `globalSonicPitch`
- `pitch takeover active`
- `captured NVDA pitch`
- `processed speech audio`
- `Sonic is unavailable`

## Ograniczenia

- Dodatek używa prywatnych mechanizmów NVDA związanych z Sonic i `WavePlayer`.
- Przetwarza audio mowy tylko w głównym procesie NVDA.
- Przetwarza 16-bitowe bloki PCM i przepuszcza wszystko inne bez zmian.
- Przyszłe zmiany w `nvwave.WavePlayer.feed`,
  `synthDrivers._sonic.SonicStream` albo ustawieniach pitch syntezatorów mogą
  wymagać aktualizacji dodatku.
- Osadzone komendy wysokości w sekwencji mowy mogą nadal należeć do
  syntezatora. Dodatek kontroluje normalne ustawienie wysokości NVDA.

## Budowanie Ze Źródeł

Katalogiem głównym paczki dodatku jest `addon`.

Ręczne budowanie:

1. Spakuj zawartość katalogu `addon`, nie zewnętrzny katalog projektu.
2. Zmień nazwę archiwum na `globalSonicPitch-<wersja>.nvda-addon`.

Przykład PowerShell:

```powershell
New-Item -ItemType Directory -Path .\dist -Force | Out-Null
Compress-Archive -Path .\addon\* -DestinationPath .\dist\globalSonicPitch.zip -Force
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.3.0.nvda-addon -Force
```

Sprawdzenie składni przed publikacją:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py
```

## Układ Repozytorium

- `addon/manifest.ini` - manifest dodatku NVDA.
- `addon/globalPlugins/` - globalny procesor Sonic i panel ustawień.
- `addon/doc/en/readme.md` - angielska pomoc dodatku.
- `addon/doc/pl/readme.md` - polska pomoc dodatku.
- `INSPECTION.md` - lokalne notatki z inspekcji NVDA.
- `TESTING.md` - ręczna macierz testów.
- `docs/technical-notes.md` - notatki techniczne.
