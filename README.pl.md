# Global Sonic Pitch

Global Sonic Pitch to dodatek do NVDA, który dodaje osobną regulację `Sonic
pitch` i stosuje ją przez przetwarzanie audio Sonic. Zwykła `Wysokość` NVDA
pozostaje natywnym ustawieniem aktywnego syntezatora. Dodatek działa globalnie
dla syntezatorów, których audio mowy przechodzi przez główny proces NVDA, a
standardowy `sapi5_32` na 64-bitowym NVDA obsługuje przez mały wrapper
32-bitowego hosta.

Dokumentacja angielska: [README.md](README.md)
Dokumentacja słowacka: [README.sk.md](README.sk.md)

## Najważniejsze Informacje

- Dodatek nie dodaje nowych syntezatorów do okna wyboru syntezatora.
- Zwykły suwak `Wysokość` NVDA nadal steruje natywną wysokością syntezatora.
- Po włączeniu trybu globalnego dodatek dodaje własne ustawienie `Sonic pitch`
  do ustawień głosu i pierścienia ustawień syntezatora dla obsługiwanych
  syntezatorów.
- `Sonic pitch` jest osobną regulacją Sonic i nie zastępuje natywnej
  `Wysokości`.
- `Sonic pitch` jest zapisywany osobno dla każdego obsługiwanego syntezatora i
  wybranego głosu.
- Audio mowy jest filtrowane przez Sonic w głównym `WavePlayer` NVDA, gdy dana
  ścieżka audio jest dostępna.
- Standardowy `sapi5_32` na 64-bitowym NVDA jest obsługiwany przez dołączony
  wrapper 32-bitowego hosta; w oknie wyboru syntezatora nadal jest to zwykły
  syntezator NVDA `sapi5_32`.
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
- standardowym SAPI5 32-bit na 64-bitowym NVDA.

## Wymagania

- NVDA 2025.1 lub nowsze.
- Windows.
- Dołączona natywna biblioteka Sonic, z biblioteką Sonic z NVDA jako
  mechanizmem awaryjnym, jeśli dołączona biblioteka nie może zostać załadowana.
- Syntezator wysyłający 16-bitowe PCM mowy przez główny `WavePlayer` NVDA albo
  standardowy `sapi5_32` na 64-bitowym NVDA.

Ostatnio testowane lokalnie konfiguracje:

- NVDA 2025.3.3 x86 portable z SAPI5 przy prędkości 100.
- NVDA 2026.2 beta AMD64 z SAPI5 przy prędkości 100.

Cel zgodności dla sklepu:

- Metadane kanału stable celują w NVDA 2026.1.1.

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

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore,
   SAPI5 64-bit albo standardowy `sapi5_32`.
2. W ustawieniach NVDA włącz `Global Sonic Pitch`.
3. Zmieniaj przetwarzanie Sonic ustawieniem głosu `Sonic pitch`, pierścieniem
   ustawień syntezatora albo przypisanym gestem wejścia. Jeśli `Sonic pitch` nie
   ma jeszcze w ustawieniach głosu, włącz tryb globalny w panelu dodatku i
   otwórz ustawienia głosu ponownie.
4. Zmieniaj natywną wysokość syntezatora normalnym ustawieniem `Wysokość`, jeśli
   chcesz używać obu regulacji równocześnie.
5. Ustawienie `50` traktuj jako neutralne dla `Sonic pitch`. Każdy obsługiwany
   syntezator i wybrany głos ma własną wartość `Sonic pitch`.
6. Jeśli coś brzmi źle, wróć do `50` albo wyłącz globalny tryb w panelu dodatku.

## Ustawienia

Panel `Global Sonic Pitch` zawiera:

- `Enable global Sonic pitch` - włącza lub wyłącza globalne przetwarzanie Sonic
  pitch.
- `Enable debug logging` - dodaje szczegółowe wpisy do logu NVDA.
- `Support the author` - otwiera zewnętrzną stronę wsparcia BuyCoffee.

Normalne ustawienie `Wysokość` w pierścieniu ustawień syntezatora pozostaje
natywnym ustawieniem aktywnego syntezatora. `Sonic pitch` jest osobnym
ustawieniem dodatku zapisywanym osobno dla obsługiwanego syntezatora i głosu.

Panel dodatku jest zawsze dostępny w ustawieniach NVDA, żeby można było włączyć
albo wyłączyć funkcję.

