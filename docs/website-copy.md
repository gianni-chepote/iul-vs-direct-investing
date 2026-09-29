# Texto del sitio web (copy deck)

**Sitio en vivo (producto final):** https://gianni-chepote.github.io/iul-vs-direct-investing/

Este archivo refleja todo el texto visible de la página (`app/index.html`), en
orden de aparición. Es una copia para revisión — el texto real vive en
`app/template.html`. Los cambios se aplican en la plantilla y la página se
reconstruye con `node scripts/build_page.mjs`. Los `{marcadores}` son valores que se calculan en vivo.

---

## Pestaña del navegador

- **Título:** IUL vs. inversión directa en un ETF del S&P 500
- **Descripción:** Una comparación de la misma aportación mensual en un IUL y en un ETF del S&P 500.

## Encabezado

- **Etiqueta superior:** Backtest histórico · ilustración hipotética
- **Título (visible, H1):** IUL vs. inversión directa en un ETF del S&P 500
- **Subtítulo (visible):** Una póliza de seguro de vida con cuenta de ahorro y un ETF del S&P 500 hacen cosas distintas. Esta página compara qué habría pasado con la misma aportación mensual en cada uno, y qué recibirías con una cobertura de $214,000 en el caso del seguro.
- **Frase dinámica (respuesta):** Si hubieras invertido **{presupuesto}** cada mes en **{ETF}** desde el **{fecha inicial}** hasta el **{fecha final}**, tus **{total aportado}** valdrían aproximadamente **{valor ETF}** al {fecha de valoración}, con dividendos reinvertidos, mientras que la ilustración publicitada del IUL muestra **{valor IUL-A}**.

> **«El IUL combina seguro y ahorro; el ETF solo invierte. Aquí medimos cuánto rinde cada uno con el mismo dinero.»**

## Las dos tarjetas

### Seguro de vida universal indexado (IUL)
**Título:** Un seguro con una cuenta de ahorro ligada al mercado
**Entradilla:** El IUL descuenta primero los costes del seguro y de la póliza, limita el crédito cuando el índice sube, no incluye los dividendos y aplica cargos si rescatas antes de tiempo. A cambio, ofrece cobertura de vida y un piso del 0% en el crédito.
- El seguro de vida universal indexado (IUL) es un seguro de vida permanente con una cuenta de valor en efectivo. Cada prima paga primero el coste del seguro y los cargos de la póliza; lo que queda se acredita con un interés ligado a un índice bursátil como el S&P 500.
- El crédito tiene tope y piso. Un tope —a menudo cercano al 8—10% limita las ganancias en los años buenos, un piso del 0% evita que una caída del índice recorte el crédito, y los dividendos quedan excluidos. Por encima del valor de la cuenta, la póliza paga un beneficio por fallecimiento mientras siga financiada.
- Es un producto sumamente *ilíquido*, pensado para un plazo largo y fijo —de 10 a 20 años, o de por vida—. Si rescatas o retiras tu cuenta antes de terminar el plazo del contrato, se aplican cargos sobre el valor de tu cuenta.

### Inversión directa en un índice
**Título:** Eres dueño del fondo, y con él de todo el mercado

- Invertir directamente significa comprar un ETF como SPY o VOO que replica el S&P 500. Eres dueño del fondo, recibes sus dividendos y su valor se mueve con el mercado.
- No hay cargos de seguro ni tope a las ganancias, pero tampoco hay piso: una caída del mercado golpea tu saldo por completo. 
- Los ETF son líquidos: puedes salir en cualquier momento al valor de mercado. El S&P 500 es un índice de las 500 mayores empresas cotizadas de EE. UU. y una referencia amplia del mercado estadounidense.

## Nota sobre las cifras

Las siguientes cifras son ilustrativas, por defecto a lo largo de 20 años (240 aportaciones mensuales).

## Tarjetas de resultados

