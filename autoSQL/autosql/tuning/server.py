from pyngrok import ngrok
from flask import Flask, request, jsonify

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

