# Guía: Configuración de Método de Envío OCA y Pruebas de Etiquetado

Esta guía describe la configuración del módulo de envío OCA en WooCommerce para realizar compras de prueba, validar la integración y aprender a imprimir las etiquetas de envío.

## 1. Configuración Inicial del Módulo OCA
Para comenzar, debes conectar tu cuenta de OCA con WooCommerce:

1. Ve a **WooCommerce** $\rightarrow$ **Ajustes** $\rightarrow$ **Envío**.
2. Selecciona **Zonas de envío** y entra en la zona donde quieras aplicar OCA (ej. "Argentina").
3. Haz clic en **Añadir método de envío** y selecciona **OCA**.
4. Entra en la configuración del método OCA e ingresa tus credenciales:
   - **Usuario de API**
   - **Token / Password de API**
   - **Número de Cuenta OCA**

## 2. Configuración de Compras de Prueba (Modo Test)
Para validar que todo funciona sin generar cargos reales ni envíos oficiales, sigue estos pasos:

### Opción A: Activar el Modo Sandbox (si el plugin lo permite)
- En los ajustes del método OCA, busca el check de **"Modo Test"** o **"Sandbox"**. Al activarlo, las solicitudes irán a un servidor de pruebas de OCA.

### Opción B: Creación de una Zona de Envío de Pruebas
Si el plugin no tiene modo test explícito, haz lo siguiente:
1. Crea una nueva **Zona de Envío** llamada "TEST OCA".
2. Asigna un código postal ficticio o una ciudad específica para esta zona.
3. Configura el método OCA solo en esta zona.
4. Realiza un pedido usando una dirección que coincida con esa zona para activar el método.

## 3. Proceso de Impresión de Etiquetas
Una vez que el pedido ha sido realizado y pagado:

1. Ve a **WooCommerce** $\rightarrow$ **Pedidos**.
2. Selecciona el pedido de prueba.
3. Busca la sección de **Envío OCA** dentro del pedido.
4. Haz clic en el botón **Generar Etiqueta** (o "Request Label").
5. El sistema se comunicará con OCA y te devolverá un archivo PDF con la etiqueta.
6. Haz clic en **Imprimir** y asegúrate de usar el tamaño de papel correcto (generalmente etiquetas térmicas de 10x15cm).

## 4. Solución de Problemas Comunes
- **Error de API**: Verifica que las credenciales sean correctas y que la cuenta de OCA esté activa.
- **No aparece el método en el Checkout**: Verifica que el peso y las dimensiones del producto estén cargados, ya que OCA requiere estos datos para calcular el costo.
- **Etiqueta no generada**: Confirma que el pedido esté en estado "Procesando" o "Completado", ya que algunos plugins no permiten etiquetas en pedidos "Pendientes".
