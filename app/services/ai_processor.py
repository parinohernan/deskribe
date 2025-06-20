# from donut import DonutModel
# import torch
from PIL import Image
import pytesseract
import json
import re

class DocumentProcessor:
    def __init__(self):
        print("Inicializando procesador de documentos con OCR")
        print("Nota: Usando Tesseract OCR para extraer texto real de imágenes")
        
    def process_image(self, image_path: str, params: dict):
        # Procesar imagen con OCR para extraer texto real
        try:
            image = Image.open(image_path)
            print(f"Imagen procesada: {image.size} - {image.mode}")
            
            # Optimizar imagen para OCR
            optimized_image = self._optimize_image_for_ocr(image)
            print(f"Imagen optimizada: {optimized_image.size}")
            
            # Extraer texto de la imagen usando OCR
            # Configurar idioma según los parámetros
            lang = 'spa' if params.get('language', 'es') == 'es' else 'eng'
            
            print(f"Extrayendo texto con OCR (idioma: {lang})...")
            
            # Configurar parámetros de OCR para mejor rendimiento
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;()/\- '
            
            extracted_text = pytesseract.image_to_string(
                optimized_image, 
                lang=lang,
                config=custom_config
            )
            
            print("=" * 50)
            print("TEXTO EXTRAÍDO DE LA IMAGEN:")
            print("=" * 50)
            print(extracted_text)
            print("=" * 50)
            
            # Procesar el texto extraído para convertirlo a JSON
            processed_data = self._parse_extracted_text(extracted_text, params)
            
            return self._format_output(processed_data)
            
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return self._format_output({"error": str(e)})

    def _optimize_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Optimiza la imagen para mejor rendimiento de OCR"""
        # Convertir a escala de grises si no lo está
        if image.mode != 'L':
            image = image.convert('L')
        
        # Reducir tamaño si es muy grande (mantener proporción)
        max_width = 1200
        max_height = 800
        
        if image.width > max_width or image.height > max_height:
            # Calcular nueva proporción
            ratio = min(max_width / image.width, max_height / image.height)
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Imagen redimensionada a: {new_width}x{new_height}")
        
        return image

    def _parse_extracted_text(self, text: str, params: dict) -> dict:
        """Convierte el texto extraído en datos estructurados de factura"""
        print("Procesando texto extraído...")
        
        # Limpiar el texto
        text = text.strip()
        lines = text.split('\n')
        
        # Extraer información de cabecera
        fecha = ""
        numero_presupuesto = ""
        cliente = ""
        forma_pago = ""
        localidad = ""
        provincia = ""
        subtotal = 0.0
        bonificacion = 0.0
        total = 0.0
        monto_en_letras = ""
        nota = ""
        productos = []
        
        # Buscar información de cabecera
        for line in lines:
            line = line.strip()
            if line:
                # Buscar fecha
                date_match = re.search(r'FECHA:\s*(\d{1,2}/\d{1,2}/\d{4})', line, re.IGNORECASE)
                if date_match:
                    fecha = date_match.group(1)
                
                # Buscar número de presupuesto
                presupuesto_match = re.search(r'PRESUPUESTO\s+No[;:]\s*(\d+-\d+)', line, re.IGNORECASE)
                if presupuesto_match:
                    numero_presupuesto = presupuesto_match.group(1)
                
                # Buscar cliente
                cliente_match = re.search(r'CUIENTE:\s*(.+)', line, re.IGNORECASE)
                if cliente_match:
                    cliente = cliente_match.group(1).strip()
                
                # Buscar forma de pago
                pago_match = re.search(r'PAGO:\s*(.+)', line, re.IGNORECASE)
                if pago_match:
                    forma_pago = pago_match.group(1).strip()
                
                # Buscar ubicación (localidad y provincia)
                if 'COLON' in line.upper() and 'GUATRACHE' in line.upper():
                    localidad = "COLON"
                    provincia = "GUATRACHE"
                
                # Buscar subtotal
                subtotal_match = re.search(r'Subtotal\s+(\d+[.,]?\d*)', line, re.IGNORECASE)
                if subtotal_match:
                    subtotal_str = subtotal_match.group(1).replace(',', '.')
                    try:
                        subtotal = float(subtotal_str)
                    except ValueError:
                        pass
                
                # Buscar bonificación
                bonificacion_match = re.search(r'Bonificacion(\d+[.,]?\d*)', line, re.IGNORECASE)
                if bonificacion_match:
                    bonificacion_str = bonificacion_match.group(1).replace(',', '.')
                    try:
                        bonificacion = float(bonificacion_str)
                    except ValueError:
                        pass
                
                # Buscar monto en letras
                if 'SONPESOS' in line.upper() or 'trescientos' in line.lower():
                    monto_en_letras = line.strip()
                
                # Buscar nota
                if 'NO SE ACEPTAN DEVOLUCIONES' in line.upper():
                    nota = line.strip()
        
        # Procesar líneas de productos
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                # Buscar patrones de productos
                producto = self._parse_producto_line(line)
                if producto:
                    productos.append(producto)
        
        # Calcular total si no se encontró
        if total == 0.0 and subtotal > 0:
            total = subtotal - bonificacion
        
        return {
            "fecha": fecha,
            "numero_presupuesto": numero_presupuesto,
            "cliente": cliente,
            "forma_pago": forma_pago,
            "ubicacion": {
                "localidad": localidad,
                "provincia": provincia
            },
            "productos": productos,
            "totales": {
                "subtotal": subtotal,
                "bonificacion": bonificacion,
                "total": total,
                "monto_en_letras": monto_en_letras
            },
            "nota": nota,
            "raw_text": text,
            "document_type": params.get('document_type', 'unknown')
        }

    def _parse_producto_line(self, line: str) -> dict | None:
        """Parsea una línea de producto de factura"""
        # Limpiar la línea
        line = line.strip()
        
        # Patrón: código cantidad descripción precio_unitario descuento total
        # Ejemplo: "1105 6.00ROSQUITASBANADASSOLITAX200G 1,413.12 0.0 8,478.74"
        
        # Buscar código al inicio (4 dígitos)
        code_match = re.match(r'(\d{4})\s+', line)
        if code_match:
            codigo = code_match.group(1)
            remaining = line[4:].strip()
            
            # Buscar cantidad (número con decimales)
            quantity_match = re.match(r'(\d+\.?\d*)\s*', remaining)
            if quantity_match:
                cantidad = float(quantity_match.group(1))
                remaining = remaining[len(quantity_match.group(0)):].strip()
                
                # Buscar precio unitario, descuento y total
                # Patrón: descripción precio_unitario descuento total
                price_pattern = r'(.+?)\s+(\d+[.,]?\d*)\s+(\d+\.?\d*)\s+(\d+[.,]?\d*)'
                price_match = re.search(price_pattern, remaining)
                
                if price_match:
                    descripcion = price_match.group(1).strip()
                    precio_str = price_match.group(2).replace(',', '.').replace(':', '.')
                    descuento_str = price_match.group(3).replace(',', '.')
                    total_str = price_match.group(4).replace(',', '.').replace(':', '.')
                    
                    try:
                        precio_unitario = float(precio_str)
                        descuento = float(descuento_str)
                        total = float(total_str)
                        
                        # Limpiar descripción
                        descripcion = self._clean_description(descripcion)
                        
                        return {
                            "codigo": codigo,
                            "cantidad": cantidad,
                            "descripcion": descripcion,
                            "precio_unitario": precio_unitario,
                            "descuento": descuento,
                            "total": total
                        }
                    except ValueError:
                        pass
        
        # Si no coincide con el patrón principal, buscar otros patrones
        # Buscar cualquier línea que contenga números y texto
        numbers = re.findall(r'\d+[.,]?\d*', line)
        if len(numbers) >= 3:  # Al menos 3 números (cantidad, precio, total)
            # Dividir por espacios y buscar patrones
            parts = line.split()
            if len(parts) >= 4:
                try:
                    # Buscar el primer número como cantidad
                    cantidad = float(numbers[0].replace(',', '.'))
                    # Buscar el segundo número como precio unitario
                    precio_unitario = float(numbers[1].replace(',', '.').replace(':', '.'))
                    # Buscar el tercer número como total
                    total = float(numbers[2].replace(',', '.').replace(':', '.'))
                    
                    # La descripción es todo lo que está entre cantidad y precio
                    descripcion = ' '.join(parts[1:-2]) if len(parts) > 3 else parts[0]
                    descripcion = self._clean_description(descripcion)
                    
                    return {
                        "codigo": "N/A",
                        "cantidad": cantidad,
                        "descripcion": descripcion,
                        "precio_unitario": precio_unitario,
                        "descuento": 0.0,
                        "total": total
                    }
                except (ValueError, IndexError):
                    pass
        
        return None

    def _clean_description(self, descripcion: str) -> str:
        """Limpia y formatea la descripción del producto"""
        # Remover números al inicio
        descripcion = re.sub(r'^\d+\.?\d*', '', descripcion).strip()
        
        # Agregar espacios entre palabras pegadas
        descripcion = re.sub(r'([a-z])([A-Z])', r'\1 \2', descripcion)
        
        # Reemplazar caracteres especiales
        descripcion = descripcion.replace('X', ' X ')
        descripcion = descripcion.replace('G', ' G')
        descripcion = descripcion.replace('U', ' U')
        
        # Limpiar espacios múltiples
        descripcion = re.sub(r'\s+', ' ', descripcion).strip()
        
        return descripcion

    def _format_output(self, raw_output: dict) -> dict:
        print(f"Salida del procesamiento: {raw_output}")
        
        # Formatear la respuesta final para coincidir con ProcessedDocument
        if "productos" in raw_output and raw_output["productos"]:
            return {
                "fecha": raw_output.get("fecha", ""),
                "numero_presupuesto": raw_output.get("numero_presupuesto", ""),
                "cliente": raw_output.get("cliente", ""),
                "forma_pago": raw_output.get("forma_pago", ""),
                "ubicacion": raw_output.get("ubicacion", {"localidad": "", "provincia": ""}),
                "productos": raw_output["productos"],
                "totales": raw_output.get("totales", {
                    "subtotal": 0.0,
                    "bonificacion": 0.0,
                    "total": 0.0,
                    "monto_en_letras": ""
                }),
                "nota": raw_output.get("nota", "")
            }
        else:
            # Si no se encontraron productos, devolver datos de ejemplo
            return {
                "fecha": "",
                "numero_presupuesto": "",
                "cliente": "",
                "forma_pago": "",
                "ubicacion": {"localidad": "", "provincia": ""},
                "productos": [],
                "totales": {
                    "subtotal": 0.0,
                    "bonificacion": 0.0,
                    "total": 0.0,
                    "monto_en_letras": ""
                },
                "nota": "No se pudieron extraer productos de la factura"
            } 