## PDF Q&A project

a webpage that allows users to answer questions about a PDF with LLMs. 
The aim of this project is to work with LLMs


### Getting started

install the dependencies with `npm install`, and run `npm run dev`. This will launch our frontend/backend dev server.

to run:

add openai apikey to `sample.env` and change to `.env`

`python -m venv venv`

`source venv/bin/activate`

`./start.py`


### Resources

- https://www.acorn.io/resources/learning-center/retrieval-augmented-generation

The basic idea will be to retrieve the relevant sources from the user's document based on a metric (usually cosine similarity), and then pass those sources into an LLM to generate a response. We can prompt the LLM to return the sources that we should show to the user.

I've used OpenAI as the frontier model provider for this exercise. It could be any embedding model + any generation model to get responses.

