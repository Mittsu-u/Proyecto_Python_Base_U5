# Unidad 5 · Integración, Pruebas y Calidad (CLN)

Proyecto de la Unidad 5 de Componentes de Lógica de Negocio (FIME, UANL). Parte del laboratorio guiado (proyecto base de pedidos) y lo extiende con la adaptación al PIA de **CleanPro** (servicios de limpieza).

## Qué incluye

- Pruebas unitarias del dominio, con casos de éxito, error y límite.
- Pruebas de integración con SQLite en memoria (commit, rollback y unicidad).
- Pruebas con mocks para servicios externos (pasarela de pago, notificación a gerencia, facturación).
- Pruebas de autorización (política de cancelación).
- Cobertura de líneas del **100%** sobre `src/` (mínimo exigido: 80%).
- Pipeline de GitHub Actions que ejecuta Ruff y pytest con umbral de cobertura.

## Arquitectura

```
Pruebas / Servicios  ->  Servicios de aplicación  ->  Entidades, Value Objects y reglas de dominio
                                  |
                          puertos (Mock / SQLAlchemy)
```

El dominio no importa SQLAlchemy ni bibliotecas de pagos. Las pruebas unitarias sustituyen los puertos con mocks; las de integración usan SQLite en memoria, con un motor por prueba.

```
src/
  domain.py              Reglas de pedidos (proyecto base)
  application.py         Servicio de cobro con pasarela (proyecto base)
  repository.py          Persistencia SQLAlchemy de pedidos (proyecto base)
  security.py            Política de cancelación (proyecto base)
  cleanpro.py            Dominio de CleanPro: cotizaciones, penalizaciones y cierre de servicio
  cleanpro_repository.py Persistencia de cotizaciones de CleanPro
tests/
  test_order.py, test_repository.py, test_service.py, test_security.py
  test_cleanpro.py, test_cleanpro_service.py, test_cleanpro_repository.py
.github/workflows/ci.yml Pipeline de calidad
casos_prueba.csv         Matriz de casos del laboratorio base
casos_cleanpro.csv       Matriz de casos de la adaptación al PIA (CleanPro)
```

## Instalación

Requiere Python 3.11 o superior.

Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Comandos

```bash
# Todas las pruebas
python -m pytest -v

# Linter
python -m ruff check src tests

# Cobertura con reporte HTML (falla si es menor a 80%)
python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
```

El reporte HTML queda en `htmlcov/index.html`. Esa carpeta no se sube al repositorio (está en `.gitignore`); se incluye en el ZIP de entrega y como captura en el documento.

## Matrices de casos de prueba

| Archivo | Contenido |
|---|---|
| `casos_prueba.csv` | Casos del proyecto base (pedidos, descuento VIP, deuda, cancelación). |
| `casos_cleanpro.csv` | Casos de CleanPro: 12 principales (5 éxito, 4 error, 3 límite), 3 de persistencia y 4 con mock. |

## Reglas de CleanPro implementadas (Actividad 3)

- **RN-01:** un descuento mayor al 10% requiere autorización de gerencia.
- Un inmueble mayor a 300 m² o un cobro mayor a $8,000 requiere autorización de gerencia.
- La superficie debe ser mayor a cero y el dinero no puede ser negativo.
- **RN-04 y RN-05:** la cancelación tardía penaliza el 50% y el acceso denegado el 100%.
- Un servicio no puede cerrarse sin la firma del cliente.

Los límites ("mayor a") se interpretaron de forma estricta y deben validarse con el stakeholder. Los documentos no definen cuántas horas hacen "tardía" una cancelación, por lo que la penalización se calcula por motivo y no por un umbral de tiempo.

## Integración continua

El workflow `CI Business Logic` (`.github/workflows/ci.yml`) se ejecuta en cada push: instala dependencias, ejecuta Ruff y corre pytest con cobertura mínima del 80%. Una prueba que falla deja el pipeline en rojo.

## Notas

- SQLite en memoria no sustituye las pruebas contra un motor productivo como PostgreSQL.
- La cobertura mide qué líneas se ejecutan, no cuántos defectos se detectan.
- Observación de diseño del proyecto base: `OrderService.checkout` confirma el pedido antes de saber si el pago fue aceptado. Se documenta como propuesta de mejora en la Evidencia 5.

## Información del Equipo

- **Materia:** Componentes de Lógica de Negocio (ACT05 - U5)
- **Docente:** Miguel Ángel Gómez Marroquín
- **Equipo:**
  - Jesús Enrique López Martínez
  - Camila Trujillo Quintanilla
  - Cesar Damian Nerio Gonzales