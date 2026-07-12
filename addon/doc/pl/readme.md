# Global Sonic Pitch

Global Sonic Pitch dodaje osobną regulację `Sonic pitch` i stosuje ją przez
Sonic. Zwykła `Wysokość` NVDA pozostaje natywnym ustawieniem aktywnego
syntezatora. Dodatek działa globalnie dla syntezatorów, których audio mowy
przechodzi przez główny proces NVDA, a standardowy `sapi5_32` na 64-bitowym
NVDA obsługuje przez mały wrapper 32-bitowego hosta.

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
- Obsługuje standardowy `sapi5_32` na 64-bitowym NVDA bez dodawania nowego
  syntezatora.
- Zawiera opcjonalny zewnętrzny link wsparcia autora.
- Może zapytać podczas instalacji, czy otworzyć stronę wsparcia.

## Szybki Start

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore,
   SAPI5 64-bit albo standardowy `sapi5_32`.
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

Dodatek powinien działać z RHVoice, eSpeak, OneCore, SAPI5 64-bit,
standardowym `sapi5_32` na 64-bitowym NVDA, eSpeak-NG SAPI przez SAPI5 i
podobnymi syntezatorami, jeśli ich 16-bitowe PCM mowy trafia do głównego
`WavePlayer` NVDA albo do 32-bitowego hosta SAPI5 NVDA.

Zewnętrzne głosy eSpeak-NG SAPI trzeba najpierw skonfigurować w konfiguratorze
eSpeak-NG SAPI. Aktualne wersje dodatku nie patchują enumeracji głosów SAPI,
nie modyfikują plików NVDA i nie zapisują tokenów głosów w rejestrze.

Standardowy `sapi5_32` na 64-bitowym NVDA działa w osobnym 32-bitowym hoście
syntezatorów. Aktualne wersje ładują w tym hoście dołączony wrapper, dzięki
czemu standardowy syntezator NVDA `sapi5_32` dostaje tę samą wartość `Sonic
pitch`. Nie modyfikuje to plików NVDA, nie zmienia listy głosów SAPI i nie
dodaje osobnego syntezatora.

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
- `globalSonicPitch: loaded bundled Sonic library`
- `globalSonicPitch: processed speech audio`

Dla standardowego `sapi5_32` oczekiwany jest wpis:

```text
Loaded synthDriver sapi5_32
globalSonicPitch: applied remote SAPI5 32-bit Sonic pitch
```

W logu hosta `%TEMP%\nvda_synthDriverHost.*.log` powinien też pojawić się wpis:

```text
globalSonicPitch sapi5_32 host: set Sonic pitch
```

## Rozwiązywanie Problemów

Jeśli `Sonic pitch` nie ma w ustawieniach głosu, włącz `Enable global Sonic
pitch` w panelu `Global Sonic Pitch`, a potem otwórz ustawienia głosu ponownie
albo przełącz syntezator.

Jeśli `Sonic pitch` się nie zmienia, upewnij się, że globalny tryb jest
włączony, a wartość `Sonic pitch` nie wynosi `50`. Dla syntezatorów z głównego
procesu sprawdź, czy w logu pojawia się `processed speech audio`. Dla
`sapi5_32` sprawdź `applied remote SAPI5 32-bit Sonic pitch` w `%TEMP%\nvda.log`
i `globalSonicPitch sapi5_32 host: set Sonic pitch` w
`%TEMP%\nvda_synthDriverHost.*.log`.

Jeśli po przełączeniu syntezatora `Sonic pitch` wraca do `50`, jest to
oczekiwane, dopóki nie ustawisz wartości dla tego konkretnego syntezatora.
Wartości są zapisywane osobno dla każdego obsługiwanego syntezatora.

Jeśli słychać natywną zmianę wysokości syntezatora, to jest oczekiwane.
`Wysokość` NVDA steruje natywną wysokością, a `Sonic pitch` steruje tylko
przetwarzaniem Sonic.

Jeśli słychać drobne przerwy, sprawdź obciążenie CPU, mniej skrajne wartości
`Sonic pitch` i porównaj kilka syntezatorów. Od wersji 0.3.1 dodatek używa
ponownie ciągłego strumienia Sonic, dopóki format audio i wybrany pitch pozostają
takie same. Aktualne wersje nie przestrajają już użytego strumienia Sonic w
locie; zmiany podczas aktywnej mowy są stosowane od następnej bezpiecznej
granicy wypowiedzi z użyciem świeżego strumienia. To omija zawieszenia widziane
z niektórymi głosami SAPI5 przy szybkim obniżaniu wysokości. Od wersji 0.4.5
dodatek zmniejsza też blokowanie między wątkami podczas przetwarzania szybkich
głosów SAPI5, takich jak eSpeak-NG SAPI przy prędkości 100.

Od wersji 0.4.10 dodatek używa dołączonych natywnych bibliotek Sonic 32-bit i
64-bit. W 32-bitowych procesach NVDA strumienie Sonic są utrzymywane przy życiu
zamiast przekazywania ich do natywnego `sonicDestroyStream`, co omija
odtworzony natywny crash sterty na NVDA 2025.3.3 x86 z SAPI5.

Od wersji 0.4.11 krótkie komunikaty po powtarzanych zmianach PageUp/PageDown
pewniej używają najnowszej wartości `Sonic pitch`.

Od wersji 0.4.12 dokumentacja repozytorium zawiera pliki licencji, notatki o
zewnętrznych bibliotekach Sonic i notatki do zgłoszenia w NVDA Add-on Store.

Od wersji 0.4.13 standardowy `sapi5_32` na 64-bitowym NVDA jest sterowany przez
dołączony wrapper 32-bitowego hosta. Ta sama wersja poprawia zachowanie dialogu
`Głos`: OK albo Zastosuj zapisuje podglądaną wartość `Sonic pitch`, a Escape
albo Anuluj przywraca poprzednią wartość.

Od wersji 0.4.14 szybkie zmiany `Sonic pitch` dla standardowego `sapi5_32` na
64-bitowym NVDA są stosowane na bezpiecznych granicach mowy w hoście 32-bitowym.
Host serializuje też operacje strumienia Sonic, co zapobiega wyciszaniu zdalnej
ścieżki SAPI przy szybkim ruszaniu suwakiem.

## Licencja

Kod źródłowy Global Sonic Pitch jest licencjonowany na GNU GPL w wersji 2 lub
nowszej. Dołączone natywne biblioteki Sonic są zewnętrznymi komponentami na
licencji Apache 2.0.

## Logi

- Aktualny log: `%TEMP%\nvda.log`
- Poprzedni log: `%TEMP%\nvda-old.log`
- Host 32-bit: `%TEMP%\nvda_synthDriverHost.*.log`
