# STP APEX

Repo base para trabajar con Oracle Database y Oracle APEX desde VS Code para el workspace `STP`.

## Arranque rapido

Antes de volver a investigar la conexion, revisar:

- `docs/oracle-connection-playbook.md`

Ese playbook deja documentado:

- la ruta mas rapida para conectarse por `ORDS`
- la URL ya validada de `REST Enabled SQL`
- el `workspace_id` de `STP`
- la version APEX instalada
- el remoto GitHub ya validado
- los limites de `SQLcl` y de la sesion de VS Code
- las rutas locales del wallet y de `DBTools`
- el flujo exacto para crear, exportar, importar y probar una app APEX

## Scripts reutilizables

Se agregaron scripts para no repetir trabajo:

- `scripts/apex/export-app.ps1`
- `scripts/apex/import-app.ps1`
- `tests/playwright/app101-smoke.spec.js`
- `playwright.config.js`

Flujo recomendado:

1. Crear la app la primera vez en APEX o exportar una app base existente.
2. Preferir export `.sql` para una importacion fiel; usar split `.zip` cuando haga falta clonar una app base.
3. Exportarla con `scripts/apex/export-app.ps1`.
4. Crear otra app a partir de ese export con `scripts/apex/import-app.ps1`.
5. Validar con Playwright al menos la carga del login.

## Estado actual

- Repo local creado en `C:\HT\stp-apex`.
- Remoto Git configurado:
  - `origin = https://github.com/htroya/stp-apex.git`
- Rama actual:
  - `master`
- Push ya realizado a GitHub:
  - `origin/master`
- Extension instalada en VS Code:
  - `Oracle SQL Developer for VS Code`
- Conexion Oracle ya existente en VS Code:
  - nombre visible: `hhhhhtroya`
  - sesion visible en la UI: `ADMIN@HHHHHTROYA_MEDIUM`
- Workspace APEX creado:
  - `STP`
- Java 17 instalado a nivel usuario para poder usar herramientas Oracle sin permisos de administrador.
- `ORDS REST Enabled SQL` es el camino mas estable para automatizacion.
- `SQLcl` sirve para exportar y sesiones manuales con clave en runtime.

## Estado APEX actual

- App `100` (`test`) existe en el workspace `STP`.
- El export base funcional disponible en el repo se genera como `apex/exports/f100.sql`.
- App `101` (`test101`) fue recreada desde ese export SQL completo y quedo con paginas `0`, `1` y `9999`.
- La URL de login de la app `101` ya responde `200` y carga `P9999_USERNAME` y `P9999_PASSWORD`.
- El smoke de Playwright `tests/playwright/app101-smoke.spec.js` ya pasa contra la app `101`.
- Estado actual de paginas en `101`:
  - `0` Global Page
  - `1` Home
  - `9999` Login
- Conclusion operativa:
  - para clonar apps por automatizacion, usar export SQL completo.
  - el import split por `ORDS` queda como alternativa avanzada y requiere validacion extra.

## Decision sobre GitHub

Si, se usa GitHub.

Este repo ya esta apuntando a:

`https://github.com/htroya/stp-apex.git`

Objetivo de GitHub:

- versionar scripts SQL
- versionar exportes de la aplicacion APEX
- guardar documentacion y decisiones
- poder retomar el trabajo sin depender de memoria o del chat

Si por cualquier razon no se quiere usar GitHub, el repo local sigue sirviendo. Pero la recomendacion es usar ambos:

- repo local en `C:\HT\stp-apex`
- remoto GitHub en `htroya/stp-apex`

## Estructura

- `db/install`: scripts base de esquema
- `db/patches`: cambios incrementales
- `apex/exports`: exportes versionados de la aplicacion APEX
- `docs`: notas operativas

## Archivos existentes

- `db/install/001_stp_base.sql`
- `docs/next-steps-apex.md`
- `.gitignore`

## Script base actual

`db/install/001_stp_base.sql` crea una tabla simple para arrancar la primera app:

- `STP_TASK`

Incluye:

- PK identity
- campo `TITLE`
- campo `STATUS`
- campo `NOTES`
- timestamp `CREATED_AT`
- 2 registros semilla

## Flujo de trabajo recomendado

1. Abrir `C:\HT\stp-apex` en VS Code.
2. Usar la conexion `hhhhhtroya` en Oracle SQL Developer.
3. Ejecutar los scripts SQL del repo desde un SQL Worksheet.
4. Crear o modificar la app en APEX.
5. Exportar la app al repo en `apex/exports`.
6. Hacer `git add`, `git commit` y `git push`.

## Lo ya resuelto

### Oracle / VS Code

