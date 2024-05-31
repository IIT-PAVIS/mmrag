
"""
TinyGptVisionWebClient is a client for the Gradio service that uses TinyGPT and Vision models.
It sends an image to the Gradio service and asks a question about the image.
The service will respond with a description of the image.
The client then sends the response back to the service.
The client uses a WebSocket connection to communicate with the service.

Usage:
    python tinygptv.py --url http://<ip>:<port> --image_url <image_url> --question <question>
    
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

class TinyGptVisionWebClient:
    def __init__(self, url):
        self.url_predict = url + "/run/predict"
        #remove http:// and add ws://
        ws_url = url.replace("http://", "ws://")
        self.url_join = ws_url + "/queue/join"

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
            "data": [2],
            "event_data": None,
            "fn_index": 1,
            "session_hash": self.hash
        }

        response = requests.post(self.url_predict, json=payload)

        # Check the response
        if response.status_code == 200:
            # Process the response (assuming it returns an image or relevant data)
            # This part depends on how the Gradio service responds
            response_data = response.json()

            print("Hash sent: {0}".format(self.hash), flush=True)

    def send_request(self, question):
        self.question = question
        
        # encode image
        self.encoded_image = self.encode_image(self.image)
        payload = {
            "data": [self.question, [], None, {"image": self.encoded_image, "mask": self.encoded_image}, None, None, None],
            "event_data": None,
            "fn_index": 6,
            "session_hash": self.hash
        }

        response = requests.post(self.url_predict, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            # You can modify this part based on how you need to process the response
            print(response_data)
        else:
            print("Error:", response.status_code, response.text)

    def inference(self):
        ws = websocket.create_connection(self.url_join)

        result = ws.recv()
        print("Received hash request: {0}".format(result), flush=True)

        ws.send(json.dumps({"session_hash": self.hash, "fn_index": 6}))

        print("Sent hash: {0}".format(self.hash), flush=True)

        result = ws.recv()
        print("Received estimation: {0}".format(result), flush=True)

        response = {
            "data": [
                [
                    [self.question, None]
                ],
                None,
                None,
                0.6
            ],
            "event_data": None,
            "fn_index": 7,
            "session_hash": self.hash
        }

        ws.send(json.dumps(response))

        result = ws.recv()
        print("Start Receiving: {0}".format(result), flush=True)

        json_result = json.loads(result)
        result = ws.recv()
        print("Receiving: {0}".format(result), flush=True)

        duration_counter = 0.0
        while True:
            try:
                result = ws.recv()
                json_result = json.loads(result)
                
                duration_counter += json_result["output"]["duration"]

                print("Elaboration: {0}s".format(duration_counter), end="\r", flush=True)
            except websocket._exceptions.WebSocketConnectionClosedException as e:
                print("Connection closed")
                break
            except Exception as e:
                print(e)
                break
                
        ws.close()
        ws.shutdown()

        self.response = json_result["output"]["data"][0][0][1]

    def get_response(self):
        return self.response

    def reset(self):
        payload = {
            "data": [None, None],
            "event_data": None,
            "fn_index": 9,
            "session_hash": self.hash
        }
        response = requests.post(self.url_predict, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            # You can modify this part based on how you need to process the response
            print(response_data)
        else:
            print("Error:", response.status_code, response.text)

    def close(self):

        payload = {
            "data": [[[self.question,self.response]], {"image": self.encoded_image, "mask": self.encoded_image}],
            "event_data": None,
            "fn_index": 8,
            "session_hash": self.hash
        }

        response = requests.post(self.url_predict, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            # You can modify this part based on how you need to process the response
            print(response_data)
        else:
            print("Error:", response.status_code, response.text)

    def set_image(self, image):
        self.image = image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Processor")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:7860",
                        help="URL of the Gradio predict endpoint")
    parser.add_argument("--image_url", type=str,
                        default="http://192.168.1.96/oneshotimage?1704720503839", help="Path to the image file")
    parser.add_argument("--question", type=str,
                        default="can you describe deeply the image?", help="Question about the image")
    
    args = parser.parse_args()

    client = TinyGptVisionWebClient(args.url)
    client.send_hash()
    client.reset()
    client.get_image(args.image_url)
    client.send_request(args.question)
    client.inference()
    client.close()

    inference = client.get_response()

    print("Inference:", inference, flush=True)