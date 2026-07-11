# Global Sonic Pitch

Global Sonic Pitch stosuje wysokość mowy NVDA przez przetwarzanie audio Sonic w
głównym procesie NVDA.

## Działanie

Dodatek dodaje panel ustawień o nazwie Global Sonic Pitch. Nie dodaje żadnych
nowych syntezatorów do okna wyboru syntezatora NVDA.

Po włączeniu dodatek przechwytuje normalne ustawienie wysokości NVDA, utrzymuje
natywną wysokość aktywnego syntezatora neutralnie na 50, jeśli to możliwe, i
stosuje zmianę wysokości na audio mowy przez Sonic.

## Użycie

1. Otwórz ustawienia NVDA.
2. Wybierz Global Sonic Pitch.
3. Włącz globalną wysokość Sonic.
4. Zmieniaj wysokość zwykłymi ustawieniami głosu NVDA albo pierścieniem
   ustawień syntezatora.

Suwak Sonic pitch w panelu dodatku zmienia tę samą wartość wysokości dodatku.

Wysokość 50 jest neutralna. Wartości poniżej 50 obniżają głos, a wartości
powyżej 50 podwyższają głos. Zakres odpowiada mniej więcej -6 do +6 półtonom.

## Uwagi

Dodatek działa tylko dla audio mowy, które trafia do głównego WavePlayer NVDA
jako 16-bitowe PCM. Standardowy syntezator SAPI5 32-bit na 64-bitowym NVDA
działa w osobnym 32-bitowym hoście syntezatorów, więc ten globalny plugin nie
przetwarza jego audio i nie przejmuje jego wysokości.

Jeśli stare syntezatory SAPI5 Sonic Pitch nadal pojawiają się na liście
syntezatorów, usuń starszy dodatek sapi5SonicPitch i zrestartuj NVDA.

Przydatne wpisy w logu: globalSonicPitch, pitch takeover active, captured NVDA
pitch i processed speech audio.
