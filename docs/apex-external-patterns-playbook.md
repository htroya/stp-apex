# APEX External Patterns Playbook

Objetivo: capturar patrones reutilizables aprendidos de fuentes externas para no volver a investigar desde cero cuando el pedido no este cubierto solo por los respaldos `f100.zip` a `f124.zip`.

Fecha de verificacion: `2026-03-21`

Fuentes base revisadas:

- `https://oracleapex.com/ords/r/gamma_dev/demo`
- `https://pretius.com/blog/oracle-apex-tutorial`
- `https://traust.com/blog-old/oracle-apex-academy/`

## Indice de fuentes exactas

### Oracleapex.com demo

- home: `https://oracleapex.com/ords/gamma_dev/r/demo/home`
- markdown: `https://oracleapex.com/ords/r/gamma_dev/demo/markdown`
- charts: `https://oracleapex.com/ords/gamma_dev/r/demo/charts`
- chat: `https://oracleapex.com/ords/r/gamma_dev/demo/chat`
- geocoding: `https://oracleapex.com/ords/r/gamma_dev/demo/geocoding`
- demo data load: `https://oracleapex.com/ords/r/gamma_dev/demo/demo-data-load`
- new features: `https://oracleapex.com/ords/r/gamma_dev/demo/new-features`

### Pretius

- tutorial base: `https://pretius.com/oracle-apex-tutorial/`

### Traust

- academy index: `https://traust.com/blog-old/oracle-apex-academy/`
- practical UX: `https://traust.com/blog/practical-ux-principles-for-oracle-apex-developers/`
- accessible color palette: `https://traust.com/blog/creating-an-accessible-color-palette-for-oracle-apex-universal-theme/`
- disable IG column: `https://traust.com/blog/disable-ig-column-in-oracle-apex/`
- page is not available: `https://traust.com/blog/oracle-apex-page-isnt-available-error/`
- collections: `https://traust.com/blog/exploring-oracle-apex-collections/`
- APEX 24.2: `https://traust.com/blog/whats-new-in-apex-24-2-enhancements-that-matter/`
- switch widgets: `https://traust.com/blog/read-only-disable-switch-widgets-in-oracle-apex/`

## Regla de uso

Leer este documento cuando pase una de estas cosas:

- el usuario pida un patron mas cercano a demos publicas que a los zips del repo
- el pedido combine UI moderna, REST, mapas, sincronizacion, PWA, UX o gobierno de desarrollo
- el pedido sea mas de practica APEX que de estructura interna de export

Orden recomendado:

1. leer este playbook para enrutar el caso
2. leer [apex-zip-reference-map.md](/C:/HT/stp-apex/docs/apex-zip-reference-map.md) para buscar el respaldo mas cercano
3. si existe patron en zip, copiarlo desde el export
4. si no existe o el ejemplo externo es mas fuerte, seguir la receta externa de este documento
5. documentar el componente terminado con export, script y prueba

## Lo nuevo que aportan estas fuentes

Los respaldos del repo sirven para copiar SQL APEX real. Estas fuentes externas agregan otras tres capas:

- patrones funcionales: como armar una demo coherente rapido
- patrones operativos: como trabajar con REST, sincronizacion, triggers JSON, theming y UX
- patrones de equipo: como versionar, coordinar multi-dev y validar despliegues

## Fuente 1: oracleapex.com demo

Uso principal: inspiracion de componentes de interfaz y demos mas "presentables" que las apps de muestra empaquetadas.

## Lo que conviene aprender de esta fuente

### 1. Demos pequenas, enfocadas y navegables

Patron:

- cada pagina resuelve una sola idea visible
- la UI demuestra una tecnica puntual, no un caso de negocio grande
- el valor esta en la experiencia concreta del usuario, no solo en la metadata

Uso practico:

- si el usuario pide "hazme un ejemplo rapido"
- si conviene demostrar un patron aislado antes de meterlo a una app mayor

### 2. Personalizacion visual sobre componentes nativos

Los resultados de esta fuente muestran demos de charts, markdown, datasets y otras variaciones de region. La lectura util es:

- no arrancar por plugins si una region nativa con CSS/JS declarativo resuelve el caso
- usar una pagina demo por tecnica
- encapsular estilos y pequenos scripts por pagina o por app, no dispersarlos sin criterio

