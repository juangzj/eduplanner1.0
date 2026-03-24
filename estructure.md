## prompt para continuar con el diseño
```shell
Estoy trabajando en un sistema web llamado Eduplanner usando Django + Bootstrap 5 y tengo un layout con sidebar fijo en escritorio y offcanvas en móvil.
El problema principal ya fue solucionado organizando correctamente la estructura base del proyecto.

Actualmente la estructura funciona así:

base.html es el layout principal del sistema.
Contiene el sidebar como componente global y el contenido dinámico se carga dentro de <main id="main-content">.
base_left_sidebar.html ya no contiene el sidebar nuevamente.
Solo extiende base.html y se usa únicamente para mostrar contenido dentro del bloque sidebar_content, evitando duplicaciones del sidebar.
En style.css ya está solucionado el problema del contenido debajo del sidebar.
Ahora #main-content tiene:
margin-left: 260px en pantallas grandes (desde 992px)
margin-left: 0 en pantallas pequeñas

Esto significa que:

En desktop el contenido se muestra correctamente al lado del sidebar
En móvil el contenido ocupa el 100% porque el sidebar es offcanvas

A partir de este contexto quiero que cualquier mejora o cambio que me sugieras respete esta estructura y solo modifique lo necesario sin romper el layout base
```






## estrucutre
```shell
eduplanner1.0/
├─ apps/
│  ├─ __pycache__/
│  │  └─ __init__.cpython-312.pyc
│  ├─ landing/
│  │  ├─ __pycache__/
│  │  │  ├─ __init__.cpython-312.pyc
│  │  │  ├─ admin.cpython-312.pyc
│  │  │  └─ apps.cpython-312.pyc
│  │  ├─ migrations/
│  │  │  ├─ __pycache__/
│  │  │  │  └─ __init__.cpython-312.pyc
│  │  │  └─ __init__.py
│  │  ├─ services/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  └─ landing_services.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  └─ landing_services.py
│  │  ├─ templates/
│  │  │  └─ landing/
│  │  │     └─ index.html
│  │  ├─ urls/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  └─ landing_urls.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  └─ landing_urls.py
│  │  ├─ views/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  └─ landing_views.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  └─ landing_views.py
│  │  ├─ __init__.py
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  └─ tests.py
│  ├─ users/
│  │  ├─ __pycache__/
│  │  │  ├─ __init__.cpython-312.pyc
│  │  │  ├─ admin.cpython-312.pyc
│  │  │  └─ apps.cpython-312.pyc
│  │  ├─ forms/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  ├─ login_teacher_form.cpython-312.pyc
│  │  │  │  └─ register_teacher_form.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  ├─ login_teacher_form.py
│  │  │  └─ register_teacher_form.py
│  │  ├─ migrations/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  └─ 0001_initial.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  └─ 0001_initial.py
│  │  ├─ models/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  └─ user_teacher.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  └─ user_teacher.py
│  │  ├─ services/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  ├─ auth_user_teacher_services.cpython-312.pyc
│  │  │  │  └─ user_teacher_services.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  ├─ auth_user_teacher_services.py
│  │  │  └─ user_teacher_services.py
│  │  ├─ templates/
│  │  │  └─ users/
│  │  │     ├─ login.html
│  │  │     └─ register_user_teacher.html
│  │  ├─ urls/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  ├─ auth_user_teacher_urls.cpython-312.pyc
│  │  │  │  └─ user_teacher_urls.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  ├─ auth_user_teacher_urls.py
│  │  │  └─ user_teacher_urls.py
│  │  ├─ views/
│  │  │  ├─ __pycache__/
│  │  │  │  ├─ __init__.cpython-312.pyc
│  │  │  │  ├─ auth_user_teacher_views.cpython-312.pyc
│  │  │  │  └─ user_teacher_views.cpython-312.pyc
│  │  │  ├─ __init__.py
│  │  │  ├─ auth_user_teacher_views.py
│  │  │  └─ user_teacher_views.py
│  │  ├─ __init__.py
│  │  ├─ admin.py
│  │  ├─ apps.py
│  │  ├─ login.html
│  │  └─ tests.py
│  └─ __init__.py
├─ config/
│  ├─ __pycache__/
│  │  ├─ __init__.cpython-312.pyc
│  │  ├─ urls.cpython-312.pyc
│  │  └─ wsgi.cpython-312.pyc
│  ├─ settings/
│  │  ├─ __pycache__/
│  │  │  ├─ base.cpython-312.pyc
│  │  │  └─ dev.cpython-312.pyc
│  │  ├─ base.py
│  │  ├─ dev.py
│  │  └─ prod.py
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ urls.py
│  └─ wsgi.py
├─ postgres_data/
│  └─ 18/
│     └─ docker/
├─ templates/
│  ├─ base/
│  │  ├─ base_left_sidebar.html
│  │  └─ base.html
│  ├─ components/
│  │  ├─ alerts.html
│  │  ├─ footer.html
│  │  └─ left_sidebar.html
│  ├─ pages/
│  │  └─ dashboard.html
│  └─ static/
│     └─ css/
│        └─ styles.css
├─ .env
├─ .gitignore
├─ docker-compose.yml
├─ manage.py
└─ requirements.txt
```