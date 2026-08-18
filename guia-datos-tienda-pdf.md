# Guía: Actualización de Datos de la Tienda en Facturas PDF

Esta guía detalla el procedimiento para cambiar la información institucional de tu negocio en las facturas PDF generadas por WooCommerce, asegurando que la imagen de marca y los datos legales sean correctos.

## 1. Acceso al Panel de Configuración
La mayoría de las tiendas utilizan el plugin **WooCommerce PDF Invoices & Packing Slips**. Para acceder a los ajustes:

1. Inicia sesión en el administrador de **WordPress**.
2. Navega a **WooCommerce** $\rightarrow$ **PDF Invoices**.
3. Quédate en la pestaña **General**.

## 2. Datos Críticos a Actualizar
En la sección de **Información de la Tienda**, debes revisar y modificar los siguientes campos:

- **Nombre Comercial**: El nombre exacto que debe aparecer como emisor de la factura.
- **Logotipo**: Si has cambiado la identidad visual, sube el nuevo logo. Asegúrate de que sea un archivo PNG con fondo transparente para un acabado profesional.
- **Datos Fiscales (CUIT/VAT)**: Es fundamental que el número de CUIT o registro fiscal esté correcto para que la factura tenga validez legal.
- **Información de Contacto**: Actualiza el teléfono, correo electrónico y sitio web.

## 3. Configuración de la Plantilla (Diseño)
Si quieres cambiar dónde aparece la información o el estilo:
1. Ve a la pestaña **Documentos** $\rightarrow$ **Invoice**.
2. Aquí puedes activar o desactivar campos específicos (como mostrar u ocultar la dirección del cliente o el número de pedido).

## 4. Proceso de Verificación Final
Para evitar errores en el envío de facturas a clientes reales, realiza esta prueba:

1. Ve a **WooCommerce** $\rightarrow$ **Pedidos**.
2. Abre un pedido ya completado.
3. Haz clic en el botón **PDF Invoice** para generar el documento.
4. Descarga el PDF y verifica:
   - Que el logo no esté pixelado.
   - Que el CUIT sea el correcto.
   - Que la dirección coincida con la oficina física actual.

---
**Nota Técnica**: Si los cambios en el panel de control no se ven reflejados, es probable que tu sitio esté usando una **plantilla personalizada**. En ese caso, los datos deben editarse directamente en el archivo PHP de la plantilla ubicada en `/wp-content/uploads/woocommerce_pdf_invoices/templates/`.
