# Guía: Cómo Cambiar la Dirección y Calle en la Factura PDF (WooCommerce)

Esta guía explica cómo modificar la dirección física que aparece en las facturas generadas en formato PDF. Para este proceso, asumimos que utilizas el plugin estándar **WooCommerce PDF Invoices & Packing Slips**.

## 1. Acceso a la Configuración de Facturas
Para cambiar la dirección de tu negocio (la dirección del emisor), sigue estos pasos:

1. Ingresa al panel de administración de **WordPress**.
2. En el menú lateral, ve a **WooCommerce** $\rightarrow$ **PDF Invoices**.
3. Asegúrate de estar en la pestaña **General**.

## 2. Modificación de la Dirección de la Tienda
Dentro de la pestaña General, busca la sección de **Información de la Tienda**. Aquí podrás editar:
- **Nombre de la tienda**
- **Dirección** (Calle, número, piso, etc.)
- **Ciudad, Provincia y Código Postal**
- **País**

Simplemente escribe la dirección correcta en los campos correspondientes y haz clic en el botón **Guardar cambios** al final de la página.

## 3. Cambio de Dirección del Cliente (Casos Especiales)
Si necesitas cambiar la dirección de un cliente específico en una factura ya emitida:
1. Ve a **WooCommerce** $\rightarrow$ **Pedidos**.
2. Haz clic en el pedido correspondiente.
3. En la sección **Dirección de facturación**, edita la calle y dirección.
4. Haz clic en **Actualizar**.
5. Al generar el PDF nuevamente, la factura tomará la dirección actualizada del pedido.

## 4. Verificación de los Cambios
Para confirmar que la dirección se ha actualizado correctamente:
1. Entra en cualquier pedido existente.
2. Haz clic en el botón **PDF Invoice** (Factura PDF) ubicado en la parte superior derecha o en la sección de acciones del pedido.
3. Descarga el archivo y verifica que la calle y dirección sean las correctas.

---
**Tip Profesional**: Si utilizas una plantilla personalizada (Custom Template), es posible que la dirección esté escrita manualmente en el código del archivo `.php` de la plantilla. En ese caso, deberás editar el archivo vía FTP o Administrador de Archivos en la ruta: `wp-content/uploads/woocommerce_pdf_invoices/templates/`.
