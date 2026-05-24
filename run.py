import os
from app.main import create_app, db

app = create_app(os.getenv("MENU_FLASK_ENV", "development"))

def listar_apis():
    print("\n" + "="*80)
    print("ENDPOINTS DISPONIBLES")
    print("="*80)
    # Obtener todas las rutas
    for rule in app.url_map.iter_rules():
        # Filtrar rutas estáticas y de debug
        if rule.endpoint != 'static':
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"{rule}  [{methods}]")
    print("="*80 + "\n")

###### Punto de entrada ###########

if __name__ == "__main__":
    print("# AQUI ENTRA")
    listar_apis()
    app.run(host="0.0.0.0", port=5000, debug=True)
