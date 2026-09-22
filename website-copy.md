# Texto del sitio web (copy deck)

Este archivo refleja todo el texto visible de la página (`app/index.html`), en
orden de aparición. Es una copia para revisión — el texto real vive en
`app/template.html`. Si editas aquí y me lo dices, lo aplico a la plantilla y
reconstruyo la página. Los `{marcadores}` son valores que se calculan en vivo.

---

## Pestaña del navegador

- **Título:** Invertir $300 al Mes
- **Descripción:** En qué se habrían convertido $300 al mes en un ETF del S&P 500, frente a una ilustración de seguro de vida universal indexado.

## Encabezado

- **Etiqueta superior:** Backtest histórico · ilustración hipotética
- **Título:** Invertir $300 al mes: ¿IUL o inversión directa?
- **Subtítulo:** Si hubieras contratado el IUL, en el caso extremo de fallecimiento —o de enfermedad terminal, según la póliza— habrías recibido el beneficio completo publicitado de $214,000.
- **Frase dinámica (respuesta):** Si hubieras invertido **{presupuesto}** cada mes en **{ETF}** desde el **{fecha inicial}** hasta el **{fecha final}**, tus **{total aportado}** valdrían aproximadamente **{valor ETF}** al {fecha de valoración}, con dividendos reinvertidos, antes de impuestos personales y costes de operación. La ilustración publicitada del IUL muestra **{valor IUL-A}**; la misma póliza acreditada sobre el índice real de precios del S&P 500 alcanza **{valor IUL-B}**.

## Las dos tarjetas

### Seguro de vida universal indexado
**Título:** Un seguro con una cuenta de ahorro ligada al mercado

- El seguro de vida universal indexado (IUL) es un seguro de vida permanente con una cuenta de valor en efectivo. Cada prima paga primero el coste del seguro y los cargos de la póliza; lo que queda se acredita con un interés ligado a un índice bursátil como el S&P 500.
- El crédito tiene tope y piso. Un tope —a menudo cercano al 8%— limita las ganancias en los años buenos, un piso del 0% evita que una caída del índice recorte el crédito, y los dividendos quedan excluidos. La póliza paga un beneficio por fallecimiento mientras siga financiada.
- Es un producto muy poco líquido, pensado para un plazo largo y fijo —de 10 a 20 años, o de por vida—. Si quieres rescatar o retirar tu cuenta antes de terminar todo el plazo del contrato, te penalizan con cargos altos sobre el valor de tu cuenta.

### Inversión directa en un índice
**Título:** Eres dueño del fondo, y con él de todo el mercado

- Invertir directamente significa comprar un ETF de bajo coste como SPY o VOO que replica el S&P 500. Eres dueño del fondo, recibes sus dividendos (aquí reinvertidos) y su valor se mueve con el mercado.
- No hay cargos de seguro ni tope a las ganancias, pero tampoco hay piso: una caída del mercado golpea tu saldo por completo. Por sí solo no ofrece ningún seguro de vida.
- Los ETF son muy líquidos: puedes salir en cualquier momento al valor de mercado, y los dividendos y las ganancias tributan. El S&P 500 es un índice de las 500 mayores empresas cotizadas de EE. UU. y una referencia amplia del mercado estadounidense.

## Nota sobre las cifras

Las siguientes cifras son ilustrativas, por defecto a lo largo de 20 años (240 aportaciones mensuales).

## Tarjetas de resultados

| Tarjeta | Etiqueta | Subtexto | Valor / subvalor |
|---|---|---|---|
| 1 | Total aportado | tu dinero | {total aportado} · {n} aportaciones mensuales |
| 2 | Valor final del ETF | Backtest histórico del ETF | {valor ETF} · {±diferencia} frente a lo aportado |
| 3 | Ilustración IUL-A | Tasa fija publicitada · hipotética | {valor IUL-A} · {rentabilidad}% de rentabilidad sobre las primas |
| 4 | IUL-B vinculado al índice | Misma póliza, créditos reales del índice | {valor IUL-B} · {x} años en el tope · {y} en el piso |

