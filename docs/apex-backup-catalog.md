# APEX Backup Catalog

Objetivo: dejar un inventario operativo de todos los respaldos `.zip` del repo para no volver a descubrir desde cero que contiene cada export, para que sirve, y cual conviene usar como referencia.

Fecha de verificacion: `2026-03-21`

Estado verificado en la base:

- workspace: `STP`
- owner/parsing schema observado en las apps de referencia: `WKSP_STP`
- APEX: `24.2.14`
- la app `101` existe actualmente y es la app usada para validacion E2E
- los respaldos `f100.zip` a `f124.zip` siguen siendo la biblioteca fuente para reconstruir o copiar componentes

## Como estan armados los respaldos

Todos los `f###.zip` del repo son exports split de APEX.

Patron comun verificado:

- `<root>/install.sql`
- `<root>/application/set_environment.sql`
- `<root>/application/delete_application.sql`
- `<root>/application/create_application.sql`
- `<root>/application/user_interfaces.sql`
- `<root>/application/pages/page_XXXXX.sql`
- `<root>/application/shared_components/...`
- `<root>/application/end_environment.sql`
- opcional: `<root>/application/supporting_objects/...`

`install.sql` define el orden real de importacion con sentencias `@@application/...`. Si hay que importar manualmente por lotes o reconstruir una pagina, ese archivo es la fuente de verdad.

## Como volver a inspeccionar rapido los respaldos

Script local agregado para repetir este analisis:

- [analyze-backups.py](/C:/HT/stp-apex/scripts/apex/analyze-backups.py)
- [apex-zip-reference-map.md](/C:/HT/stp-apex/docs/apex-zip-reference-map.md)

Ejemplo:

```powershell
python .\scripts\apex\analyze-backups.py --format markdown
python .\scripts\apex\analyze-backups.py --format json
python .\scripts\apex\analyze-backups.py --format markdown --page-limit 0
python .\scripts\apex\analyze-backups.py --contains NATIVE_IG --format markdown --page-limit 0
python .\scripts\apex\analyze-backups.py --contains create_map_region_layer --format markdown --page-limit 0
python .\scripts\apex\analyze-backups.py --contains create_search_region_source --format markdown --page-limit 0
```

Salida nueva del analizador:

- `capability tags` para cada backup
- `page index` con `page file -> page name -> alias`
- categorias de `shared_components`
- categorias y archivos de `supporting_objects`

Regla operativa:

- para una respuesta rapida, empezar por [apex-zip-reference-map.md](/C:/HT/stp-apex/docs/apex-zip-reference-map.md)
- usar este catalogo para entender contexto y alcance
- usar el analizador solo para confirmar pagina exacta, supporting objects y token tecnico

## Catalogo por respaldo

### `f100.zip`

- App: `test`
- Alias: `TEST`
- Paginas exportadas: `3` utiles (`0`, `1`, `9999`)
- Perfil tecnico: app minima con contenido estatico, login y pocos procesos
- Procedimientos dominantes: `create_page`, `create_page_plug`, `create_page_process`, `create_page_item`
- Procesos dominantes: `NATIVE_INVOKE_API`, `NATIVE_SESSION_STATE`, `NATIVE_PLSQL`
- Uso recomendado: app base minima para clonar y luego agregar paginas

### `f101.zip`

- App: `test101`
- Alias exportado: `TEST100`
- Paginas exportadas: `4` utiles (`0`, `1`, `2`, `9999`)
- Perfil tecnico: clon de `f100.zip` con una `Blank Page`
- Hallazgo importante: el alias del export no es confiable como base canonica
- Uso recomendado: inspeccionar `page_00002.sql` como ejemplo de pagina vacia; no usarlo como base principal de import sin corregir alias/nombre

### `f102.zip`

- App: `Sample Cards`
- Alias: `SAMPLE-CARDS`
- Paginas: `25`
- Regiones dominantes: `NATIVE_CARDS`, `NATIVE_FACETED_SEARCH`, `NATIVE_FORM`
- Procedimientos dominantes: `create_card`, `create_card_action`, `create_page_plug`, `create_data_profile_col`
- Procesos dominantes: `NATIVE_FORM_DML`, `NATIVE_PLSQL`
- Paginas utiles: `Basic Cards`, `Image URL`, `Embedded Video`, `Faceted Search with Cards`
- Uso recomendado: cards, media cards, cards con BLOB/URL, cards con faceted search

### `f103.zip`

- App: `Sample Charts`
- Alias: `SAMPLE-CHARTS`
- Paginas: `49`
- Regiones dominantes: `NATIVE_JET_CHART`, `NATIVE_IG`, `NATIVE_IR`
- Procedimientos dominantes: `create_jet_chart`, `create_jet_chart_series`, `create_jet_chart_axis`
- Procesos dominantes: `NATIVE_PLSQL`
- Paginas utiles: `Area`, `Pie`, `Dashboard`, `Scatter`, `Bar`, `Line`
- Uso recomendado: Oracle JET Charts y combinaciones con IG/IR

