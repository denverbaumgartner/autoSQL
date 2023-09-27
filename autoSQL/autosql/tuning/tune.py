import os
import threading
from dotenv import load_dotenv

import replicate
from pyngrok import ngrok
from flask import Flask, request, jsonify

load_dotenv("../../.env")

MODEL_VERSION = os.environ.get("REPLICATE_LLAMA_13B_BASE")
TRAINING_DATA = os.environ.get("TRAINING_DATA_LLAMA_13B_1_0_0")
MODEL_DESINATION = os.environ.get("REPLICATE_LLAMA_13B_TUNE")

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
    training = replicate.trainings.create(
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