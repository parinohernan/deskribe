# Deskribe - API de Procesamiento de Facturas con IA

Deskribe es una API desarrollada con FastAPI que utiliza OCR (Tesseract) para extraer y procesar información de facturas y presupuestos, convirtiendo imágenes en datos estructurados en formato JSON.

## 🚀 Características

- **Procesamiento de imágenes**: Extrae texto de facturas y presupuestos usando OCR
- **Estructuración de datos**: Convierte texto extraído en JSON estructurado
- **Optimización de imágenes**: Redimensiona y optimiza imágenes para mejor rendimiento
- **API REST**: Endpoint simple para procesar documentos
- **Soporte multiidioma**: Español e inglés

## 📋 Requisitos Previos

### Sistema Operativo
- Linux (Ubuntu/Debian recomendado)
- macOS
- Windows (con WSL recomendado)

### Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y tesseract-ocr tesseract-ocr-spa
sudo apt install -y pkg-config libssl-dev
sudo apt install -y rustc cargo

# macOS
brew install tesseract tesseract-lang
brew install rust

# Windows (con chocolatey)
choco install tesseract
```

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd deskribe
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar instalación
```bash
# Verificar Tesseract
tesseract --version

# Verificar Python y dependencias
python -c "import pytesseract, PIL; print('Instalación correcta')"
```

## 🚀 Uso

### 1. Iniciar el servidor
```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: `http://localhost:8000`

### 2. Documentación de la API
Una vez iniciado el servidor, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 3. Procesar una imagen

#### Usando curl:
```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ruta/a/tu/factura.jpg" \
  -F "params={\"document_type\": \"invoice\", \"language\": \"es\"}"
```

#### Usando Python:
```python
import requests

url = "http://localhost:8000/api/v1/process"
files = {"file": open("factura.jpg", "rb")}
data = {"params": '{"document_type": "invoice", "language": "es"}'}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result)
```

#### Usando Postman:
1. Método: `POST`
2. URL: `http://localhost:8000/api/v1/process`
3. Body: `form-data`
   - `file`: Seleccionar archivo de imagen
   - `params`: `{"document_type": "invoice", "language": "es"}`

## 📊 Formato de Respuesta

La API devuelve un JSON estructurado con la siguiente información:

```json
{
  "fecha": "17/6/2025",
  "numero_presupuesto": "0003-00099458",
  "cliente": "PROST CELIA",
  "forma_pago": "CTA CTE",
  "ubicacion": {
    "localidad": "COLON",
    "provincia": "GUATRACHE"
  },
  "productos": [
    {
      "codigo": "1105",
      "cantidad": 6.00,
      "descripcion": "ROSQUITAS BAÑADAS SOLITA X 300 G",
      "precio_unitario": 1413.12,
      "descuento": 0.0,
      "total": 8478.74
    }
  ],
  "totales": {
    "subtotal": 362567.22,
    "bonificacion": 0.00,
    "total": 362567.22,
    "monto_en_letras": "trescientos sesenta y dos mil quinientos sesenta y siete y 22 / 100"
  },
  "nota": "NO SE ACEPTAN DEVOLUCIONES DESPUÉS DE LAS 48 HORAS"
}
```

## ⚙️ Configuración

### Parámetros de procesamiento:
- `document_type`: Tipo de documento ("invoice" o "price_list")
- `language`: Idioma del documento ("es" para español, "en" para inglés)
- `expected_vendor`: Nombre esperado del vendedor (opcional)

### Optimización de imágenes:
- Las imágenes se redimensionan automáticamente a máximo 1200x800 píxeles
- Se convierten a escala de grises para mejor rendimiento de OCR
- Configuración optimizada de Tesseract para mejor precisión

## 🔧 Solución de Problemas

### Error: "Address already in use"
```bash
# Detener procesos de uvicorn
pkill -f uvicorn

# O usar un puerto diferente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Error: "Tesseract not found"
```bash
# Verificar instalación de Tesseract
which tesseract

# Instalar si no está presente
sudo apt install tesseract-ocr tesseract-ocr-spa
```

### Error: "Permission denied"
```bash
# Dar permisos de ejecución
chmod +x venv/bin/activate
```

### Procesamiento lento
- Las imágenes grandes pueden tardar más en procesarse
- El sistema optimiza automáticamente las imágenes
- Considera reducir el tamaño de las imágenes antes de enviarlas

## 📁 Estructura del Proyecto

```
deskribe/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de FastAPI
│   │   ├── __init__.py
│   │   └── document.py      # Modelos de datos
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_processor.py  # Procesador de OCR
│   └── api/
│       ├── __init__.py
│       └── endpoints.py     # Endpoints de la API
├── requirements.txt         # Dependencias de Python
├── .gitignore              # Archivos a ignorar en Git
└── README.md               # Este archivo
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la documentación de la API en `/docs`
2. Verifica los logs del servidor
3. Asegúrate de que todas las dependencias estén instaladas correctamente

## 🔄 Actualizaciones

Para actualizar el proyecto:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Deskribe** - Transformando facturas en datos estructurados con IA 🚀
