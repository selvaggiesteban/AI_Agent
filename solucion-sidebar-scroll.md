# Solución: Scroll Vertical para la Barra Lateral de la Tienda

Para implementar un scroll vertical independiente en la barra lateral (sidebar) de la tienda en `decotay.com.ar` y `mayorista.decotay.com.ar`, debes agregar el siguiente código CSS al personalizador de WordPress o al archivo `style.css` del tema.

## Código CSS a Implementar

```css
/* 
 * Implementación de scroll vertical para el sidebar de la tienda.
 * Asegura que el menú de categorías sea accesible sin desplazar toda la página.
 */

.woocommerce-sidebar, 
.sidebar-shop, 
#secondary {
    position: sticky;
    top: 20px; /* Ajustar según la altura del header sticky si existe */
    max-height: calc(100vh - 40px); /* Altura total menos el margen superior e inferior */
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 10px; /* Espacio para el scrollbar */
}

/* Personalización estética del scrollbar para un look profesional */
.woocommerce-sidebar::-webkit-scrollbar,
.sidebar-shop::-webkit-scrollbar,
#secondary::-webkit-scrollbar {
    width: 6px;
}

.woocommerce-sidebar::-webkit-scrollbar-track,
.sidebar-shop::-webkit-scrollbar-track,
#secondary::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.woocommerce-sidebar::-webkit-scrollbar-thumb,
.sidebar-shop::-webkit-scrollbar-thumb,
#secondary::-webkit-scrollbar-thumb {
    background: #ccc;
    border-radius: 10px;
}

.woocommerce-sidebar::-webkit-scrollbar-thumb:hover,
.sidebar-shop::-webkit-scrollbar-thumb:hover,
#secondary::-webkit-scrollbar-thumb:hover {
    background: #999;
}

/* Ajuste para móviles: Deshabilitar sticky y permitir scroll normal */
@media (max-width: 768px) {
    .woocommerce-sidebar, 
    .sidebar-shop, 
    #secondary {
        position: static;
        max-height: none;
        overflow-y: visible;
    }
}
```

## Explicación Técnica

1. **`position: sticky`**: Mantiene la barra lateral visible mientras el usuario hace scroll en los productos, mejorando la navegación.
2. **`max-height: calc(100vh - 40px)`**: Limita la altura de la barra al tamaño de la ventana del navegador (Viewport Height), evitando que el sidebar se extienda infinitamente hacia abajo.
3. **`overflow-y: auto`**: Activa la barra de desplazamiento vertical solo cuando el contenido excede la altura máxima definida.
4. **Custom Scrollbar**: Se añaden pseudo-elementos `::-webkit-scrollbar` para que la barra de desplazamiento sea delgada y minimalista, acorde a la estética de la tienda.

## Pasos para la Instalación

1. Ve al panel de **WordPress**.
2. Navega a **Apariencia** $\rightarrow$ **Personalizar**.
3. Haz clic en la sección **CSS Adicional**.
4. Pega el código anterior y haz clic en **Publicar**.
5. Verifica el resultado abriendo la tienda en una ventana de incógnito.
