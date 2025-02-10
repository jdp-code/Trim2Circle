from flask import Flask, request, render_template, send_file
import os
from PIL import Image, ImageDraw, ImageOps, ImageFont
import io
import zipfile
import math
import base64
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, A3, A5, B4, B5, TABLOID
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
import logging
from textwrap import wrap
from html.parser import HTMLParser

try:
    from pdf2image import convert_from_bytes
except ImportError:
    raise ImportError("pdf2image module is not installed. Please install it using 'pip install pdf2image'.")

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def mm_to_pixels(mm, dpi=300):
    return int(mm * 0.0393701 * dpi)

def mm_to_points(mm):
    return mm * 2.83465

class HTMLTextParser(HTMLParser):
    """Parser für HTML-Tags, um fettgedruckte Texte zu unterstützen."""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.bold = False

    def handle_starttag(self, tag, attrs):
        if tag == 'b':
            self.bold = True

    def handle_endtag(self, tag):
        if tag == 'b':
            self.bold = False

    def handle_data(self, data):
        self.text_parts.append((data, self.bold))

def parse_html_text(html_text):
    parser = HTMLTextParser()
    parser.feed(html_text)
    return parser.text_parts

def draw_curved_text(draw, text, diameter, font_size=20, y_offset=0):
    """Zeichnet geschwungenen Text entlang eines Kreises."""
    radius = diameter / 2
    text_parts = parse_html_text(text)

    angle_per_char = 360 / sum(len(part[0]) for part in text_parts)
    current_angle = -len(text) * angle_per_char / 2  # Zentriere den Text

    for part, is_bold in text_parts:
        font = ImageFont.truetype("arialbd.ttf" if is_bold else "arial.ttf", font_size)
        for char in part:
            radians = math.radians(current_angle)
            x = radius + radius * math.cos(radians) - font_size / 2
            y = radius + radius * math.sin(radians) + y_offset
            draw.text((x, y), char, font=font, fill=(0, 0, 0), anchor="mm")
            current_angle += angle_per_char

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    diameter_mm = int(request.form['diameter']) if 'diameter' in request.form else None
    margin_mm = int(request.form['margin']) if 'margin' in request.form else 10
    spacing_mm = int(request.form['spacing']) if 'spacing' in request.form else 5
    output_format = request.form['output_format'].lower()
    paper_size = request.form['paper_size']
    add_border = 'add_border' in request.form
    border_width_mm = float(request.form.get('border_width', 0)) if add_border else 0.0
    input_files = request.files.getlist('input_files')
    titles = request.form.getlist('titles[]')  # Titel-Liste aus Formular

    images = []
    for i, file in enumerate(input_files):
        if file.filename.endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = Image.open(file.stream).convert("RGBA")
                title = titles[i] if i < len(titles) else ""  # Titel für das Bild
                
                if diameter_mm:
                    image = resize_image(image, diameter_mm)
                    output_image = crop_to_circle(image, diameter_mm, title, add_border, border_width_mm)
                else:
                    output_image = image
                
                images.append(output_image)
            except Exception as e:
                logging.error(f"Error processing image {file.filename}: {e}")
                return f"Error processing image {file.filename}", 500

    # PDF-Vorschau generieren
    preview_base64 = None
    if images:
        pdf_buffer = io.BytesIO()
        create_pdf(images[:1], diameter_mm, margin_mm, spacing_mm, pdf_buffer, paper_size)  # Nur erste Seite
        pdf_buffer.seek(0)
        
        # PDF in PNG konvertieren
        preview_image = convert_from_bytes(pdf_buffer.read(), fmt='png', single_file=True)[0]
        preview_buffer = io.BytesIO()
        preview_image.save(preview_buffer, format='PNG')
        preview_base64 = base64.b64encode(preview_buffer.getvalue()).decode('utf-8')

    # Ausgabe generieren
    if output_format == 'pdf':
        pdf_buffer = io.BytesIO()
        create_pdf(images, diameter_mm, margin_mm, spacing_mm, pdf_buffer, paper_size)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='processed_images.pdf')
    elif output_format == 'png':
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for i, image in enumerate(images):
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                zf.writestr(f'image_{i+1}.png', img_buffer.read())
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='processed_images.zip')
    elif output_format == 'zip':
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for i, image in enumerate(images):
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                zf.writestr(f'image_{i+1}.png', img_buffer.read())
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='processed_images.zip')
    else:
        return "Invalid output format", 400

def resize_image(image, diameter_mm):
    diameter_pixels = mm_to_pixels(diameter_mm)
    return image.resize((diameter_pixels, diameter_pixels), Image.LANCZOS)

def crop_to_circle(image, diameter_mm, title="", add_border=False, border_width_mm=0):
    diameter_pixels = mm_to_pixels(diameter_mm)
    
    # Kreis-Maske erstellen
    mask = Image.new('L', (diameter_pixels, diameter_pixels), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter_pixels, diameter_pixels), fill=255)
    
    # Bild zuschneiden
    result = Image.new('RGBA', (diameter_pixels, diameter_pixels), (0, 0, 0, 0))
    result.paste(image, (0, 0), mask=mask)

    # Titel hinzufügen
    if title:
        draw = ImageDraw.Draw(result)
        draw_curved_text(draw, title, diameter_pixels, y_offset=-20)  # Oberhalb des Kreises
        
    # Schwarzen Rand hinzufügen (falls aktiviert)
    if add_border and border_width_mm > 0:
        border_pixels = mm_to_pixels(border_width_mm)
        draw = ImageDraw.Draw(result)
        draw.ellipse(
            (0, 0, diameter_pixels, diameter_pixels),
            outline=(0, 0, 0, 255),  # Schwarzer Rand
            width=border_pixels
        )

    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
