# Global Sonic Pitch

Global Sonic Pitch dodaje osobną regulację `Sonic pitch` i stosuje ją przez
Sonic. Zwykła `Wysokość` NVDA pozostaje natywnym ustawieniem aktywnego
syntezatora. Dodatek działa globalnie dla syntezatorów, których audio mowy
przechodzi przez główny proces NVDA.

## Co Robi Dodatek

- Dodaje panel ustawień `Global Sonic Pitch`.
- Nie dodaje nowych syntezatorów do okna wyboru syntezatora.
- Dodaje ustawienie `Sonic pitch` do standardowych ustawień głosu i pierścienia
  ustawień syntezatora, gdy globalny Sonic pitch jest włączony i aktywny
  syntezator jest obsługiwany.
- Zwykłe ustawienie `Wysokość` NVDA nadal steruje natywną wysokością
  syntezatora.
- `Sonic pitch` jest osobną regulacją Sonic.
- `Sonic pitch` jest zapisywany osobno dla każdego obsługiwanego syntezatora.
- Przetwarza audio mowy przez Sonic.
- Zawiera opcjonalny zewnętrzny link wsparcia autora.
- Może zapytać podczas instalacji, czy otworzyć stronę wsparcia.

## Szybki Start

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore albo
   SAPI5 64-bit.
2. Otwórz ustawienia NVDA.
3. Wybierz kategorię `Global Sonic Pitch`.
4. Włącz `Enable global Sonic pitch`.
5. Zmieniaj przetwarzanie Sonic ustawieniem głosu `Sonic pitch`, pierścieniem
   ustawień syntezatora albo przypisanym gestem wejścia.
6. Zmieniaj natywną wysokość normalnym ustawieniem `Wysokość`, jeśli chcesz
   używać obu regulacji równocześnie.

`Sonic pitch` `50` jest neutralny. Wartości poniżej `50` obniżają głos przez
Sonic, a wartości powyżej `50` podwyższają głos przez Sonic. Każdy obsługiwany
syntezator ma własną wartość `Sonic pitch`.

## Ustawienia

- `Enable global Sonic pitch` - włącza globalne przetwarzanie Sonic pitch.
- `Enable debug logging` - zapisuje szczegółowe wpisy do logu NVDA.
- `Support the author` - otwiera zewnętrzną stronę wsparcia BuyCoffee.

Zwykła `Wysokość` w pierścieniu ustawień głosu NVDA pozostaje natywną
wysokością syntezatora. `Sonic pitch` jest osobnym ustawieniem dodatku
zapisywanym per obsługiwany syntezator.

Panel dodatku jest zawsze dostępny. Osobny suwak `Sonic pitch` jest dodawany do
dialogu `Głos` i pierścienia ustawień syntezatora tylko wtedy, gdy `Enable
global Sonic pitch` jest włączone. Gdy globalny Sonic pitch jest wyłączony,
ustawienie znika z tych kontrolek głosu. Jeśli używasz dodatku `Synth ring
settings selector`, `sonicPitch` jest dopisywane do jego listy ustawień.

W globalnym panelu dodatku celowo nie ma suwaka `Sonic pitch`. Panel globalny
włącza procesor audio, a wartość `Sonic pitch` zmienia się z poziomu ustawień
głosu, pierścienia ustawień syntezatora albo przypisanych gestów dla bieżącego
obsługiwanego syntezatora.

W `Zdarzeniach wejścia` w kategorii `Global Sonic Pitch` można przypisać gesty
do włączania, odczytu stanu, otwierania strony wsparcia, zwiększania,
zmniejszania i resetowania Sonic pitch bieżącego obsługiwanego syntezatora.

## Wsparcie Autora

Przycisk `Support the author` i komenda `Open support page` w `Zdarzeniach
wejścia` otwierają:

```text
https://buycoffee.to/kazimierz-parzych
```

To dobrowolne zewnętrzne wsparcie. Dodatek nie obsługuje płatności, nie zapisuje
danych płatniczych i nie odblokowuje funkcji po wsparciu.

Podczas instalacji albo aktualizacji Sonic Pitch może pokazać mały opcjonalny
komunikat wsparcia. `Yes` otwiera tę samą stronę w domyślnej przeglądarce.
`No` kontynuuje instalację i nie zmienia działania dodatku.

## Zgodność

Dodatek powinien działać z RHVoice, eSpeak, OneCore, SAPI5 64-bit, eSpeak-NG
SAPI przez SAPI5 i podobnymi syntezatorami, jeśli ich 16-bitowe PCM mowy trafia
do głównego `WavePlayer` NVDA.