## Sección: Configura el escenario

**Nota:** Usa esto para saber cuánto habría crecido tu dinero en un periodo determinado, con una cantidad determinada invertida en los ETF que replican el S&P 500. Cada cifra se actualiza desde el historial de precios en caché — sin rentabilidades supuestas en el lado del ETF. El cargo mensual del IUL se ajusta una sola vez a la ilustración reportada de $142,672 y luego se mantiene fijo; cambiar el presupuesto o el periodo no lo reajusta.

**Controles** (botón: Restablecer valores)

- **Aportaciones**
  - Presupuesto mensual (USD)
  - Historial del ETF: `SPY — proxy histórico del ETF del S&P 500 (desde 1993)` / `VOO — historial real (desde sept. 2010)`
    - Pista SPY: SPY hace de sustituto del índice; VOO se lanzó después.
    - Pista VOO: Solo historial de VOO — sin relleno anterior a 2010.
  - Periodo (mes inicial / mes final)
    - Pista: Comprando al cierre de cada fin de mes. Último cierre verificado: {fecha}.
- **IUL-A · publicitado**
  - Tasa acreditada (anual efectiva) — pista: Hipotética; origen no verificado.
  - Cargo mensual equivalente (USD) — pista: Aproximación ajustada, no cargos verificados de la póliza.
  - Aportación neta al valor en efectivo / mes: {importe} / mes
- **IUL-B · créditos indexados**
  - Tope / Piso / Participación / Diferencial
  - Pista: Punto a punto anual sobre el índice de precios del S&P 500 (sin dividendos).

## Gráfico: Crecimiento en el tiempo

- **Nota:** El backtest del ETF y ambas líneas del IUL en un mismo eje de dólares, sobre las aportaciones acumuladas. Pasa el cursor para ver el valor de cada uno en cualquier mes.
- **Encabezado:** Valor de la cuenta, fin de mes — ETF {valor} · publicitado {valor} · vinculado al índice {valor}
- **Leyenda:** ETF (rentabilidad total) · IUL-A publicitado · IUL-B vinculado al índice · Aportaciones

## Gráfico: Cómo se sintió la montaña rusa del ETF

- **Nota:** La caída desde máximos mide cuánto estuvo el ETF por debajo de su máximo previo, usando la serie de rentabilidad sin aportaciones para que los depósitos no oculten las pérdidas. Una línea suave del IUL no prueba que la póliza carezca de riesgo.
- **Encabezado:** Caída desde el máximo previo — Peor: {%}
- **Tooltip:** Bajo el máximo

## Gráfico: A dónde va el dinero, y cómo termina

- **Nota:** Cada prima se divide en un cargo de seguro y una aportación al valor en efectivo. El cargo compra la cobertura — la diferencia final entre el ETF y el IUL no es toda comisiones; los créditos con tope, los dividendos excluidos y la capitalización perdida también influyen.
- **Panel izquierdo:** Cada prima mensual de {presupuesto} — leyenda: Cargo de seguro · Al valor en efectivo
- **Panel derecho:** Valor final, por origen — leyenda: Aportaciones netas · Crecimiento

## Gráfico: Dinero disponible al salir

- **Nota:** Lo que podrías retirar hoy, antes de impuestos personales. El ETF se puede vender en el mercado; el valor de la cuenta del IUL se reduce por cualquier cargo de rescate — y el rescate termina la cobertura.
- **Barras:** ETF (vender en el mercado) · Valor de la cuenta del IUL · Valor de rescate del IUL
- **Nota inferior:** El valor de rescate mostrado es igual al valor de la cuenta porque no se ha proporcionado un calendario de cargos de rescate — **un calendario real lo reduciría, sobre todo en los primeros años**. El importe de retiro anticipado del IUL está totalmente especificado en el contrato y puede llegar a superar la mitad del valor de la cuenta. Rescatar también termina la cobertura de {beneficio}. Las cifras del ETF son antes de impuestos personales, comisiones y diferenciales.

