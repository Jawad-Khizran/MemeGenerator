from flask import Flask, jsonify, Response
from Gemini_GetApi_Class import GetApi  # Import your script


app = Flask(__name__)
gemini_api = GetApi()  # Instantiate my GetApi class


@app.route('/get_meme', methods=['GET'])
def get_api_response():

    response, sentiment = gemini_api.get_meme()

    if response:
        print(f"{response}")
        return Response(response, mimetype='text/plain'), 200 #Response:Used to send raw text with line breaks directly instead of JSON.
        #mimetype='text/plain': Specifies that the response is plain text, not JSON.
    else:
        return jsonify({"error": "Failed to retrieve data"}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