Zewnętrzne głosy eSpeak-NG SAPI trzeba najpierw skonfigurować w konfiguratorze
eSpeak-NG SAPI. Od wersji 0.4.6 dodatek pomaga NVDA pokazać skonfigurowane
dynamiczne głosy eSpeak-NG SAPI na normalnej liście głosów SAPI5 64-bit. Od
wersji 0.4.7 uzupełnia też standardową listę głosów `sapi5_32`. Dzieje się to
w czasie działania, bez modyfikowania plików NVDA i bez zapisywania tokenów
głosów w rejestrze.

Standardowy `sapi5_32` na 64-bitowym NVDA jest celowo pomijany. Działa w osobnym
32-bitowym hoście syntezatorów, więc ten globalny plugin nie może przetwarzać
jego audio. Dodatek może pokazać skonfigurowane głosy eSpeak-NG SAPI w
`sapi5_32`, ale ta ścieżka nadal nie ma globalnego przetwarzania Sonic.

Standardowy `sapi5` na 32-bitowym NVDA 2025.x też jest celowo pomijany. Logi z
NVDA 2025.3.3 x86 pokazują powtarzalne natywne crashe sterty w `ntdll.dll` z
wyjątkiem `0xc0000374` podczas szybkich zmian Sonic pitch. Wersja 0.4.9 i nowsze
zostawiają SAPI5 działające normalnie na tej linii NVDA, ale nie dodają tam
ustawienia głosu `Sonic pitch`.

## Migracja Ze Starej Wersji

Stary dodatek `sapi5SonicPitch` dodawał osobne syntezatory SAPI5 Sonic Pitch.
Aktualny dodatek `globalSonicPitch` nie dodaje syntezatorów. Jeśli nadal widzisz
`SAPI5 32-bit Sonic Pitch` albo `SAPI5 64-bit Sonic Pitch` w wyborze
syntezatora, usuń stary dodatek `sapi5SonicPitch` i zrestartuj NVDA.

## Sprawdzanie Działania

Włącz `Enable debug logging`, zrestartuj NVDA i sprawdź `%TEMP%\nvda.log`.

Przydatne wpisy:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: processed speech audio`

Dla standardowego `sapi5_32` oczekiwany jest wpis:

```text
Loaded synthDriver sapi5_32
```

Przy skonfigurowanych głosach eSpeak-NG SAPI od wersji 0.4.7 może pojawić się
też wpis:

```text
globalSonicPitch: added 2 eSpeak-NG SAPI dynamic voices to NVDA sapi5_32 voice list
```

## Rozwiązywanie Problemów

Jeśli `Sonic pitch` nie ma w ustawieniach głosu, włącz `Enable global Sonic
pitch` w panelu `Global Sonic Pitch`, a potem otwórz ustawienia głosu ponownie
albo przełącz syntezator.

Jeśli `Sonic pitch` się nie zmienia, upewnij się, że globalny tryb jest
włączony, a wartość `Sonic pitch` nie wynosi `50`. Sprawdź też, czy w logu pojawia się
`processed speech audio`.

Jeśli po przełączeniu syntezatora `Sonic pitch` wraca do `50`, jest to
oczekiwane, dopóki nie ustawisz wartości dla tego konkretnego syntezatora.
Wartości są zapisywane osobno dla każdego obsługiwanego syntezatora.

Jeśli słychać natywną zmianę wysokości syntezatora, to jest oczekiwane.
`Wysokość` NVDA steruje natywną wysokością, a `Sonic pitch` steruje tylko
przetwarzaniem Sonic.

Jeśli słychać drobne przerwy, sprawdź obciążenie CPU, mniej skrajne wartości
`Sonic pitch` i porównaj kilka syntezatorów. Od wersji 0.3.1 dodatek używa
ciągłego strumienia Sonic, żeby ograniczyć mikroprzerwy między blokami audio. Od
wersji 0.4.4 zmiana wysokości podczas aktywnej mowy resetuje procesor Sonic
zamiast zmieniać aktywny strumień w locie, co omija zawieszenia widziane z
niektórymi głosami SAPI5 przy szybkim obniżaniu wysokości. Od wersji 0.4.5
dodatek zmniejsza też blokowanie między wątkami podczas przetwarzania szybkich
głosów SAPI5, takich jak eSpeak-NG SAPI przy prędkości 100.

## Logi

- Aktualny log: `%TEMP%\nvda.log`
- Poprzedni log: `%TEMP%\nvda-old.log`
- Host 32-bit: `%TEMP%\nvda_synthDriverHost.*.log`
