# TelegramCalendarBot
A telegram bot which can be used to update and create calendar events.

## Setup
The easiest way to get up and running is to install [Docker](https://www.docker.com/products/docker-desktop).

Obtain your Bot Token using the [Bot Father](https://telegram.me/botfather).

Once Docker is setup you will need to create a google account and go to https://console.developers.google.com/. From here you will need to enable Google Calendar API. After the API is enabled you will need to create credentials. Go to the credentials tab and create a "OAuth 2.0 Client IDs" make the type Web App. Download your credentials as a JSON and save this json file as client_secret.json (can be changed in properties.py).

From this point you will need to choose your method to obtain your refresh token, you can try to use [Postman](https://www.getpostman.com/downloads/). Once you have your refresh token save it as a json file called token.json (can be changed in properties.py). After the client_secret.json and token.json file are in the root directory of this project you can modify the docker-compose.yml to use your BOT_TOKEN and your google calendar CALENDAR_ID values.

After the docker-compose file is completed you will need to run `docker-compose build` and `docker-compose up` to get the Bot up and running.

## Supported Commands
* /create - Quick create an event using Google Calendar API /quickAdd.
* /upcoming - See upcoming events
* /going - Going to event
* /not - Not going to specified event
* /undecided - Undecided about specified event
* /details - See additional information about specified event
* /help - shows the supported commands


## Notes
Please keep in mind that this bot does not currently use the Telegram Bot API Webhook, rather this bot uses the polling method provided by [Updater::start_polling](https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.updater.html#telegram.ext.Updater.start_polling). This means that bot polls every 2 seconds for new messages sent to it.
