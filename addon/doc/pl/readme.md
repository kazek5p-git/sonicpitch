# Global Sonic Pitch

Global Sonic Pitch przejmuje normalne ustawienie wysokości mowy NVDA i stosuje
je przez Sonic. Dodatek działa globalnie dla syntezatorów, których audio mowy
przechodzi przez główny proces NVDA.

## Co Robi Dodatek

- Dodaje panel ustawień `Global Sonic Pitch`.
- Nie dodaje nowych syntezatorów do okna wyboru syntezatora.
- Po włączeniu przechwytuje normalne ustawienie `Wysokość` NVDA.
- Utrzymuje natywną wysokość aktywnego syntezatora neutralnie na `50`, jeśli
  dany sterownik na to pozwala.
- Przetwarza audio mowy przez Sonic.

## Szybki Start

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore albo
   SAPI5 64-bit.
2. Otwórz ustawienia NVDA.
3. Wybierz kategorię `Global Sonic Pitch`.
4. Włącz `Enable global Sonic pitch`.
5. Zmieniaj wysokość zwykłym ustawieniem głosu NVDA albo suwakiem
   `Sonic pitch`.

Wysokość `50` jest neutralna. Wartości poniżej `50` obniżają głos, a wartości
powyżej `50` podwyższają głos.

## Ustawienia

- `Enable global Sonic pitch` - włącza globalne przejęcie wysokości.
- `Sonic pitch` - ustawia wysokość używaną przez Sonic.
- `Enable debug logging` - zapisuje szczegółowe wpisy do logu NVDA.

Gdy tryb globalny jest włączony, zwykły pierścień ustawień głosu NVDA zmienia
tę samą wartość co suwak `Sonic pitch`.

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
- `globalSonicPitch: installed synth pitch takeover hook`
- `globalSonicPitch: pitch takeover active`
- `globalSonicPitch: captured NVDA pitch`
- `globalSonicPitch: processed speech audio`

Dla standardowego `sapi5_32` oczekiwany jest wpis:

```text
globalSonicPitch: pitch takeover not available for synth=sapi5_32
```

## Rozwiązywanie Problemów

Jeśli wysokość się nie zmienia, upewnij się, że globalny tryb jest włączony, a
wartość pitch nie wynosi `50`. Sprawdź też, czy w logu pojawia się
`processed speech audio`.

Jeśli słychać natywną zmianę wysokości syntezatora, sprawdź w logu wpis
`pitch takeover active`. Brak tego wpisu oznacza, że dodatek nie mógł przejąć
ustawienia pitch danego sterownika.

Jeśli słychać drobne przerwy, sprawdź obciążenie CPU, mniej skrajne wartości
pitch i porównaj kilka syntezatorów. Od wersji 0.3.1 dodatek używa ciągłego
strumienia Sonic, żeby ograniczyć mikroprzerwy między blokami audio.

## Logi

- Aktualny log: `%TEMP%\nvda.log`
- Poprzedni log: `%TEMP%\nvda-old.log`
- Host 32-bit: `%TEMP%\nvda_synthDriverHost.*.log`
