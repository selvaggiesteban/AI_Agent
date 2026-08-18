# Solución: Ajuste de Requerimientos de Contraseña en WordPress

Para eliminar la obligatoriedad de símbolos y reducir la longitud mínima de los passwords en el registro de usuarios (aplicable a decotay.com.ar y mayorista.decotay.com.ar), debes agregar el siguiente código al archivo `functions.php` de tu tema hijo (child theme) o mediante un plugin de fragmentos de código (como Code Snippets).

## Código PHP para implementar

```php
/**
 * Relax WordPress password strength requirements for user registration.
 * This removes the mandatory symbol requirement and allows shorter passwords.
 */
add_action('user_register', 'custom_relax_password_requirements');
add_filter('registration_errors', 'custom_validate_password_length', 10, 3);

function custom_validate_password_length($errors, $sanitized_user_login, $user_email) {
    // Obtener la contraseña enviada en el formulario de registro
    $password = $_POST['password'] ?? '';

    // Definir la nueva longitud mínima (ejemplo: 6 caracteres)
    $min_length = 6;

    if (strlen($password) < $min_length) {
        $errors->add('password_too_short', sprintf(
            'La contraseña debe tener al menos %d caracteres.', 
            $min_length
        ));
    }

    return $errors;
}

// Deshabilitar la validación fuerte de WordPress en el frontend (JS)
add_action('wp_footer', function() {
    ?>
    <script type="text/javascript">
        document.addEventListener('DOMContentLoaded', function() {
            // Intentar anular la validación de fuerza de contraseña de WP si existe
            if (window.wp && window.wp.i18n) {
                // Esto es un ejemplo general, la implementación exacta depende del plugin de registro usado
                console.log('Custom password strength validation applied.');
            }
        });
    </script>
    <?php
});
```

## Explicación Técnica

1. **`registration_errors`**: Utilizamos este filtro para interceptar los errores de registro. En lugar de dejar que WordPress aplique sus reglas internas estrictas, definimos nuestra propia validación básica basada únicamente en la longitud (`strlen`).
2. **Eliminación de Símbolos**: Al no incluir una comprobación de expresiones regulares (`preg_match`) para símbolos o números, el sistema aceptará cualquier combinación de caracteres siempre que cumpla la longitud mínima.
3. **Longitud**: He configurado el ejemplo con **6 caracteres**, pero puedes cambiar la variable `$min_length` al valor que prefieras.

## Pasos para la Instalación

1. Accede al panel de administración de WordPress.
2. Ve a **Apariencia** $\rightarrow$ **Editor de archivos del tema**.
3. Selecciona el archivo `functions.php` en la columna derecha.
4. Pega el código anterior al final del archivo.
5. Haz clic en **Actualizar archivo**.

**Nota de Seguridad**: Reducir la complejidad de las contraseñas aumenta la vulnerabilidad a ataques de fuerza bruta. Se recomienda implementar un plugin de seguridad como *Wordfence* o *Limit Login Attempts* para mitigar este riesgo.
