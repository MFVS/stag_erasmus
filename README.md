# STAG Erasmus

Seznam předmětů nabízených pro zahraniční studenty.

## Customize bulma

```bash
cd app/static
sass --sourcemap=none --style=compressed sass/mystyles.scss:css/mystyles.css
```

```bash
sass --watch --sourcemap=none sass/mystyles.scss:css/mystyles.css
```

## Použité služby

- [/predmety/getPredmetyByFakulta](https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetyByFakulta)
  - parametr `jenNabizeneECTSPrijezdy` se nastaví na `true`

- [/predmety/getPredmetInfo](https://ws.ujep.cz/ws/services/rest2/predmety/getPredmetInfo)

## TODO

- fakulty
- roky
- cachovani dat

## Schůze 27.2.2024

přídat filtry:
úvodní stránka kde si uživatel bude muset zvolit následujícíc parametry

- [x] fakulta (povinný filtr)
- [x] akademický rok (povinný filtr)

- [x] jazyk vyuky
- [x] kredity
- [x] typ studia

[ ] předpoklady
