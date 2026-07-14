# Global Sonic Pitch

Global Sonic Pitch pridáva samostatné nastavenie `Sonic pitch` pre podporované
syntetizéry NVDA. Mení výšku reči cez spracovanie Sonic a bežné nastavenie
NVDA `Výška` ponecháva ako natívnu výšku syntetizéra.

## Čo Pridáva

- Panel nastavení `Global Sonic Pitch`.
- Samostatné nastavenie hlasu `Sonic pitch`, keď je globálne spracovanie
  zapnuté.
- Hodnoty Sonic pitch osobitne pre syntetizér a hlas.
- Spracovanie podporovaného zvuku reči v hlavnej zvukovej ceste NVDA.
- Podporu štandardného `sapi5_32` v 64-bitovom NVDA cez pribalený wrapper
  32-bitového hosta.
- Voliteľné ladiace logovanie.
- Voliteľný odkaz na podporu autora.

Doplnok nepridáva náhradný syntetizér do dialógu výberu syntetizéra a nemení
súbory NVDA na disku.

## Rýchly Štart

1. Vyberte bežný syntetizér NVDA, napríklad RHVoice, eSpeak, OneCore,
   64-bitový SAPI5 alebo štandardný `sapi5_32`.
2. Otvorte nastavenia NVDA.
3. Vyberte `Global Sonic Pitch`.
4. Zapnite `Enable global Sonic pitch`.
5. Znovu otvorte nastavenia hlasu alebo použite kruh nastavení syntetizéra.
6. Nastavte `Sonic pitch`.

Hodnota `50` je neutrálna. Nižšie hodnoty znižujú reč cez Sonic a vyššie
hodnoty ju zvyšujú.

## Nastavenia

- `Enable global Sonic pitch` zapína alebo vypína spracovanie Sonic pitch.
- `Enable debug logging` zapisuje podrobné položky doplnku do logu NVDA.
- `Support the author` otvorí externú stránku podpory.

Panel doplnku ovláda iba globálne spracovanie a diagnostiku. Hodnota `Sonic
pitch` sa mení v nastaveniach hlasu, v kruhu nastavení syntetizéra alebo
priradenými vstupnými gestami.

Keď je globálne spracovanie vypnuté, nastavenie `Sonic pitch` sa odstráni z
nastavení hlasu a kruhu nastavení syntetizéra.

## Natívna Výška A Sonic Pitch

Bežné nastavenie NVDA `Výška` zostáva natívnou výškou syntetizéra. `Sonic
pitch` je dodatočná hodnota spracovania patriaca tomuto doplnku.

Ak sú obe nastavenia mimo `50`, počujete kombinovaný výsledok:

- natívnu výšku syntetizéra z bežného nastavenia `Výška`;
- spracovanie Sonic z nastavenia `Sonic pitch`.

## Hodnoty Pre Jednotlivé Hlasy

`Sonic pitch` sa ukladá osobitne pre každý podporovaný syntetizér a vybraný
hlas. Napríklad dva hlasy v SAPI5 môžu mať rozdielne hodnoty Sonic pitch.

Nové hlasy začínajú na `50`, kým ich nezmeníte. Návrat k hlasu obnoví hodnotu
uloženú pre tento hlas.

## Vstupné Gestá

Kategória `Global Sonic Pitch` vo vstupných gestách obsahuje príkazy na:

- zapnutie a vypnutie globálneho Sonic pitch;
- oznámenie aktuálneho stavu;
- otvorenie stránky podpory;
- zvýšenie Sonic pitch pre aktuálny syntetizér a hlas;
- zníženie Sonic pitch pre aktuálny syntetizér a hlas;
- obnovenie Sonic pitch pre aktuálny syntetizér a hlas.

Gestá nie sú predvolene priradené.

## Kompatibilita

Očakávané podporované cesty:

- RHVoice, ak zvuk reči prechádza do hlavného `WavePlayer` NVDA.
- eSpeak NG v hlavnom procese NVDA.
- OneCore v hlavnom procese NVDA.
- 64-bitový SAPI5, ak používa bežnú zvukovú cestu NVDA.
- Štandardný `sapi5_32` v 64-bitovom NVDA cez pribalený wrapper 32-bitového
  hosta.
- Iné syntetizéry, ktoré posielajú kompatibilný zvuk reči cez NVDA.

Hlasy tretej strany eSpeak-NG SAPI treba najprv nakonfigurovať v ich vlastnom
konfiguračnom nástroji. Doplnok neopravuje enumeráciu hlasov SAPI, nezapisuje
tokeny hlasov do registra a nemení zoznam hlasov SAPI.

## Štandardný SAPI5 32-bit V 64-bitovom NVDA

Štandardný `sapi5_32` v 64-bitovom NVDA beží v samostatnom 32-bitovom hoste
syntetizérov. Global Sonic Pitch načíta v tomto hoste pribalený wrapper, aby
štandardný syntetizér NVDA `sapi5_32` dostal aktuálnu hodnotu `Sonic pitch`.

Tým sa zachováva bežná položka syntetizéra NVDA `sapi5_32`. Doplnok nepridáva
nový syntetizér a nenahrádza súbory NVDA.

## Odkaz Na Podporu

Tlačidlo `Support the author` a príkaz `Open support page` otvárajú:

```text
https://buycoffee.to/kazimierz-parzych
```

Podpora je dobrovoľná. Doplnok nespracúva platby, neukladá platobné údaje a
neodomyká funkcie na základe podpory.

Počas inštalácie alebo aktualizácie môže doplnok zobraziť malú voliteľnú správu
podpory. `Yes` otvorí rovnakú stránku v predvolenom prehliadači. `No` pokračuje
v inštalácii bez zmeny správania doplnku.

## Riešenie Problémov

Ak `Sonic pitch` nie je v nastaveniach hlasu, zapnite `Enable global Sonic
pitch`, potom znovu otvorte nastavenia hlasu alebo prepnite syntetizér.

Ak zmena `Sonic pitch` nemá počuteľný efekt, skontrolujte, či je globálne
spracovanie zapnuté a hodnota nie je `50`.

Ak sa po prepnutí syntetizéra alebo hlasu zdá, že `Sonic pitch` je resetovaný,
nastavte hodnotu pre tento syntetizér a hlas. Hodnoty sa ukladajú nezávisle.

Ak štandardný `sapi5_32` v 64-bitovom NVDA nezobrazuje `Sonic pitch`,
reštartujte NVDA alebo prepnite zo `sapi5_32` na iný syntetizér a späť.

Ak chýba externý hlas SAPI, najprv ho nakonfigurujte v nástroji príslušného
hlasového balíka a potom reštartujte NVDA.

## Logy

Užitočné logy:

- Aktuálny log NVDA: `%TEMP%\nvda.log`
- Predchádzajúci log NVDA: `%TEMP%\nvda-old.log`
- Logy 32-bitového hosta: `%TEMP%\nvda_synthDriverHost.*.log`

Užitočné frázy:

- `globalSonicPitch`
- `added Sonic pitch voice setting`
- `captured Sonic pitch setting`
- `processed speech audio`
- `applied remote SAPI5 32-bit Sonic pitch`
- `globalSonicPitch sapi5_32 host: set Sonic pitch`

## Licencia

Zdrojový kód Global Sonic Pitch je licencovaný pod GNU GPL verzie 2 alebo
novšej. Pribalené natívne knižnice Sonic sú externé komponenty pod licenciou
Apache 2.0.
