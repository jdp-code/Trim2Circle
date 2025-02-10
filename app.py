from flask import Flask, request, render_template, send_file
import os
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import math
import base64
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, A3, A5, B4, B5, TABLOID
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
import logging

# Ensure pdf2image is installed
try:
    from pdf2image import convert_from_bytes
except ImportError:
    raise ImportError("pdf2image module is not installed. Please install it using 'pip install pdf2image'.")

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tmp'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def mm_to_pixels(mm, dpi=300):
    return int(mm * 0.0393701 * dpi)

def mm_to_points(mm):
    return mm * 2.83465

def draw_centered_text(draw, text, diameter, font_size=20, bold_words=[], y_offset=0):
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
        bold_font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
        bold_font = font

    # Textbreite berechnen
    text_width = sum(font.getsize(c)[0] for c in text)
    radius = diameter / 2
    start_angle = 270 - (text_width / (diameter * math.pi)) * 180
    
    words = text.split()
    angle_per_char = 360 * text_width / (diameter * math.pi) / len(text)

    current_angle = start_angle
    for word in words:
        word_width = sum(font.getsize(c)[0] for c in word)
        word_angle = angle_per_char * len(word)
        
        # Wortposition berechnen
        mid_angle = current_angle + word_angle/2
        radians = math.radians(mid_angle)
        x = radius + (radius - 20) * math.cos(radians)
        y = radius + (radius - 20) * math.sin(radians) + y_offset
        
        # Fettdruck prüfen
        use_bold = word.strip() in bold_words
        draw.text((x, y), word, 
                 font=bold_font if use_bold else font, 
                 fill=(0, 0, 0),
                 anchor="mm")
        
        current_angle += word_angle + angle_per_char  # + Leerzeichen

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    try:
        params = {
            'diameter': int(request.form['diameter']),
            'margin': int(request.form.get('margin', 10)),
            'spacing': int(request.form.get('spacing', 5)),
            'font_size': int(request.form['font_size']),
            'output_format': request.form['output_format'],
            'paper_size': request.form['paper_size'],
            'add_border': 'add_border' in request.form,
            'border_width': float(request.form.get('border_width', 0.5)),
            'bold_words': [w.strip() for w in request.form.get('bold_words', '').split(',')]
        }
    except Exception as e:
        return f"Fehler in Parametern: {str(e)}", 400

    images = []
    for i, file in enumerate(request.files.getlist('input_files')):
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        try:
            img = Image.open(file.stream).convert("RGBA")
            title = request.form.get(f'title_{i}', '')
            
            if params['diameter'] > 0:
                size = mm_to_pixels(params['diameter'])
                img = img.resize((size, size), Image.LANCZOS)
                img = crop_to_circle(img, params, title)
            
            images.append(img)
        except Exception as e:
            logging.error(f"Fehler bei {file.filename}: {str(e)}")
            return f"Fehler bei {file.filename}", 500

    preview = generate_preview(images[0]) if images else None

    if params['output_format'] == 'pdf':
        pdf_buffer = io.BytesIO()
        create_pdf(images, params, pdf_buffer)
        return send_file(pdf_buffer, mimetype='application/pdf', 
                       as_attachment=True, 
                       download_name='circle_images.pdf')
    
    elif params['output_format'] == 'png':
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for i, img in enumerate(images):
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                zf.writestr(f'image_{i+1}.png', buf.getvalue())
        return send_file(zip_buffer, mimetype='application/zip',
                       as_attachment=True,
                       download_name='circle_images.zip')

    return "Ungültiges Format", 400

def crop_to_circle(img, params, title):
    size = img.width
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)
    
    if params['add_border']:
        border = mm_to_pixels(params['border_width'])
        draw = ImageDraw.Draw(result)
        draw.ellipse((0, 0, size, size), outline="black", width=border)

    if title:
        draw = ImageDraw.Draw(result)
        draw_centered_text(draw, title, size, 
                          params['font_size'],
                          params['bold_words'],
                          y_offset=-size*0.1)
    
    return result

def generate_preview(image):
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def create_pdf(images, params, buffer):
    page_size = get_paper_size(params['paper_size'])
    c = canvas.Canvas(buffer, pagesize=page_size)
    
    diameter = mm_to_points(params['diameter'])
    margin = mm_to_points(params['margin'])
    spacing = mm_to_points(params['spacing'])
    
    x = margin
    y = page_size[1] - margin - diameter
    
    for img in images:
        if x + diameter > page_size[0] - margin:
            x = margin
            y -= diameter + spacing
            if y < margin:
                c.showPage()
                y = page_size[1] - margin - diameter
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        c.drawImage(ImageReader(buf), x, y, width=diameter, height=diameter)
        x += diameter + spacing
    
    c.save()

def get_paper_size(name):
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
    return sizes.get(name.upper(), A4)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
