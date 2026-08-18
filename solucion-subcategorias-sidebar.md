# Solución: Mostrar Subcategorías en la Barra Lateral de la Tienda

Para implementar la funcionalidad de desplegar subcategorías al hacer clic en una categoría padre en la barra lateral de la tienda, utilizaremos una combinación de CSS para el estado inicial y JavaScript (jQuery) para manejar la interacción.

## 1. Código CSS (Estilos)
Agrega este código en **Apariencia** $\rightarrow$ **Personalizar** $\rightarrow$ **CSS Adicional**. Este código oculta las subcategorías por defecto y define la animación de apertura.

```css
/* Ocultar subcategorías por defecto */
.widget_product_category ul.product-categories .children {
    display: none;
    margin-left: 15px;
    transition: all 0.3s ease;
}

/* Clase para mostrar subcategorías cuando el padre es activo */
.widget_product_category ul.product-categories .cat-item.active-category > .children {
    display: block;
}

/* Estilo para el indicador de "flecha" en categorías con hijos */
.widget_product_category ul.product-categories .cat-item.cat-parent > a:after {
    content: ' ▾';
    font-size: 0.8em;
    color: #888;
}

.widget_product_category ul.product-categories .cat-item.active-category.cat-parent > a:after {
    content: ' ▴';
}
```

## 2. Código JavaScript/jQuery (Interacción)
Este script detecta el clic en las categorías que tienen hijos y alterna la visibilidad de los mismos. Debes agregarlo en tu archivo `.js` del tema o mediante un plugin como **Code Snippets** (seleccionando la opción "Insertar en el footer").

```javascript
jQuery(document).ready(function($) {
    // Detectar clic en categorías que son padres (.cat-parent)
    $('.widget_product_category ul.product-categories .cat-item.cat-parent > a').on('click', function(e) {
        e.preventDefault(); // Evitar que navegue inmediatamente si solo queremos desplegar

        var $parentLi = $(this).parent('.cat-item');
        var $children = $parentLi.find('> .children');

        // Alternar la clase 'active-category'
        $parentLi.toggleClass('active-category');

        // Desplegar/Ocultar con animación simple
        $children.slideToggle(300);
        
        // Opcional: Cerrar otros menús abiertos al abrir uno nuevo (acordeón)
        $('.widget_product_category ul.product-categories .cat-item').not($parentLi).removeClass('active-category').find('> .children').slideUp(300);
    });
});
```

## 3. Guía de Instalación Paso a Paso

1. **CSS**: Ve a `Personalizar` $\rightarrow$ `CSS Adicional` $\rightarrow$ Pega el código CSS $\rightarrow$ `Publicar`.
2. **JS**: 
   - Si usas el plugin **Code Snippets**: Crea un nuevo snippet $\rightarrow$ Pega el código JS envuelto en etiquetas `<script></script>` $\rightarrow$ Selecciona "Solo en el frente del sitio" $\rightarrow$ Guardar.
   - Si tienes acceso a archivos: Pégalo al final de tu archivo `main.js` o `custom.js`.
3. **Verificación**: 
   - Abre la tienda en modo incógnito.
   - Dirígete a la barra lateral.
   - Haz clic en una categoría que sepas que tiene subcategorías.
   - Verifica que el menú se despliegue suavemente.

## Consideraciones Técnicas
- **Especificidad**: He utilizado selectores estándar de WooCommerce (`.widget_product_category`). Si tu tema usa clases personalizadas, es posible que debamos ajustar `.cat-item` por la clase específica del tema.
- **Experiencia de Usuario (UX)**: Se ha implementado un efecto de "acordeón" para evitar que la barra lateral se vuelva demasiado larga y confusa.
