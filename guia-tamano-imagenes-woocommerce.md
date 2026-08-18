# Guía: Cómo Cambiar el Tamaño de las Imágenes de Productos en WooCommerce

Esta guía detalla los pasos para ajustar el tamaño de las imágenes en la página de producto individual y en el catálogo de la tienda.

## 1. Acceso a la Configuración de Visualización
Para cambiar el tamaño de las imágenes sin necesidad de código, sigue estos pasos en el panel de administración de WordPress:

1. Inicia sesión en tu panel de **WordPress**.
2. Ve al menú lateral izquierdo y selecciona **WooCommerce** $\rightarrow$ **Ajustes**.
3. Haz clic en la pestaña **Productos**.
4. Busca la sección **Visualización**.

## 2. Ajuste de Dimensiones
En la sección de Visualización encontrarás las siguientes opciones:

- **Ancho de la imagen principal**: Define el tamaño de la imagen que aparece en la página del producto individual. 
  - *Recomendación*: Un valor entre 600px y 800px suele ser ideal para mantener la calidad sin afectar la carga.
- **Ancho de la miniatura**: Define el tamaño de las imágenes en la página de la tienda (catálogo) y las miniaturas debajo de la imagen principal.
  - *Recomendación*: 300px es el estándar para una rejilla equilibrada.

**Importante**: Una vez realizado el cambio, haz clic en el botón **Guardar cambios** al final de la página.

## 3. ¿Qué hacer si los cambios no se reflejan? (Regenerar Miniaturas)
WooCommerce crea versiones físicas de las imágenes en el servidor basándose en estos ajustes. Si cambias los números pero las imágenes siguen viéndose igual o se ven borrosas, es necesario "regenerar" las miniaturas.

1. Instala el plugin gratuito **Regenerate Thumbnails**.
2. Ve a **Herramientas** $\rightarrow$ **Regenerate Thumbnails**.
3. Haz clic en el botón **Regenerar miniaturas**. 
4. El plugin procesará todas las imágenes de la biblioteca para ajustarlas a los nuevos tamaños configurados.

## 4. Tips Adicionales para Imágenes Profesionales
- **Relación de Aspecto**: Intenta que todas tus imágenes tengan la misma proporción (ej. 1:1 cuadrado) para que el catálogo se vea alineado.
- **Optimización**: Antes de subir imágenes, pásalas por herramientas como *TinyPNG* para reducir el peso sin perder calidad.
- **Fondo**: Para tiendas de decoración (como Decotay), el fondo blanco limpio es el estándar que mejor convierte.
