# Global Sonic Pitch

Global Sonic Pitch pridáva samostatné nastavenie `Sonic pitch` a používa ho
cez spracovanie zvuku Sonic. Bežné nastavenie NVDA `Výška` zostáva natívnym
nastavením výšky aktívneho syntetizéra. Doplnok pracuje globálne so
syntetizérmi, ktorých zvuk reči prechádza hlavným procesom NVDA, a podporuje
štandardný `sapi5_32` v 64-bitovom NVDA cez malý wrapper 32-bitového hosta.

## Čo Doplnok Robí

- Pridáva panel nastavení `Global Sonic Pitch`.
- Nepridáva nové syntetizéry do dialógu výberu syntetizéra.
- Pridáva nastavenie `Sonic pitch` do štandardných nastavení hlasu a kruhu
  nastavení syntetizéra, keď je globálny Sonic pitch zapnutý a aktívny
  syntetizér je podporovaný.
- Bežné nastavenie NVDA `Výška` naďalej ovláda natívnu výšku syntetizéra.
- `Sonic pitch` je samostatné nastavenie Sonic.
- `Sonic pitch` sa ukladá osobitne pre každý podporovaný syntetizér a vybraný
  hlas.
- Spracúva zvuk reči cez Sonic.
- Podporuje štandardný `sapi5_32` v 64-bitovom NVDA bez pridania nového
  syntetizéra.
- Obsahuje voliteľný externý odkaz na podporu autora.
- Počas inštalácie sa môže opýtať, či chcete otvoriť stránku podpory.

## Rýchly Štart

1. Vyberte bežný syntetizér NVDA, napríklad RHVoice, eSpeak, OneCore,
   64-bitový SAPI5 alebo štandardný `sapi5_32`.
2. Otvorte nastavenia NVDA.
3. Vyberte kategóriu `Global Sonic Pitch`.
4. Zapnite `Enable global Sonic pitch`.
5. Meníte spracovanie Sonic pomocou nastavenia hlasu `Sonic pitch`, kruhu
   nastavení syntetizéra alebo priradeného vstupného gesta.
6. Natívnu výšku hlasu meníte bežným nastavením NVDA `Výška`, ak chcete používať
   obe nastavenia naraz.

Hodnota `Sonic pitch` `50` je neutrálna. Hodnoty pod `50` znižujú reč cez
Sonic a hodnoty nad `50` ju zvyšujú. Každý podporovaný syntetizér a vybraný
hlas má vlastnú hodnotu `Sonic pitch`.

## Nastavenia

- `Enable global Sonic pitch` - zapína globálne spracovanie Sonic pitch.
- `Enable debug logging` - zapisuje podrobné položky do logu NVDA.
- `Support the author` - otvorí externú stránku podpory BuyCoffee.

Bežné nastavenie NVDA `Výška` zostáva natívnou výškou syntetizéra. `Sonic
pitch` je samostatné nastavenie doplnku uložené pre podporovaný syntetizér a
hlas.

Panel doplnku je dostupný vždy. Samostatný posuvník `Sonic pitch` sa pridáva do
dialógu hlasu a kruhu nastavení syntetizéra iba vtedy, keď je zapnuté `Enable
global Sonic pitch`. Keď je globálny Sonic pitch vypnutý, nastavenie sa z týchto
ovládacích prvkov odstráni. Ak používate doplnok `Synth ring settings
selector`, `sonicPitch` sa pridá do jeho zoznamu nastavení.

V globálnom paneli doplnku úmyselne nie je posuvník `Sonic pitch`. Globálny
panel zapína zvukový procesor; hodnota `Sonic pitch` sa mení v nastaveniach
hlasu, v kruhu nastavení syntetizéra alebo priradenými gestami pre aktuálny
podporovaný syntetizér a hlas.

V časti Vstupné gestá kategória `Global Sonic Pitch` umožňuje priradiť gestá na
zapnutie, oznámenie stavu, otvorenie stránky podpory, zvýšenie, zníženie a
obnovenie Sonic pitch pre aktuálny podporovaný syntetizér a hlas.

## Podpora Autora

Tlačidlo `Support the author` a príkaz `Open support page` vo vstupných gestách
otvárajú:

```text
https://buycoffee.to/kazimierz-parzych
```

Ide o dobrovoľnú externú podporu. Doplnok nespracúva platby, neukladá platobné
údaje a neodomyká funkcie na základe podpory.

Počas inštalácie alebo aktualizácie môže Sonic Pitch zobraziť malú voliteľnú
správu podpory. `Áno` otvorí rovnakú stránku v predvolenom prehliadači. `Nie`
pokračuje v inštalácii bez zmeny správania doplnku.

## Kompatibilita

