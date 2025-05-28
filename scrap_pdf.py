
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import easyocr
from PIL import Image
import time
import os
import requests
import random
import cv2
import numpy as np

# Initialize Chrome with download preferences
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": os.path.join(os.getcwd(), "GR_Downloads"),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

# Initialize EasyOCR reader (only need to do this once)
reader = easyocr.Reader(['en'])

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

def preprocess_captcha(image_path):
    """Enhance CAPTCHA image for better OCR results"""
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = np.ones((2,2), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    processed_path = "processed_captcha.png"
    cv2.imwrite(processed_path, img)
    return processed_path

def solve_captcha():
    """Function to handle CAPTCHA solving with EasyOCR"""
    captcha_element = wait.until(EC.presence_of_element_located((By.ID, "SitePH_ImgCaptcha")))
    time.sleep(0.5)
    captcha_element.screenshot("raw_captcha.png")
    
    # Preprocess the image
    processed_path = preprocess_captcha("raw_captcha.png")
    
    # Use EasyOCR for better accuracy
    result = reader.readtext(processed_path, detail=0)
    captcha_text = ''.join(result).strip() if result else ""
    
    print(f"Extracted CAPTCHA: {captcha_text}")
    driver.find_element(By.ID, "SitePH_txtimgcode").clear()
    driver.find_element(By.ID, "SitePH_txtimgcode").send_keys(captcha_text)
    return captcha_text

def download_pdfs(page_num=1):
    """Function to download PDFs from current page"""
    pdf_links = driver.find_elements(By.CSS_SELECTOR, "#SitePH_dgvDocuments a[target='_blank']")
    print(f"Page {page_num}: Found {len(pdf_links)} PDFs")
    
    for i, link in enumerate(pdf_links):
        pdf_url = link.get_attribute("href")
        pdf_url = pdf_url.replace("../", "https://gr.maharashtra.gov.in/")
        
        filename = os.path.join("GR_Downloads", f"Page_{page_num}_GR_{i+1}.pdf")
        
        if not os.path.exists(filename):
            try:
                response = requests.get(pdf_url, stream=True, timeout=10)
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded {filename}")
                time.sleep(random.uniform(0.5, 2))  # Randomized delay
            except Exception as e:
                print(f"Failed to download {filename}: {str(e)}")

try:
    driver.get("https://gr.maharashtra.gov.in/1145/Government-Resolutions")
    
    if not os.path.exists("GR_Downloads"):
        os.makedirs("GR_Downloads")

    # Select department
    dept_dropdown = Select(wait.until(EC.presence_of_element_located((By.ID, "SitePH_ddlDepartmentType"))))
    dept_dropdown.select_by_value("26")  # Soil & Water Conservation Department
    print("Selected Department")
    time.sleep(3)
    
    # Solve CAPTCHA and submit
    solve_captcha()
    wait.until(EC.element_to_be_clickable((By.ID, "SitePH_btnSearch"))).click()
    print("Submitted search form")
    time.sleep(5)
    
    # Download PDFs from all pages
    pdf_count = 0
    page_num = 1
    max_pdfs = 50  # Target number of PDFs to download
    
    while pdf_count < max_pdfs:
        # Download PDFs from current page
        download_pdfs(page_num)
        current_pdfs = len(driver.find_elements(By.CSS_SELECTOR, "#SitePH_dgvDocuments a[target='_blank']"))
        pdf_count += current_pdfs
        
        # Check if we've reached our target or if there are no more pages
        if pdf_count >= max_pdfs:
            break
            
        # Try to navigate to next page
        next_page_selector = f"a[id^='SitePH_ucPaging_p'][id$='_{page_num+1}']"
        next_page_buttons = driver.find_elements(By.CSS_SELECTOR, next_page_selector)
        
        if not next_page_buttons:
            print("No more pages available")
            break
            
        next_page_buttons[0].click()
        print(f"Navigating to page {page_num + 1}")
        time.sleep(5)
        
        # Solve CAPTCHA if it appears again
        if driver.find_elements(By.ID, "SitePH_ImgCaptcha"):
            solve_captcha()
            wait.until(EC.element_to_be_clickable((By.ID, "SitePH_btnSearch"))).click()
            time.sleep(5)
            
        page_num += 1

except Exception as e:
    print(f"An error occurred: {e}")
    driver.save_screenshot("error_screenshot.png")
    print("Saved error screenshot as error_screenshot.png")

finally:
    print(f"Total downloaded PDFs: {len([f for f in os.listdir('GR_Downloads') if f.endswith('.pdf')]) if os.path.exists('GR_Downloads') else 0}")
    input("Press Enter to exit...")
    driver.quit()