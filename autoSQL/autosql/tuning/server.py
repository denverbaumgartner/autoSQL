import os
from dotenv import load_dotenv

import replicate
from pyngrok import ngrok
from flask import Flask, request, jsonify

load_dotenv("../../.env")

MODEL_VERSION = os.environ.get("REPLICATE_LLAMA_13B_BASE")
TRAINING_DATA = os.environ.get("TRAINING_DATA")
MODEL_DESINATION = os.environ.get("REPLICATE_LLAMA_13B_TEST_DESTINATION")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # Assuming the incoming data is in JSON format
    print("Received webhook data:")
    print(data)
    
    # Process the webhook data here (e.g., save to a database, send notifications, etc.)

    return jsonify({'message': 'Webhook received successfully'}), 200

if __name__ == '__main__':

    # Open a ngrok tunnel to the HTTP service
    public_url = ngrok.connect(3000)
    print("Public URL:", public_url)

    # Start your local Flask server on port 3000
    app.run(host='0.0.0.0', port=3000)

    # Tune the model 
    training = replicate.trainings.create(
        version= MODEL_VERSION, # "meta/llama-2-7b:bf0a2a692f015ee21527ed2668e338032c1f937b4fcfa1f217f5cd79bf33478c",
        input={
            "train_data": TRAINING_DATA, # "https://gist.githubusercontent.com/denverbaumgartner/85882b04c2f8e28aa05b68d9aea0f14f/raw/8f0a44682d6a84f243be2fc54acaa56d191c91ab/SAMSum_50_subset.jsonl",
            "num_train_epochs": 1,
        },
        destination=MODEL_DESINATION, # "denverbaumgartner/llama2-summarizer", 
        webhook=public_url
    )

    print("Training started:", training)