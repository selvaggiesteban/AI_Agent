<?php
/**
 * Snippet: Mostrar cantidad de productos en el carrito
 * Carrito: debajo de "TOTALES DEL CARRITO" | Checkout: debajo de "TU PEDIDO"
 */

// Carrito
add_action('woocommerce_before_cart_totals', 'mostrar_cantidad_carrito');

function mostrar_cantidad_carrito() {
    $total = WC()->cart->get_cart_contents_count();
    $texto = $total == 1 ? 'producto' : 'productos';
    echo '<p style="margin: -10px 0 15px 0; font-size: 14px; color: #555;"><strong>' . $total . ' ' . $texto . ' en tu carrito</strong></p>';
}

// Checkout
add_action('woocommerce_review_order_before_cart_contents', 'mostrar_cantidad_checkout');

function mostrar_cantidad_checkout() {
    static $ya_mostrado = false;
    if ($ya_mostrado) return;
    $ya_mostrado = true;

    $total = WC()->cart->get_cart_contents_count();
    $texto = $total == 1 ? 'producto' : 'productos';
    echo '<tr><td colspan="2" style="padding: 10px 0;"><strong>' . $total . ' ' . $texto . ' en tu carrito</strong></td></tr>';
}