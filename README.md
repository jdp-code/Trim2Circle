# Trim2Circle

Trim2Circle is a web application that allows users to upload images, resize and crop them to a circle, and generate a PDF, PNG, or ZIP file with the processed images.

## Usecase

Custom figurines and tags for Teddy Cloud

https://github.com/toniebox-reverse-engineering/teddycloud

https://gt-blog.de/toniebox-hacking-how-to-get-started/

https://forum.revvox.de/t/teddycloud-esp32-newbie-documentation-deprecated/112

https://www.youtube.com/watch?v=JpMRyshgy9o

## Features

- Upload multiple images (PNG, JPG, JPEG)
- Resize images to a specified diameter
- Crop images to a circle
- Add a black border with a specified thickness (thanks sorz2122)
- Generate a PDF with the processed images
- Generate a PNG with the processed images
- Generate a ZIP file with the processed images
- Automatically convert multi-page PDFs to PNGs and package them in a ZIP file if necessary

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

1. Select the output format (PDF, PNG, or ZIP).
2. If PDF or PNG is selected, specify the diameter (in mm) and the paper size.
3. Optionally, specify the margin and spacing (in mm).
4. Optionally, add a black border and specify the border thickness (in mm).
5. Upload the images you want to process.
6. Click the "Process" button to generate the output file.

## Example Output PDF

Interface
![image](https://github.com/user-attachments/assets/ae4f707f-a140-4f37-832e-7c8ba8efcdd2)

Without Border
![image](https://github.com/user-attachments/assets/2f7c7840-0b33-4b70-bdcd-8fbce054c381)

With Border
![image](https://github.com/user-attachments/assets/60ce47ad-349c-4964-92ac-de401500cc20)


## Deploy with Portainer

To deploy Trim2Circle as a stack using Portainer, follow these steps:

1. Open Portainer and navigate to the "Stacks" section.
2. Click on "Add stack".
3. Name your stack (e.g., `Trim2Circle`).
4. In the "Web editor" section, paste the following content:

    ```yaml
    services:
        web:
            image: jdpcode/trim2circle
            #Only needed if building the image yourself
            #build: .
            ports:
            - "5000:5000"
            #Only needed if building the image yourself
            #volumes:
            #- .:/app
            #environment:
            #  FLASK_ENV: production
    ```

5. Replace `/path/to/local/data` with the path to the directory on your host where you want to store the application data.
6. Click "Deploy the stack".

7. Open your web browser and go to `http://<your-portainer-host>:5000`.

## Dependencies

- Flask
- Pillow
- reportlab
- pdf2image

## License

This project is licensed under the MIT License. See the LICENSE file for details.
