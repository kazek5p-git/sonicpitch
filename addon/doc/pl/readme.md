# SAPI5 Sonic Pitch

SAPI5 Sonic Pitch dodaje osobne syntezatory SAPI5, które stosują ustawienie
wysokości NVDA przez wewnętrzne przetwarzanie audio Sonic. Zawiera też
eksperymentalny globalny procesor Sonic dla audio mowy PCM.

## Dodane Syntezatory

- SAPI5 32-bit Sonic Pitch
- SAPI5 64-bit Sonic Pitch

To są osobne syntezatory. Dodatek nie modyfikuje standardowych syntezatorów
SAPI5 32-bit ani SAPI5 64-bit wbudowanych w NVDA.

Procesor globalny jest domyślnie wyłączony. Można go włączyć w ustawieniach
NVDA, w kategorii SAPI5 Sonic Pitch.

## Cel

Niektóre głosy SAPI5 ignorują normalne ustawienie wysokości NVDA albo realizują
je w sposób, który brzmi słabo. Ten dodatek utrzymuje SAPI XML pitch w pozycji
neutralnej i stosuje globalną wysokość przez Sonic.

Dodatek wpływa tylko na własne syntezatory Sonic Pitch. Nie wpływa na OneCore,
eSpeak, RHVoice, Vocalizer ani inne sterowniki syntezatorów, chyba że włączysz
opcjonalny procesor globalny.

## Wymagania

- NVDA 2025.1 lub nowsze.
- Windows z zainstalowanymi głosami SAPI5.
- Wyjście audio NVDA korzystające z nowoczesnej ścieżki WASAPI/Sonic.
- Dla głosów 32-bitowych na 64-bitowym NVDA potrzebny jest 32-bitowy host
  syntezatorów NVDA.

## Użycie

1. Otwórz okno wyboru syntezatora w NVDA.
2. Wybierz SAPI5 32-bit Sonic Pitch albo SAPI5 64-bit Sonic Pitch.
3. Otwórz ustawienia głosu NVDA.
4. Zmieniaj wysokość zwykłym ustawieniem wysokości.

Wysokość 50 jest neutralna. Wartości poniżej 50 obniżają głos, a wartości
powyżej 50 podwyższają głos. Pełny zakres wysokości NVDA odpowiada mniej więcej
-6 do +6 półtonom i jest ograniczony do współczynnika Sonic 0.70..1.45.

Tempo, głośność, wybór głosu i rate boost nadal obsługuje normalna logika
sterownika SAPI5 w NVDA.

## Globalny Sonic Pitch

Procesor globalny podpina się w czasie działania do speech `WavePlayer` w NVDA.
Przetwarza 16-bitowe bloki PCM przez Sonic i przepuszcza oryginalne audio, jeśli
przetwarzanie się nie powiedzie.

Domyślnie pomija własne syntezatory SAPI5 Sonic Pitch, żeby uniknąć podwójnego
przetwarzania. Do najczystszego testu z eSpeak, RHVoice, OneCore albo
Vocalizerem ustaw natywną wysokość wybranego syntezatora neutralnie i używaj
globalnego ustawienia wysokości w panelu SAPI5 Sonic Pitch.

Standardowy syntezator SAPI5 32-bit nie jest filtrowany globalnie na 64-bitowym
NVDA, bo działa w osobnym 32-bitowym hoście syntezatorów NVDA. Dla głosów SAPI5
32-bit użyj SAPI5 32-bit Sonic Pitch.

## Głosy 32-bit I 64-bit

Windows przechowuje głosy SAPI5 32-bit i 64-bit osobno. Głos 32-bitowy może nie
pojawić się w syntezatorze 64-bitowym, a głos 64-bitowy może nie pojawić się w
syntezatorze 32-bitowym.

Na 64-bitowym NVDA syntezator 32-bit Sonic Pitch działa przez 32-bitowy host
syntezatorów NVDA. Syntezator 64-bit Sonic Pitch działa bezpośrednio w NVDA.

## Rozwiązywanie Problemów

Jeśli syntezator Sonic Pitch nie pojawia się na liście, sprawdź, czy odpowiednia
wbudowana ścieżka SAPI5 jest dostępna w NVDA.

Jeśli nie ładuje się syntezator 32-bit Sonic Pitch, najpierw przetestuj
wbudowany syntezator Microsoft Speech API version 5 (32 bit). Jeśli wbudowany
syntezator też nie działa, problem nie dotyczy tylko tego dodatku.

Jeśli standardowe syntezatory SAPI5 przestają działać tylko wtedy, gdy ten
dodatek jest włączony, wyłącz globalne przetwarzanie Sonic w panelu
SAPI5 Sonic Pitch i sprawdź log NVDA. Dodatek nie powinien łatać standardowych
sterowników SAPI5.

Przydatne logi:

- %TEMP%\nvda.log
- %TEMP%\nvda-old.log
- %TEMP%\nvda_synthDriverHost.*.log

W logach szukaj wpisów sapi5SonicPitch, sapi5SonicPitch32,
sapi5SonicPitch64, sapi5SonicPitchGlobal albo Sonic pitch unavailable.

## Ograniczenia

- Dodatek używa prywatnych wewnętrznych mechanizmów NVDA związanych z WASAPI i
  Sonic.
- Procesor globalny podpina się w czasie działania do `nvwave.WavePlayer.feed`.
- Przyszłe zmiany w NVDA mogą wymagać aktualizacji dodatku.
- Starsze ścieżki audio bez Sonic nie mogą używać tej metody zmiany wysokości.
- Osadzone komendy wysokości mogą być neutralizowane, żeby uniknąć podwójnego
  przetwarzania wysokości.