Uso practico:

- charts con custom JS y colores controlados
- pages con presentacion tipo showcase
- demos con contenido enriquecido sin cambiar el core del componente

### 2.1 Markdown sin plugin extra

El demo de markdown muestra varios caminos reutilizables:

- `Display Only` convertido a markdown con JavaScript
- columna de `Classic Report` en modo markdown
- item o contenido estatico que ya renderiza markdown

Regla practica:

- si el usuario pide markdown en una pagina existente, primero probar soporte nativo del item o columna
- si no alcanza, aplicar una clase CSS a un bloque acotado y transformar el HTML con JS solo ahi
- no meter un parser markdown global a toda la app si el caso es local

### 2.2 Chart tuning declarativo + JS Initialization Code

El demo de charts expone algo valioso: el chart sigue siendo nativo, pero el ajuste fino vive en dos lugares claros:

- SQL que devuelve columnas de estilo, como color o ancho
- `JavaScript Initialization Code` para radio interno, etiquetas centrales u otras opciones

Patron:

1. query simple y legible
2. columnas auxiliares de presentacion
3. JS corto para opciones avanzadas

Regla:

- si el usuario pide "hazlo mas bonito" para charts, empezar por SQL + init JS; no por plugin ni reescritura completa

### 2.3 Chat region sobre Comments template

El demo de chat es especialmente reutilizable porque no depende de un plugin dedicado.

Patron:

1. `Classic Report`
2. template de comentarios
3. query con columna que marca si el mensaje es propio
4. clase CSS del reporte para invertir alineacion y globos

Uso practico:

- chats internos
- hilos de comentario
- bitacoras conversacionales

Regla:

- si el usuario pide "chat" o "timeline conversacional", primero intentar este patron
- usar tabla real si hay persistencia multiusuario
- usar collection si es un borrador temporal por sesion

### 2.4 Geocoding como paso previo al mapa

El demo de geocoding deja una leccion importante:

- no todo flujo geografico empieza por un `Map Region`
- a veces el paso critico es validar y normalizar la direccion antes de guardar coordenadas

Patron:

1. captura de pais y direccion
2. geocodificacion por proveedor
3. normalizacion de direccion
4. almacenamiento de latitud y longitud
5. recien despues visualizacion en mapa

Uso practico:

- direcciones postales
- catalogos de clientes o sucursales
- formularios con validacion geografica

### 2.5 Drag and drop para carga de archivos

El demo de data load muestra un patron visible y facil de repetir:

- area `drag and drop`
- carga desde `File Browse`
- grilla o reporte de archivos cargados

Regla:

- si el usuario pide "subir archivo" con buena UX, no quedarse solo con el item file
- completar con vista de estado, listado de resultados y metadatos del archivo

### 3. Combinacion de data source + presentacion

El valor de `oracleapex.com` no es solo la region. Tambien muestra el patron completo:

1. dataset o fuente
2. region nativa
3. ajuste visual o de interaccion
4. navegacion minima para probarlo

Regla operativa:

- si el usuario pide una demo visible, no crear solo la tabla y la region
- crear tambien el acceso navegable, datos semilla y una pagina enfocada

## Como usar esta fuente rapido

Si el pedido dice:

- `haz una demo rapida`: crear pagina aislada, region unica, datos semilla y entrada de navegacion
- `quiero que se vea mejor`: revisar primero `f115.zip` para theme/layout y despues aplicar el estilo de demo enfocado
- `quiero mostrar X en una sola pagina`: separar el componente en una pagina dedicada antes de integrarlo a una app grande

## Fuente 2: Pretius tutorial

Fuente:

- `https://pretius.com/blog/oracle-apex-tutorial`

Uso principal: flujo extremo a extremo para pasar de dataset a aplicacion funcional con mapas, REST y sincronizacion.

## Aportes concretos de Pretius

### 1. Pensar APEX como RAD stack: ORDS + APEX + Database

Patron:

- la pagina vive en APEX
- ORDS la expone y hace de pasarela
- la base aloja app, metadata y datos

Consecuencia operativa:

- cuando algo falle, revisar siempre estos tres planos
- no tratar APEX como si fuera solo front-end

Checklist rapido:

- `ORDS` y URL correctas
- metadata APEX valida
- tablas, vistas, triggers o paquetes del esquema validos