Gdy `Enable global Sonic pitch` jest włączone, dodatek próbuje też dodać osobne
ustawienie `Sonic pitch` do standardowego dialogu `Głos` i do pierścienia
ustawień syntezatora. To ustawienie jest dokładane dynamicznie do aktywnego
syntezatora, bez modyfikowania rdzenia NVDA. Gdy globalny Sonic pitch jest
wyłączony, ustawienie znika z dialogu `Głos` i pierścienia ustawień syntezatora.

W globalnym panelu dodatku celowo nie ma suwaka `Sonic pitch`. Panel globalny
włącza procesor audio, a wartość `Sonic pitch` zmienia się z poziomu ustawień
głosu, pierścienia ustawień syntezatora albo przypisanych gestów dla bieżącego
obsługiwanego syntezatora.

Jeśli używasz dodatku `Synth ring settings selector`, `sonicPitch` jest
dopisywane do jego listy dostępnych ustawień, żeby mogło pojawić się w
pierścieniu po włączeniu trybu globalnego.

W `Zdarzeniach wejścia` w kategorii `Global Sonic Pitch` dostępne są komendy:

- `Toggle global Sonic pitch`;
- `Report global Sonic pitch status`;
- `Open support page`;
- `Increase Sonic pitch for the current synthesizer`;
- `Decrease Sonic pitch for the current synthesizer`;
- `Reset Sonic pitch for the current synthesizer`.

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
własnej wartości `Sonic pitch` aktywnego syntezatora. Zwykła `Wysokość` NVDA
nadal działa jako natywna wysokość syntezatora. Jeśli oba suwaki są ustawione
poza `50`, usłyszysz połączenie obu efektów.

Od wersji 0.4.9 zmiany `Sonic pitch` są stosowane na granicach wypowiedzi.
Aktywny strumień Sonic zachowuje dotychczasową wartość do końca bieżącej
wypowiedzi. Następna wypowiedź używa już nowej wartości. Dzięki temu dodatek nie
wymienia natywnych obiektów Sonic w środku aktywnych callbacków audio.

Od wersji 0.4.10 dodatek zawiera własne natywne biblioteki Sonic 32-bit i
64-bit. W 32-bitowych procesach NVDA dodatek dodatkowo omija natywne niszczenie
strumienia Sonic i używa ponownie aktywnego strumienia po zdarzeniach
stop/reset. To obejście usuwa lokalnie odtworzony natywny crash sterty
`0xc0000374` na NVDA 2025.3.3 x86 z SAPI5.

Od wersji 0.4.11 krótkie komunikaty zwrotne po szybkich zmianach `Sonic pitch`,
na przykład PageUp/PageDown w ustawieniach głosu albo pierścieniu ustawień
syntezatora, pewniej używają najnowszej wartości od następnej granicy
wypowiedzi.

Wersja 0.4.12 jest wydaniem przygotowującym dodatek do sklepu. Aktualizuje
metadane pod najnowszy stabilny cel API NVDA, dodaje dokumentację licencji w
repozytorium i zapisuje checklistę zgłoszenia do NVDA Add-on Store w
`docs/addon-store-submission.md`.

Wersja 0.4.13 dodaje sterowanie Sonic pitch dla standardowego `sapi5_32` na
64-bitowym NVDA przez dołączony wrapper 32-bitowego hosta. Dodaje też
transakcyjne zachowanie w dialogu `Głos`: zmiana `Sonic pitch` jest słyszalna
od razu jako podgląd, ale Escape/Anuluj przywraca poprzednią wartość. OK albo
Zastosuj zapisuje zmianę.

Wersja 0.4.14 stabilizuje szybkie zmiany `Sonic pitch` dla standardowego
`sapi5_32` na 64-bitowym NVDA. Host 32-bitowy stosuje oczekujące zmiany pitch na
bezpiecznych granicach mowy i serializuje operacje strumienia Sonic, dzięki
czemu zdalna ścieżka SAPI nie milknie przy szybkim ruszaniu suwakiem.

Wersja 0.4.15 wzmacnia to obejście dla realnego zachowania dialogu `Głos`, gdzie
NVDA szybko anuluje mowę, zmienia ustawienie i wypowiada nową wartość. Host
32-bitowy blokuje teraz cały callback audio SAPI, wymienia strumień Sonic przy
zmianie pitch i odzyskuje działanie po uszkodzonym bloku Sonic zamiast zostawiać
`sapi5_32` bez mowy.