### `f104.zip`

- App: `Sample Document Generator`
- Alias: `SAMPLE-DOCGEN`
- Paginas: `4`
- Regiones dominantes: `NATIVE_DYNAMIC_CONTENT`, `NATIVE_CARDS`
- Procesos dominantes: `PLUGIN_COM.ORACLE.APEX.DOCGEN`, `NATIVE_PLSQL`, `NATIVE_INVOKE_API`
- Hallazgo clave: el generador de documentos depende de un plugin/proceso dedicado
- Uso recomendado: document generation y patrones de contenido dinamico

### `f105.zip`

- App: `Sample Data Loading`
- Alias: `SAMPLE-DATA-LOADING`
- Paginas: `18`
- Regiones dominantes: `NATIVE_IR`
- Procesos dominantes: `NATIVE_DATA_LOADING`, `NATIVE_PARSE_UPLOADED_DATA`, `NATIVE_LOAD_UPLOADED_DATA`, `NATIVE_EXECUTION_CHAIN`
- Paginas utiles: `CSV Load`, `Transform and Lookup`, `Background Load`, `Load Status`
- Uso recomendado: asistentes de carga, parsing y validacion de archivos

### `f106.zip`

- App: `Sample Dynamic Actions`
- Alias: `SAMPLE-DYNAMIC-ACTIONS`
- Paginas: `27`
- Regiones dominantes: `NATIVE_IR`
- Procedimientos dominantes: `create_page_da_event`, `create_page_da_action`
- Procesos dominantes: `NATIVE_FORM_FETCH`, `NATIVE_FORM_PROCESS`, `NATIVE_PLSQL`
- Paginas utiles: `Disable/Enable`, `Hide/Show`, `Execute PL/SQL Code`, `Set Values (SQL)`
- Uso recomendado: Dynamic Actions y patron declarativo evento -> accion

### `f107.zip`

- App: `Sample File Upload and Download`
- Alias: `SAMPLE-FILE-UPLOAD-DOWNLOAD`
- Paginas: `13`
- Regiones dominantes: `NATIVE_IR`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_FORM_FETCH`, `NATIVE_FORM_PROCESS`
- Paginas utiles: `Projects`, `Files`, `Delete Files`, `File`, `Project`
- Uso recomendado: carga/descarga de archivos y manejo de BLOBs

### `f108.zip`

- App: `Sample Email Authentication`
- Alias: `EMA`
- Paginas: `16`
- Regiones dominantes: `NATIVE_IR`, `NATIVE_FORM`, `NATIVE_DYNAMIC_CONTENT`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_INVOKE_API`, `NATIVE_CLOSE_WINDOW`
- Paginas utiles: `Protected Page`, `User Verification`, `Manage User Access`
- Uso recomendado: autenticacion por email, verificacion de usuario y manejo de errores/mensajes

### `f109.zip`

- App: `Sample Interactive Grids`
- Alias: `SAMPLE-INTERACTIVE-GRIDS`
- Paginas: `49`
- Regiones dominantes: `NATIVE_IG`
- Procedimientos dominantes: `create_region_column`, `create_interactive_grid`, `create_ig_report`, `create_ig_report_view`, `create_ig_report_column`
- Procesos dominantes: `NATIVE_IG_DML`
- Paginas utiles: `Basic Reporting`, `Basic Editing`, `Validation`, `Master Detail`, `Dynamic Actions`
- Uso recomendado: fuente principal para construir y entender Interactive Grid, especialmente editable

### `f110.zip`

- App: `Sample Maps`
- Alias: `SAMPLE-MAPS`
- Paginas: `17`
- Regiones dominantes: `NATIVE_MAP_REGION`, `NATIVE_IR`, `NATIVE_CARDS`, `NATIVE_FACETED_SEARCH`
- Procedimientos dominantes: `create_map_region_layer`
- Paginas utiles: `Airports Heat Map`, `Airports Map`, `Airports Faceted Search`, `Map and Report`, `Nearest Neighbor Search`
- Uso recomendado: mapas nativos, capas y combinaciones mapa + reporte

### `f111.zip`

- App: `Sample Master Detail`
- Alias: `SAMPLE-MASTER-DETAIL`
- Paginas: `34`
- Regiones dominantes: `NATIVE_IG`, `NATIVE_FORM`, `NATIVE_IR`, `NATIVE_CSS_CALENDAR`
- Procedimientos dominantes: `create_region_column`, `create_ig_report_column`, `create_page_item`
- Procesos dominantes: `NATIVE_IG_DML`, `NATIVE_FORM_INIT`, `NATIVE_FORM_DML`, `NATIVE_CLOSE_WINDOW`
- Paginas utiles: `Side by Side`, `Tasks`, `Task Detail`, `Stacked with Sub Detail`
- Uso recomendado: master-detail, dialogs, formularios y grids coordinados

