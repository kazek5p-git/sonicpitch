# Global Sonic Pitch

Global Sonic Pitch dodaje osobną regulację `Sonic pitch` dla obsługiwanych
syntezatorów NVDA. Zmienia wysokość mowy przez przetwarzanie Sonic, a zwykłe
ustawienie NVDA `Wysokość` pozostaje natywną wysokością syntezatora.

## Co Dodaje

- Panel ustawień `Global Sonic Pitch`.
- Osobne ustawienie głosu `Sonic pitch`, gdy globalne przetwarzanie jest
  włączone.
- Wartości Sonic pitch osobne dla syntezatora i głosu.
- Przetwarzanie obsługiwanego audio mowy w głównej ścieżce audio NVDA.
- Obsługę standardowego `sapi5_32` na 64-bitowym NVDA przez dołączony wrapper
  hosta 32-bitowego.
- Opcjonalne logowanie debugowania.
- Opcjonalny link wsparcia autora.

Dodatek nie dodaje zastępczego syntezatora do okna wyboru syntezatora i nie
modyfikuje plików NVDA na dysku.

## Szybki Start

1. Wybierz normalny syntezator NVDA, na przykład RHVoice, eSpeak, OneCore,
   SAPI5 64-bit albo standardowy `sapi5_32`.
2. Otwórz ustawienia NVDA.
3. Wybierz `Global Sonic Pitch`.
4. Włącz `Enable global Sonic pitch`.
5. Otwórz ponownie ustawienia głosu albo użyj pierścienia ustawień syntezatora.
6. Ustaw `Sonic pitch`.

Wartość `50` jest neutralna. Niższe wartości obniżają mowę przez Sonic, a
wyższe wartości ją podwyższają.

## Ustawienia

- `Enable global Sonic pitch` włącza albo wyłącza przetwarzanie Sonic pitch.
- `Enable debug logging` zapisuje szczegółowe wpisy dodatku do logu NVDA.
- `Support the author` otwiera zewnętrzną stronę wsparcia.

Panel dodatku steruje tylko globalnym przetwarzaniem i diagnostyką. Wartość
`Sonic pitch` zmienia się w ustawieniach głosu, pierścieniu ustawień
syntezatora albo przypisanymi gestami wejścia.

Gdy globalne przetwarzanie jest wyłączone, ustawienie `Sonic pitch` znika z
ustawień głosu i pierścienia ustawień syntezatora.

## Natywna Wysokość I Sonic Pitch

Zwykłe ustawienie NVDA `Wysokość` pozostaje natywną wysokością syntezatora.
`Sonic pitch` jest dodatkową wartością przetwarzania należącą do tego dodatku.

Jeśli obie regulacje są poza `50`, słychać wynik łączony:

- natywną wysokość syntezatora z normalnego ustawienia `Wysokość`;
- przetwarzanie Sonic z ustawienia `Sonic pitch`.

## Wartości Per Głos

`Sonic pitch` jest zapisywany osobno dla każdego obsługiwanego syntezatora i
wybranego głosu. Na przykład dwa głosy w SAPI5 mogą mieć różne wartości Sonic
pitch.

Nowe głosy zaczynają od `50`, dopóki ich nie zmienisz. Powrót do głosu
przywraca wartość zapisaną dla tego głosu.

## Gesty Wejścia

Kategoria `Global Sonic Pitch` w zdarzeniach wejścia zawiera komendy do:

- włączania i wyłączania globalnego Sonic pitch;
- odczytu bieżącego stanu;
- otwierania strony wsparcia;
- zwiększania Sonic pitch dla bieżącego syntezatora i głosu;
- zmniejszania Sonic pitch dla bieżącego syntezatora i głosu;
- resetowania Sonic pitch dla bieżącego syntezatora i głosu.

Gesty nie są przypisane domyślnie.

## Zgodność

Oczekiwane obsługiwane ścieżki:

- RHVoice, jeśli audio mowy trafia do głównego `WavePlayer` NVDA.
- eSpeak NG w głównym procesie NVDA.
- OneCore w głównym procesie NVDA.
- SAPI5 64-bit, jeśli używa normalnej ścieżki audio NVDA.
- Standardowy `sapi5_32` na 64-bitowym NVDA przez dołączony wrapper hosta
  32-bitowego.
- Inne syntezatory, które wysyłają zgodne audio mowy przez NVDA.

Zewnętrzne głosy eSpeak-NG SAPI trzeba najpierw skonfigurować w ich własnym
narzędziu konfiguracyjnym. Dodatek nie patchuje enumeracji głosów SAPI, nie
zapisuje tokenów głosów w rejestrze i nie zmienia listy głosów SAPI.

## Standardowy SAPI5 32-bit Na 64-bitowym NVDA

Standardowy `sapi5_32` na 64-bitowym NVDA działa w osobnym 32-bitowym hoście
syntezatorów. Global Sonic Pitch ładuje w tym hoście dołączony wrapper, aby
standardowy syntezator NVDA `sapi5_32` otrzymał bieżącą wartość `Sonic pitch`.

To zachowuje normalną pozycję syntezatora NVDA `sapi5_32`. Dodatek nie dodaje
nowego syntezatora i nie podmienia plików NVDA.

## Link Wsparcia

Przycisk `Support the author` i komenda `Open support page` otwierają:

```text
https://buycoffee.to/kazimierz-parzych
```

Wsparcie jest dobrowolne. Dodatek nie obsługuje płatności, nie zapisuje danych
płatniczych i nie odblokowuje funkcji po wsparciu.

Podczas instalacji albo aktualizacji dodatek może pokazać mały opcjonalny
komunikat wsparcia. `Yes` otwiera tę samą stronę w domyślnej przeglądarce.
`No` kontynuuje instalację bez zmiany działania dodatku.

## Rozwiązywanie Problemów

Jeśli `Sonic pitch` nie ma w ustawieniach głosu, włącz `Enable global Sonic
pitch`, a potem otwórz ustawienia głosu ponownie albo przełącz syntezator.

Jeśli zmiana `Sonic pitch` nie daje słyszalnego efektu, upewnij się, że globalne
przetwarzanie jest włączone, a wartość nie wynosi `50`.

Jeśli po przełączeniu syntezatora albo głosu `Sonic pitch` wygląda jak
zresetowany, ustaw wartość dla tego syntezatora i głosu. Wartości są zapisywane
niezależnie.

Jeśli standardowy `sapi5_32` na 64-bitowym NVDA nie pokazuje `Sonic pitch`,
zrestartuj NVDA albo przełącz się z `sapi5_32` na inny syntezator i wróć.

Jeśli brakuje zewnętrznego głosu SAPI, skonfiguruj go najpierw w narzędziu tego
pakietu głosowego, a potem zrestartuj NVDA.

## Logi

Przydatne pliki logów:

- Aktualny log NVDA: `%TEMP%\nvda.log`
- Poprzedni log NVDA: `%TEMP%\nvda-old.log`
- Logi hosta 32-bitowego: `%TEMP%\nvda_synthDriverHost.*.log`

Przydatne frazy:

- `globalSonicPitch`
- `added Sonic pitch voice setting`
- `captured Sonic pitch setting`
- `processed speech audio`
- `applied remote SAPI5 32-bit Sonic pitch`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`

## Licencja

Kod źródłowy Global Sonic Pitch jest licencjonowany na GNU GPL w wersji 2 lub
nowszej. Dołączone natywne biblioteki Sonic są zewnętrznymi komponentami na
licencji Apache 2.0.