- La conexion `hhhhhtroya` ya esta creada y conectada en la extension Oracle.
- La extension corre un servidor local DB Tools.
- Se detecto una sesion activa de esa conexion en el servidor local de la extension.

### Java / SQLcl

- Java 17 quedo instalado como usuario, sin admin.
- `JAVA_HOME` de usuario fue configurado.
- El runtime quedo en una ruta de usuario similar a:
  - `%USERPROFILE%\tools\temurin-17-jre\...`

Nota:

- El `sql.exe` de SQLcl da mensajes de `java.io.IOException: Funcion incorrecta` en algunas invocaciones del wrapper.
- Aun asi SQLcl si responde en modo util para automatizacion cuando se lo invoca de ciertas formas desde VS Code/terminal.

### Git

- El repo local ya existe.
- El remoto `origin` ya esta configurado a GitHub.

## Flujo base para una app nueva

### Paso 1. Ejecutar el script base

Desde la conexion `hhhhhtroya`, abrir un SQL Worksheet y ejecutar:

`db/install/001_stp_base.sql`

Resultado esperado:

- existe la tabla `STP_TASK`
- hay 2 filas de ejemplo

### Paso 2. Crear la primera app APEX

Dentro del workspace `STP`:

1. `App Builder`
2. `Create`
3. `New Application`
4. Nombre: `STP`
5. Agregar una pagina `Report and Form`
6. Tabla base: `STP_TASK`
7. Crear la aplicacion
8. Ejecutarla

Resultado esperado:

- pagina inicial con reporte sobre `STP_TASK`
- formulario CRUD basico
- aplicacion ejecutable desde APEX

### Paso 3. Exportar la app

Una vez creada la app:

- exportar la aplicacion APEX
- guardar el export en `apex/exports`

Convencion sugerida:

- `apex/exports/f100.sql` si se exporta en archivo unico
- o formato split si luego se automatiza con SQLcl/APEX export

## Crear una pagina nueva rapido

Si la necesidad es agregar una pagina vacia a una app ya existente, la via mas rapida es la UI de APEX:

1. Abrir `App Builder`.
2. Entrar a la aplicacion, por ejemplo `101`.
3. Click en `Create Page`.
4. Elegir `Blank Page`.
5. Definir `Page Number`, `Name` y `Navigation`.
6. Crear la pagina.
7. Ejecutar la app y validar la nueva ruta.

Nota:

- la automatizacion de export/import ya esta cerrada
- la creacion automatizada de paginas individuales no se dejo como flujo principal
- para una pagina vacia simple, el wizard de APEX sigue siendo lo mas rapido y menos riesgoso

## Estado de automatizacion

La automatizacion ya cubre export e import de manera funcional cuando se usa export SQL completo.

Lo investigado:

- la extension Oracle guarda la conexion en el secure store de VS Code
- el alias visible es `hhhhhtroya`
- la sesion local detectada fue `ADMIN@HHHHHTROYA_MEDIUM`
- la extension expone un servidor local DB Tools en `localhost`
- se localizaron referencias a la conexion y sesion en logs
- la definicion reusable de la conexion quedo localizada en:
  - `C:\Users\hernan.troya\AppData\Roaming\DBTools\connections\nvL1f1LKhg3dUVx2fm3log`
- dentro de esa carpeta existen:
  - `dbtools.properties`
  - `tnsnames.ora`
  - `cwallet.sso`
  - `credentials.sso`
  - `ojdbc.properties`

Bloqueo actual:

- la password no esta guardada de forma reutilizable para `SQLcl`
- `SQLcl` si detecta la conexion `hhhhhtroya`, pero la muestra como `password: sin guardar`
- por eso, aunque el alias, el usuario y el wallet si se pueden reutilizar, la autenticacion no entra desde terminal sin volver a proporcionar la clave
- la sesion viva de la UI de VS Code no se puede enganchar de forma estable desde terminal para ejecutar SQL como si ya estuviera autenticada

Conclusion practica:

- para crear la primera app rapido, usar APEX web
- para versionar y replicar, exportar la app y trabajar sobre scripts/versionados
- preferir export `.sql` como flujo principal
- si se usa export split `.zip`, validar autenticacion, URLs y apertura de paginas despues del import

## Conexion Oracle recuperable

Datos confirmados localmente:

- alias visible: `hhhhhtroya`
- usuario: `ADMIN`
- servicio configurado: `HHHHHTROYA_MEDIUM`
- ruta de la conexion: `C:\Users\hernan.troya\AppData\Roaming\DBTools\connections\nvL1f1LKhg3dUVx2fm3log`
- host ADB en `tnsnames.ora`: `adb.us-ashburn-1.oraclecloud.com`

