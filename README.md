# Web-Scraping-PDF-PPT
This API allows you to retrieve data from various websites in the form of PDF documents. It supports multiple websites including Slideplayer, Issuu, Slideteam, and Slideshare.

## How to Use the API

To use the API, follow these steps:

1. Make a GET request to the following URL:
   ```
   https://your-domain.com/apii?url=(pdf_url)
   ```

   Replace `(pdf_url)` in the URL with the actual URL of the PDF file you want to retrieve data from.

2. Wait for the API to process your request.

3. Once the processing is complete, you will receive the PDF document containing the extracted data.

## Supported Websites

The API supports data extraction from the following websites:

- **Slideplayer**: Extracts data from Slideplayer presentations.
- **Issuu**: Extracts data from documents hosted on Issuu.
- **Slideteam**: Extracts data from Slideteam presentations.
- **Slideshare**: Extracts data from Slideshare presentations.

## Error Handling

If an error occurs during the process, you will receive an error message indicating the issue. Possible errors include:
- Invalid URL: The provided URL is not supported or is incorrect.
- Missing 'url' parameter: The request is missing the required 'url' parameter.

## Sample Usage

Here's an example of how to use the API:

```python
import requests

url = "https://your-domain.com/apii?url=https://www.slideshare.net/example"
response = requests.get(url)

if response.status_code == 200:
    with open("extracted_data.pdf", "wb") as f:
        f.write(response.content)
    print("Data extracted successfully!")
else:
    print("Error:", response.text)
```

## Dependencies

- [requests](https://pypi.org/project/requests/): For making HTTP requests.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/): For parsing HTML content.
- [img2pdf](https://pypi.org/project/img2pdf/): For converting images to PDF.
- [Flask](https://pypi.org/project/Flask/): For creating the API.

## Running the API

To run the API locally, make sure you have Python installed along with the required dependencies. Then, execute the following command:

```bash
python your_api_script.py
```

By default, the API will run on http://localhost:8000/.