### 2. Empezar con dataset o modelo ya listo

Pretius usa `Sample Datasets` para acelerar la primera version.

Uso practico:

- si el usuario pide una demo inmediata, empezar por dataset o tabla ya lista
- despues iterar con mapas, REST o LOVs

Regla:

- primero hacer que la app exista y sea navegable
- luego enriquecerla

Patron fuerte del tutorial:

- `SQL Workshop > Utilities > Sample Datasets`
- instalar dataset cercano al dominio
- pulsar `Create Application`
- correr la app antes de personalizarla

### 3. Convertir latitud/longitud en mapa sin rehacer la app

Patron del tutorial:

1. abrir pagina existente
2. arrastrar region `Map`
3. configurar tabla y columnas de coordenadas
4. ejecutar y validar

Uso practico:

- agregar mapa a pagina existente sin redisenar todo
- si el usuario tiene tabla con `latitude` y `longitude`, esta es la primera ruta

Relacion con respaldos del repo:

- para SQL real mirar `f110.zip`
- para idea funcional del flujo rapido mirar Pretius

### 4. Importar REST Source Catalog en vez de configurar REST a mano

Patron:

1. importar catalogo REST
2. crear `REST Data Source` desde catalogo
3. revisar metadata
4. usar la fuente en region o sincronizacion

Uso practico:

- ahorrar tiempo cuando ya existe definicion REST exportable
- evitar errores repetitivos de configuracion manual

Relacion con respaldos del repo:

- para objetos APEX mirar `f114.zip`
- para estrategia de montaje rapido usar este tutorial

### 5. Sincronizar REST a tabla local

Patron del tutorial:

1. crear `REST Data Source`
2. crear `Synchronization`
3. generar tabla local
4. definir agenda de ejecucion
5. ejecutar y revisar log

Uso practico:

- cuando el usuario quiera consultar remoto pero operar localmente
- cuando haga falta cache, historico o procesamiento posterior

Decision reutilizable:

- si el feed es append-only, una tabla local sincronizada simplifica reportes y procesos
- si ademas hace falta transformar JSON, usar trigger o proceso intermedio

Checklist recomendado:

- definir clave tecnica del feed
- decidir si la sincronizacion reemplaza o acumula
- guardar fecha de ultima sync
- revisar log antes de culpar a la UI

### 6. Transformar JSON con trigger y `JSON_TABLE`

El tutorial usa una tabla de sincronizacion y un trigger para descomponer JSON de detalle a tablas relacionales.

Patron tecnico:

1. llega fila sincronizada
2. trigger lee payload JSON
3. `JSON_TABLE` descompone el arreglo
4. se insertan filas en tablas maestras y detalle

Uso practico:

- APIs con cabecera y detalle
- integraciones ligeras dentro de la base

Regla:

- si la API trae estructuras anidadas, no intentar meter todo directo a un IR o IG
- primero normalizar datos

### 7. Enriquecer reportes con LOVs de descripcion

Patron del tutorial:

- sustituir IDs por valores legibles usando LOVs
- si APEX no trae LOV hecha, construirla con query builder

Uso practico:

- siempre revisar columnas tecnicas en reportes creados por wizard
- transformar claves foraneas visibles en descripciones antes de dar por terminada una pagina

Regla:

- si una pagina se ve "hecha por wizard", casi siempre falta este paso

## Ruta rapida inspirada en Pretius

Si el usuario pide:

- `crea una app demo rapido`: dataset primero, wizard despues
- `agrega un mapa`: agregar region `Map` sobre pagina existente
- `consume una API REST`: catalogo REST y `REST Data Source`
- `sincroniza datos remotos`: `Synchronization` + tabla local + log
- `la API trae JSON anidado`: tabla de staging + `JSON_TABLE`
- `el reporte se ve tecnico`: LOVs y labels antes de cerrar

## Fuente 3: Traust Oracle APEX Academy

Fuente:

- `https://traust.com/blog-old/oracle-apex-academy/`

Uso principal: buenas practicas tecnicas y de equipo alrededor de APEX, no solo componentes.

## Lo mas valioso que expone Traust

### 1. DevOps y CI/CD para APEX

La academia destaca trabajo reciente sobre `Oracle APEX DevOps` y despliegue seguro. La implicacion practica es clara:

