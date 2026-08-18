<?php
/**
 * Snippet: 10% de descuento en compras >= $100.000
 */

add_action('woocommerce_cart_calculate_fees', 'descuento_10_porcentaje');

function descuento_10_porcentaje($cart) {
    if (is_admin() && !defined('DOING_AJAX')) return;

    $total = $cart->get_subtotal();

    if ($total >= 100000) {
        $descuento = $total * 0.10;
        $cart->add_fee('Descuento 10%', -$descuento);
    }
}