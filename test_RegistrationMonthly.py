import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options for running in CI environments like GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run headless in CI
options.add_argument("--no-sandbox")  # Overcome limited resource problems
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920x1080")

# Initialize ChromeDriver using Service in Selenium 4.x and WebDriver Manager to auto-manage the driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open the registration page
driver.get("https://smoothmaths.co.uk/register/11-plus-subscription-plan/")

# Wait for the page to load
time.sleep(3)

# Fill out registration form
driver.find_element(By.ID, 'user_login').send_keys("test_user")
driver.find_element(By.ID, 'user_email').send_keys("test_email@example.com")
driver.find_element(By.ID, 'password_1').send_keys("Password123")
driver.find_element(By.ID, 'password_2').send_keys("Password123")

# Scroll down to the payment form (if needed)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# Switch to the Stripe iframe for card details input
iframe = driver.find_element(By.CSS_SELECTOR, "iframe[name^='__privateStripeFrame']")
driver.switch_to.frame(iframe)

# Fill out Stripe test card details
driver.find_element(By.NAME, 'cardnumber').send_keys("4242 4242 4242 4242")
driver.find_element(By.NAME, 'exp-date').send_keys("12/34")
driver.find_element(By.NAME, 'cvc').send_keys("123")

# Switch back to main content
driver.switch_to.default_content()

# Create the screenshots directory if it doesn't exist
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# Capture screenshot before submission
driver.save_screenshot("screenshots/before_submit.png")

# Submit the form
submit_button = driver.find_element(By.NAME, 'woocommerce_checkout_place_order')
submit_button.click()

# Wait for a few seconds to process the payment
time.sleep(10)

# Capture screenshot after submission
driver.save_screenshot("screenshots/after_submit.png")

# Check for confirmation message and save the result
try:
    confirmation_message = driver.find_element(By.CSS_SELECTOR, ".woocommerce-thankyou-order-received")
    if confirmation_message:
        result = "Test passed: Registration and payment successful"
    else:
        result = "Test failed: No confirmation message found"
except Exception as e:
    result = f"Test failed with error: {e}"

# Log result in CSV
with open('test_results.csv', mode='a') as file:
    writer = csv.writer(file)
    writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), result])

# Output the result
print(result)

# Close the browser
driver.quit()