Archivo `dbtools.properties` detectado:

```properties
name=hhhhhtroya
type=ORACLE_DATABASE
userName=ADMIN
connectionString=HHHHHTROYA_MEDIUM
```

Servicios disponibles en `tnsnames.ora`:

- `hhhhhtroya_high`
- `hhhhhtroya_medium`
- `hhhhhtroya_low`
- `hhhhhtroya_tp`
- `hhhhhtroya_tpurgent`

## Como retomar rapido la conexion

### Opcion 1. Seguir por la UI de VS Code

Es la opcion mas rapida cuando la conexion `hhhhhtroya` ya aparece conectada.

Pasos:

1. Abrir el panel Oracle en VS Code.
2. Verificar que `hhhhhtroya` siga conectada.
3. Abrir un `SQL Worksheet`.
4. Ejecutar desde ahi los scripts del repo.

### Opcion 2. Conectar desde terminal con SQLcl

Condicion importante:

- hace falta la clave del usuario, porque `SQLcl` no la recupera de la sesion abierta en la UI

Variables necesarias para que `SQLcl` funcione de forma consistente en esta maquina:

```powershell
$env:JAVA_HOME='C:\Users\hernan.troya\.vscode\extensions\oracle.sql-developer-25.4.1-win32-x64\dbtools\jdk'
$env:PATH="$env:JAVA_HOME\bin;$env:PATH"
$env:TNS_ADMIN='C:\Users\hernan.troya\AppData\Roaming\DBTools\connections\nvL1f1LKhg3dUVx2fm3log'
```

Prueba minima de `SQLcl`:

```powershell
cmd /c "echo exit | sql /nolog"
```

Conexion interactiva:

```powershell
sql /nolog
connect ADMIN@hhhhhtroya_medium
```

o directa:

```powershell
sql ADMIN@hhhhhtroya_medium
```

Nota:

- en ambos casos `SQLcl` va a pedir la clave si no se la pasas en ese momento
- no dejar la clave escrita en el repo ni en scripts versionados

## Comandos utiles de diagnostico

Mostrar conexiones conocidas por `SQLcl`:

```powershell
cmd /c "(echo connmgr list -flat& echo exit) | sql -home C:\Users\hernan.troya\AppData\Roaming\DBTools /nolog"
```

Ver detalle de la conexion:

```powershell
cmd /c "(echo connmgr show hhhhhtroya& echo exit) | sql -home C:\Users\hernan.troya\AppData\Roaming\DBTools /nolog"
```

Resultado esperado del detalle:

- nombre: `hhhhhtroya`
- usuario: `ADMIN`
- cadena de conexion: `HHHHHTROYA_MEDIUM`
- password: `sin guardar`

Probar la conexion:

```powershell
cmd /c "(echo connmgr test hhhhhtroya& echo exit) | sql -home C:\Users\hernan.troya\AppData\Roaming\DBTools /nolog"
```

Si pide password o responde `ORA-01017`, el problema no es el wallet ni el alias:

- falta volver a ingresar la clave del usuario
- la extension de VS Code puede estar conectada, pero esa autenticacion no queda reutilizable desde `SQLcl`

## Proximo punto de retomada

Cuando se retome esta tarea, arrancar aqui:

1. abrir `C:\HT\stp-apex`
2. verificar conexion `hhhhhtroya`
3. si se necesita terminal, exportar `JAVA_HOME`, `PATH` y `TNS_ADMIN` como se indica arriba
4. si `SQLcl` pide password, ingresarla en el momento; no asumir que la UI conectada la comparte
5. ejecutar `db/install/001_stp_base.sql`
6. crear app `STP` sobre `STP_TASK`
7. exportar la app a `apex/exports`
8. hacer primer commit a GitHub

## Comandos Git utiles

Desde `C:\HT\stp-apex`:

```powershell
git status
git add .
git commit -m "Base inicial STP APEX"
git push -u origin <rama-actual>
```

## Riesgos / notas

- No compartir URLs APEX con `session=...`.
- No guardar passwords, wallet zip ni secretos dentro del repo.
- No guardar la clave de `ADMIN` en `README.md`, scripts, historial versionado ni archivos `.sql`.
- No dejar la app final sobre `ADMIN` si luego se decide separar esquemas.

## Recomendacion tecnica

Para salir rapido:

- usar `ADMIN` para la primera prueba funcional

Para dejarlo bien:

- crear luego un esquema propio, por ejemplo `STP_APP`
- mover los objetos de negocio a ese esquema
- dejar `ADMIN` solo para administracion
