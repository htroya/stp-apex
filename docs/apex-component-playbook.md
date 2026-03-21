# APEX Component Playbook

Objetivo: documentar como crear componentes APEX a partir de los respaldos reales del repo, que export usar como patron, y cual es la secuencia correcta para import/export y montaje de nuevas apps.

Fecha de verificacion: `2026-03-21`

## Lectura minima antes de tocar APEX

1. [oracle-connection-playbook.md](/C:/HT/stp-apex/docs/oracle-connection-playbook.md)
2. [apex-backup-catalog.md](/C:/HT/stp-apex/docs/apex-backup-catalog.md)
3. [README.md](/C:/HT/stp-apex/README.md)

## Flujo recomendado de trabajo

1. Conectarse por `ORDS REST Enabled SQL`.
2. Usar `f100.sql` como base para recrear o clonar una app minima.
3. Elegir un respaldo de referencia segun el componente a copiar.
4. Extraer del zip la pagina o shared component que ya resuelve ese problema.
5. Adaptar owner, nombre de tabla, IDs y alias.
6. Importar la app o crear la pagina faltante.
7. Validar en la base y luego en APEX.

## Export: flujo ya validado

Script:

- [export-app.ps1](/C:/HT/stp-apex/scripts/apex/export-app.ps1)

Formas soportadas:

- export SQL completo por ORDS:

```powershell
.\scripts\apex\export-app.ps1 -ApplicationId 100 -OutputPath .\apex\exports
```

- export split por `SQLcl`:

```powershell
.\scripts\apex\export-app.ps1 -ApplicationId 109 -OutputPath . -Split
```

Hallazgo importante:

- el export SQL completo es la ruta mas estable para clonar apps
- el split `.zip` es mejor para estudiar componentes, paginas y shared components

## Import: flujo ya validado

Script:

- [import-app.ps1](/C:/HT/stp-apex/scripts/apex/import-app.ps1)

Ruta recomendada:

```powershell
.\scripts\apex\import-app.ps1 `
  -SourcePath .\apex\exports\f100.sql `
  -TargetApplicationId 101 `
  -TargetApplicationAlias test101 `
  -TargetApplicationName test101 `
  -ReplaceExisting