Wersja 0.4.17 aktualizuje metadane autorów dodatku i wydawcy w sklepie, aby
zawierały Kazimierza Parzycha i DJ Graco. Działanie audio nie zmienia się
względem wersji 0.4.16.

Wersja 0.4.18 zapisuje wartości Sonic pitch osobno dla obsługiwanego
syntezatora i wybranego głosu. W SAPI5 oznacza to, że Paulina i eSpeak-NG SAPI
mogą mieć różne wartości Sonic pitch, mimo że oba głosy działają w tym samym
syntezatorze SAPI5.

## Zgodność Syntezatorów

| Syntezator | Oczekiwane działanie |
| --- | --- |
| RHVoice | Obsługiwany, jeśli audio trafia do głównego `WavePlayer`. |
| eSpeak NG | Obsługiwany w głównym procesie NVDA. |
| eSpeak-NG SAPI przez SAPI5 | Obsługiwany jako zwykły głos SAPI5 po skonfigurowaniu i pojawieniu się na standardowej liście głosów SAPI5 w NVDA. Dodatek nie uzupełnia już list głosów SAPI. |
| OneCore | Obsługiwany w głównym procesie NVDA. |
| SAPI5 64-bit | Obsługiwany, gdy używa ścieżki audio NVDA. |
| SAPI5 32-bit na 64-bitowym NVDA | Obsługiwany przez dołączony wrapper 32-bitowego hosta. |
| Dodatkowe syntezatory | Mogą działać, jeśli wysyłają 16-bitowe PCM przez główny `WavePlayer`. |

## SAPI5 32-bit Na 64-bitowym NVDA

Standardowy `sapi5_32` działa na 64-bitowym NVDA przez osobny 32-bitowy host
syntezatorów. Hook `WavePlayer` w głównym procesie nie widzi tego audio, więc
dodatek rejestruje mały wrapper dla 32-bitowego hosta. Wrapper ładuje oryginalny
32-bitowy sterownik SAPI5 z NVDA i wystawia jeden dodatkowy parametr hosta:
`sonicPitch`, który ustawia wysokość istniejącego strumienia Sonic w hoście.

To nie dodaje nowego syntezatora i nie modyfikuje plików NVDA. W oknie wyboru
syntezatora nadal widoczny jest `Microsoft Speech API version 5 (32 bit)`. Jeśli
`sapi5_32` był aktywny już podczas startu dodatku, dodatek może przeładować go
raz, żeby został użyty wrapper.

Wartości Sonic pitch są zapisywane pod kluczami zależnymi od architektury:

- `sapi5_32` dla zwykłego `sapi5` w 32-bitowym NVDA oraz dla `sapi5_32` w
  64-bitowym NVDA.
- `sapi5_64` dla standardowego `sapi5` w 64-bitowym NVDA.