- APEX no debe quedarse solo en cambios manuales por builder
- cada cambio importante debe terminar en export versionado
- la automatizacion necesita scripts de export, import y validacion

Reglas operativas para este repo:

1. no cerrar una tarea APEX sin export o script reproducible
2. versionar `db/install`, `db/patches`, `apex/exports`, `apex/snippets` y pruebas
3. preferir pruebas automatizadas sobre las paginas criticas

Relacion con este repo:

- ya existe base en [export-app.ps1](/C:/HT/stp-apex/scripts/apex/export-app.ps1)
- ya existe base en [import-app.ps1](/C:/HT/stp-apex/scripts/apex/import-app.ps1)
- ya existe base en [app101-smoke.spec.js](/C:/HT/stp-apex/tests/playwright/app101-smoke.spec.js)

### 2. Trabajo multi-desarrollador

Traust enfatiza que APEX multi-dev cambia cuando escala el equipo.

Interpretacion operativa:

- definir ownership por pagina o modulo
- evitar que varias personas editen la misma app sin exportar y sincronizar
- separar supporting objects, snippets y patches por unidad de cambio

Reglas para responder rapido a futuros pedidos:

- si el pedido toca una pagina existente, ubicar su export y no reconstruir a ciegas
- si el pedido agrega un modulo nuevo, crear pagina nueva + snippet + patch + prueba
- si el pedido es transversal, documentar impacto en navegacion, seguridad y objetos compartidos

### 3. Theming y branding mantenibles

La academia lista una guia reciente de theming. Lo reutilizable no es una paleta concreta sino el proceso:

1. ajustar Theme Roller o variables del tema
2. definir iconografia y branding consistentes
3. validar contraste y accesibilidad
4. encapsular CSS en nivel pagina/app, no en hacks dispersos

Uso practico:

- si el usuario pide "que se vea mejor", no tocar componentes al azar
- empezar por theme, tipografia, contrastes, iconos y layout

Relacion con respaldos:

- para referencias concretas abrir `f115.zip`
- para criterio de mantenimiento usar Traust

Acciones concretas:

1. revisar `Theme Roller`
2. validar contraste de colores
3. unificar texto claro u oscuro por familia de colores
4. evitar una paleta incoherente por pagina

La guia de paleta accesible agrega una decision importante:

- no asumir que la paleta por defecto cumple contraste suficiente
- si hace falta branding ligero y rapido, definir una paleta accesible primero y luego adaptar componentes

### 4. Principios de UX para APEX

La academia destaca que muchas apps APEX fallan mas por UX que por tecnologia.

Checklist reutilizable:

- una pagina, una tarea principal
- columnas visibles legibles, no IDs crudos
- navegacion obvia
- labels y mensajes claros
- reducir ruido en dialogs, botones y regiones

Regla:

- si la primera version funciona pero no se entiende, todavia no esta terminada

### 5. Collections como staging temporal

Traust tiene articulo especifico sobre `Oracle APEX Collections`.

Patron reutilizable:

- usar collections para datos temporales por sesion
- usar tabla real cuando haga falta persistencia, integridad o concurrencia durable

Decision rapida:

- wizard, carrito temporal, multistep form o seleccion intermedia: `APEX_COLLECTION`
- CRUD normal editable y compartido: tabla real

Relacion con respaldos:

- ejemplos SQL reales en `f124.zip`

### 6. Friendly URLs y errores de pagina no disponible

Traust tiene articulo sobre el error `Page isn't Available`.

Regla practica:

- cuando una pagina no abre, revisar alias, friendly URL y convenciones de nombre antes de culpar al componente
- si se clona una app, validar alias de app y alias de pagina

Uso directo en este repo:

- ya hubo errores por alias inconsistentes y pages importadas
- este tipo de revision debe ser parte del checklist post-import

### 7. Interactive Grid: columnas, errores y enlaces

Traust expone contenido sobre:

- deshabilitar columnas de IG
- errores condicionales en IG
- enlaces dinamicos desde reportes

Reglas reutilizables:

- no todo IG editable debe dejar todas las columnas editables
- la PK y columnas tecnicas deben tratarse distinto
- cuando el usuario reporta error de IG, revisar primero PK, proceso `NATIVE_IG_DML`, nullability y metadata de columnas

