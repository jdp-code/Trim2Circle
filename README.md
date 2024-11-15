# Trim2Circle

Image Processor is a web application that allows users to upload images, resize and crop them to a circle, and generate a PDF or ZIP file with the processed images.

## Features

- Upload multiple images (PNG, JPG, JPEG)
- Resize images to a specified diameter
- Crop images to a circle
- Generate a PDF with the processed images
- Generate a ZIP file with the processed images

## Installation

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/jdp-code/Trim2Circle.git
    cd Trim2Circle
    ```

2. Build and run the application using Docker Compose:

    ```sh
    docker compose up -d
    ```

3. Open your web browser and go to `http://localhost:5000`.

## Usage

1. Select the output format (PDF or ZIP).
2. If PDF is selected, specify the diameter (in mm) and the paper size.
3. Upload the images you want to process.
4. Click the "Process" button to generate the output file.

## Dependencies

- Flask
- Pillow
- reportlab

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