```

Hallazgos importantes del import:

- `ORDS` cancela scripts si aparecen tokens como `&APP_ID.` o `&APP_SESSION.` sin neutralizar
- el importador del repo ya convierte esos tokens con `chr(38)` para evitar el `Substitution cancelled`
- para clonar apps completas, usar el `.sql` completo
- para estudiar estructura interna de paginas y shared components, usar el `.zip`

## Anatomia real de un componente en un export split

El patron real verificado en los zips es:

1. `create_page`
2. `create_page_plug`
3. `create_region_column` o estructura especifica de la region
4. componente principal (`create_interactive_grid`, `create_jet_chart`, `create_map_region_layer`, etc.)
5. vista/reporte asociado (`create_ig_report`, `create_ig_report_view`, etc.) cuando aplica
6. `create_page_process` y `create_page_da_*` si el componente lo necesita

No conviene inventar ese orden: copiarlo desde el zip o desde `install.sql` evita errores.

## Como crear cada familia de componente

### Base minima de app

Referencia:

- `f100.zip`
- [f100.sql](/C:/HT/stp-apex/apex/exports/f100.sql)

Uso:

- crear una app minima con `Home` y `Login`
- despues agregar paginas nuevas encima

### Pagina vacia

Referencia:

- `f101.zip`
- `f101/application/pages/page_00002.sql`

Uso:

- crear una pagina vacia con `create_page`
- punto de partida para injertar regiones nuevas

### Interactive Grid editable

Referencia principal:

- `f109.zip`
- pagina: `f109/application/pages/page_00030.sql`
- nombre de pagina: `Basic Editing`

Stack minimo verificado:

1. `create_page`
2. `create_page_plug` con `p_plug_source_type=>'NATIVE_IG'`
3. `create_region_column` para:
   - `APEX$ROW_SELECTOR`
   - `APEX$ROW_ACTION`
   - PK oculta
   - columnas editables
4. `create_interactive_grid`
5. `create_ig_report`
6. `create_ig_report_view`
7. `create_ig_report_column`
8. `create_page_process` con `p_process_type=>'NATIVE_IG_DML'`

Requisitos de tabla para IG editable:

- estar en el owner de la app, aqui `WKSP_STP`
- tener PK real
- la columna PK suele ir como `NATIVE_HIDDEN`
- el proceso `NATIVE_IG_DML` se apoya en la fuente de la region

Referencia local creada para este repo:

- [002_wksp_stp_page2_grid.sql](/C:/HT/stp-apex/db/install/002_wksp_stp_page2_grid.sql)
- [app101_page_00002_editable_grid.sql](/C:/HT/stp-apex/apex/snippets/app101_page_00002_editable_grid.sql)

### Cards

Referencia:

- `f102.zip`

Patron:

- region `NATIVE_CARDS`
- `create_card`
- `create_card_action`

### Charts

Referencia:

- `f103.zip`

Patron:

- region `NATIVE_JET_CHART`
- `create_jet_chart`
- `create_jet_chart_series`
- `create_jet_chart_axis`

### Data Loading

Referencia:

- `f105.zip`

Patron:

- `NATIVE_DATA_LOADING`
- `NATIVE_PARSE_UPLOADED_DATA`
- `NATIVE_LOAD_UPLOADED_DATA`

### Dynamic Actions

Referencia:

- `f106.zip`

Patron:

- `create_page_da_event`
- `create_page_da_action`

### Upload / Download de archivos

Referencia:

- `f107.zip`

Patron:

- formularios + procesos PL/SQL
- reportes para listar binarios

### Autenticacion por email

Referencia:

- `f108.zip`

Patron:

- paginas de verificacion y administracion de acceso
- mezcla de `NATIVE_PLSQL` y `NATIVE_INVOKE_API`

### Maps

Referencia:

- `f110.zip`

Patron:

- `NATIVE_MAP_REGION`
- `create_map_region_layer`

### Master Detail

Referencia:

- `f111.zip`

Patron:

- formularios + IGs
- `NATIVE_FORM_INIT`
- `NATIVE_FORM_DML`
- `NATIVE_IG_DML`

### Reporting

Referencia:

- `f112.zip`

Patron:

- `NATIVE_IR`
- reportes clasicos
- `NATIVE_IG`

### Trees

Referencia:

- `f113.zip`

Patron:

- `NATIVE_JSTREE`

### REST Data Sources

Referencia:

- `f114.zip`

Patron:

- `create_web_source_operation`
- `create_data_profile_col`
- combinacion de REST con IR, charts, cards, maps y calendar

### Universal Theme y layout

Referencia:

- `f115.zip`

Uso:

- referencia general para templates, display selectors, theme options, layouts y tipos de region

### Search / Vector Search

Referencias:

- `f116.zip`
- `f123.zip`

Patron:

- `NATIVE_SEARCH_REGION`
- `create_search_region_source`

### Workflow / Approvals / Tasks

Referencia:

- `f117.zip`

Patron:

- `create_workflow_activity`
- `create_workflow_transition`
- procesos `NATIVE_WORKFLOW`, `NATIVE_MANAGE_TASK`, `NATIVE_CREATE_TASK`

### RTE con imagenes

Referencia:

- `f118.zip`

Patron:

- contenido dinamico
- RTE + endpoint para servir imagenes

### App mixta de referencia realista

Referencias:

- `f119.zip`
- `f120.zip`
- `f121.zip`
- `f122.zip`
- `f124.zip`

Uso:

- ver combinaciones reales de cards, calendarios, mapas, PWA, collections y contenido dinamico

## Decision operativa para la app 101

Ruta elegida y ya documentada:

1. importar `f100.sql` como app `101`
2. asegurar tabla `WKSP_STP.STP_PAGE2_GRID`
3. crear `page 2` como pagina nueva
4. montar un `NATIVE_IG` editable sobre `WKSP_STP.STP_PAGE2_GRID`

Activos del repo para repetir esa construccion:

- [f100.sql](/C:/HT/stp-apex/apex/exports/f100.sql)
- [002_wksp_stp_page2_grid.sql](/C:/HT/stp-apex/db/install/002_wksp_stp_page2_grid.sql)
- [app101_page_00002_editable_grid.sql](/C:/HT/stp-apex/apex/snippets/app101_page_00002_editable_grid.sql)

## Regla practica para futuras tareas

Si la tarea es nueva, no empezar por APIs internas a ciegas.

Orden correcto:

1. identificar el zip que ya contiene el componente
2. ubicar la pagina exacta dentro del zip
3. copiar el patron de `create_*`
4. adaptar owner, tabla, IDs y alias
5. importar o ejecutar el SQL

Ese enfoque ya quedo comprobado como mas rapido y mas estable que intentar reconstruir componentes complejos desde cero.