Relacion con este repo:

- esto ya aplica a `app 101`, `page 2`

Patrones concretos de Traust:

- columna de IG deshabilitada por `Static ID` + `Dynamic Action` + JS
- widgets `Switch` deshabilitados visualmente con JS sin perder session state
- errores de pagina no disponible ligados a alias duplicados y friendly URLs

### 8. Version control desde SQL Developer / export consistente

La academia incluye material viejo pero util sobre version control.

Regla:

- el builder es el editor, pero Git es la memoria real del trabajo
- exportar despues de cambios estables, no solo al final de semanas de trabajo

### 9. Quick SQL y modelado rapido

La academia menciona `Quick SQL`.

Uso practico:

- para prototipos o tablas ficticias, Quick SQL puede acelerar el primer modelo
- luego se consolida en `db/install` o `db/patches`

### 10. Testing y validacion

Aunque la pagina academy mezcla temas, el hilo comun es que APEX serio necesita pruebas.

Regla de este repo:

- cambios de paginas criticas se validan con Playwright
- cambios de esquema con SQL verificable
- cambios de import/export con script reproducible

### 11. APEX 24.2: que conviene explotar ya

La lectura de Traust sobre APEX 24.2 aporta una lista util para futuras tareas:

- `JSON Sources` reutilizables
- perfiles de datos autogenerados para JSON
- reportes, forms e IG declarativos sobre JSON
- DML declarativo sobre JSON con `JSON_TRANSFORM`
- workflows anidados y reanudables
- `Template Components`
- dialogs redimensionables
- mejoras de navegacion en Page Designer
- `Select Many` mas usable
- paginacion declarativa en refresh
- mejoras en `APEX_LANG`

Regla practica:

- si el usuario pide integrar JSON o automatizar procesos, revisar primero si APEX 24.2 lo resuelve declarativamente antes de escribir PL/SQL extra
- si el usuario pide UI reutilizable, considerar `Template Components` antes de duplicar regiones por copia manual

## Enrutador rapido por tipo de pedido

| Si el usuario pide... | Arranque recomendado |
| --- | --- |
| `haz una demo bonita y rapida` | `oracleapex.com` para patron de pagina enfocada + `f100.zip` o `f101.zip` para base |
| `conecta una API REST` | Pretius para flujo funcional + `f114.zip` para SQL real |
| `muestra datos en mapa` | Pretius para flujo de builder + `f110.zip` para estructura exportada |
| `sincroniza API a tablas` | Pretius: REST Sync + tabla local + trigger `JSON_TABLE` |
| `mejora look and feel` | Traust theming + UX + `f115.zip` |
| `aplica novedades utiles de APEX 24.2` | Traust 24.2 + revisar si basta `JSON Sources`, `Template Components` o workflow declarativo |
| `arma proceso con datos temporales` | Traust collections + `f124.zip` |
| `corrige pagina que no abre` | Traust friendly URLs + revisar alias de app/page |
| `equipo grande / no perder cambios` | Traust DevOps + multi-dev + export/import versionado |
| `quiero algo estilo showcase` | `oracleapex.com` + una pagina dedicada por tecnica |

## Protocolo reforzado para futuras tareas

Si el pedido es de APEX y hay que moverse rapido:

1. clasificar el pedido: `componente`, `integracion`, `UX/theme`, `operacion`, `gobierno`
2. abrir este documento
3. decidir si el patron dominante viene de `zips`, de `Pretius`, de `Traust` o de una demo tipo `oracleapex.com`
4. aterrizarlo en artefactos del repo:
   - `db/install` o `db/patches`
   - `apex/snippets`
   - `apex/exports`
   - `tests/playwright`
   - documentacion
5. no cerrar la tarea sin:
   - SQL reproducible o export
   - ruta de navegacion
   - validacion tecnica
   - nota en docs si el patron se va a reusar

## Checklist de salida

Antes de considerar "aprendido" un patron externo:

- existe fuente apuntada por URL
- existe equivalente local en script, snippet o export
- existe regla de cuando usarlo
- existe criterio para elegir entre tabla real, collection, REST directo o sincronizado
- existe criterio de validacion

Si falta una de esas cinco cosas, la documentacion todavia no esta lista para reutilizacion rapida.
