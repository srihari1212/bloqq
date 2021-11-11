# Files and their descriptions

1. Dataset: This folder contains the dataset which is helpful in training and prediction for the prediction module as well as for the optimization module.
2. Documents: This folder contains the documentation related to modelling and development.
3. Static: This contains the design of the html pages such as java script functions, css and images used in the html files.
4. Templates: This contains the html files used for hosting this project
5. CreatePickle.py: Reads the XL files present in the Dataset folder and then convert them in the pickle format so that it would be easy to use in the main processing module (Demo.py).
6. Demo.py: This is the main program (flask server), we have created different apis for different purpose inside this.
7. Temp.py: J=To test random stuff used in the project (Not relevant)
8. Demo-Copy.py: Just the replica

# Setup

## POSIX

1. Clone repo:
```
git clone git@gitlab.com:avinash_kumar_singh/bloq.git
cd bloq
```

2. Install and activate python virtual environment and dependancies:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the demo code:
```
python Demo.py
```
