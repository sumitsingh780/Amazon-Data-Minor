# Amazon-Data-Minor
This project is a web scraping tool built with Flask and Selenium to extract detailed product information from Amazon based on ASINs. It enables users to upload an Excel file containing ASINs, process the data, and extract key product details such as price, rating, reviews, size, color, delivery date, and more.The application is designed to handle multiple ASINs at once, with results saved into an Excel file for easy download.

# Key Features:
Flask Web Application: Simple web interface to upload ASIN list and download results.
Amazon Data Extraction: Scrapes important product details including ratings, reviews, price, delivery dates, size, and color.
Excel File Upload: Users can upload an Excel file containing ASINs for batch processing.
Web Scraping with Selenium: Uses Selenium with a headless Chrome browser to automate the data extraction process from Amazon.
User-Agent Rotation: Rotates through different user agents to prevent IP blocking and scraping throttling.
Random Delays: Implements random delays between requests to simulate human-like behavior and reduce the chance of being blocked by Amazon.
Output as Excel: Processed product data is saved and available for download in Excel format.

# Technologies Used:
Flask: Web framework used to build the backend and serve the web interface.
Selenium: Automates web browsing to scrape product information from Amazon.
Pandas: Data manipulation and exporting the scraped data into Excel.
WebDriver Manager: Automatically manages ChromeDriver installations.
HTML/CSS: Frontend for file upload and result display.
Python: Programming language for backend and scraping logic.

#How it Works:
Users upload an Excel file with a list of Amazon ASINs.
The backend processes the file, scrapes the product data from Amazon for each ASIN using Selenium and headless Chrome.
The extracted product details, including price, rating, reviews, size, and color, are saved into a new Excel file.
The user can download the processed Excel file from the web interface.

#Requirements:
Python 3.x
Flask
Selenium
Pandas
WebDriver Manager
Chrome (for Selenium WebDriver)
An active internet connection for scraping data from Amazon

# Setup:
Clone this repository:

bash
Copy code
git clone https://github.com/yourusername/amazon-data-miner.git
cd amazon-data-miner
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Flask app:

bash
Copy code
python app.py
Open the browser and go to http://127.0.0.1:5000 to access the web interface.

# Contributions:
Feel free to fork the repository, open issues, or submit pull requests for bug fixes or feature requests.
