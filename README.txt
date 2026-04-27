API PUBLICADOR DE KITS MERCADOLIBRE

DESCRIPCIÓN
Esta aplicación es una API desarrollada con FastAPI y Python para generar y publicar automáticamente kits de repuestos en MercadoLibre.

La lógica principal consiste en recibir una lista de repuestos, generar combinaciones de productos desde tamaño N hasta combinaciones de 2 productos, calcular el precio final del kit, buscar imágenes desde una biblioteca local, subirlas a MercadoLibre y crear la publicación directamente mediante la API.

--------------------------------------------------

ESTRUCTURA DE CARPETAS

app/
  main.py
    Archivo principal de FastAPI. Inicializa la aplicación y registra las rutas.

  core/
    config.py
      Lee las variables de entorno desde el archivo .env.
      Aquí se cargan datos como MELI_APP_ID, MELI_CLIENT_SECRET, ACCESS_TOKEN, categoría, stock por defecto y ruta de imágenes.

  api/
    routes/
      kits.py
        Contiene los endpoints relacionados con la generación y publicación de kits.

      mercadolibre.py
        Contiene endpoints auxiliares para probar conexión o manejar autenticación con MercadoLibre.

  schemas/
    producto_schema.py
      Define los datos de entrada de cada repuesto.

    kit_schema.py
      Define los datos de entrada para generar kits y las respuestas de la API.

    meli_schema.py
      Define la estructura del payload que se enviará a MercadoLibre.

  domain/
    models/
      repuesto.py
        Modelo interno de un repuesto.

      kit.py
        Modelo interno de un kit generado.

    services/
      combinador_kits.py
        Genera combinaciones de repuestos.
        Si el usuario ingresa N productos, genera kits de N, N-1, N-2 hasta llegar a 2 productos.

      pricing_service.py
        Calcula el precio final del kit.
        Si la suma está entre 16000 y 19980, el precio final queda en 19999.
        Si el precio final es mayor o igual a 19999, la publicación será premium.

      image_service.py
        Busca imágenes en la biblioteca local.
        Las imágenes deben tener formato:
        nombre_repuesto_1.jpg
        nombre_repuesto_2.jpg

      description_service.py
        Genera el título y la descripción del kit.

      attributes_service.py
        Genera los atributos requeridos o recomendados para MercadoLibre.

  application/
    use_cases/
      preview_kits.py
        Genera los kits sin publicarlos.
        Sirve para revisar títulos, precios, combinaciones e imágenes.

      crear_kits_publicaciones.py
        Ejecuta el flujo completo:
        genera kits, busca imágenes, sube imágenes y publica en MercadoLibre.

  infrastructure/
    mercadolibre/
      auth_client.py
        Maneja tokens de MercadoLibre.

      picture_client.py
        Sube imágenes a MercadoLibre.

      item_client.py
        Crea publicaciones en MercadoLibre usando POST /items.

    filesystem/
      image_repository.py
        Lee la carpeta local de imágenes.

  utils/
    slug.py
      Convierte nombres de repuestos a formato compatible con nombres de archivos.

    validators.py
      Funciones auxiliares de validación.

--------------------------------------------------

VARIABLES DE ENTORNO

El archivo .env debe contener:

MELI_APP_ID=tu_app_id
MELI_CLIENT_SECRET=tu_client_secret
MELI_ACCESS_TOKEN=tu_access_token
MELI_REFRESH_TOKEN=tu_refresh_token

MELI_SITE_ID=MLC
MELI_CATEGORY_ID=MLC455614

IMAGE_LIBRARY_PATH=./imagenes
DEFAULT_STOCK=100
DEFAULT_BRAND=Genérica

--------------------------------------------------

FORMATO DE IMÁGENES

Las imágenes se ingresan desde una carpeta local, por ejemplo:

imagenes/
  carburador_1.jpg
  carburador_2.jpg
  brida_admision_1.jpg
  brida_admision_2.jpg
  bujia_1.jpg

