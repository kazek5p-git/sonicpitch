# Global Sonic Pitch

Global Sonic Pitch to dodatek do NVDA, który dodaje osobną regulację `Sonic
pitch` i stosuje ją przez przetwarzanie audio Sonic. Zwykła `Wysokość` NVDA
pozostaje natywnym ustawieniem aktywnego syntezatora. Dodatek działa globalnie
dla syntezatorów, których audio mowy przechodzi przez główny proces NVDA.

Dokumentacja angielska: [README.md](README.md)

## Najważniejsze Informacje

- Dodatek nie dodaje nowych syntezatorów do okna wyboru syntezatora.
- Zwykły suwak `Wysokość` NVDA nadal steruje natywną wysokością syntezatora.
- Po włączeniu trybu globalnego dodatek dodaje własne ustawienie `Sonic pitch`
  do ustawień głosu i pierścienia ustawień syntezatora dla obsługiwanych
  syntezatorów.
- `Sonic pitch` jest osobną regulacją Sonic i nie zastępuje natywnej
  `Wysokości`.
- Audio mowy jest filtrowane przez Sonic w głównym `WavePlayer` NVDA.
- Standardowy `sapi5_32` na 64-bitowym NVDA jest celowo pomijany, bo działa w
  osobnym 32-bitowym hoście.
- Dodatek zawiera dobrowolny link wsparcia autora, który otwiera BuyCoffee w
  domyślnej przeglądarce.
- Podczas instalacji dodatek może zapytać, czy otworzyć stronę wsparcia.

## Dla Kogo Jest Ten Dodatek

Użyj Global Sonic Pitch, jeśli chcesz mieć dodatkową, niezależną regulację
wysokości przez Sonic dla różnych syntezatorów NVDA. Przydaje się to szczególnie
wtedy, gdy natywna regulacja wysokości danego głosu brzmi gorzej albo zachowuje
się niespójnie.

Dodatek był testowany lokalnie z:

- RHVoice;
- eSpeak NG;
- eSpeak-NG SAPI przez SAPI5;
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
3. Zmieniaj przetwarzanie Sonic ustawieniem głosu `Sonic pitch` albo panelem
   dodatku. Jeśli `Sonic pitch` nie ma jeszcze w ustawieniach głosu, włącz tryb
   globalny w panelu dodatku i otwórz ustawienia głosu ponownie.
4. Zmieniaj natywną wysokość syntezatora normalnym ustawieniem `Wysokość`, jeśli
   chcesz używać obu regulacji równocześnie.
5. Ustawienie `50` traktuj jako neutralne dla `Sonic pitch`.
6. Jeśli coś brzmi źle, wróć do `50` albo wyłącz globalny tryb w panelu dodatku.

## Ustawienia

Panel `Global Sonic Pitch` zawiera:

- `Enable global Sonic pitch` - włącza lub wyłącza globalne przetwarzanie Sonic
  pitch.
- `Sonic pitch` - ustawia wartość wysokości używaną przez Sonic.
- `Enable debug logging` - dodaje szczegółowe wpisy do logu NVDA.
- `Support the author` - otwiera zewnętrzną stronę wsparcia BuyCoffee.

Normalne ustawienie `Wysokość` w pierścieniu ustawień syntezatora pozostaje
natywnym ustawieniem aktywnego syntezatora. `Sonic pitch` jest osobnym
ustawieniem dodatku.

Panel dodatku jest zawsze dostępny w ustawieniach NVDA, żeby można było włączyć
albo wyłączyć funkcję.

Gdy `Enable global Sonic pitch` jest włączone, dodatek próbuje też dodać osobne
ustawienie `Sonic pitch` do standardowego dialogu `Głos` i do pierścienia
ustawień syntezatora. To ustawienie jest dokładane dynamicznie do aktywnego
syntezatora, bez modyfikowania rdzenia NVDA. Gdy globalny Sonic pitch jest
wyłączony, ustawienie znika z dialogu `Głos` i pierścienia ustawień syntezatora.

Jeśli używasz dodatku `Synth ring settings selector`, `sonicPitch` jest
dopisywane do jego listy dostępnych ustawień, żeby mogło pojawić się w
pierścieniu po włączeniu trybu globalnego.

W `Zdarzeniach wejścia` w kategorii `Global Sonic Pitch` dostępne są komendy:

- `Toggle global Sonic pitch`;
- `Report global Sonic pitch status`;
- `Open support page`;
- `Increase global Sonic pitch`;
- `Decrease global Sonic pitch`;
- `Reset global Sonic pitch`.

Komendy nie mają domyślnych gestów, więc możesz przypisać własne skróty.

## Wsparcie Autora

Przycisk `Support the author` w panelu ustawień oraz komenda `Open support page`
w `Zdarzeniach wejścia` otwierają:

```text
https://buycoffee.to/kazimierz-parzych
```

To dobrowolny zewnętrzny link wsparcia. Dodatek nie obsługuje płatności, nie
zapisuje danych płatniczych i nie odblokowuje żadnych funkcji po wsparciu.

Podczas instalacji albo aktualizacji Sonic Pitch pokazuje też mały opcjonalny
komunikat wsparcia. Wybranie `Yes` otwiera tę samą stronę w domyślnej
przeglądarce. Wybranie `No` kontynuuje instalację i nie zmienia działania
dodatku.

## Jak Działa Wysokość

NVDA używa skali od `0` do `100`.

