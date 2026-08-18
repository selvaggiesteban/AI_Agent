<?php
/**
 * Snippet: Traducir "Población" por "Partido/Localidad"
 */

add_filter('gettext', 'traducir_poblacion', 20, 3);

function traducir_poblacion($translation, $text, $domain) {
    if ($domain === 'woocommerce' && $text === 'Población') {
        return 'Partido/Localidad';
    }
    return $translation;
}