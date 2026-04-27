#!/bin/bash
# Script para verificar que los archivos estáticos se recopilan correctamente

echo "=== Limpiando staticfiles previousos ==="
rm -rf staticfiles/

echo "=== Recopilando archivos estáticos ==="
python manage.py collectstatic --noinput --clear

echo "=== Verificando que se recopilaron ==="
if [ -d "staticfiles/admin/css" ]; then
    echo "✓ Admin CSS encontrado"
    ls -la staticfiles/admin/css/ | head -5
else
    echo "✗ ERROR: Admin CSS no encontrado"
    exit 1
fi

if [ -d "staticfiles/css" ]; then
    echo "✓ CSS del proyecto encontrado"
    ls -la staticfiles/css/ | head -5
else
    echo "✗ ERROR: CSS del proyecto no encontrado"
    exit 1
fi

echo ""
echo "=== Resumen ==="
echo "Total de archivos: $(find staticfiles -type f | wc -l)"
echo "✓ Colección completada exitosamente"