## Gráfico: Cómo se forma un crédito indexado

- **Nota:** Esta es la regla exacta detrás de la línea IUL-B, dibujada desde tu tope, piso, participación y diferencial en vivo. Los puntos son las 20 rentabilidades anuales reales del precio del S&P 500 en el periodo, asignadas al crédito que ganó cada una.
- **Regla (dinámica):** crédito = max(piso {piso}%, min(tope {tope}%, {participación}% × rentabilidad del índice − diferencial {diferencial}%))
- **Leyenda:** Tasa acreditada · Años reales de la póliza

## Sección: En qué se diferencian de verdad

**Nota:** Ninguno es simplemente mejor — la elección depende de si necesitas un seguro de vida duradero y de cómo valoras topes, comisiones, liquidez e impuestos. Las cifras del ETF en esta página son antes de impuestos personales, así que el tratamiento fiscal del IUL es una ventaja real que los gráficos no muestran.

| | Seguro de vida universal indexado | Inversión directa en ETF |
|---|---|---|
| Motor de crecimiento | Crédito indexado, con tope y piso; dividendos excluidos | Rentabilidad total del mercado, con dividendos, sin tope |
| Años a la baja | El piso del 0% protege el interés acreditado — pero los cargos siguen aplicándose | Asumes toda la pérdida del mercado; sin piso |
| Costes | Coste del seguro más cargos de la póliza, que suben con la edad | Ratio de gastos del fondo (~0.03–0.09%) y costes de operación |
| Acceso al efectivo | Cargos de rescate durante años; los préstamos reducen el beneficio | Vender cualquier día de mercado, luego liquidación e impuestos |
| Seguro de vida | Beneficio por fallecimiento mientras esté financiado (aquí $214,000) | Ninguno — combínalo con un seguro temporal si lo necesitas |
| Impuestos | Crecimiento con impuestos diferidos; el beneficio por fallecimiento suele estar exento; los préstamos pueden ser libres de impuestos | Los dividendos y las ganancias realizadas tributan |
| Más adecuado para | Una necesidad duradera de seguro más ahorro con ventaja fiscal, aceptando topes y comisiones | Crecimiento a largo plazo cuando el coste, la liquidez y la simplicidad son lo más importante |

**Advertencias:**

- El IUL es un seguro permanente. Un plan de primas a 20 años no garantiza una póliza pagada por completo — los cargos crecientes pueden exigir más financiación más adelante.
- Un piso del 0% no evita pérdidas del valor en efectivo por **cargos**. Si dejas de pagar las primas, los cargos continúan; la póliza puede caducar.
- Los cargos de rescate pueden dejar lo recibido por debajo de las primas pagadas, y rescatar termina la cobertura.
- Con cobertura nivelada, los beneficiarios reciben el beneficio por fallecimiento, no el beneficio **más** el valor en efectivo.
- Un ETF no ofrece ningún seguro de vida. "Compra un seguro temporal e invierte la diferencia" combina cobertura temporal barata con el crecimiento del mercado.
- Esta página compara rentabilidades pasadas reales del ETF con una ilustración modelada del IUL. Los resultados pasados no predicen los futuros.

## Pie de página

- **Aviso:** Backtest histórico del ETF e ilustraciones modeladas del IUL (tasa fija publicitada y reconstrucción vinculada al índice). Ninguna garantiza resultados futuros.
- **Nota técnica:** Precios: {proveedor}, obtenidos el {fecha}. El ETF usa el cierre ajustado (rentabilidad total); el IUL-B acredita el índice de precios del S&P 500 (dividendos excluidos). Las cifras de la póliza son reportadas por el usuario y no verificadas. La comprobación iterativa frente a la directa del ETF coincide en {importe}.
