## Setup libs and environment variables
Install Python 3.12.4

Create virtual env to run python:
```
python -m venv venv
```


Activate virtual env:
```
.\venv\Scripts\activate
```

Install libs:
```
pip install -r requirements.txt
```

Create file .env, and add config to it:
```
MONGODB_URL=<MONGODB server url>
```

## Instruction to run server
__NOTE__: Run server before running client

Activate venv and run server.py
```
.\venv\Scripts\activate
python server.py
```

# Instruction to run client

Activate venv and run client.py
```
.\venv\Scripts\activate
python client.py
```
__NOTE__: Server can handle requests from many clients at the same time