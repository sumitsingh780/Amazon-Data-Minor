import time
import pandas as pd
import os
import random
from flask import Flask, render_template, request, send_file, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Initialize Flask app
app = Flask(__name__)

# Setup for file upload
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed_files'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# List of user agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
]

# Function to create a WebDriver instance with a random User-Agent
def create_driver():
    options = Options()
    options.headless = True  # Run the browser in headless mode (without opening the window)
    user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to extract size and color data from the product page
def extract_size_and_color(driver):
    size = "Not Available"
    color = "Not Available"

    # Extract size using the specified XPath
    try:
        size = driver.find_element(By.XPATH, '//*[@id="variation_size_name"]/div/span').text.strip()
    except NoSuchElementException:
        size = "Not Available"
    
    # Extract color using the specified XPath
    try:
        color = driver.find_element(By.XPATH, '//*[@id="variation_color_name"]/div/span').text.strip()
    except NoSuchElementException:
        color = "Not Available"
    
    return {"Size": size, "Color": color}

# Function to extract data from a single Amazon product page
def extract_amazon_data(driver, asin):
    url = f'https://www.amazon.com/dp/{asin}'
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dp-container"))
        )
    except Exception as e:
        print(f"Error loading page for ASIN {asin}: {e}")
        return None
    
    product_data = {'ASIN': asin}
    
    try:
        rating = driver.find_element(By.ID, 'acrPopover').get_attribute('title')
    except Exception:
        rating = "No Rating"
    
    try:
        reviews = driver.find_element(By.ID, 'acrCustomerReviewText').text
    except Exception:
        reviews = "No Reviews"
    
    # Only extract price from specific locations
    try:
        # Check for the whole price and decimal price in the specified path
        whole_price = driver.find_element(By.XPATH, '//*[@class="a-price-whole"]').text.strip()
        decimal_price = driver.find_element(By.XPATH, '//*[@class="a-price-fraction"]').text.strip()
        price = f"{whole_price}.{decimal_price}"
    except NoSuchElementException:
        price = "Price Not Available"
    
    # Handling multiple cases for delivery date
    try:
        # Check if the Prime-specific XPath exists
        delivery_date = driver.find_element(By.XPATH, '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_MEDIUM"]/span/span[2]').text
    except NoSuchElementException:
        try:
            delivery_date = driver.find_element(By.CSS_SELECTOR, 'span.a-text-bold').text
        except Exception:
            delivery_date = "Delivery date not available"
    
    try:
        sold_by = driver.find_element(By.ID, 'sellerProfileTriggerId').text
    except Exception:
        sold_by = "Sold by info not available"
    
    # Extract size and color data
    size_color_data = extract_size_and_color(driver)
    
    product_data.update({
        'Rating': rating,
        'Reviews': reviews,
        'Price': price,
        'Sold by': sold_by,
        'Delivery Date': delivery_date,
        'Size': size_color_data['Size'],
        'Color': size_color_data['Color']
    })
    
    return product_data

# Function to process the uploaded ASIN list and return the processed file
def process_asin_list(file_path):
    df = pd.read_excel(file_path)
    
    # Check if 'ASIN' exists in the DataFrame
    if 'ASIN' not in df.columns:
        print("Error: 'ASIN' column not found in the input Excel file.")
        return None
    
    driver = create_driver()  # Create driver with precautions

    extracted_data = []
    
    for asin in df['ASIN']:
        print(f"Processing ASIN: {asin}")
        data = extract_amazon_data(driver, asin)
        
        if data:
            extracted_data.append(data)
        else:
            print(f"Failed to extract data for ASIN {asin}")
        
        # Add random sleep time to avoid getting blocked (2 to 5 seconds)
        time.sleep(random.uniform(2, 5))  # Sleep between 2 and 5 seconds
    
    driver.quit()
    
    # Convert to DataFrame and save to output file
    result_df = pd.DataFrame(extracted_data)
    output_file = os.path.join(OUTPUT_FOLDER, 'output_data.xlsx')
    result_df.to_excel(output_file, index=False)
    
    return output_file

# Route for the main page with the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    # Check if file is provided
    if file.filename == '':
        return redirect(request.url)
    
    # Save the uploaded file to the server
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    # Process the file and extract ratings data
    output_file = process_asin_list(file_path)
    
    if output_file:
        filename = os.path.basename(output_file)
        return render_template('index.html', filename=filename)
    else:
        return render_template('index.html', message="Error processing the file.")

# Route to handle downloading the results file
@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
