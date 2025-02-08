Trim2Circle

Trim2Circle is a web application that allows users to upload images, resize and crop them to a circle, and generate a PDF or ZIP file with the processed images.

Usecase

Custom figurines and tags for Teddy Cloud

https://github.com/toniebox-reverse-engineering/teddycloud

https://gt-blog.de/toniebox-hacking-how-to-get-started/

https://forum.revvox.de/t/teddycloud-esp32-newbie-documentation-deprecated/112

https://www.youtube.com/watch?v=JpMRyshgy9o

Features

Upload multiple images (PNG, JPG, JPEG)

Resize images to a specified diameter

Crop images to a circle

Generate a PDF with the processed images

Generate a ZIP file with the processed images

New in this fork: Option to add a black border for cutting guidance

New in this fork: Ability to specify the border width

Installation

Prerequisites

Docker

Docker Compose

Steps

Clone the repository:

git clone https://github.com/jdp-code/Trim2Circle.git
cd Trim2Circle

Build and run the application using Docker Compose:

docker compose up -d

Open your web browser and go to http://localhost:5041.

Usage

Select the output format (PDF or ZIP).

If PDF is selected, specify the diameter (in mm) and the paper size.

Upload the images you want to process.

(Optional) Enable the black border option and specify the border width.

Click the "Process" button to generate the output file.

Example Output PDF





Dependencies

Flask

Pillow

reportlab

License

This project is licensed under the MIT License. See the LICENSE file for details.

