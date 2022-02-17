This is a tiny example plugin for specter. It's no way into complete and only interesting for developers right now.

The goal of this extension is to show how [Satoshi Dice](https://en.bitcoin.it/wiki/Satoshi_Dice) can be implemented 
based on a Specter Extension. This is for educational purposes only.

In order to use this:
```
git clone git@github.com:k9ert/specterext-dice.git
cd specterext-dice
pip3 install virtualenv
virtualenv --python=python3 .env
source .env/bin/activate
pip3 install -r requirements.txt
python3 -m cryptoadvance.specter server --config DevelopmentConfig --debug
# point your browser to http://localhost:25441
# "choose Services" --> dice
```

If you want to start hacking on this, i'll recommend [Visualstudio Code](https://code.visualstudio.com/). 
The procedure above will activate hot-code-reloading and if you modify the templates, it'll reflect in your browser
right away.


PRs welcome.
