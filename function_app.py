import azure.functions as func
import logging
import openai
from azurefunctions.extensions.http.fastapi import Request, StreamingResponse
import asyncio
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Azure OpenAI Configuration
endpoint = "https://azuretrail11.openai.azure.com/"
deployment = "gpt-35"
api_key = "54789fbd9c524a2b81a040b4f526ed31"
temperature = 0.7

client = openai.AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-01"     #2023-09-01-preview
)

# Get data from Azure Open AI
def stream_processor(response):
    for chunk in response:
        if len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content: # Get remaining generated response if applicable
                # await asyncio.sleep(0.1)
                yield delta.content


@app.route(route="http_trigger", methods=[func.HttpMethod.GET])
def http_trigger(req: Request) -> StreamingResponse:
    logging.info('Python HTTP trigger function processed a request.')
    print("http_trigger function triggered")
    
    # prompt = "List the 100 most populous cities in the United States."
    query = req.query_params.get("query")
    prompt = query

    Completion_prompt_new = f"""
    You are an intelligent assistant chatbot designed to help users with questions related to medical topics.
    Instructions
    - Only answer if questions are related to medical topics. Recommend users go to a medical website or consult a healthcare professional for more information.
    - If you're sure that the question is related to medical topics, provide relevant information and recommend users go to a medical website or consult a healthcare professional for more information.
    - If you're unsure of an answer, you must say "I don't know. I know only about medical topics."
    - If a question is not related to medical topics, you must say "I don't know. I know only about medical topics."
    - Don't hallucinate or provide answers based on guesses.
    - For any questions related to personal state, identity, or nature, you must respond with "I don't know. I know only about medical topics."
    - Follow these instructions strictly.
    examples
    User - "What are the common symptoms of flu?" 
    Assistant - "Common symptoms of the flu include fever, cough, sore throat, runny or stuffy nose, muscle aches, headaches, and fatigue. Recommend users go to a medical website or consult a healthcare professional for more information."
    User - "Who is the founder of Microsoft?" 
    Assistant - "I don't know. I know only about medical topics."
    User - "What is the treatment for a broken leg?" 
    Assistant - "Treatment for a broken leg typically involves immobilization with a cast or splint, pain management, and possibly surgery. Recommend users go to a medical website or consult a healthcare professional for more information."
    User - "Tell me something interesting?" 
    Assistant - "I don't know. I know only about medical topics."
    User - "Who are you?" 
    Assistant - "I don't know. I know only about medical topics."
    """

    azure_open_ai_response = client.chat.completions.create(
        model=deployment,
        temperature=temperature,
        max_tokens=1000,
        messages=[{"role": "system", "content":Completion_prompt_new},
                  {"role": "user", "content": prompt}],
        stream=True
    )

    return StreamingResponse(stream_processor(azure_open_ai_response), media_type="text/event-stream")









