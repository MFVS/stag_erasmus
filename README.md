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

<https://www.svgbackgrounds.com/set/free-svg-backgrounds-and-patterns/>

## Použité WS STAG služby

- [/predmety/getPredmetyByFakulta](https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakulta)
  - parametr `jenNabizeneECTSPrijezdy` se nastaví na `true`

## TODO

- [x] Uzivatel do .env

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
~/go/bin/go-wrk -d 30 -c 6 http://127.00.1:80/subjects/?faculty=fsi\&year=2024
```

## TODO

- Roky - zjistit jestli uz jsou predmety z aktualniho roku:
  - davaji se vse najednou?
