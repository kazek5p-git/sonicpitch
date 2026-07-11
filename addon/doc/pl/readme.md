# SAPI5 Sonic Pitch

Ten dodatek NVDA dodaje osobne sterowniki syntezatora SAPI5 z korekcja
wysokosci przez Sonic:

- SAPI5 32-bit Sonic Pitch
- SAPI5 64-bit Sonic Pitch

Dodatek jest przeznaczony dla glosow SAPI5, ktore ignoruja ustawienie wysokosci
NVDA albo realizuja je slabo. Nie wplywa na OneCore, eSpeak, RHVoice,
Vocalizer ani inne syntezatory.

Wymagane jest NVDA 2025.1 lub nowsze. Dodatek przetestowano na NVDA 2026.2 beta,
Python 3.13, 64-bit.

## Dzialanie wysokosci

Pitch 50 jest neutralny. Zakres NVDA 0..100 mapuje sie na okolo -6..+6
poltonow, a potem na wspolczynnik Sonic. Wspolczynnik jest ograniczony do
0.70..1.45.

Sterownik neutralizuje SAPI XML pitch przez zwracanie 0 z `_percentToPitch`.
Zapobiega to podwojnej zmianie wysokosci, ale dynamiczne komendy wysokosci w
sekwencji mowy moga byc rowniez zneutralizowane.

## Rozdzielenie 32-bit i 64-bit

Na 64-bitowym NVDA sterownik 64-bit dziedziczy po `synthDrivers.sapi5.SynthDriver`.
Sterownik 32-bit uzywa `SynthDriverProxy32` oraz prywatnego modulu hosta, aby
Sonic pitch byl ustawiany w procesie 32-bitowego hosta SAPI5.

Na 32-bitowym NVDA sterownik 32-bit dziedziczy po lokalnym
`synthDrivers.sapi5.SynthDriver`. Sterownik 64-bit odmawia zaladowania.

Kazdy sterownik pokazuje tylko glosy dostepne dla wlasnej bitowosci SAPI5.

## Ograniczenia

- Dodatek nie zawiera wlasnych bibliotek Sonic DLL ani innych binariow.
- Uzywane sa prywatne elementy NVDA zwiazane z WASAPI i Sonic.
- Jesli NVDA zmieni `sonicStream` albo `_initWasapiAudio`, dodatek moze wymagac zmian.
- Starsza sciezka audio bez WASAPI nie udostepnia `sonicStream`, wiec Sonic pitch nie zadziala.
