# APEX Zip Reference Map

Objetivo: tener un enrutador rapido para futuras tareas. Si el pedido del usuario menciona un componente o patron APEX, este documento debe ser la primera parada antes de abrir un zip o tocar SQL.

Fecha de verificacion: `2026-03-21`

## Uso en 60 segundos

1. identificar el sustantivo principal del pedido: `IG`, `Cards`, `Search`, `Map`, `Workflow`, `PWA`, `Calendar`, `Tree`, `Chart`, `File Upload`, `REST`, `Theme`, `Blank Page`
2. buscar ese sustantivo en la tabla de abajo
3. abrir el zip recomendado
4. abrir primero las paginas exactas listadas
5. si hace falta mas detalle, correr:

```powershell
python .\scripts\apex\analyze-backups.py --format markdown --page-limit 0
python .\scripts\apex\analyze-backups.py --contains NATIVE_IG --format markdown --page-limit 0
python .\scripts\apex\analyze-backups.py --contains create_search_region_source --format markdown --page-limit 0
python .\scripts\apex\analyze-backups.py --contains create_map_region_layer --format markdown --page-limit 0
```

## Mapa por zip

| Zip | Patron principal | Primeras paginas a inspeccionar | Supporting objects | Usar cuando el usuario pida... |
| --- | --- | --- | --- | --- |
| `f100.zip` | base app minima | `page_00001.sql` Home; `page_09999.sql` Login Page | none | clonar una app minima, login, home, menu lateral |
| `f101.zip` | blank page sobre base minima | `page_00002.sql` Blank Page | none | una pagina vacia o un injerto sobre la app base |
| `f102.zip` | cards | `page_00003.sql` Basic Cards; `page_00012.sql` Faceted Search with Cards; `page_00015.sql` Full Card Action | `install_scripts/*emp*` y `eba_demo_card_pkg.sql` | cards, media cards, actions, cards con faceted search |
| `f103.zip` | charts | `page_00002.sql` Area; `page_00004.sql` Pie; `page_00015.sql` Line; `page_00030.sql` JavaScript Code Customizations | `sample_data.sql`, `tables.sql`, `triggers.sql` | JET charts, ejes, leyendas, custom JS sobre charts |
| `f104.zip` | document generation | `page_00001.sql` Home; `page_10010.sql` About | `emp_dept.sql`, `order_items.sql` | document generator, dynamic content, plugin DocGen |
| `f105.zip` | data loading | `page_00011.sql` CSV Load; `page_00015.sql` Transform and Lookup; `page_00017.sql` Background Load; `page_00032.sql` Load Data using PL/SQL API | `create_tables.sql`, `eba_demo_data_load.sql`, `seed_sample_data.sql` | asistentes de carga, parseo, validacion, cargas en background |
| `f106.zip` | dynamic actions | `page_00002.sql` Disable/Enable; `page_00004.sql` Hide/Show; `page_00011.sql` Execute PL/SQL Code; `page_00012.sql` Set Values (SQL) | `create_tables.sql`, `insert_data.sql` | eventos declarativos, acciones cliente, refrescos y timers |
| `f107.zip` | file upload / download | `page_00002.sql` Projects; `page_00003.sql` Files; `page_00011.sql` Delete Files; `page_00012.sql` File | `files.sql`, `projects.sql`, `demo_load_body.sql` | BLOBs, subida y descarga de archivos, catalogos de archivos |
| `f108.zip` | email authentication | `page_00100.sql` Protected Page; `page_09998.sql` User Verification; `page_10031.sql` Manage User Access | `create_first_user.sql`, `package_spec.sql`, `package_body.sql` | autenticacion por email, verificacion, alta de usuarios |
| `f109.zip` | interactive grid | `page_00003.sql` Basic Reporting; `page_00030.sql` Basic Editing; `page_00031.sql` Validation; `page_00035.sql` Master Detail; `page_00058.sql` Dynamic Actions | `data.sql`, `install.sql`, helper Oracle Text | IG editable, reportes IG, validaciones, master-detail con IG |
| `f110.zip` | maps | `page_00110.sql` Airports Heat Map; `page_00111.sql` Airports Map; `page_00120.sql` Airports Faceted Search; `page_00123.sql` Map and Report; `page_00124.sql` Nearest Neighbor Search | `create_spatial_indexes.sql`, `table_eba_sample_map_airports.sql`, `table_eba_sample_map_states.sql` | mapas, capas, heatmaps, busquedas geoespaciales |
| `f111.zip` | master detail | `page_00002.sql` Side by Side; `page_00005.sql` Project Detail; `page_00008.sql` Tasks; `page_00033.sql` Stacked with Sub Detail | `create_tables.sql`, `create_data_package.sql` | formularios + grids coordinados, dialogs, subdetail |
| `f112.zip` | reporting | `page_00001.sql` Interactive Report; `page_00003.sql` Classic Report; `page_00005.sql` Filtering; `page_00017.sql` Interactive Grid | `create_table.sql`, `load_data.sql`, `pipelined_function_package.sql`, `upgrade_scripts/*` | IR, classic report, analytic queries, mezcla report + IG |
| `f113.zip` | trees | `page_00003.sql` Project Tracking; `page_00004.sql` Project Dashboard; `page_00005.sql` Create/Edit Project; `page_00006.sql` Create/Edit Tasks | `create_tables.sql`, `create_view.sql`, `create_triggers.sql` | arboles, jerarquias, navegacion parent-child |
| `f114.zip` | REST data sources | `page_00101.sql` Simple HTTP; `page_00102.sql` ORDS; `page_00304.sql` Cards Layout; `page_00307.sql` Map; `page_00405.sql` Nested JSON & Dynamic Actions | `ords_definition.sql`, `table_definition.sql`, `etlprocess.sql` | REST, web sources, mezclas REST + UI nativa, nested JSON |
| `f115.zip` | Universal Theme reference | `page_00407.sql` Navigation; `page_01120.sql` Navigation Menu - Menu Bar Preview; `page_01410.sql` Interactive Grid; `page_01413.sql` Reports - Search Region; `page_01906.sql` Map | `create_tables.sql`, `create_airports_table.sql`, `upgrade_scripts/*` | templates, navigation, layout, theme options, previews UT |
| `f116.zip` | vector search | `page_00010.sql` Movie Vector Search; `page_00015.sql` Basic Vector Search; `page_00024.sql` Custom Vector Search; `page_00054.sql` Set AI Provider | `create_sample_data.sql`, `helper_package.sql` | vector search, embeddings, AI provider, search semantico |
| `f117.zip` | workflow / approvals / tasks | `page_00003.sql` My Tasks; `page_00004.sql` Request Salary Change; `page_00012.sql` Pending Approvals; `page_00030.sql` Workflow Dashboard; `page_00031.sql` Workflow Diagram | `installlaptoprequeststable.sql`, `installotherschemaobjects.sql`, `installsampledata.sql` | workflows, approvals, tasks, manage task, workflow diagram |
| `f118.zip` | RTE with images | `page_00002.sql` Image Support Demo; `page_00003.sql` Edit Content; `page_09000.sql` Get Image | `create_tables_and_view.sql`, `util_spec.sql`, `util_body.sql` | rich text editor con imagenes y endpoint binario |
| `f119.zip` | realistic mixed app | `page_00010.sql` Store Locations Map; `page_00017.sql` Activity Calendar; `page_00023.sql` Sales History Interactive Grid; `page_00046.sql` Sales History Cards | muchos `install_scripts/*` de datos y logging | app realista que mezcla mapas, calendarios, grids, cards y reportes |
| `f120.zip` | mobile / consumer style | `page_00001.sql` Welcome; `page_00002.sql` Discover; `page_00005.sql` Restaurant; `page_00008.sql` Cart; `page_00009.sql` Orders | `install_restaurant_tables.sql`, `install_manage_orders_package.sql` | experiencias mobile-first, consumer flows, cards + mapa + carrito |
| `f121.zip` | PWA | `page_00003.sql` Push Notifications; `page_00005.sql` Service Worker; `page_00007.sql` Installation; `page_00011.sql` Offline Fallback | none | manifest, service worker, push notifications, offline |
| `f122.zip` | calendar | `page_00004.sql` Time Line; `page_00030.sql` Standard Calendars; `page_00034.sql` Weekly Calendar: Drag & Drop; `page_00110.sql` Custom Calendar Initialization | `create_tables.sql`, `insert_data.sql` | calendarios, drag & drop, client events, custom JS |
| `f123.zip` | application search | `page_00101.sql` Single Search Configuration; `page_00102.sql` Multiple Search Configurations; `page_00204.sql` Custom Result Row Template; `page_00302.sql` Map Region | `data.sql`, `install.sql`, helper Oracle Text | search region, search configs, result templates, search con mapa o cards |
| `f124.zip` | collections | `page_00002.sql` Create Collection; `page_00003.sql` Modify Collection; `page_00006.sql` Data Synchronization; `page_00012.sql` API Examples | `create_eba_demo_cs_emp_table.sql`, `sample_data.sql` | APEX collections, staging temporal, sincronizacion |

