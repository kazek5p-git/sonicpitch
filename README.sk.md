# Global Sonic Pitch

Global Sonic Pitch je doplnok pre NVDA, ktorý pridáva samostatné nastavenie
`Sonic pitch` pre podporované syntetizéry. Mení výšku reči cez spracovanie
Sonic a bežné nastavenie NVDA `Výška` ponecháva ako natívnu výšku syntetizéra.

## Rýchly Štart

1. Nainštalujte `globalSonicPitch-<verzia>.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. Reštartujte NVDA.
3. Otvorte nastavenia NVDA a vyberte `Global Sonic Pitch`.
4. Zapnite `Enable global Sonic pitch`.
5. Otvorte nastavenia hlasu alebo kruh nastavení syntetizéra a upravte
   `Sonic pitch`.

## Funkcie

- Pridáva panel nastavení `Global Sonic Pitch`.
- Pridáva samostatné nastavenie `Sonic pitch`, keď je globálne spracovanie
  zapnuté.
- Ponecháva bežné nastavenie NVDA `Výška` ako natívnu výšku syntetizéra.
- Ukladá `Sonic pitch` osobitne pre každý podporovaný syntetizér a vybraný hlas.
- Ponúka voliteľný rozšírený rozsah približne `-20..+20` poltónov.
- Podporuje zvuk syntetizérov v hlavnom procese NVDA a štandardné `sapi5_32` /
  `sapi4_32` v 64-bitovom NVDA cez pribalené wrappery 32-bitového hosta.
- Obsahuje pribalené 32-bitové a 64-bitové natívne knižnice Sonic.
- Obsahuje pomoc doplnku v angličtine, poľštine a slovenčine.
- Obsahuje poľský a slovenský preklad rozhrania.

## Dokumentácia

- Anglická pomoc: [addon/doc/en/readme.md](addon/doc/en/readme.md)
- Poľská pomoc: [addon/doc/pl/readme.md](addon/doc/pl/readme.md)
- Slovenská pomoc: [addon/doc/sk/readme.md](addon/doc/sk/readme.md)
- Technické poznámky: [docs/technical-notes.md](docs/technical-notes.md)
- Kontrolný zoznam testov: [TESTING.md](TESTING.md)
- Šablóna prekladu: [addon/locale/nvda.pot](addon/locale/nvda.pot)

## Zmeny

- 1.0: Stabilné vydanie nahrádzajúce stiahnuté zostavenie 1.0. Zlepšuje
  spracovanie krátkych blokov zvuku a spevňuje čistenie dialógu nastavení
  hlasu.
- 0.4.20: Pridaný voliteľný rozsah 20 poltónov a podpora štandardného
  `sapi4_32` cez 32-bitový host v 64-bitovom NVDA.
- 0.4.19: Vyčistená a usporiadaná verejná dokumentácia pre recenziu v NVDA
  Add-on Store. Bez zmien v spracovaní zvuku.
- 0.4.18: Pridané hodnoty `Sonic pitch` pre jednotlivé hlasy a poľská/slovenská
  lokalizácia.
- 0.4.15: Stabilizované rýchle zmeny `Sonic pitch` pre štandardný `sapi5_32` v
  64-bitovom NVDA.
- 0.4.13: Pridaná podpora štandardného `sapi5_32` v 64-bitovom NVDA cez
  pribalený wrapper hosta.
- 0.4.10: Pribalené natívne knižnice Sonic pre 32-bitové a 64-bitové NVDA.

História vydaní je v [CHANGELOG.md](CHANGELOG.md).

## Zdrojový Kód

- Hlavný plugin: [addon/globalPlugins/globalSonicPitch.py](addon/globalPlugins/globalSonicPitch.py)
- Wrapper hosta SAPI5 32-bit: [addon/sapi32HostDrivers/sapi5.py](addon/sapi32HostDrivers/sapi5.py)
- Wrapper hosta SAPI4 32-bit: [addon/sapi32HostDrivers/sapi4.py](addon/sapi32HostDrivers/sapi4.py)
- Poznámky k pribalenému Sonic: [addon/globalPlugins/sonicPitchNative/README.txt](addon/globalPlugins/sonicPitchNative/README.txt)

## Inštalácia

1. Stiahnite najnovší súbor `.nvda-addon` z
   [Releases](https://github.com/kazek5p-git/sonicpitch/releases/latest).
2. V NVDA otvorte obchod doplnkov alebo správcu doplnkov a vyberte inštaláciu
   zo súboru.
3. Vyberte stiahnutý balík doplnku.
4. Po výzve reštartujte NVDA.

Najnovší balík:
[globalSonicPitch-1.0.nvda-addon](https://github.com/kazek5p-git/sonicpitch/releases/latest)

## Licencia

Global Sonic Pitch je licencovaný pod GNU GPL verzie 2 alebo novšej. Pribalené
natívne knižnice Sonic sú externé komponenty pod licenciou Apache 2.0.