Od wersji 0.4.18 identyfikator wybranego głosu jest dopisywany do tego klucza
bazowego. Istniejące wartości zapisane tylko pod `sapi5_32`, `sapi5_64` albo
innym kluczem syntezatora są migrowane przy pierwszym użyciu do pierwszego
wybranego głosu tego syntezatora. Nowe głosy zaczynają od neutralnej wartości
Sonic pitch `50`, dopóki ich nie zmienisz.

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
globalSonicPitch: loaded bundled Sonic library
globalSonicPitch: processed speech audio; synth=RHVoice; pitch=75
```

Jeśli wybrany jest `sapi5_32`, oczekiwany wpis to:

```text
Loaded synthDriver sapi5_32
globalSonicPitch: applied remote SAPI5 32-bit Sonic pitch
```

Log 32-bitowego hosta w `%TEMP%\nvda_synthDriverHost.*.log` powinien też
zawierać:

```text
globalSonicPitch sapi5_32 host: set Sonic pitch
```

## Rozwiązywanie Problemów

### Sonic pitch nie ma w ustawieniach głosu

Włącz `Enable global Sonic pitch` w panelu `Global Sonic Pitch`, a potem otwórz
ustawienia głosu ponownie albo przełącz syntezator. Dodatek ukrywa ustawienie
`Sonic pitch` w dialogu `Głos`, gdy globalny Sonic pitch jest wyłączony.

### Sonic pitch się nie zmienia

Sprawdź, czy globalny tryb jest włączony i czy wartość `Sonic pitch` nie wynosi
`50`. Dla RHVoice, eSpeak, OneCore i SAPI5 64-bit sprawdź log NVDA pod kątem
`processed speech audio`. Jeśli tego wpisu nie ma dla jednego z tych
syntezatorów, jego audio prawdopodobnie nie przechodzi przez główny
`WavePlayer`.

Dla standardowego `sapi5_32` na 64-bitowym NVDA sprawdź `applied remote SAPI5
32-bit Sonic pitch` w `%TEMP%\nvda.log` i `globalSonicPitch sapi5_32 host: set
Sonic pitch` w `%TEMP%\nvda_synthDriverHost.*.log`.

Jeśli po przełączeniu syntezatora albo głosu `Sonic pitch` wraca do `50`, jest
to oczekiwane, dopóki nie ustawisz wartości dla tej konkretnej pary syntezatora
i głosu. Wartości są zapisywane osobno dla każdego obsługiwanego syntezatora i
wybranego głosu.

### Syntezator zmienia swoją natywną wysokość

To jest teraz oczekiwane zachowanie. Zwykła `Wysokość` NVDA steruje natywną
wysokością syntezatora, a `Sonic pitch` steruje tylko przetwarzaniem Sonic.

### Słychać drobne przerwy albo artefakty

Od wersji 0.3.1 dodatek utrzymuje ciągły strumień Sonic dla aktywnego
`WavePlayer` i nie wykonuje `flush()` po każdym małym bloku audio. Jeśli nadal
słychać przerwy, sprawdź czy nie masz bardzo dużego obciążenia CPU, bardzo
agresywnego `Sonic pitch` oraz czy problem występuje na więcej niż jednym
syntezatorze.

Wersja 0.4.4 wprowadziła zasadę, że dodatek nie zmienia wysokości użytego już
strumienia Sonic w locie. Aktualne wersje odkładają zmiany podczas aktywnej mowy,
a gdy wybrany `Sonic pitch` różni się od poprzedniego, tworzą świeży strumień
Sonic na następnej bezpiecznej granicy. To bardziej konserwatywne, ale omija
zawieszenia widziane z niektórymi głosami SAPI5 przy szybkim obniżaniu
wysokości.

Wersja 0.4.5 dodatkowo zmniejsza blokowanie między wątkami podczas
przetwarzania szybkich głosów SAPI5, w tym eSpeak-NG SAPI przy prędkości 100.

Wersja 0.4.9 stosuje zmiany wysokości od następnej wypowiedzi zamiast wymieniać
aktywny procesor Sonic podczas mowy. Jeśli przesuniesz `Sonic pitch`, gdy NVDA
już mówi, słyszalna zmiana może pojawić się dopiero przy następnej wypowiedzi.
To zachowanie jest celowe i stawia stabilność ponad natychmiastowe przestrajanie
w środku słowa.

Wersja 0.4.11 poprawia wykrywanie granic krótkich komunikatów ustawień, więc
powtarzane zmiany PageUp/PageDown nie powinny już zostawać na oryginalnej
wysokości aż do kilku kolejnych ruchów suwakiem.

### eSpeak-NG SAPI nie pojawia się w SAPI5

Zewnętrzny głos eSpeak-NG SAPI trzeba najpierw skonfigurować jego własnym
konfiguratorem. Po utworzeniu albo włączeniu profilu głosu zrestartuj NVDA i
wybierz ten głos z normalnej listy głosów SAPI5.

NVDA 2026.2 czyta standardowe głosy SAPI5 bezpośrednio z rejestru z gałęzi
używanej przez zwykłe głosy. eSpeak-NG SAPI wystawia skonfigurowane głosy przez
dynamiczny enumerator tokenów SAPI. Aktualne wersje dodatku nie patchują
enumeracji głosów SAPI, nie modyfikują plików NVDA i nie zapisują tokenów
głosów w rejestrze. Jeśli głos nie jest widoczny w SAPI5, trzeba najpierw
naprawić konfigurację eSpeak-NG SAPI.

### Sonic pitch w dialogu Głos cofa się po Escape

Zmiany zrobione w dialogu `Głos` są tymczasowe do momentu naciśnięcia OK albo
Zastosuj. Escape albo Anuluj przywraca poprzednią wartość `Sonic pitch`. Zmiany
z pierścienia ustawień syntezatora i z gestów wejścia są zapisywane od razu.

### Standardowy SAPI5 32-bit nie pokazuje Sonic pitch

Na 64-bitowym NVDA `sapi5_32` musi zostać załadowany przez wrapper hosta
dodatku. Zrestartuj NVDA albo przełącz się z `sapi5_32` na inny syntezator i
wróć do `sapi5_32`. Następnie sprawdź w logu NVDA wpis
`applied remote SAPI5 32-bit Sonic pitch`.

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
- `applied remote SAPI5 32-bit Sonic pitch`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`
- `loaded bundled Sonic library`
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
- mały wrapper 32-bitowego hosta SAPI5 dla standardowego `sapi5_32` na
  64-bitowym NVDA;
