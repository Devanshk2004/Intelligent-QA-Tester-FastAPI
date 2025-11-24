import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# --- Setup WebDriver (CRITICAL) ---
try:
    print("Setting up Chrome WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    print("WebDriver setup successful.")
except WebDriverException as e:
    print(f"Error setting up WebDriver: {e}")
    print("Please ensure Chrome browser is installed and up-to-date.")
    exit()

# --- Determine the correct path to the HTML file ---
current_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(current_dir, 'checkout.html')

if not os.path.exists(html_file_path):
    project_assets_dir = os.path.join(current_dir, 'project_assets')
    html_file_path = os.path.join(project_assets_dir, 'checkout.html')

if not os.path.exists(html_file_path):
    print(f"Error: checkout.html not found in '{current_dir}' or '{project_assets_dir}'")
    driver.quit()
    exit()

print(f"Loading HTML file from: file:///{html_file_path}")
driver.get(f"file:///{html_file_path}")
time.sleep(3) 

try:
    print("\n--- TEST CASE: Apply 'SAVE15' discount when cart has items ---")

    print("\nStep 1: Adding items to the cart...")
    
    wireless_mouse_button = driver.find_element(By.XPATH, "//div[contains(.,'Wireless Mouse')]/button[contains(.,'Add to Cart')]")
    wireless_mouse_button.click()
    print("Clicked 'Add to Cart' for Wireless Mouse ($25).")
    time.sleep(3) 

    mechanical_keyboard_button = driver.find_element(By.XPATH, "//div[contains(.,'Mechanical Keyboard')]/button[contains(.,'Add to Cart')]")
    mechanical_keyboard_button.click()
    print("Clicked 'Add to Cart' for Mechanical Keyboard ($80).")
    time.sleep(3) 

    cart_total_element = driver.find_element(By.ID, "cart-total")
    current_total = float(cart_total_element.text)
    expected_initial_total = 105.0
    assert current_total == expected_initial_total, \
        f"Assertion Failed: Expected initial cart total {expected_initial_total}, but got {current_total}"
    print(f"Verification: Cart Total is ${current_total} (correct).")
    time.sleep(3) 

    # 2. Enter "SAVE15" in the discount code field and click 'Apply'
    print("\nStep 2: Entering 'SAVE15' into discount code field and clicking 'Apply'...")
    
    discount_code_input = driver.find_element(By.ID, "discount-code")
    discount_code_input.send_keys("SAVE15")
    print("Entered 'SAVE15' into the discount code field.")
    time.sleep(3) # Slow Motion

    apply_discount_button = driver.find_element(By.ID, "apply-discount")
    apply_discount_button.click()
    print("Clicked the 'Apply' discount button.")
    time.sleep(3) # Slow Motion

    # 3. Assertions: Verify discounted total and success message
    print("\nStep 3: Verifying the discounted total and discount message...")

    # Verify updated cart total (105 * 0.85 = 89.25)
    updated_total_element = driver.find_element(By.ID, "cart-total")
    updated_total = float(updated_total_element.text)
    expected_discounted_total = 89.25
    assert updated_total == expected_discounted_total, \
        f"Assertion Failed: Expected discounted cart total {expected_discounted_total}, but got {updated_total}"
    print(f"Verification: Discounted Cart Total is ${updated_total} (correct).")

    # Verify discount message text
    discount_msg_element = driver.find_element(By.ID, "discount-msg")
    msg_text = discount_msg_element.text
    expected_msg_text = "Coupon Applied: 15% Off"
    assert msg_text == expected_msg_text, \
        f"Assertion Failed: Expected discount message '{expected_msg_text}', but got '{msg_text}'"
    print(f"Verification: Discount message is '{msg_text}' (correct).")

    # Verify discount message color (CRITICAL)
    msg_color = discount_msg_element.value_of_css_property("color")
    print(f"Debug: Discount message CSS color property: {msg_color}")
    
    # Check if the color matches any of the specified green formats
    is_green = ("green" in msg_color.lower() or
                "rgb(0, 128, 0)" in msg_color.lower() or
                "rgba(0, 128, 0, 1)" in msg_color.lower())
    
    assert is_green, f"Assertion Failed: Expected discount message color to be green, but got {msg_color}"
    print("Verification: Discount message color is green (correct).")
    time.sleep(3) # Slow Motion

    print("\n--- TEST CASE PASSED: 'SAVE15' discount applied successfully! ---")

except Exception as e:
    print(f"\n--- TEST CASE FAILED ---")
    print(f"An error occurred: {e}")

finally:
    print("\nClosing the browser...")
    driver.quit()