## Mapa por pedido

| Si el pedido dice... | Ir primero a... |
| --- | --- |
| `pagina vacia` | `f101.zip` -> `page_00002.sql` |
| `agrega navegacion / menu / shortcut` | `f100.zip` y `f115.zip` -> `shared_components/navigation` |
| `interactive grid editable` | `f109.zip` -> `page_00030.sql` |
| `master detail` | `f111.zip` -> `page_00002.sql`, `page_00033.sql` |
| `cards` | `f102.zip` -> `page_00003.sql`, `page_00012.sql` |
| `charts` | `f103.zip` -> `page_00002.sql`, `page_00015.sql` |
| `mapa` | `f110.zip` -> `page_00111.sql`, `page_00123.sql` |
| `rest data source` | `f114.zip` -> `page_00101.sql`, `page_00304.sql` |
| `workflow / approvals / tasks` | `f117.zip` -> `page_00003.sql`, `page_00030.sql`, `page_00031.sql` |
| `search` | `f123.zip` -> `page_00101.sql`, `page_00204.sql` |
| `vector search / ai` | `f116.zip` -> `page_00010.sql`, `page_00024.sql`, `page_00054.sql` |
| `calendar` | `f122.zip` -> `page_00030.sql`, `page_00034.sql`, `page_00110.sql` |
| `pwa` | `f121.zip` -> `page_00003.sql`, `page_00005.sql`, `page_00011.sql` |
| `tree` | `f113.zip` -> `page_00003.sql` |
| `rich text editor con imagenes` | `f118.zip` -> `page_00002.sql`, `page_09000.sql` |
| `collections` | `f124.zip` -> `page_00002.sql`, `page_00006.sql`, `page_00012.sql` |

## Regla de oro

No inventar desde cero si ya existe una pagina de muestra.

Orden correcto:

1. leer este mapa
2. abrir el zip fuente correcto
3. abrir la pagina exacta
4. copiar el patron `create_*` en el orden real
5. adaptar ids, owner, alias, tablas y supporting objects
6. validar por metadata y por navegador/Playwright
