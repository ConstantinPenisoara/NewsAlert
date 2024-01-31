import requests
import datetime as dt
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
stock_URL = "https://www.alphavantage.co/query"
stock_APIKEY = "P3VEL42N9KKCJI5V"

news_URL = "https://newsapi.org/v2/everything"
news_APIKEY = "55daba2de1834acea10c02a71c99fc04"

account_sid = "ACb0496837f5e7c00904db1ff027672de1"
auth_token = "a8d9b96bcabce7d38a0082881a79d474"

# Getting the data from alpha API
stock_parameters = {
    "function": "GLOBAL_QUOTE",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": stock_APIKEY
}

stock_response = requests.get(url=stock_URL, params=stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()
fluctuation = float(stock_data["Global Quote"]["10. change percent"].strip("%"))

# If the fluctuation in stock price is greater that 1% or lower than -1%, we get the top 3 pieces of news concerning
# the selected company, in this case Tesla
if fluctuation < -1 or fluctuation > 1:
    # getting yesterday's date
    yesterday = dt.date.today() - dt.timedelta(days=1)

    # getting the news using newsapi
    news_parameters = {
        "q": COMPANY_NAME,
        "from": yesterday,
        "to": yesterday,
        "sortBy": "popularity",
        "language": "en",
        "pageSize": 3,
        "apiKey": news_APIKEY,
    }

    news_response = requests.get(url=news_URL, params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()

    # styling the fluctuation
    styled_fluctuation = ""
    if str(fluctuation)[0] == "-":
        styled_fluctuation = str(fluctuation)[0].replace("-", "🔻") + str(fluctuation)[1:]
    else:
        styled_fluctuation = "🔺" + str(fluctuation)[0:]

    # writing the news to file
    with open("message.txt", "w") as file:
        file.write(f"TSLA: {styled_fluctuation}%\n")
        for article in news_data["articles"]:
            file.write(f"Headline: {article['title']}\n")
            file.write(f"Brief: {article['description']}\n")

    # opening the file containing the news and sending the SMS via Twilio
    with open("message.txt", "r") as file:
        content = file.read()

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=content,
        from_="+14696063576",
        to="+40727855511"
    )
    print(message.status)

