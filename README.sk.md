# Global Sonic Pitch

Slovenská používateľská dokumentácia je dodaná aj priamo v balíku doplnku.

Anglická dokumentácia: [README.md](README.md)  
Poľská dokumentácia: [README.pl.md](README.pl.md)

Global Sonic Pitch pridáva samostatné nastavenie `Sonic pitch` a používa ho cez
spracovanie zvuku Sonic. Bežné nastavenie NVDA `Výška` zostáva natívnou výškou
aktívneho syntetizéra. Doplnok nepridáva nové syntetizéry do dialógu výberu
syntetizéra.

## Najdôležitejšie

- `Sonic pitch` je samostatné nastavenie a nenahrádza natívnu `Výšku`.
- Hodnoty sa ukladajú osobitne pre podporovaný syntetizér a vybraný hlas.
- V SAPI5 môže mať napríklad Paulina inú hodnotu než eSpeak-NG SAPI.
- Štandardný `sapi5_32` v 64-bitovom NVDA zostáva normálnym syntetizérom NVDA;
  doplnok používa iba pribalený wrapper 32-bitového hosta.
- Doplnok nemení súbory NVDA, neupravuje zoznam hlasov SAPI a nezapisuje tokeny
  hlasov do registra.
- Obsahuje dobrovoľný odkaz `Support the author` na BuyCoffee.

## Inštalácia

1. Stiahnite najnovší súbor `.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. Ak máte starý doplnok `SAPI5 Sonic Pitch` / `sapi5SonicPitch`, najprv ho
   odstráňte a reštartujte NVDA.
3. Otvorte súbor `globalSonicPitch-<verzia>.nvda-addon` v NVDA.
4. Potvrďte inštaláciu a reštartujte NVDA.
5. Otvorte nastavenia NVDA, vyberte `Global Sonic Pitch` a zapnite
   `Enable global Sonic pitch`.

## Použitie

Vyberte bežný syntetizér NVDA, napríklad RHVoice, eSpeak, OneCore, 64-bitový
SAPI5 alebo štandardný `sapi5_32`. Keď je globálny režim zapnutý, doplnok pridá
nastavenie `Sonic pitch` do nastavení hlasu a kruhu nastavení syntetizéra.

Hodnota `50` je neutrálna. Nižšie hodnoty znižujú reč cez Sonic, vyššie hodnoty
ju zvyšujú. Bežné nastavenie `Výška` v NVDA stále ovláda natívnu výšku
syntetizéra.

Hodnota `Sonic pitch` sa ukladá osobitne pre každý podporovaný syntetizér a
vybraný hlas. Ak prepnete zo SAPI5 Paulina na eSpeak-NG SAPI, nový hlas môže
začať na `50`, kým mu nenastavíte vlastnú hodnotu.

## Nastavenia A Gestá

Panel `Global Sonic Pitch` obsahuje:

- `Enable global Sonic pitch` - zapne alebo vypne spracovanie Sonic pitch.
- `Enable debug logging` - zapisuje podrobné položky do logu NVDA.
- `Support the author` - otvorí externú stránku BuyCoffee.

V globálnom paneli nie je samostatný posuvník `Sonic pitch`. Hodnota sa mení v
nastaveniach hlasu, v kruhu nastavení syntetizéra alebo cez vlastné vstupné
gestá. Kategória `Global Sonic Pitch` vo vstupných gestách umožňuje zapnúť
alebo vypnúť doplnok, oznámiť stav, otvoriť stránku podpory, zvýšiť, znížiť a
obnoviť hodnotu pre aktuálny syntetizér a hlas.

## Riešenie Problémov

Ak `Sonic pitch` nie je v nastaveniach hlasu, zapnite `Enable global Sonic
pitch`, potom znovu otvorte nastavenia hlasu alebo prepnite syntetizér.

Ak sa hodnota nemení, skontrolujte, či globálny režim je zapnutý a hodnota nie
je `50`. Pri `sapi5_32` v 64-bitovom NVDA hľadajte v logu `%TEMP%\nvda.log`
položku `applied remote SAPI5 32-bit Sonic pitch` a v logu hosta
`%TEMP%\nvda_synthDriverHost.*.log` položku `globalSonicPitch sapi5_32 host:
set Sonic pitch`.

Ak prepnutie syntetizéra alebo hlasu vyzerá ako reset na `50`, je to očakávané,
kým nastavíte hodnotu pre konkrétny syntetizér a hlas.

## Logy

- Aktuálny log: `%TEMP%\nvda.log`
- Predchádzajúci log: `%TEMP%\nvda-old.log`
- 32-bitový host: `%TEMP%\nvda_synthDriverHost.*.log`

## Licencia

Zdrojový kód Global Sonic Pitch je licencovaný pod GNU GPL verzie 2 alebo
novšej. Pribalené natívne binárne súbory Sonic sú externé komponenty pod
licenciou Apache 2.0.
