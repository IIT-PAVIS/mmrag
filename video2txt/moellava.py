"""
This script is used to interact with the Gradio service for the MoeLLava model.
It sends a request to the service to get a description of an image.
The script can be used to send multiple requests to the service.
The script uses the requests library to communicate with the service.
The script also uses the base64 library to encode and decode images.
The script uses the argparse library to parse command line arguments.
The script uses the random and string libraries to generate random session hashes.
The script uses the cv2 and numpy libraries to work with images.
The script uses the time library to add delays between requests.
The script defines a MoeLLava class that contains methods to send requests to the service.

Usage:
    python moellava.py --url http://<ip>:<port> --image_url <image_url> --question <question>
Author: Pavis
Date: 25/03/2024
"""
import requests
import base64
import argparse
import random
import string
import websocket
import json
import time
import cv2
import numpy as np

class MoeLLava:
    def __init__(self, url):
        self.url_predict = url + "/run/predict"

    def random_hash(self):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(10))

    def encode_image(self, image):
        # image is a numpy array
        # convert to string
        _, encoded_image = cv2.imencode('.jpg', image)
        encoded_image = base64.b64encode(encoded_image).decode('utf-8')
        return encoded_image
    
    def decode_image(self, encoded_image):
        # encoded_image is a string
        # convert to numpy array
        decoded_image = base64.b64decode(encoded_image)
        decoded_image = np.frombuffer(decoded_image, dtype=np.uint8)
        decoded_image = cv2.imdecode(decoded_image, cv2.IMREAD_COLOR)
        return decoded_image
    
    def get_image(self, image_url):
        # image_url is a string
        # get image from url
        stream = cv2.VideoCapture(image_url)
        _, self.image = stream.read()
        stream.release()
    
    def send_hash(self):
        self.hash = self.random_hash()

        # first request, to set the session hash
        payload = {
            "data": [0],
            "event_data": None,
            "fn_index": 0,
            "session_hash": self.hash
        }

        response = requests.post(self.url_predict, json=payload)

        # Check the response
        if response.status_code == 200:
            # Process the response (assuming it returns an image or relevant data)
            # This part depends on how the Gradio service responds
            response_data = response.json()

            #print("Hash sent: {0}".format(self.hash), flush=True)
            #print("Response: {0}".format(response_data), flush=True)

    def send_request(self, question):
        self.question = question
        
        # encode image
        self.encoded_image = self.encode_image(self.image)
        payload = {
            "data": [self.encoded_image, self.question, None, None, None, None],
            "event_data": None,
            "fn_index": 1,
            "session_hash": self.hash
        }

        response = requests.post(self.url_predict, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            # You can modify this part based on how you need to process the response
            # print(response_data)
            self.response = response_data["data"][2][0][1]
        else:
            print("Error:", response.status_code, response.text)

    def get_response(self):
        return self.response

    def set_image(self, image):
        self.image = image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Processor")
    parser.add_argument("--url", type=str, default="http://10.245.83.46:7860",
                        help="URL of the Gradio predict endpoint")
    parser.add_argument("--image_url", type=str,
                        default="", help="Path to the image file")
    parser.add_argument("--question", type=str,
                        default="can you describe deeply the image?", help="Question about the image")
    
    args = parser.parse_args()

    client = MoeLLava(args.url)
    
    client.send_hash()
    client.get_image(args.image_url)
    client.send_request(args.question)

    inference = client.get_response()

    print("Inference:", inference, flush=True)