```
git clone git@github.com:k9ert/specterext-dice.git
cd specterext-dice
pip3 install virtualenv
virtualenv --python=python3 .env
source .env/bin/activate
pip3 install -r requirements.txt
python3 -m cryptoadvance.specter server --config DevelopmentConfig --debug
# point your browser to http://localhost:25441
# "choose Services" --> dummy
```