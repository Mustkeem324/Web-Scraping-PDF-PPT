import requests
from urllib.parse import urlparse
import json
import re
from bs4 import BeautifulSoup
import img2pdf
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, send_from_directory
import os
import json

#app flask mak api function
app = Flask(__name__)

# Create the ThreadPoolExecutor outside the fast_download function.
executor = ThreadPoolExecutor()

@app.route('/', methods=['GET'])
def home():
    return """<!DOCTYPE html>
<html>
<head>
    <style>
        /* CSS styles */
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
            margin: 0;
            padding: 20px;
        }

        h1 {
            color: #333;
            font-size: 24px;
        }

        p {
            color: #666;
            font-size: 16px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 4px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        .api-link {
            color: #007bff;
            text-decoration: none;
        }

        .api-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>How to Use this API?</h1>
        <p>
            To use the API, make a GET request to the following URL:
            <br>
            <a href="https://webpage.com/apii?url=(pdf_url)" class="api-link">https://webpage.com/apii?url=(pdf_url)</a>
        </p>
        <p>
            Replace "(pdf_url)" in the URL with the actual URL of the PDF file you want to retrieve data from.
        </p>
    </div>
</body>
</html>
"""

def download_slide_images(url):
    def download_image(url):
        with app.app_context():
            response = requests.get(url ,stream=True)
            # Check if the renquest was successful
            if response.status_code == 200:
                print(f"Response Status: {response}")
            return response.content

    if url.startswith("https://slideplayer.com"):
        print(f'Slideplayer Link: {url}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
        }

        response = requests.get(url, headers=headers,stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            # Get the content length to track progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
        matches = re.findall(r'<script type="application\/ld\+json">(.*?)<\/script>', response.text, re.DOTALL)
        json_data = matches
        content_urls = []
        for json_str in json_data:
            decoded_data = json.loads(json_str)
            if 'contentUrl' in decoded_data:
                content_urls.append(decoded_data['contentUrl'])

        image_data_list = []
        slide_folder = "slide"
        os.makedirs(slide_folder, exist_ok=True)  # Create the "slide" folder if it doesn't exist
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_image, url) for url in content_urls]
            for future, url in zip(as_completed(futures), content_urls):
                image_data_list.append(future.result())
                # Save the image to the "slide" folder
                image_filename = url.split("/")[-1].split("?")[0]  # Get the image filename from the URL
                image_filepath = os.path.join(slide_folder, image_filename)
                with open(image_filepath, "wb") as image_file:
                    image_file.write(future.result())

        with open("output.pdf", "wb") as pdf_file:
            pdf_bytes = img2pdf.convert(image_data_list)
            for data in response.iter_content(chunk_size=1024):
                pdf_file.write(pdf_bytes)
                downloaded_size += len(data)
                print(f"Download Progress: {downloaded_size}/{total_size} bytes")

        # After creating the PDF, remove the image files from the "slide" folder
        for image_filepath in os.listdir(slide_folder):
            os.remove(os.path.join(slide_folder, image_filepath))
        os.rmdir(slide_folder)  # Remove the "slide" folder
        return send_from_directory('.', 'output.pdf', as_attachment=True)

    elif url.startswith("https://issuu.com/"):
        print(f'Issuu Link: {url}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
        }

        parsed_url = urlparse(url)
        publisher_id = parsed_url.path.split('/')[1]
        document_id = parsed_url.path.split('/')[2]
        json_file = parsed_url.path.split('/')[3]
        json_url = f'https://reader3.isu.pub/{publisher_id}/{json_file}/reader3_4.json'

        response = requests.get(json_url, headers=headers,stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            # Get the content length to track progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
        response_data = json.loads(response.text)

        image_data_list = []
        slide_folder = "slide"
        os.makedirs(slide_folder, exist_ok=True)  # Create the "slide" folder if it doesn't exist
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_image, f'https://{page["imageUri"]}') for page in response_data['document']['pages']]
            for future, url in zip(as_completed(futures),  response_data['document']['pages']):
                image_data_list.append(future.result())
                # Save the image to the "slide" folder
                image_filename = url.split("/")[-1].split("?")[0]  # Get the image filename from the URL
                image_filepath = os.path.join(slide_folder, image_filename)
                with open(image_filepath, "wb") as image_file:
                    image_file.write(future.result())
                    
        with open("output.pdf", "wb") as pdf_file:
            pdf_bytes = img2pdf.convert(image_data_list)
            for data in response.iter_content(chunk_size=1024):
                pdf_file.write(pdf_bytes)
                downloaded_size += len(data)
                print(f"Download Progress: {downloaded_size}/{total_size} bytes")
        # After creating the PDF, remove the image files from the "slide" folder
        for image_filepath in os.listdir(slide_folder):
            os.remove(os.path.join(slide_folder, image_filepath))
        os.rmdir(slide_folder)  # Remove the "slide" folder
        return send_from_directory('.', 'output.pdf', as_attachment=True)

    elif url.startswith("https://www.slideteam.net/"):
        print(f'Slideteam Link: {url}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
        }

        response = requests.get(url, headers=headers,stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            # Get the content length to track progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
        soup = BeautifulSoup(response.content, 'html.parser')
        div_tags = soup.find_all('div', {'class': 'product-gallery-slider'})

        link_list = []
        for div_tag in div_tags:
            img_tags = div_tag.find_all('a')
            for img in img_tags:
                src = img.get('href')
                if src and src.endswith('.jpg'):
                    link_list.append(src)

        image_data_list = []
        slide_folder = "slide"
        os.makedirs(slide_folder, exist_ok=True)  # Create the "slide" folder if it doesn't exist
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_image, link) for link in link_list]
            for future, url in zip(as_completed(futures),  link_list):
                image_data_list.append(future.result())
                # Save the image to the "slide" folder
                image_filename = url.split("/")[-1].split("?")[0]  # Get the image filename from the URL
                image_filepath = os.path.join(slide_folder, image_filename)
                with open(image_filepath, "wb") as image_file:
                    image_file.write(future.result())

        with open("output.pdf", "wb") as pdf_file:
            pdf_bytes = img2pdf.convert(image_data_list)
            for data in response.iter_content(chunk_size=1024):
                pdf_file.write(pdf_bytes)
                downloaded_size += len(data)
                print(f"Download Progress: {downloaded_size}/{total_size} bytes")
        # After creating the PDF, remove the image files from the "slide" folder
        for image_filepath in os.listdir(slide_folder):
            os.remove(os.path.join(slide_folder, image_filepath))
        os.rmdir(slide_folder)  # Remove the "slide" folder
        return send_from_directory('.', 'output.pdf', as_attachment=True)

    elif url.startswith("https://www.slideshare.net") and "slideshare" in url:
        print(f'Slideshare Link: {url}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Connection': 'keep-alive',
        }

        response = requests.get(url, headers=headers,stream=True)
        # Check if the request was successful
        if response.status_code == 200:
            # Get the content length to track progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
        soup = BeautifulSoup(response.content, "html.parser")
        images = soup.find_all("img", class_="SlideImage_img__0DmDo")

        image_data_list = []
        slide_folder = "slide"
        os.makedirs(slide_folder, exist_ok=True)  # Create the "slide" folder if it doesn't exist
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_image, image.get("srcset").split(",")[-1].split("?")[0]) for image in images]
            for future, url in zip(as_completed(futures),  images):
                image_data_list.append(future.result())
                # Save the image to the "slide" folder
                image_filename = url.split("/")[-1].split("?")[0]  # Get the image filename from the URL
                image_filepath = os.path.join(slide_folder, image_filename)
                with open(image_filepath, "wb") as image_file:
                    image_file.write(future.result())

        with open("output.pdf", "wb") as pdf_file:
            pdf_bytes = img2pdf.convert(image_data_list)
            for data in response.iter_content(chunk_size=1024):
                pdf_file.write(pdf_bytes)
                downloaded_size += len(data)
                print(f"Download Progress: {downloaded_size}/{total_size} bytes")
        # After creating the PDF, remove the image files from the "slide" folder
        for image_filepath in os.listdir(slide_folder):
            os.remove(os.path.join(slide_folder, image_filepath))
        os.rmdir(slide_folder)  # Remove the "slide" folder
        return send_from_directory('.', 'output.pdf', as_attachment=True)

    else:
        return "<p>Error: Invalid URL</p>"

# Add the necessary import and function definition for `send_from_directory`
def fast_download(url):
    # Use the global executor.
    return executor.submit(download_slide_images, url).result()

@app.route('/apii', methods=['GET'])
def process_slideshare_api():
    with app.app_context():
        url = request.args.get('url')
        if url:
            result = fast_download(url)
            return result
        else:
            return "Error: Missing 'url' parameter.", 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)),debug=True)