### `f112.zip`

- App: `Sample Reporting`
- Alias: `SAMPLE-REPORTING`
- Paginas: `42`
- Regiones dominantes: `NATIVE_IR`, `NATIVE_IG`, `NATIVE_JET_CHART`, `NATIVE_CARDS`, `NATIVE_FACETED_SEARCH`
- Procedimientos dominantes: `create_worksheet_column`, `create_report_columns`, `create_region_column`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_IG_DML`
- Paginas utiles: `Interactive Report`, `Classic Report`, `Filtering`, `Interactive Grid`, `Analytic Function Examples`
- Uso recomendado: reportes clasicos, IR, IG y consultas analiticas

### `f113.zip`

- App: `Sample Trees`
- Alias: `SAMPLE-TREES`
- Paginas: `11`
- Regiones dominantes: `NATIVE_JSTREE`, `NATIVE_JET_CHART`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_FORM_FETCH`, `NATIVE_FORM_PROCESS`
- Paginas utiles: `Project Tracking`, `Project Dashboard`, `Create/Edit Project`, `Create/Edit Tasks`
- Uso recomendado: arboles, jerarquias y mantenimiento sobre estructuras padre-hijo

### `f114.zip`

- App: `Sample REST Services`
- Alias: `SAMPLE-REST-SERVICES`
- Paginas: `37`
- Regiones dominantes: `NATIVE_IR`, `NATIVE_JET_CHART`, `NATIVE_CARDS`, `NATIVE_MAP_REGION`, `NATIVE_CSS_CALENDAR`, `NATIVE_SMART_FILTERS`
- Procedimientos dominantes: `create_web_source_operation`, `create_data_profile_col`, `create_region_column`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_WORKFLOW`, `NATIVE_INVOKE_API`
- Paginas utiles: `Simple HTTP`, `ORDS`, `OData`, `Cards Layout`, `Map`, `Calendar`
- Uso recomendado: REST Data Sources, web source modules, integracion HTTP y mezcla de REST con UI nativa

### `f115.zip`

- App: `Universal Theme 24.2 Reference`
- Alias: `UT`
- Paginas: `120`
- Regiones dominantes: `NATIVE_DISPLAY_SELECTOR`, `NATIVE_CARDS`, `NATIVE_IR`, `NATIVE_IG`, `NATIVE_SEARCH_REGION`, `NATIVE_CSS_CALENDAR`, `NATIVE_MAP_REGION`, `NATIVE_JSTREE`
- Procedimientos dominantes: `create_page_plug`, `create_page_button`, `create_region_column`, `create_report_region`
- Paginas utiles: `Grid Layout`, `Colors`, `Theme Styles`, `Navigation`, `Data Entry`, `Layout`
- Uso recomendado: referencia de templates, theme options, layouts y patrones visuales de UT 24.2

### `f116.zip`

- App: `Sample Vector Search`
- Alias: `SAMPLE-VECTOR-SEARCH109`
- Paginas: `27`
- Regiones dominantes: `NATIVE_SEARCH_REGION`, `NATIVE_CARDS`
- Procedimientos dominantes: `create_search_region_source`, `create_page_validation`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_EXECUTION_CHAIN`, `NATIVE_DATA_LOADING`, `NATIVE_INVOKE_API`
- Paginas utiles: `Movie Vector Search`, `Basic Vector Search`, `Vector vs. Oracle Text`, `Custom Vector Search`
- Uso recomendado: vector search, ingestion de embeddings y comparacion con Oracle Text

### `f117.zip`

- App: `Sample Workflow, Approvals, and Tasks`
- Alias: `SAMPLE-WORKFLOW-APPROVALS`
- Paginas: `34`
- Regiones dominantes: `NATIVE_IG`, `NATIVE_FORM`, `NATIVE_WORKFLOW_DIAGRAM`, `NATIVE_SMART_FILTERS`, `NATIVE_JSTREE`
- Procedimientos dominantes: `create_workflow_activity`, `create_workflow_transition`, `create_region_column`
- Procesos dominantes: `NATIVE_MANAGE_TASK`, `NATIVE_WORKFLOW`, `NATIVE_CREATE_TASK`, `NATIVE_IG_DML`
- Paginas utiles: `My Tasks`, `Request Salary Change`, `Pending Approvals`, `Task Administration`
- Uso recomendado: workflows, approvals, tasks y dashboards operativos

### `f118.zip`