| Tarjeta | Etiqueta | Subtexto | Valor / subvalor |
|---|---|---|---|
| 1 | Total aportado | tu dinero | {total aportado} · {n} aportaciones mensuales |
| 2 | Valor final del ETF | Backtest histórico del ETF | {valor ETF} · {±diferencia} frente a lo aportado |
| 3 | IUL: según la ilustración | Tasa fija publicitada · hipotética | {valor IUL-A} · Tasa publicitada: {tasa}% anual |
| 4 | IUL: modelo con índice real | Misma póliza, créditos reales del índice | {valor IUL-B} · {x} años en el tope · {y} en el piso |

**Línea "qué mirar" (bajo las tarjetas):** La brecha entre el ETF y el IUL refleja los costes del seguro, los topes y la exclusión de dividendos, pero también incluye lo que el IUL ofrece a cambio: cobertura de vida y piso del 0%.

## Sección: Compruébalo tú mismo — cómo crecen tus aportaciones con el tiempo

**Nota:** Usa esto para saber cuánto habría crecido tu dinero en un periodo determinado, con una cantidad determinada invertida en los ETF que replican el S&P 500. Cada cifra se actualiza desde el historial de precios en caché — sin rentabilidades supuestas en el lado del ETF. El cargo mensual del IUL se ajusta una sola vez a la ilustración reportada de $142,672 y luego se mantiene fijo; cambiar el presupuesto o el periodo no lo reajusta.

**Controles** (botón: Restablecer valores)

- **Aportaciones**
  - Presupuesto mensual (USD)
  - Historial del ETF: `SPY — proxy histórico del ETF del S&P 500 (desde 1993)` / `VOO — historial real (desde sept. 2010)`
    - Pista SPY: SPY hace de sustituto del índice; VOO se lanzó después.
    - Pista VOO: Solo historial de VOO — sin relleno anterior a 2010.
  - Periodo (mes inicial / mes final)
    - Pista: Comprando al cierre de cada fin de mes. Último cierre verificado: {fecha}.
- **IUL: según la ilustración (fijo, no editable)**
  - Tasa acreditada (anual efectiva): 8% anual · fijo — pista: Hipotética; origen no verificado. No editable.
  - Cargo mensual equivalente (USD): $49.26 / mes · fijo — pista: Aproximación ajustada, no cargos verificados de la póliza.
  - Aportación neta al valor en efectivo / mes: {importe} / mes — pista: Lo que de verdad entra a tu cuenta cada mes, después de aplicar el coste del seguro y los demás cargos.
- **IUL: lo realista** → **Opciones avanzadas** (desplegable)
  - Tope / Piso / Participación / Diferencial
  - Pista: Punto a punto anual sobre el índice de precios del S&P 500 (sin dividendos).

## Gráfico: Crecimiento en el tiempo

- **Nota:** El backtest del ETF y ambas líneas del IUL en dólares, sobre las aportaciones acumuladas. Pasa el cursor para ver el valor de cada uno en cualquier mes. El IUL-B aplica la regla real de la póliza: en los años en que el índice cae, acredita 0% (el piso) —no pierde por el índice, pero los cargos siguen restando—, y en los años buenos el tope limita la ganancia.
- **Encabezado:** Valor de la cuenta, fin de mes — ETF {valor} · publicitado {valor} · vinculado al índice {valor}
- **Leyenda:** ETF (rentabilidad total) · IUL prometido · IUL realista · Aportaciones

## Gráfico: Si mañana necesitas tu dinero, ¿cuánto puedes recuperar realmente?

- **Nota:** Lo que podrías retirar hoy. El ETF se puede vender en el mercado; el valor de la cuenta del IUL se reduce por cualquier cargo de rescate — y el rescate termina la cobertura.
- **Barras:** ETF (vender en el mercado) · Valor de la cuenta del IUL · Rescate del IUL (supuesto, 45%)
- **Nota inferior:** **Supuesto:** el valor de rescate mostrado es una suposición — **el 45% del valor de la cuenta**, es decir, un cargo de rescate del 55%. El calendario real está totalmente especificado en tu contrato y, sobre todo en los primeros años, puede quedarse con más de la mitad de tu dinero. Rescatar también termina la cobertura de {beneficio}. Las cifras del ETF son antes de impuestos personales, comisiones y diferenciales.


