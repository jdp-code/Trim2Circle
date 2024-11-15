from flask import Flask, request, render_template, send_file
import os
from PIL import Image, ImageDraw
import io
import zipfile
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, A3, A5, B4, B5, TABLOID
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_images():
    diameter_mm = int(request.form['diameter']) if 'diameter' in request.form else None
    output_format = request.form['output_format']
    paper_size = request.form['paper_size']
    input_files = request.files.getlist('input_files')

    images = []
    total_files = len(input_files)
    for i, file in enumerate(input_files):
        if file.filename.endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(file.stream).convert("RGBA")
            if diameter_mm:
                image = resize_image(image, diameter_mm)
                output_image = crop_to_circle(image, diameter_mm)
            else:
                output_image = image
            images.append(output_image)

    if output_format == 'pdf':
        pdf_buffer = io.BytesIO()
        create_pdf(images, diameter_mm, pdf_buffer, paper_size)
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='processed_images.pdf')
    elif output_format == 'zip':
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, image in enumerate(images):
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='PNG')
                zip_file.writestr(f'image_{i + 1}.png', output_buffer.getvalue())
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='processed_images.zip')

def resize_image(image, diameter_mm):
    dpi = image.info.get('dpi', (300, 300))[0]  # Default to 300 DPI if not available
    diameter_pixels = mm_to_pixels(diameter_mm, dpi)
    return image.resize((diameter_pixels, diameter_pixels), Image.LANCZOS)

def crop_to_circle(image, diameter_mm):
    dpi = image.info.get('dpi', (300, 300))[0]  # Default to 300 DPI if not available
    diameter_pixels = mm_to_pixels(diameter_mm, dpi)
    # Create a mask to crop the image to a circle
    mask = Image.new('L', (diameter_pixels, diameter_pixels), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, diameter_pixels, diameter_pixels), fill=255)
    result = Image.new('RGBA', (diameter_pixels, diameter_pixels))
    result.paste(image, (0, 0), mask=mask)
    # Add a white background to the image
    background = Image.new('RGBA', result.size, (255, 255, 255, 255))
    background.paste(result, (0, 0), result)
    return background

def mm_to_pixels(mm, dpi):
    return int(mm * 0.0393701 * dpi)

def mm_to_points(mm):
    return mm * 2.83465

def get_paper_size(size_name):
    sizes = {
        'A3': A3,
        'A4': A4,
        'A5': A5,
        'LETTER': LETTER,
        'LEGAL': LEGAL,
        'B4': B4,
        'B5': B5,
        'TABLOID': TABLOID
    }
    return sizes.get(size_name, A4)

def create_pdf(images, diameter_mm, buffer, paper_size):
    page_size = get_paper_size(paper_size)
    c = canvas.Canvas(buffer, pagesize=page_size)
    diameter_points = mm_to_points(diameter_mm) if diameter_mm else None
    margin_points = mm_to_points(10)
    spacing_points = mm_to_points(5)
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

        # Save the image to a buffer to preserve transparency
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)
        c.drawImage(img_reader, x, y, width=diameter_points, height=diameter_points)
        x += diameter_points + spacing_points

    c.save()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)