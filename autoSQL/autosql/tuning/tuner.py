import os
import threading
from dotenv import load_dotenv

import replicate
from replicate import Client as rc

from pyngrok import ngrok
from flask import Flask, request, jsonify

load_dotenv("../../.env")

MODEL_VERSION = os.environ.get("REPLICATE_LLAMA_13B_BASE") # meta/llama-2-13b:078d7a002387bd96d93b0302a4c03b3f15824b63104034bfa943c63a8f208c38
TRAINING_DATA = os.environ.get("TRAINING_DATA_LLAMA_13B_1_0_0") # https://gist.githubusercontent.com/denverbaumgartner/ab7c430d27bdd8b7de396bef2f9ff8f1/raw/1ec0d10f9c10bc4eddbb4327c515bfa3af9673b0/training_data_llama_7b_1_0_0.jsonl
MODEL_DESINATION = os.environ.get("REPLICATE_LLAMA_13B_TUNE") # denverbaumgartner/llama-2-13b-sql
REPLICATE_API_TOKEN=os.environ.get("REPLICATE_API_TOKEN")

replic = rc(REPLICATE_API_TOKEN)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_root_post():
    data = request.json
    print("Received webhook data:")
    print(data)

    return jsonify({'message': 'Webhook received successfully'}), 200

def start_training():
    # Open a ngrok tunnel to the HTTP service
    tunnel = ngrok.connect(3000)
    print("Public URL:", tunnel.public_url)

    # Tune the model 
    training = replic.trainings.create(
        version= MODEL_VERSION,
        input={
            "train_data": TRAINING_DATA,
            "num_train_epochs": 3,
        },
        destination=MODEL_DESINATION,
        webhook=tunnel.public_url
    )

    print("Training started:", training)

if __name__ == '__main__':
    # Start the training process in a separate thread
    training_thread = threading.Thread(target=start_training)
    training_thread.start()

    # Start your local Flask server on port 3000
    app.run(host='0.0.0.0', port=3000)