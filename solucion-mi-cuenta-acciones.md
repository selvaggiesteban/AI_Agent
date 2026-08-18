# Solución: Acciones Avanzadas en Página "Mi Cuenta" (Decotay)

Para implementar las acciones de **Ver**, **Comparar** y **Repetir Pedido** en la sección de pedidos de la página "Mi Cuenta" para `decotay.com.ar` y `mayorista.decotay.com.ar`, utilizaremos el hook de WooCommerce `woocommerce_my_account_my_orders_actions`.

## 1. Implementación Técnica (Código PHP)

Copia y pega el siguiente código en el archivo `functions.php` de tu tema hijo o mediante un plugin de fragmentos de código (Code Snippets).

```php
/**
 * Agregar acciones personalizadas a la tabla de pedidos en Mi Cuenta.
 */
add_filter( 'woocommerce_my_account_my_orders_actions', 'custom_my_account_order_actions', 10, 2 );

function custom_my_account_order_actions( $actions, $order ) {
    // 1. Acción "Ver" (Redirige al detalle del pedido)
    // WooCommerce ya trae 'view', pero podemos personalizar el label
    if ( isset( $actions['view'] ) ) {
        $actions['view'] = array(
            'url'  => $actions['view']['url'],
            'name' => __( 'Ver Detalle', 'woocommerce' ),
        );
    }

    // 2. Acción "Comparar"
    // Redirige a una página de comparación pasando el ID del pedido
    $actions['compare'] = array(
        'url'  => add_query_arg( 'compare_order', $order->get_id(), wc_get_page_permalink( 'my-account' ) ),
        'name' => __( 'Comparar', 'woocommerce' ),
    );

    // 3. Acción "Repetir Pedido"
    // Llama a una función personalizada que añade los productos al carrito
    $actions['repeat'] = array(
        'url'  => wp_nonce_url( add_query_arg( 'repeat_order', $order->get_id(), home_url( '/' ) ), 'repeat_order_nonce' ),
        'name' => __( 'Repetir Pedido', 'woocommerce' ),
    );

    return $actions;
}

/**
 * Lógica para la acción "Repetir Pedido".
 * Captura la petición y añade los productos del pedido antiguo al carrito actual.
 */
add_action( 'template_redirect', 'handle_repeat_order_action' );

function handle_repeat_order_action() {
    if ( ! isset( $_GET['repeat_order'] ) || ! wp_verify_nonce( $_GET['_wpnonce'], 'repeat_order_nonce' ) ) {
        return;
    }

    $order_id = absint( $_GET['repeat_order'] );
    $order = wc_get_order( $order_id );

    if ( ! $order ) {
        wc_add_notice( 'No se pudo encontrar el pedido.', 'error' );
        wp_redirect( wc_get_page_permalink( 'my-account' ) );
        exit;
    }

    // Limpiar carrito actual (Opcional: comentar la siguiente línea si prefieres sumar al carrito existente)
    WC()->cart->empty_cart();

    // Añadir cada producto del pedido al carrito
    foreach ( $order->get_items() as $item_id => $item ) {
        $product_id = $item->get_product_id();
        $quantity = $item->get_quantity();
        $variation_id = $item->get_variation_id();

        if ( $product_id ) {
            WC()->cart->add_to_cart( $product_id, $quantity, $variation_id );
        }
    }

    wc_add_notice( 'Los productos del pedido anterior han sido añadidos al carrito.', 'success' );
    wp_redirect( wc_get_cart_url() );
    exit;
}
```

## 2. Explicación de las Funcionalidades

### Acción: Ver Detalle
Se mantiene la funcionalidad nativa de WooCommerce pero se renombra la etiqueta para que sea más clara para el usuario final.

### Acción: Comparar
Crea un enlace que envía el ID del pedido a la página de mi cuenta con un parámetro `compare_order`. 
*Nota*: Para que esto funcione visualmente, se requiere una página de destino o un script que procese ese parámetro y muestre la comparativa de productos.

### Acción: Repetir Pedido
Esta es la función más potente. Utiliza un `nonce` de seguridad para evitar ataques CSRF. Cuando el usuario hace clic:
1. El sistema identifica el pedido original.
2. Recorre todos los productos y variaciones.
3. Los añade automáticamente al carrito actual.
4. Redirige al usuario al Carrito para finalizar la compra.

## 3. Guía de Implementación y Pruebas

1. **Instalación**: Pega el código en `functions.php`.
2. **Prueba de "Repetir"**: 
   - Ve a la cuenta de un cliente con pedidos previos.
   - Haz clic en "Repetir Pedido".
   - Verifica que el carrito ahora contenga los mismos productos que el pedido seleccionado.
3. **Prueba de "Ver"**: Verifica que el enlace lleve correctamente a la vista detallada del pedido.
