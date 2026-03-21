# APEX E2E Playbook

Objetivo: dejar un flujo fijo para probar apps APEX con Playwright sin volver a descubrir URLs, usuarios, paginas, ni selectores.

Fecha de verificacion: `2026-03-21`

## Lectura minima

1. [README.md](/C:/HT/stp-apex/README.md)
2. [oracle-connection-playbook.md](/C:/HT/stp-apex/docs/oracle-connection-playbook.md)
3. [apex-component-playbook.md](/C:/HT/stp-apex/docs/apex-component-playbook.md)

## App 101: superficie real a probar

App validada:

- app id: `101`
- app alias: `TEST101`
- parsing schema: `WKSP_STP`

Paginas actuales:

- `9999` - `Login Page`
- `1` - `Home`
- `2` - `Editable Grid`
- `0` - `Global Page`

Regla importante:

- `page 0` no es una pagina navegable por URL; es infraestructura comun y no se prueba como pagina independiente en Playwright.
- las paginas navegables que si deben probarse son `9999`, `1` y `2`.

## Credenciales y variables de entorno

Usuario de aplicacion APEX validado:

- `STP`

Hallazgo importante:

- `ADMIN` no autentica contra la app `101`; sirve para administrar la base y APEX por `ORDS SQL`, no como usuario funcional de la aplicacion.

No guardar la clave en el repo. Cargarla solo en la sesion actual antes de ejecutar pruebas.

PowerShell:

```powershell
$env:APP_URL='https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/r/stp/test101'
$env:APP_USERNAME='STP'
$env:APP_PASSWORD='***solo en la sesion actual***'
```

## Suite validada

Archivo:

- [app101-smoke.spec.js](/C:/HT/stp-apex/tests/playwright/app101-smoke.spec.js)

Cobertura actual:

- carga de `/login`
- autenticacion con `STP`
- apertura de `/home`
- apertura de `/editable-grid` desde la navegacion real de la app
- edicion y guardado de una fila del `Interactive Grid`
- reversion del cambio para no dejar datos sucios
- autocorreccion del baseline si una corrida anterior dejo `Fila 2 PW`
- deteccion de banners `ORA-` o `error has occurred`

Comando recomendado:

```powershell
npm run test:app101
```

Equivalente directo:

```powershell
npx playwright test tests/playwright/app101-smoke.spec.js --reporter=line
```

## Flujo tecnico validado para APEX

El patron que ya quedo comprobado es:

1. abrir `/login`
2. autenticar con usuario APEX
3. validar `Home`
4. abrir la pagina de negocio desde la navegacion real
5. validar el contenido funcional de la pagina

Hallazgo UI importante:

- en Universal Theme la entrada del menu lateral puede renderizarse como `treeitem`, no como `link`
- para `page 2` de la app `101`, Playwright debe buscar `Editable Grid` como `treeitem`

## Interactive Grid de la page 2

Objetivo funcional:

- region `Interactive Grid` sobre `WKSP_STP.STP_PAGE2_GRID`
- columnas reales: `ID`, `NAME`
- fila semilla usada por la prueba: `Fila 2`
- `ID` debe quedar como identidad compatible con `NULL` desde el `IG`
- validacion SQL ya comprobada: `insert ... values (null, ...)` funciona y se puede revertir con `rollback`

Secuencia validada para editar:

1. abrir `Editable Grid` desde el menu lateral
2. asegurar baseline `Fila 2`
3. pulsar `Edit`
4. seleccionar la celda del valor
5. abrir el editor del grid
6. editar el `textbox` `Name`
7. confirmar el valor con `Tab`
8. pulsar `Save`
9. esperar `Changes saved`
10. recargar la pagina y confirmar persistencia
11. revertir el valor original

Selectores utiles ya comprobados:

- entrada del menu lateral: `treeitem "Editable Grid"`
- editor de celda: `textbox "Name"`
- mensaje de commit correcto: `Changes saved`

## Cuando una prueba falle

La configuracion actual conserva:

- screenshot en fallos
- trace en fallos

Rutas de interes:

- `test-results/`
- `playwright-report/` si se genera reporte HTML manualmente

Diagnostico rapido:

1. mirar la URL final para confirmar pagina y `session`
2. revisar screenshot
3. abrir el trace si el fallo es intermitente
4. confirmar si cambio el texto visible de la app, no solo los selectores

## Regla operativa para futuras apps APEX

Si una app nueva expone login por APEX Accounts, repetir este patron:

1. definir `APP_URL`
2. usar usuario APEX valido
3. probar primero la pagina de login
4. probar luego una pagina simple
5. probar despues el componente critico
6. si el componente muta datos, revertir el cambio dentro del mismo test

Ese flujo ya quedo validado sobre la app `101` y es la base reutilizable para nuevas apps del workspace `STP`.
