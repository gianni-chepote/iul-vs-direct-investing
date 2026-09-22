# IUL vs. Direct Investing

**🔗 Sitio en vivo (producto final):** https://gianni-chepote.github.io/iul-vs-direct-investing/

Enlace estable y siempre disponible (GitHub Pages). Es el enlace para compartir.
Se redespliega solo en cada push a `main`. La app de Streamlit existe como
respaldo, pero puede dormirse por inactividad.

---

Una comparación honesta y basada en datos: en qué se habría convertido $300 al
mes en un ETF del S&P 500, frente a una ilustración de seguro de vida universal
indexado (IUL).

El lado del ETF usa **rentabilidades históricas totales reales** (dividendos
reinvertidos). El IUL se modela de dos formas:

- **IUL prometido (IUL-A):** una tasa fija del 8% anual, ajustada una vez al
  valor final reportado de $142,672 y luego mantenida fija.
- **IUL realista (IUL-B):** la misma prima y el mismo cargo, pero el valor en
  efectivo se acredita aplicando la regla del contrato
  `max(piso, min(tope, participación × retorno − diferencial))` sobre el
  **índice de precios real del S&P 500** (sin dividendos), punto a punto anual.

## Estructura

- `IUL-vs-index-investing.md` — brief original.
- `revisions/` — revisiones del brief y variantes de instrucciones.
- `website-copy.md` — todo el texto del sitio, para revisión.
- `app/calc.js` — motor de cálculo (fuente única, probada).
- `app/template.html` — marcado, estilos y lógica de la interfaz.
- `app/index.html` — página construida, autónoma (se abre directamente).
- `data/prices.json` — snapshot de precios en caché; `data/provenance.json`.
- `scripts/` — snapshot de datos, verificación y build de la página.
- `.github/workflows/pages.yml` — despliegue a GitHub Pages.

## Reconstruir y verificar

```bash
python scripts/snapshot_prices.py   # refresca el snapshot de precios
node scripts/verify.mjs             # arnés de verificación (34 checks)
node scripts/build_page.mjs         # -> app/index.html
```

## Datos y descargo

Precios vía Yahoo Finance (yfinance). El ETF usa el cierre ajustado
(rentabilidad total); el IUL-B acredita el índice de precios del S&P 500
(dividendos excluidos). Backtest histórico del ETF e ilustraciones modeladas del
IUL — ninguna garantiza resultados futuros. Las cifras de la póliza son
reportadas por el usuario y no verificadas.
