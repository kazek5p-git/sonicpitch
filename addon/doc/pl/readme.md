# Global Sonic Pitch

Global Sonic Pitch przejmuje normalne ustawienie wysokości mowy NVDA i stosuje
je przez Sonic. Dodatek działa globalnie dla syntezatorów, których audio mowy
przechodzi przez główny proces NVDA.

## Co Robi Dodatek

- Dodaje panel ustawień `Global Sonic Pitch`.
- Nie dodaje nowych syntezatorów do okna wyboru syntezatora.
- Dodaje ustawienie `Sonic pitch` do standardowych ustawień głosu i pierścienia
  ustawień syntezatora, jeśli aktywny syntezator jest obsługiwany.
- Zwykłe ustawienie `Wysokość` NVDA nadal steruje natywną wysokością
  syntezatora.
- `Sonic pitch` jest osobną regulacją Sonic.
- Przetwarza audio mowy przez Sonic.

## Szybki Start

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore albo
   SAPI5 64-bit.
2. Otwórz ustawienia NVDA.
3. Wybierz kategorię `Global Sonic Pitch`.
4. Włącz `Enable global Sonic pitch`.
5. Zmieniaj przetwarzanie Sonic ustawieniem głosu `Sonic pitch` albo suwakiem
   `Sonic pitch` w panelu dodatku.
6. Zmieniaj natywną wysokość normalnym ustawieniem `Wysokość`, jeśli chcesz
   używać obu regulacji równocześnie.

Wysokość `50` jest neutralna. Wartości poniżej `50` obniżają głos, a wartości
powyżej `50` podwyższają głos.

## Ustawienia

- `Enable global Sonic pitch` - włącza globalne przetwarzanie Sonic pitch.
- `Sonic pitch` - ustawia wysokość używaną przez Sonic.
- `Enable debug logging` - zapisuje szczegółowe wpisy do logu NVDA.

Zwykła `Wysokość` w pierścieniu ustawień głosu NVDA pozostaje natywną
wysokością syntezatora. `Sonic pitch` jest osobnym ustawieniem dodatku.

Dodatek próbuje dodać osobny suwak `Sonic pitch` do dialogu `Głos` i do
pierścienia ustawień syntezatora bez modyfikowania rdzenia NVDA. Jeśli używasz
dodatku `Synth ring settings selector`, `sonicPitch` jest dopisywane do jego
listy ustawień.

W `Zdarzeniach wejścia` w kategorii `Global Sonic Pitch` można przypisać gesty
do włączania, odczytu stanu, zwiększania, zmniejszania i resetowania Sonic
pitch.

## Zgodność

Dodatek powinien działać z RHVoice, eSpeak, OneCore, SAPI5 64-bit i podobnymi
syntezatorami, jeśli ich 16-bitowe PCM mowy trafia do głównego `WavePlayer`
NVDA.

Standardowy `sapi5_32` na 64-bitowym NVDA jest celowo pomijany. Działa w osobnym
32-bitowym hoście syntezatorów, więc ten globalny plugin nie może przetwarzać
jego audio.

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

## Rozwiązywanie Problemów

Jeśli wysokość się nie zmienia, upewnij się, że globalny tryb jest włączony, a
wartość pitch nie wynosi `50`. Sprawdź też, czy w logu pojawia się
`processed speech audio`.

Jeśli słychać natywną zmianę wysokości syntezatora, to jest oczekiwane.
`Wysokość` NVDA steruje natywną wysokością, a `Sonic pitch` steruje tylko
przetwarzaniem Sonic.

Jeśli słychać drobne przerwy, sprawdź obciążenie CPU, mniej skrajne wartości
pitch i porównaj kilka syntezatorów. Od wersji 0.3.1 dodatek używa ciągłego
strumienia Sonic, żeby ograniczyć mikroprzerwy między blokami audio.

## Logi

- Aktualny log: `%TEMP%\nvda.log`
- Poprzedni log: `%TEMP%\nvda-old.log`
- Host 32-bit: `%TEMP%\nvda_synthDriverHost.*.log`
