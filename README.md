T80S GRB follow up daemon
-------------------------


* Anaconda (development) install:

    
    # Enviroment setup:
    conda create -n t80s_grb python=2.7 numpy astropy ephem
    conda activate t80s_grb
    pip install pygcn
    
    git clone https://github.com/wschoenell/t80s_grb.git
    conda develop t80s_grb/

    # To download the Schlegel dust maps run:
    cd data/
    bash wget_dustmaps.sh
    
* Edit the config.json file. There is an example file named *config_test.json*.

* To get chat_id for the Telegram BOT you should say anything to the bot, then download:


    curl -i -X GET https://api.telegram.org/bot<apikey>/getUpdates
    
a chat id in the JSON data will be shown.

* Running:


    ./pygcn-listen config.json


