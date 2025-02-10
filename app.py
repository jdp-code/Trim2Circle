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

# Ensure pdf2image is installed
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

def draw_curved_text(draw, text, diameter, font_size=20, bold_words=[], y_offset=0):
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        bold_font = ImageFont.truetype("arialbd.ttf", font_size)  # Fettdruck
    except:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()

    radius = diameter / 2
    angle_step = 360 / len(text)
    current_angle = 270  # Beginne oben

    for char in text:
        radians = math.radians(current_angle)
        x = radius + (radius - 10) * math.cos(radians)
        y = radius + (radius - 10) * math.sin(radians) + y_offset

        # Prüfe ob das Zeichen fett sein soll
        use_bold = char in bold_words
        draw.text((x, y), char, 
                 font=bold_font if use_bold else font,
                 fill=(0, 0, 0),
                 anchor="mm")

        current_angle -= angle_step

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    # Formularparameter
    try:
        params = {
            'diameter': int(request.form.get('diameter', 0)),
            'margin': int(request.form.get('margin', 10)),
            'spacing': int(request.form.get('spacing', 5)),
            'font_size': int(request.form.get('font_size', 20)),
            'output_format': request.form.get('output_format', 'pdf').lower(),
            'paper_size': request.form.get('paper_size', 'A4'),
            'add_border': 'add_border' in request.form,
            'border_width': float(request.form.get('border_width', 0.5)),
            'bold_words': request.form.get('bold_words', '').split(',')
        }
    except ValueError as e:
        logging.error(f"Fehler bei der Verarbeitung der Parameter: {str(e)}")
        return render_template('error.html', message="Ungültige Eingabeparameter")

    # Dateien verarbeiten
    images = []
    for i, file in enumerate(request.files.getlist('input_files')):
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img = Image.open(file.stream).convert("RGBA")
                title = request.form.get(f'title_{i}', '')

                if params['diameter'] > 0:
                    img = img.resize((mm_to_pixels(params['diameter']),) * 2, Image.LANCZOS)
                    img = crop_to_circle(img, params, title)

                images.append(img)
            except Exception as e:
                logging.error(f"Fehler bei {file.filename}: {str(e)}")
                return render_template('error.html', message=f"Fehler bei {file.filename}")

    # Vorschau generieren
    preview = None
    if images:
        preview = generate_preview(images[0])

    # Ausgabe generieren
    if params['output_format'] == 'pdf':
        pdf_buffer = io.BytesIO()
        create_pdf(images, params, pdf_buffer)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='processed_images.pdf')
    elif params['output_format'] == 'png':
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

def crop_to_circle(image, params, title):
    diameter = image.width
    draw = ImageDraw.Draw(image)

    # Kreis zeichnen
    mask = Image.new('L', (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter, diameter), fill=255)
    result = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    result.paste(image, (0, 0), mask=mask)

    # Text hinzufügen
    if title:
        draw_curved_text(ImageDraw.Draw(result), 
                        title,
                        diameter,
                        params['font_size'],
                        params['bold_words'],
                        y_offset=-20)

    # Rand hinzufügen
    if params['add_border']:
        border = mm_to_pixels(params['border_width'])
        ImageDraw.Draw(result).ellipse((0, 0, diameter, diameter), 
                                      outline=(0, 0, 0), 
                                      width=border)
    return result

def generate_preview(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def create_pdf(images, params, buffer):
    page_size = get_paper_size(params['paper_size'])
    c = canvas.Canvas(buffer, pagesize=page_size)
    diameter_points = mm_to_points(params['diameter']) if params['diameter'] else None
    margin_points = mm_to_points(params['margin'])
    spacing_points = mm_to_points(params['spacing'])
    page_width, page_height = page_size

    x = margin_points
    y = page_height - margin_points - (diameter_points if diameter_points else 0)

    for image in images:
        if diameter_points and x + diameter_points > page_width - margin_points:
            x = margin_points
            y -= diameter_points + spacing_points
            if y < margin_points:
                c.showPage()
                y = page_height - margin_points - diameter_points

        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        c.drawImage(ImageReader(img_buffer), x, y, width=diameter_points, height=diameter_points, mask='auto')
        x += diameter_points + spacing_points

    c.save()

def get_paper_size(size_name):
    sizes = {
        'A3': A3,
        'A4': A4,
        'A5': A5,
        'LETTER': LETTER,
        'LEGAL': LEGAL,
        'B4': B4,
        'B5': B5,
        'TABLOID': TABLOID,
        'CANON_SELPHY': (10*cm, 14.8*cm)
    }
    return sizes.get(size_name, A4)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
