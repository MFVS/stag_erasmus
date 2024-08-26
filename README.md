# STAG Erasmus

> _Course catalogue for Erasmus+ incoming students_

Digitalizace katalogu kurzů pro incomingové studenty.
Seznam předmětů nabízených pro zahraniční studenty.

![Fastapi](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)![Pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)![Ruff](https://img.shields.io/badge/ruff-%23D7FF64.svg?style=for-the-badge&logo=ruff&logoColor=black)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)![HTMX](https://img.shields.io/badge/%3C/%3E%20htmx-3366CC?style=for-the-badge&logo=mysl&logoColor=white)![Bulma](https://img.shields.io/badge/Bulma-00D1B2?style=for-the-badge&logo=bulma&logoColor=white)![Jinja](https://img.shields.io/badge/jinja-B41717?style=for-the-badge&logo=jinja&logoColor=black)

## Popis projektu

Jedná se o webovou aplikaci, která nabízí přehled předmětů pro zahraniční studenty v rámci programu **Erasmus+**.

### Použité technologie

#### Backend


#### Frontend

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

## Test

```bash
~/go/bin/go-wrk -d 30 -c 6 http://localhost:8000/subjects/fsi/2024
```
