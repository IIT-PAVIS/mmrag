"""
This script downloads a video from a specified URL using Selenium and Chrome WebDriver.
It takes the following arguments:
    --base_url: Base URL of the video page
    --output_folder: Folder to save the downloaded video
The script uses the download_file function to download the video with progress indication.
The video information is saved to a text file with the same name as the video file but with a .txt extension.
The script uses Selenium to interact with the webpage and Chrome WebDriver to download the video.
Author: Pavis
Date: 25/03/2024
"""

import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests
from tqdm import tqdm

def download_file(url, filename):
    """Download file with progress bar using requests and tqdm."""
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")

def get_video(base_url, output_folder):
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ensure Chrome runs in headless mode
        chrome_options.add_argument("--disable-gpu")  # Recommended as needed for headless mode
        chrome_options.add_argument("--window-size=1920x1080")  # Optional, but may help with certain scenarios

        # Setup Selenium WebDriver
        driver = webdriver.Chrome(options=chrome_options)  # Ensure chromedriver is installed and in your PATH

        # Navigate to the video page
        driver.get(base_url)

        # Wait for the page and elements to load
        wait = WebDriverWait(driver, 10)

        video_information = ""

        # Find title and read the text inside, it is in h3 tag
        video_title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h3"))).text
        print("Title:", video_title)

        video_information += f"Title: {video_title}\n"

        # Find class testo and read the text inside removing html tags
        video_description = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "testo"))).text
        print("Content:", video_description)

        video_information += f"Content: {video_description}\n"

        # Find class data (video creation date) and read the text inside
        video_creation_date = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "data"))).text
        print("Date:", video_creation_date)

        video_information += f"Date: {video_creation_date}\n"
    
        # Open the download popup
        download_popup_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#download-box-main']")))
        download_popup_link.click()

        # Wait for the download link within the popup to be clickable
        download_link_within_popup = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='download-box-main']//a[contains(@class, 'btn-link') and @target='_blank']")))

        # Get the download URL
        final_download_url = download_link_within_popup.get_attribute('href')

        print("Download URL:", final_download_url)

        # Create video filename from the finale download URL, like https://webtv.camera.it/download/flash_7/2024/AI_20240207_ch28_24496.mp4
        video_filename = final_download_url.split('/')[-1]

        video_filename = f"{output_folder}/{video_filename}"

        # Download the video with progress indication
        download_file(final_download_url, video_filename)

        print(f"Video successfully downloaded as {video_filename}.")

        # Save video information to a text file with the same name as the video file but with a .txt extension
        text_filename = video_filename.replace('.mp4', '.txt')
        with open(text_filename, 'w') as file:
            file.write(video_information)

        print(f"Video information saved to {text_filename}.")

    finally:
        # Cleanup
        driver.quit()

def main():
    parser = argparse.ArgumentParser(description="Download videos from a specified URL.")
    
    parser.add_argument("--base_url", type=str, default="https://webtv.camera.it/evento/24495", help="Base URL of the video page.")
    parser.add_argument("--output_folder", type=str, default=".", help="Folder to save the downloaded video.")

    args = parser.parse_args()
    
    get_video(args.base_url, args.output_folder)
   
if __name__ == "__main__":
    main()