Cada repuesto puede tener más de una imagen.

El número final no representa la posición del repuesto en el kit, sino la cantidad de imágenes disponibles para ese mismo repuesto.

Ejemplo:
carburador_1.jpg
carburador_2.jpg
carburador_3.jpg

--------------------------------------------------

LÓGICA DE COMBINACIONES

Si el usuario ingresa 4 repuestos:

Carburador
Brida admisión
Bujía
Filtro de aire

La aplicación genera combinaciones de:

4 productos
3 productos
2 productos

No genera kits de 1 producto.

--------------------------------------------------

LÓGICA DE PRECIO

La aplicación suma los precios unitarios de los repuestos del kit.

Regla especial:

Si la suma está entre 16000 y 19980, el precio final será 19999.

Ejemplos:

Suma: 15000
Precio final: 15000

Suma: 17000
Precio final: 19999

Suma: 25000
Precio final: 25000

--------------------------------------------------

TIPO DE PUBLICACIÓN

Si el precio final es mayor o igual a 19999:

listing_type_id = gold_pro

Si el precio final es menor a 19999:

listing_type_id = gold_special

--------------------------------------------------

DATOS FIJOS DE MERCADOLIBRE

Categoría:
MLC455614

Stock:
100

Condición:
Nuevo

Buying mode:
buy_it_now

Moneda:
CLP

--------------------------------------------------

ATRIBUTOS MERCADOLIBRE

Para la categoría MLC455614 se usan los siguientes atributos:

BRAND
Marca del producto.
Por defecto: Genérica

MODEL
Modelo o compatibilidad principal.
Ejemplo: Desbrozadora 43cc 52cc

PIECES_NUMBER
Cantidad de piezas incluidas en el kit.

PIECES_INCLUDED
Listado de repuestos incluidos en el kit.

IS_KIT
Indica que la publicación corresponde a un kit.

--------------------------------------------------

FLUJO DE LA APLICACIÓN

1. La API recibe una lista de repuestos.
2. Valida los datos de entrada.
3. Genera combinaciones desde N hasta 2 productos.
4. Calcula el precio final de cada kit.
5. Define si la publicación será premium o clásica.
6. Busca las imágenes locales asociadas a cada repuesto.
7. Sube las imágenes a MercadoLibre.
8. Construye el payload de publicación.
9. Publica el item en MercadoLibre.
10. Devuelve el resultado con los IDs de publicaciones creadas.

--------------------------------------------------

ENDPOINTS PRINCIPALES

POST /api/kits/preview

Genera los kits, pero no publica en MercadoLibre.
Sirve para revisar antes de crear publicaciones reales.

POST /api/kits/publish

Genera los kits y los publica directamente en MercadoLibre.

--------------------------------------------------

EJEMPLO DE REQUEST

{
  "nombre_maquina": "Desbrozadora 43cc 52cc",
  "tipo_maquina": "Desbrozadora",
  "max_productos_por_kit": 4,
  "compatibilidad": "CG430, CG520, 43cc, 52cc",
  "repuestos": [
    {
      "nombre": "Carburador",
      "precio_unitario": 6990,
      "cantidad_piezas": 1,
      "nombre_imagen": "carburador"
    },
    {
      "nombre": "Brida admisión",
      "precio_unitario": 3990,
      "cantidad_piezas": 1,
      "nombre_imagen": "brida_admision"
    },
    {
      "nombre": "Bujía",
      "precio_unitario": 2990,
      "cantidad_piezas": 1,
      "nombre_imagen": "bujia"
    }
  ]
}

--------------------------------------------------

IMPORTANTE

Antes de usar /publish, se recomienda usar /preview para revisar que los kits, precios, títulos e imágenes estén correctos.

El archivo .env no debe subirse a GitHub.

La carpeta imagenes/ tampoco debería subirse si contiene imágenes pesadas o privadas.