- App: `Image Support for Rich Text Editor`
- Alias: `IMAGE-SUPPORT-RTE`
- Paginas: `7`
- Regiones dominantes: `NATIVE_DYNAMIC_CONTENT`, `NATIVE_FORM`, `NATIVE_IR`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_INVOKE_API`, `NATIVE_FORM_INIT`
- Paginas utiles: `Image Support Demo`, `Edit Content`, `Get Image`
- Uso recomendado: Rich Text Editor con soporte de imagenes y entrega de binarios

### `f119.zip`

- App: `Brookstrut Sample App`
- Alias: `BROOKSTRUT`
- Paginas: `49`
- Regiones dominantes: `NATIVE_IR`, `NATIVE_DYNAMIC_CONTENT`, `NATIVE_FACETED_SEARCH`, `NATIVE_CSS_CALENDAR`, `NATIVE_MAP_REGION`, `NATIVE_IG`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_FORM_FETCH`, `NATIVE_FORM_PROCESS`
- Paginas utiles: `Store Locations Map`, `Products`, `Sales History Classic`, `Region Stores`
- Uso recomendado: referencia mixta de una app mas realista que combina varios componentes

### `f120.zip`

- App: `APEXToGo`
- Alias: `APEXTOGO`
- Paginas: `18`
- Regiones dominantes: `NATIVE_CARDS`, `TMPL_THEME_42$CONTENT_ROW`, `NATIVE_MAP_REGION`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_INVOKE_API`
- Paginas utiles: `Welcome`, `Discover`, `Restaurant`, `Cart`, `Orders`
- Uso recomendado: experiencia mobile-first, cards, content rows y flujo tipo consumer app

### `f121.zip`

- App: `APEX PWA Reference`
- Alias: `APEX-PWA-REFERENCE`
- Paginas: `16`
- Procedimientos dominantes: `create_pwa_shortcut`, `create_pwa_screenshot`, `create_report_region`
- Regiones dominantes: `NATIVE_DISPLAY_SELECTOR`
- Paginas utiles: `Push Notifications`, `Service Worker`, `Installation`, `Offline Fallback`
- Uso recomendado: PWA, manifest, shortcuts, screenshots y capacidades offline

### `f122.zip`

- App: `Sample Calendar`
- Alias: `SAMPLE-CALENDAR`
- Paginas: `37`
- Regiones dominantes: `NATIVE_CSS_CALENDAR`, `NATIVE_IR`, `NATIVE_FACETED_SEARCH`
- Procedimientos dominantes: `create_page_da_event`, `create_page_da_action`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_FORM_FETCH`, `NATIVE_FORM_PROCESS`, `NATIVE_CLOSE_WINDOW`
- Paginas utiles: `Time Line`, `Standard Calendars`, `Monthly Calendar: Projects`, `Week Calendar: Conference`
- Uso recomendado: calendarios, timeline y mantenimiento de eventos

### `f123.zip`

- App: `Sample Application Search`
- Alias: `SAMPLE-APPLICATION-SEARCH222776222`
- Paginas: `31`
- Regiones dominantes: `NATIVE_SEARCH_REGION`, `NATIVE_FORM`, `NATIVE_CARDS`, `NATIVE_MAP_REGION`
- Procedimientos dominantes: `create_search_region_source`, `create_page_process`, `create_page_item`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_FORM_INIT`, `NATIVE_FORM_DML`, `NATIVE_INVOKE_API`
- Paginas utiles: `Single Search Configuration`, `Multiple Search Configurations`, `REST Data Source`, `Custom Result Row Template`
- Uso recomendado: busqueda nativa, search configurations y resultados enriquecidos

### `f124.zip`

- App: `Sample Collections`
- Alias: `SAMPLE-COLLECTIONS`
- Paginas: `14`
- Regiones dominantes: `NATIVE_IR`
- Procesos dominantes: `NATIVE_PLSQL`, `NATIVE_SESSION_STATE`
- Paginas utiles: `Create Collection`, `Modify Collection`, `Data Synchronization`, `API Examples`
- Uso recomendado: APEX collections, staging temporal y sincronizacion de datos

## Hallazgos operativos clave

- `f109.zip` es la referencia principal para `Interactive Grid`, y la pagina mas util para clonar un grid editable simple es `page_00030.sql` (`Basic Editing`).
- `f101.zip` sirve como referencia de una pagina vacia sobre la base `test/test101`, pero no como export confiable de plantilla porque el alias exportado quedo `TEST100`.
- `f100.zip` sigue siendo la mejor base minima para recrear la app `101`.
- `f115.zip` es la referencia de Universal Theme y ayuda cuando hace falta saber que template option, tipo de region o layout usa un componente nativo.
- `f114.zip`, `f117.zip`, `f121.zip` y `f123.zip` son las mejores referencias para componentes avanzados que no aparecen en la app base.
