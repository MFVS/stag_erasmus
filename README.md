# STAG Erasmus

Digitalizace katalogu kurzů pro incomingové studenty.
Seznam předmětů nabízených pro zahraniční studenty.

## Customize bulma

```bash
cd app/static
sass --sourcemap=none --style=compressed sass/mystyles.scss:css/mystyles.css
```

```bash
sass --watch --sourcemap=none sass/mystyles.scss:css/mystyles.css
```

## SpinKit

<https://github.com/tobiasahlin/SpinKit>

## MDI icons

<https://pictogrammers.com/library/mdi/>

## SVG

<https://app.haikei.app/>

## Použité WS STAG služby

- [/predmety/getPredmetyByFakulta](https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakultaFullInfo)
  - parametr `jenNabizeneECTSPrijezdy` se nastaví na `true`
- [/ciselniky/getCiselnik](https://ws.ujep.cz/ws/services/rest2/ciselniky/getCiselnik)
  - parametr `domena` = JEDNOTKA_VYUKY
  - tento číselník byl přeložen do angličtiny

## Schůze 27.2.2024

přídat filtry:
úvodní stránka kde si uživatel bude muset zvolit následujícíc parametry

- [x] fakulta (povinný filtr)
- [x] akademický rok (povinný filtr)

- [x] jazyk vyuky
- [x] kredity
- [x] typ studia

[ ] předpoklady

## Dokumentace k některým knihovnám

<https://ttl255.com/jinja2-tutorial-part-6-include-and-import/>

## Test

```bash
~/go/bin/go-wrk -d 30 -c 6 http://localhost:8000/subjects/fsi/2024
```

## TODO

- prelozit hodiny/tyd atd.
- ve vyhledavani vyhledavat i v nazvech
- vyhledavani seradit podle abecedy (nazev)
- v tabulce radky klikatelne znazornit
