# Revisión: Descuento por Transferencia Bancaria Directa

Esta revisión analiza la configuración del descuento aplicado cuando un cliente elige el método de pago "Transferencia Bancaria Directa" (BACS) en WooCommerce, asegurando que se aplique al monto total del carrito.

## 1. Verificación de la Configuración Actual
Para revisar cómo se está aplicando el descuento, sigue estos pasos:

1. Ve a **WooCommerce** $\rightarrow$ **Ajustes** $\rightarrow$ **Pagos**.
2. Busca el método **Transferencia bancaria directa** y haz clic en **Gestionar**.
3. Verifica si hay alguna configuración de descuento nativa (generalmente WooCommerce no ofrece descuentos por método de pago de forma nativa; esto se hace mediante plugins como *WooCommerce Smart Coupons* o fragmentos de código personalizados).

## 2. Problema Común: Subtotal vs Total
Muchos sistemas de descuento aplican el porcentaje solo sobre el **subtotal** de los productos, ignorando el costo de envío o los impuestos. Para asegurar que el descuento se aplique al **monto total del carrito**, se requiere una intervención via código.

## 3. Solución Técnica: Aplicar Descuento al Total
Si el descuento no se está aplicando al total, implementa el siguiente código en `functions.php`:

```php
/**
 * Aplica un descuento porcentual al TOTAL del carrito 
 * solo si el método de pago seleccionado es Transferencia Bancaria.
 */
add_action( 'woocommerce_cart_calculate_fees', 'apply_bank_transfer_discount', 10, 1 );

function apply_bank_transfer_discount( $cart ) {
    if ( is_admin() && ! defined( 'DOING_AJAX' ) ) return;

    // Definir el porcentaje de descuento (ejemplo: 10%)
    $percentage = 0.10; 
    
    // Obtener el método de pago seleccionado en el checkout
    $chosen_payment_method = WC()->session->get('chosen_payment_method');

    if ( $chosen_payment_method == 'bacs' ) {
        // Calcular el descuento basado en el TOTAL (incluyendo envío e impuestos)
        $total = $cart->get_total( 'edit' );
        $discount = $total * $percentage;

        // Agregar el descuento como un cargo negativo (Fee)
        $cart->add_fee( __( 'Descuento por Transferencia Bancaria', 'woocommerce' ), -$discount );
    }
}
```

## 4. Protocolo de Verificación Final

Para confirmar que la configuración es correcta, realiza la siguiente prueba:

1. **Agregar Productos**: Añade productos al carrito que sumen un monto significativo.
2. **Configurar Envío**: Asegúrate de que el pedido tenga un costo de envío asociado.
3. **Simular Checkout**:
   - Selecciona **Transferencia Bancaria Directa**.
   - Verifica que el descuento aparezca en el resumen del pedido.
   - **Cálculo Matemático**: Suma (Productos + Envío + Impuestos) $\times$ (1 - % Descuento). El resultado debe coincidir exactamente con el total final mostrado.
4. **Cambiar Método**: Cambia el método de pago a "Tarjeta de Crédito" o "PayPal" y verifica que el descuento **desaparezca** automáticamente.