## Gráfico: Las caídas del ETF

- **Nota:** La caída desde máximos mide cuánto estuvo el ETF por debajo de su máximo previo. Una línea suave del IUL no prueba que la póliza carezca de riesgo.
- **Encabezado:** Caída desde el máximo previo — Peor: {%}
- **Tooltip:** Bajo el máximo


## Sección: En qué se diferencian de verdad

**Nota:** Ninguno es «bueno» o «malo»: resuelven problemas distintos. Si tu objetivo es solo acumular capital, en este backtest el ETF acumuló más, con menos costes y más liquidez, aunque con caídas de mercado que el IUL no tiene. Si además necesitas cobertura de vida permanente y valoras el crédito con piso, el IUL cubre esa necesidad, pero conviene tener presente el coste, los topes y los cargos de rescate. Una alternativa habitual es un seguro temporal más un ETF con la diferencia; consulta con un asesor independiente antes de decidir.

| | Seguro de vida universal indexado                                                                                                    | Inversión directa en ETF                                                                     |
|---|--------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Motor de crecimiento | Crédito indexado, con tope y piso; dividendos excluidos                                                                              | Rentabilidad total del mercado, con dividendos, sin tope                                     |
| Años a la baja | El piso del 0% protege el interés acreditado — pero los cargos siguen aplicándose                                                    | Asumes toda la pérdida del mercado; sin piso                                                 |
| Costes | Coste del seguro más cargos de la póliza, que suben con la edad                                                                      | Ratio de gastos del fondo, muy bajo (~0.03–0.09%), y costes de operación                     |
| Acceso al efectivo | Penalización alta por retiros o cancelación anticipada | Líquido: vender cualquier día de mercado                                                     |
| Seguro de vida | Beneficio por fallecimiento mientras esté financiado (aquí $214,000)                                                                 | Ninguno                                    |
| Impuestos | Crecimiento con impuestos diferidos; el beneficio por fallecimiento suele estar exento; los préstamos pueden ser libres de impuestos | Los dividendos y las ganancias realizadas tributan                                           |
| Más adecuado para | Una necesidad duradera de seguro más ahorro con ventaja fiscal, aceptando topes y comisiones                                         | Crecimiento a largo plazo cuando el coste, la liquidez y la simplicidad son lo más importante |

**Advertencias:**

- El IUL es un seguro permanente. Un plan de primas a 20 años no garantiza una póliza pagada por completo — los cargos crecientes pueden exigir más financiación más adelante.
- Un piso del 0% no evita pérdidas del valor en efectivo por **cargos**. Si dejas de pagar las primas, los cargos continúan; la póliza puede caducar.
- Los cargos por cancelación anticipada pueden dejar lo recibido por debajo de las primas pagadas, y rescatar termina la cobertura.
- Con cobertura nivelada, los beneficiarios reciben el beneficio por fallecimiento, no el beneficio **más** el valor en efectivo.
- Un ETF no ofrece ningún seguro de vida. "Compra un seguro temporal e invierte la diferencia" combina cobertura temporal barata con el crecimiento del mercado.
- Esta página compara rentabilidades pasadas reales del ETF con una ilustración modelada del IUL. Los resultados pasados no predicen los futuros.

## Pie de página

- **Aviso:** Backtest histórico del ETF e ilustraciones modeladas del IUL (tasa fija publicitada y reconstrucción vinculada al índice). Ninguna garantiza resultados futuros.
- **Nota técnica:** Precios: {proveedor}, obtenidos el {fecha}. El ETF usa el cierre ajustado (rentabilidad total); el IUL-B acredita el índice de precios del S&P 500 (dividendos excluidos). Las cifras de la póliza son reportadas por el usuario y no verificadas. La comprobación iterativa frente a la directa del ETF coincide en {importe}.
