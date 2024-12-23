# Setup

In this directory, you'll find a Python script that uses the OpenAI API to answer questions about a given file.

You can use any in-memory vector db of your choice. One simple option is below. Make sure your vector db can customize the way embeddings are inserted.

https://pypi.org/project/vectordb/

## Installing requirements

Initialize a virtual environment and install the requirements:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuring environment variables

Copy the `.env.example` file to `.env` and fill in the values with your OpenAI API key.

## Running the script

Run the script with the following command:

```bash
./start.sh
```



