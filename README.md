# 🛒 Tienda Web Full-Stack con Flask y Oracle Database

Aplicación web de comercio electrónico desarrollada como práctica de bases de datos y desarrollo web. Permite la visualización de un catálogo de productos, procesamiento de compras transaccionales con control de stock, y un panel de administración (Dashboard) con métricas en tiempo real.

---

## 🚀 Tecnologías Utilizadas

* **Backend:** Python 3.13, Flask, `oracledb` (Thin Mode)
* **Frontend:** HTML5, Bootstrap 5, Jinja2 Templates
* **Base de Datos:** Oracle Database (Pluggable Database: `FREEPDB1`)

---

## 📁 Estructura del Proyecto

```text
mi-tienda-oracle/
│
├── templates/
│   ├── base.html
│   ├── tienda.html
│   └── dashboard.html
│
├── bdd_tienda.py          # Archivo principal de la aplicación Flask
├── requirements.txt       # Dependencias de Python
└── README.md              # Documentación del proyecto