Doplnok by mal fungovať s RHVoice, eSpeak, OneCore, 64-bitovým SAPI5,
štandardným `sapi5_32` v 64-bitovom NVDA, eSpeak-NG SAPI cez SAPI5 a podobnými
syntetizérmi, keď ich 16-bitový PCM zvuk reči prechádza hlavným `WavePlayer`
NVDA alebo 32-bitovým hostom SAPI5 NVDA.

Hlasy tretej strany eSpeak-NG SAPI je najprv potrebné nakonfigurovať v
konfiguračnom nástroji eSpeak-NG SAPI. Aktuálne verzie doplnku neopravujú
enumeráciu hlasov SAPI, nemenia súbory NVDA a nezapisujú tokeny hlasov do
registra.

Štandardný `sapi5_32` v 64-bitovom NVDA beží v samostatnom 32-bitovom hoste
syntetizérov. Aktuálne verzie načítajú do tohto hosta pribalený wrapper, takže
štandardný syntetizér NVDA `sapi5_32` dostane rovnakú hodnotu `Sonic pitch`.
Tým sa nemenia súbory NVDA, zoznam hlasov SAPI ani sa nepridáva samostatný
syntetizér.

## Migrácia Zo Starého Doplnku

Starý doplnok `sapi5SonicPitch` pridával samostatné syntetizéry SAPI5 Sonic
Pitch. Aktuálny doplnok `globalSonicPitch` syntetizéry nepridáva. Ak sa v
dialógu syntetizéra stále zobrazuje `SAPI5 32-bit Sonic Pitch` alebo `SAPI5
64-bit Sonic Pitch`, odstráňte starý doplnok `sapi5SonicPitch` a reštartujte
NVDA.

## Overenie Správania

Zapnite `Enable debug logging`, reštartujte NVDA a skontrolujte `%TEMP%\nvda.log`.

Užitočné položky:

- `globalSonicPitch: installed WavePlayer speech feed hook`
- `globalSonicPitch: installed synth Sonic pitch setting hook`
- `globalSonicPitch: added Sonic pitch voice setting`
- `globalSonicPitch: captured Sonic pitch setting`
- `globalSonicPitch: loaded bundled Sonic library`
- `globalSonicPitch: processed speech audio`

Pre štandardný `sapi5_32` je očakávaná položka:

```text
Loaded synthDriver sapi5_32
globalSonicPitch: applied remote SAPI5 32-bit Sonic pitch
```

Log hosta `%TEMP%\nvda_synthDriverHost.*.log` by mal obsahovať aj:

```text
globalSonicPitch sapi5_32 host: set Sonic pitch
```

## Riešenie Problémov

Ak `Sonic pitch` nie je v nastaveniach hlasu, zapnite `Enable global Sonic
pitch` v paneli `Global Sonic Pitch`, potom znovu otvorte nastavenia hlasu
alebo prepnite syntetizér.

Ak sa `Sonic pitch` nemení, skontrolujte, či je globálny režim zapnutý a hodnota
`Sonic pitch` nie je `50`. Pri syntetizéroch v hlavnom procese skontrolujte, či
sa v logu zobrazuje `processed speech audio`. Pri `sapi5_32` hľadajte `applied
remote SAPI5 32-bit Sonic pitch` v `%TEMP%\nvda.log` a `globalSonicPitch
sapi5_32 host: set Sonic pitch` v `%TEMP%\nvda_synthDriverHost.*.log`.

Ak sa pri prepnutí syntetizéra alebo hlasu zdá, že sa `Sonic pitch` vracia na
`50`, je to očakávané, kým nenastavíte hodnotu pre konkrétny syntetizér a hlas.
Hodnoty sa ukladajú osobitne pre každý podporovaný syntetizér a vybraný hlas.

Ak počujete zmenu natívnej výšky syntetizéra, je to očakávané. Nastavenie NVDA
`Výška` ovláda natívnu výšku, zatiaľ čo `Sonic pitch` ovláda iba spracovanie
Sonic.

Ak zostávajú malé medzery vo zvuku, skontrolujte záťaž CPU, menej extrémne
hodnoty `Sonic pitch` a viac ako jeden syntetizér. Aktuálne verzie nemenia už
použitý stream Sonic priamo; zmeny počas aktívnej reči sa použijú na najbližšej
bezpečnej hranici výpovede s novým streamom.

Od verzie 0.4.18 sa hodnoty Sonic pitch ukladajú osobitne pre podporovaný
syntetizér a vybraný hlas. V SAPI5 môžu rôzne hlasy v tom istom syntetizéri
SAPI5 používať rôzne hodnoty Sonic pitch.

## Licencia

Zdrojový kód Global Sonic Pitch je licencovaný pod GNU GPL verzie 2 alebo
novšej. Pribalené natívne binárne súbory Sonic sú externé komponenty pod
licenciou Apache 2.0.

## Logy

- Aktuálny log: `%TEMP%\nvda.log`
- Predchádzajúci log: `%TEMP%\nvda-old.log`
- 32-bitový host: `%TEMP%\nvda_synthDriverHost.*.log`
