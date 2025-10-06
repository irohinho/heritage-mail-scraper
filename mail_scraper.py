import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def main():
    driver = webdriver.Firefox()
    driver.get("https://theheritage.ac.in/hitadmissionletterprint.aspx")

    results = dict()
    missing = set()
    null_count = 0

    for i in range(51, 64):
        for j in range(1, 220):
            if null_count >= 5:
                break
            roll_no = "25" + str(i) + str(j).zfill(3)

            mail = get_mail(driver, roll_no)
            print(f"{roll_no} - {mail}")
            if mail is None:
                null_count += 1
                missing.add(roll_no)
            elif mail == "":
                missing.add(roll_no)
            else:
                results[roll_no] = mail
                print(f"Found {roll_no} - {mail}")
            
            # Reload the page for the next iteration
            driver.get("https://theheritage.ac.in/hitadmissionletterprint.aspx")
            
        null_count = 0

    with open("autonomy_rolls.json", "w") as f:
        json.dump(results, f, indent=4)

    with open("missing_rolls.txt", "w") as f:
        for roll in sorted(missing):
            f.write(roll + "\n")

    driver.quit()


def get_mail(driver, roll_no):
    try:
        college_roll = driver.find_element(By.ID, "txtAutonomyExamRollNo")
        driver.execute_script(
            "arguments[0].setAttribute('value', arguments[1])", college_roll, str(roll_no)
        )
    except (NoSuchElementException, TimeoutException):
        return None

    # Wait for any modal to disappear before clicking Submit
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modalPopup_backgroundElement"))
        )
    except:
        pass  # Modal might not be present

    # Wait for the Submit button to be clickable and click with Selenium
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnSubmit"))
        )
        submit_button.click()
    except (NoSuchElementException, TimeoutException):
        return None

    # Wait for any modal to disappear before clicking Generate OTP
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modalPopup_backgroundElement"))
        )
    except:
        pass  # Modal might not be present

    # Wait for the Generate OTP button to be clickable and click with Selenium
    try:
        generate_otp_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnGenerateOTP"))
        )
        generate_otp_button.click()
    except (NoSuchElementException, TimeoutException):
        return None

    # Wait for the email/OTP message to appear
    try:
        mail_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "lblOTPMsg"))
        )
        mail = mail_element.text
    except (NoSuchElementException, TimeoutException):
        return None
    return mail


if __name__ == "__main__":
    main()
