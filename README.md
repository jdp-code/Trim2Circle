# Trim2Circle

Trim2Circle is a web application that allows users to upload images, resize and crop them to a circle, and generate a PDF or ZIP file with the processed images.

## Usecase

Custome figurines and tags for Teddy Cloud

https://github.com/toniebox-reverse-engineering/teddycloud

https://gt-blog.de/toniebox-hacking-how-to-get-started/

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

## Example Output PDF
![image](https://github.com/user-attachments/assets/76447906-c8c0-443b-a392-6238ead95970)

![image](https://github.com/user-attachments/assets/2f7c7840-0b33-4b70-bdcd-8fbce054c381)


## Dependencies

- Flask
- Pillow
- reportlab

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
