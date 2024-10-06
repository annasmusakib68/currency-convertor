from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    data = request.get_json()

    # Extracting the data from Dialogflow request
    source_currency = data['queryResult']['parameters']['unit-currency'][0]['currency']
    amount = data['queryResult']['parameters']['unit-currency'][0]['amount']
    target_currency = data['queryResult']['parameters']['currency-name'][0]

    print(f"Amount: {amount}, Source currency: {source_currency}, Target currency: {target_currency}")

    # Fetching conversion factor
    cf = fetch_conversion_factor(source_currency, target_currency)

    # Error handling if API fails or no conversion factor found
    if cf is None:
        return jsonify({
            "fulfillmentText": "Sorry, I couldn't fetch the conversion rate. Please try again later."
        })

    final_amount = amount * cf
    print(final_amount)

    # Returning the response back to Dialogflow in JSON format
    response_text = f"{amount} {source_currency} is equal to {final_amount} {target_currency}."

    return jsonify({
        "fulfillmentText": response_text
    })


def fetch_conversion_factor(source, target):
    url = f"https://v6.exchangerate-api.com/v6/0bb07346ace1725290a5ba24/latest/{source}"
    response = requests.get(url)

    # Checking if the response status is OK
    if response.status_code != 200:
        return None

    data = response.json()

    # Safely extract conversion rate from the JSON response
    try:
        conversion_rate = data['conversion_rates'][target]
        return conversion_rate
    except KeyError:
        return None


if __name__ == "__main__":
    app.run(debug=True)