- `50` jest neutralne.
- `0..49` obniża głos.
- `51..100` podwyższa głos.
- Pełny zakres odpowiada mniej więcej `-6..+6` półtonom.
- Współczynnik Sonic jest ograniczony do `0.70..1.45`, żeby uniknąć skrajnych
  zniekształceń.

Gdy globalny tryb jest włączony, dodatek przetwarza audio mowy przez Sonic według
wartości `Sonic pitch`. Zwykła `Wysokość` NVDA nadal działa jako natywna
wysokość syntezatora. Jeśli oba suwaki są ustawione poza `50`, usłyszysz
połączenie obu efektów.

## Zgodność Syntezatorów

| Syntezator | Oczekiwane działanie |
| --- | --- |
| RHVoice | Obsługiwany, jeśli audio trafia do głównego `WavePlayer`. |
| eSpeak NG | Obsługiwany w głównym procesie NVDA. |
| eSpeak-NG SAPI przez SAPI5 | Obsługiwany jako głos SAPI5 po skonfigurowaniu go w konfiguratorze eSpeak-NG SAPI. |
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
4. Ustaw `Sonic pitch` na wartość inną niż `50`, na przykład `75`.
5. Otwórz aktualny log NVDA: `%TEMP%\nvda.log`.

W logu powinny pojawić się wpisy podobne do:

```text
globalSonicPitch: installed WavePlayer speech feed hook
globalSonicPitch: installed synth Sonic pitch setting hook
globalSonicPitch: added Sonic pitch voice setting; synth=RHVoice
globalSonicPitch: processed speech audio; synth=RHVoice; pitch=75
```

Jeśli wybrany jest `sapi5_32`, oczekiwany wpis to:

```text
Loaded synthDriver sapi5_32
```

## Rozwiązywanie Problemów

### Sonic pitch nie ma w ustawieniach głosu

Włącz `Enable global Sonic pitch` w panelu `Global Sonic Pitch`, a potem otwórz
ustawienia głosu ponownie albo przełącz syntezator. Dodatek ukrywa ustawienie
`Sonic pitch` w dialogu `Głos`, gdy globalny Sonic pitch jest wyłączony.

### Sonic pitch się nie zmienia

Sprawdź, czy globalny tryb jest włączony i czy wartość `Sonic pitch` nie wynosi
`50`. Sprawdź też log NVDA pod kątem `processed speech audio`. Jeśli tego wpisu
nie ma, audio danego syntezatora prawdopodobnie nie przechodzi przez główny
`WavePlayer`.

### Syntezator zmienia swoją natywną wysokość

To jest teraz oczekiwane zachowanie. Zwykła `Wysokość` NVDA steruje natywną
wysokością syntezatora, a `Sonic pitch` steruje tylko przetwarzaniem Sonic.

### Słychać drobne przerwy albo artefakty

Od wersji 0.3.1 dodatek utrzymuje ciągły strumień Sonic dla aktywnego
`WavePlayer` i nie wykonuje `flush()` po każdym małym bloku audio. Jeśli nadal
słychać przerwy, sprawdź czy nie masz bardzo dużego obciążenia CPU, bardzo
agresywnego `Sonic pitch` oraz czy problem występuje na więcej niż jednym
syntezatorze.

Wersja 0.4.4 dodatkowo unika zmieniania wysokości aktywnego strumienia Sonic w
locie. Gdy `Sonic pitch` zmienia się podczas mowy, stary procesor jest odrzucany,
a świeży procesor startuje od następnego bloku audio. To bardziej konserwatywne,
ale omija zawieszenia widziane z niektórymi głosami SAPI5 przy szybkim obniżaniu
wysokości.

Wersja 0.4.5 dodatkowo zmniejsza blokowanie między wątkami podczas
przetwarzania szybkich głosów SAPI5, w tym eSpeak-NG SAPI przy prędkości 100.

### eSpeak-NG SAPI nie pojawia się w SAPI5

Zewnętrzny głos eSpeak-NG SAPI trzeba najpierw skonfigurować jego własnym
konfiguratorem. Po utworzeniu albo włączeniu profilu głosu zrestartuj NVDA i
wybierz ten głos z normalnej listy głosów SAPI5.

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
- `added Sonic pitch voice setting`
- `captured Sonic pitch setting`
- `processed speech audio`
- `Sonic is unavailable`

## Szczegóły Techniczne

Dodatek działa tylko w czasie działania NVDA. Nie modyfikuje plików
zainstalowanego NVDA.

Mechanizmy używane przez dodatek:

- globalny plugin NVDA;
- hook `nvwave.WavePlayer.feed`;
- hook `WavePlayer.idle`, `stop` i `close` do obsługi końca strumienia;
- dynamiczne dodanie ustawienia `sonicPitch` do `supportedSettings` aktywnego
  syntezatora;
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
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.4.5.nvda-addon -Force
```

Sprawdzenie składni:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py addon\installTasks.py
```

## Układ Repozytorium

- `addon/manifest.ini` - manifest dodatku NVDA.
- `addon/installTasks.py` - opcjonalny komunikat wsparcia podczas instalacji.
- `addon/globalPlugins/globalSonicPitch.py` - główny plugin.
- `addon/doc/en/readme.md` - angielska pomoc dodatku.
- `addon/doc/pl/readme.md` - polska pomoc dodatku.
- `docs/technical-notes.md` - notatki techniczne dla utrzymania.
- `TESTING.md` - macierz testów.
- `CHANGELOG.md` - historia zmian.