- dołączone natywne DLL-e Sonic 32-bit i 64-bit ładowane przez `ctypes`;
- wewnętrzny `synthDrivers._sonic.SonicStream` z NVDA jako mechanizm awaryjny,
  gdy dołączona biblioteka Sonic nie jest dostępna.

Sonic jest używany ponownie jako ciągły strumień per `WavePlayer`, dopóki format
audio i wybrany `Sonic pitch` pozostają takie same. Gdy format albo pitch się
zmienia, dodatek tworzy świeży strumień na bezpiecznej granicy zamiast
przestrajać już użyty strumień. Dzięki temu unika niestabilności natywnej
biblioteki, a jednocześnie nie tworzy nowego strumienia dla każdego małego bloku
audio.

W 32-bitowych procesach NVDA strumienie Sonic są utrzymywane przy życiu zamiast
przekazywania ich do natywnego `sonicDestroyStream`. To omija odtworzony crash
natywnej sterty 32-bit; zwykła mowa używa ponownie bieżącego strumienia, a nowe
strumienie są alokowane tylko wtedy, gdy wymaga tego zmiana pitch albo formatu.

## NVDA Add-on Store

Notatki przygotowujące dodatek do sklepu są w
`docs/addon-store-submission.md`. Ten plik zawiera szkic metadanych, politykę
bezpieczeństwa wydań i checklistę weryfikacji przed zgłoszeniem dodatku do NVDA
Add-on Store.

Dla zgłoszenia do kanału stable manifest dodatku powinien wskazywać najnowszy
stabilny cel API NVDA, nie wersję beta. Wersja 0.4.18 deklaruje:

```ini
minimumNVDAVersion = 2025.1.0
lastTestedNVDAVersion = 2026.1.1
```

## Licencja

Kod źródłowy Global Sonic Pitch jest licencjonowany na GNU GPL w wersji 2 lub
nowszej. Zobacz `LICENSE.md`.

Dołączone natywne biblioteki Sonic są zewnętrznymi komponentami na licencji
Apache 2.0. Zobacz `THIRD_PARTY_NOTICES.md` oraz
`addon/globalPlugins/sonicPitchNative/LICENSE-Sonic.txt`.

## Budowanie Ze Źródeł

Katalogiem głównym paczki dodatku jest `addon`.

Ręczne budowanie:

1. Spakuj zawartość katalogu `addon`, nie zewnętrzny katalog projektu.
2. Zmień nazwę archiwum na `globalSonicPitch-<wersja>.nvda-addon`.

Przykład PowerShell:

```powershell
New-Item -ItemType Directory -Path .\dist -Force | Out-Null
Compress-Archive -Path .\addon\* -DestinationPath .\dist\globalSonicPitch.zip -Force
Move-Item .\dist\globalSonicPitch.zip .\dist\globalSonicPitch-0.4.18.nvda-addon -Force
```

Sprawdzenie składni:

```powershell
python -m py_compile addon\globalPlugins\globalSonicPitch.py addon\sapi32HostDrivers\sapi5.py addon\installTasks.py
```

## Układ Repozytorium

- `addon/manifest.ini` - manifest dodatku NVDA.
- `addon/installTasks.py` - opcjonalny komunikat wsparcia podczas instalacji.
- `addon/globalPlugins/globalSonicPitch.py` - główny plugin.
- `addon/globalPlugins/sonicPitchNative/` - dołączone natywne DLL-e Sonic i
  metadane licencji Apache 2.0.
- `addon/sapi32HostDrivers/` - wrapper rejestrowany tylko dla 32-bitowego hosta
  SAPI5 w NVDA.
- `addon/doc/en/readme.md` - angielska pomoc dodatku.
- `addon/doc/pl/readme.md` - polska pomoc dodatku.
- `docs/technical-notes.md` - notatki techniczne dla utrzymania.
- `TESTING.md` - macierz testów.
- `CHANGELOG.md` - historia zmian.
