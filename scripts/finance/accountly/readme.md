# 📊 Accountly

> **La inteligencia financiera a tu alcance.**  
> Transforma datos contables crudos en dashboards visuales, interactivos y accionables de forma automática.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build: Professional](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)]()

---

## 🚀 ¿Qué es Accountly?

**Accountly** es una solución de visualización financiera diseñada para pequeños negocios, contadores y analistas que necesitan rapidez sin sacrificar profundidad. Olvídate de procesar hojas de cálculo manualmente; Accountly se encarga de la extracción, el procesamiento y la generación de métricas clave en una interfaz moderna y fluida.

### ✨ Características Principales

*   **Extracción Inteligente:** Módulos optimizados para leer y limpiar datos financieros complejos de forma automatizada.
*   **Dashboards Interactivos:** Gráficos dinámicos (gracias a Chart.js) para analizar tendencias, ingresos y gastos de un vistazo.
*   **Arquitectura Modular:** Separación clara entre extracción (`extractors.py`), lógica de negocio (`processors.py`) y representación visual.
*   **Privacidad por Diseño (Local-First):** Tus datos financieros nunca salen de tu máquina. El procesamiento es 100% local.
*   **Interfaz Premium:** Basada en Bootstrap con un diseño limpio, profesional y totalmente responsivo.

---

## 🛠️ Stack Tecnológico

*   **Backend:** Python (Procesamiento de datos robusto)
*   **Frontend:** HTML5, CSS3 (Bootstrap), JavaScript (Chart.js)
*   **Arquitectura:** Motor de procesamiento modular basado en el patrón Generador-Procesador.

---

## 📦 Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/accountly.git
cd accountly
```

### 2. Instalar dependencias
Se recomienda el uso de un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
python main.py
```
Luego, abre tu navegador en `http://localhost:5000` (o el puerto configurado).

---

## 📂 Estructura del Proyecto

```text
├── src/
│   ├── extractors.py   # Módulos de lectura de datos.
│   ├── processors.py   # Lógica contable y limpieza.
│   └── generator.py    # Transformación de datos para el dashboard.
├── templates/          # Vistas HTML (Jinja2).
├── assets/             # Estilos, scripts y librerías (Bootstrap, Chart.js).
└── data/               # (Opcional) Carpeta para archivos de entrada.
```

---

## 🛣️ Roadmap / Próximas Mejoras

- [ ] Soporte para exportación de reportes en PDF.
- [ ] Integración directa con APIs bancarias.
- [ ] Selector de Tema (Modo Oscuro / Modo Claro).
- [ ] Sistema de autenticación de usuarios.

---

## 🤝 Contribuciones

¡Las contribuciones son lo que hacen a la comunidad de código abierto un lugar increíble para aprender, inspirar y crear! Cualquier contribución que hagas será **muy apreciada**.

1. Haz un Fork del proyecto.
2. Crea tu Rama de Función (`git checkout -b feature/AmazingFeature`).
3. Haz un Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4. Haz un Push a la Rama (`git push origin feature/AmazingFeature`).
5. Abre un Pull Request.

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.

---

**Desarrollado con ❤️ por Esteban Selvaggi**  
*Impulsando la claridad financiera, un dato a la vez.*
