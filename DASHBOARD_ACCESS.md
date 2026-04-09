# 📊 Acceso al Panel de Estadísticas

## Cómo acceder al Dashboard

Después de que el sistema esté en marcha, puedes acceder al panel de estadísticas de dos formas:

### Opción 1: URL Directa
Ingresa a tu navegador y dirígete a:
```
http://localhost:8000/admin/dashboard/
```

### Opción 2: Desde el Admin de Django
1. Ve a `http://localhost:8000/admin/`
2. Inicia sesión con tu cuenta de administrador
3. En la parte superior del admin, verás un enlace directo al Dashboard

---

## Requisitos de Acceso

- **Solo para administradores**: Solo usuarios con permisos de staff (`is_staff=True`) pueden acceder.
- **Autenticación requerida**: Debes estar autenticado en el sistema.

---

## ¿Qué información puedes ver en el dashboard?

El panel centraliza estadísticas de todas las apps:

### 👥 **Usuarios Docentes**
- Total de docentes registrados
- Docentes activos/inactivos
- Personal con acceso administrativo

### 🔬 **Laboratorio de Prompts**
- Total de prompts creados
- Prompts generados por IA vs. por usuarios
- Puntuación promedio de prompts
- Top 10 docentes por actividad
- Actividad en los últimos 7 días

### 📚 **Niveles de Desempeño**
- Total de templates de niveles
- Niveles generados
- Rúbricas de evaluación
- Desglose por área académica
- Desglose por grado

### ✏️ **Planeaciones de Clase**
- Total de planeaciones creadas
- Clases generadas por IA
- Actividad reciente (últimos 7 días)
- Top docentes por planeaciones

### 💬 **Interacciones**
- Total de likes en clases
- Total de comentarios
- Comentarios activos
- Clases más likeadas
- Clases más comentadas

---

## Estructura del Código

El sistema de estadísticas está diseñado para ser **limpio y escalable**:

### Modularidad
Cada app tiene su propio archivo `stats.py`:
- `apps/levels/stats.py` - Estadísticas de planeaciones y clases
- `apps/prompt_lab/stats.py` - Estadísticas de prompts
- `apps/users/stats.py` - Estadísticas de usuarios
- `apps/interactions/stats.py` - Estadísticas de likes y comentarios

### Centralización
- `config/admin_views.py` - Vista centralizada del dashboard
- `config/urls.py` - Ruta del dashboard (`/admin/dashboard/`)
- `templates/admin/dashboard.html` - Plantilla HTML limpia y profesional

### Escalabilidad
Para agregar nuevas estadísticas:
1. Agrega funciones en el archivo `stats.py` de la app correspondiente
2. Llama a esas funciones en `config/admin_views.py`
3. Añade los datos al contexto y renderiza en la plantilla

---

## Ejemplo: Agregar una Nueva Estadística

Si quieres agregar una nueva métrica, por ejemplo, "Prompts por mes en prompt_lab":

1. **En `apps/prompt_lab/stats.py`**, agrega una función:
```python
def get_prompts_by_month():
    """Retorna prompts agrupados por mes"""
    by_month = (
        Prompt.objects
        .filter(deleted_at__isnull=True)
        .extra(select={'month': 'DATE_TRUNC(\'month\', created_at)'})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')
    )
    return list(by_month)
```

2. **En `config/admin_views.py`**, importa y agrega al contexto:
```python
from apps.prompt_lab.stats import get_prompts_by_month

context = {
    ...
    'prompts_monthly': get_prompts_by_month(),
}
```

3. **En `templates/admin/dashboard.html`**, agrega la visualización en la sección de prompts.

---

## Sistema de Seguridad

El dashboard está protegido por:
- Decorador `@staff_member_required` - Solo permite acceso a administradores
- Decorador `@require_http_methods(["GET"])` - Solo permite requests GET
- Autenticación de Django - Requerida antes de acceder

---

## Performance y Optimización

- Las consultas están optimizadas con `select_related` y `values()` para agregaciones
- Se filtran registros no eliminados (`deleted_at__isnull=True`)
- Los datos se calculan dinámicamente cada vez que se accede (no hay caching, por ahora)

Para optimizar aún más, puedes:
- Agregar caché con Redis
- Generar reportes offline
- Usar `django-admin-tools` para widgets específicos

---

## Soporte y Mantenimiento

El dashboard se actualiza automáticamente cada vez que accedes. No requiere configuración adicional.

Si tienes dudas o quieres agregar más estadísticas, consulta con el equipo de desarrollo.
