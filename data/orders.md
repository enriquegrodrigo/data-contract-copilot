# Dataset: `orders`

Este dataset contiene pedidos normalizados para analítica y reporting.

## Esquema esperado (alto nivel)
- `order_id` (string): identificador único del pedido.
- `status` (string, UPPER): estado del pedido. Valores esperados: `PENDING`, `SHIPPED`, `CANCELED`.
- `amount` (number, EUR): importe total del pedido. Normalmente **≥ 0**; rango típico **0–500 EUR** (excepcionalmente < 1000 EUR).
- `event_time` (timestamp, Europe/Madrid): marca temporal del evento del pedido.
- `country_code` (string): código de país en **ISO-3166-1 alpha-2** (p. ej., ES, FR, DE, IT, PT, NL, CH). No se limita a una lista cerrada si cumple ISO.

## Reglas de negocio propuestas para el contrato de datos
1. **Identidad**
   - `order_id` es **único** por fila (no debe tener duplicados).

2. **Dominios / Enumeraciones**
   - `status` ∈ {`PENDING`, `SHIPPED`, `CANCELED`} (en mayúsculas).
   - `country_code` debe cumplir **ISO-3166-1 alpha-2**.

3. **Rangos y formatos**
   - `amount` ≥ 0. Rango típico **0–500 EUR**; valores fuera de ese rango deben revisarse (excepcionales < 1000).
   - `event_time` no debe estar en el **futuro**.

4. **Frecuencia y Frescura (SLA)**
   - Actualización **DIARIA**; el dataset debe estar disponible **antes de 08:00 Europe/Madrid** cada día natural.

5. **Volumen esperado**
   - Volumen diario habitual: **15–30 filas/día** (en entornos de prueba puede ser menor).

## Notas de calidad y consideraciones
- El dataset puede incluir pedidos cancelados con `amount = 0`.
- Los valores de `status` adicionales o desconocidos deben registrarse como discrepancias.
- El contrato debe incluir **justificación** (“grounding”) de cada regla, con referencia a esta documentación o a evidencias del perfilado/consultas.
