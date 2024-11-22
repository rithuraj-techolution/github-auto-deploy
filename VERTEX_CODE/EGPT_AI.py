import json
import requests
import re
import uuid
import traceback
import urllib.parse

from openai import AzureOpenAI

from config import POST_URL, GET_URL, REFACTOR_FUNC_NAME, UNITTEST_FUNC_NAME
from utils.utils import handle_exception



def utf8_encode(input_code: str) -> str:
    """
    Encode the input string in utf-8 format and return the encoded string.

    Args:
        input_code (str): The input string to be encoded.

    Returns:
        str: The utf-8 encoded string.
    """
    utf8_encoded_bytes = urllib.parse.quote(input_code.encode('utf-8'))
    return utf8_encoded_bytes


def inferense_post(prompt: str, assistant_name: str = None) -> tuple:
    """
    Post the inference request and return the status code and request ID.

    Args:
        prompt (str): The prompt for the inference.
        assistant_name (str, optional): The name of the assistant. Defaults to None.

    Returns:
        tuple: The status code and request ID.
    """
    assistant = assistant_name if assistant_name else REFACTOR_FUNC_NAME
    payload = {
        "aiModel": "bestai",
        "name": assistant,
        "organizationName": "84lumber",
        "prompt": utf8_encode(prompt),
        "requestId": str(uuid.uuid4())
    }
    response = requests.post(POST_URL, json=payload)
    return response.status_code, payload["requestId"]


def get_events(url: str, params: dict, headers: dict):
    """
    Get the events from the given URL with the provided parameters and headers.

    Args:
        url (str): The URL to get the events from.
        params (dict): The parameters for the get request.
        headers (dict): The headers for the get request.

    Returns:
        str: The events from the get request.
    """
    try:
        with requests.get(url, params=params, headers=headers, stream=True, timeout=600) as response:
            for chunk in response.iter_lines():
                yield chunk.decode("utf-8")

    except requests.Timeout:
        print("Timeout error: Request timed out.")
        return None

    except Exception as e:
        print("Error getevents ---", e)


def stream_inference(prompt: str, assistant_name: str = None) -> str:
    """
    Stream the inference from the post request and return the content value.

    Args:
        prompt (str): The prompt for the inference.
        assistant_name (str, optional): The name of the assistant. Defaults to None.

    Returns:
        str: The content value from the inference.
    """
    status_code, request_id = inferense_post(prompt, assistant_name)
    print('request ID : ', request_id)
    assistant = assistant_name if assistant_name else REFACTOR_FUNC_NAME

    if status_code == 200:
        params = {
            'name': assistant,
            'organizationName': '84lumber-',
            'aiModel': 'bestai',
            'requestId': request_id
        }

        headers = {
            'Cookie': f'Enterprise-GPT-Maker-84lumber-{assistant}=84lumber-{assistant}-1c6aea85-a892-4c43-ba8b-5ed9d065120a'
        }
        response_chunks = []
        try:
            for event in get_events(GET_URL, params, headers):
                if event != '':
                    response_chunks.append(event)
                    print("Chunk appeneded--------", event)

            # print("Complete response----", response_chunks)
        except Exception as e:
            print("Error---", e)

        if len(response_chunks) >= 2:
            last_data_chunk = response_chunks[-2]
            match = re.search(r'data:\s*({.*})', last_data_chunk)
            if match:
                last_data = match.group(1)
                data = json.loads(last_data)
                content_value = data['choices'][0]['delta']['content']
                # print("Content Value----------", content_value)
                return content_value


def unittest_post(prompt: str) -> tuple:
    """
    Post the unittest request and return the status code and request ID.

    Args:
        prompt (str): The prompt for the unittest.

    Returns:
        tuple: The status code and request ID.
    """
    payload = {
        "aiModel": "bestai",
        "name": UNITTEST_FUNC_NAME,
        "organizationName": "84lumber",
        "prompt": utf8_encode(prompt),
        "requestId": str(uuid.uuid4())
    }
    response = requests.post(POST_URL, json=payload)
    return response.status_code, payload["requestId"]


def stream_unittest_cases(prompt: str) -> str:
    """
    Stream the unittest cases from the post request and return the content value.

    Args:
        prompt (str): The prompt for the unittest.

    Returns:
        str: The content value from the unittest.
    """
    status_code, request_id = unittest_post(prompt)

    if status_code == 200:
        params = {
            'name': UNITTEST_FUNC_NAME,
            'organizationName': '84lumber',
            'aiModel': 'bestai',
            'requestId': request_id
        }
        headers = {
            'Cookie': f'Enterprise-GPT-Maker-84lumber-{UNITTEST_FUNC_NAME}=84lumber-{UNITTEST_FUNC_NAME}-1c6aea85-a892-4c43-ba8b-5ed9d065120a'
        }

        response_chunks = []
        try:
            for event in get_events(GET_URL, params, headers):
                if event != '':
                    response_chunks.append(event)
                    print("Chunk appeneded--------", event)

            # print("Complete response----", response_chunks)
        except Exception as e:
            print("Error---", e)

        if len(response_chunks) >= 2:
            last_data_chunk = response_chunks[-2]
            # print("Last Chunk ------", last_data_chunk)
            match = re.search(r'data:\s*({.*})', last_data_chunk)
            print("Match---------", match)
            if match:
                last_data = match.group(1)
                print("Last_data--------", last_data)
                data = json.loads(last_data)
                print("data-------", data)
                content_value = data['choices'][0]['delta']['content']
                # print("Content Value----------", content_value)
                return content_value


def error_to_message(error: str, code: str, language: str, config_class) -> str:
    """
    Convert error message and code into a feedback message.

    Args:
        error (str): The error generated by the Python code.
        code (str): The Python code snippet.
        language (str): The source code language
        config_class: Config class which contains values of API keys and URL

    Returns:
        str: Feedback message incorporating the error and code.

    """
    try:
        conversation = [
            {
                "role": "system",
                "content": "As an error to message converter, your role is to explain the exact error in one line",
            },
            {
                "role": "user",
                "content": f"I will give you the error generated by the {language} code and the code , I want you to state that error into a feedback message and make sure to not miss any information in it.\nSo Error is {error},{language} code is {code} . Please add message to refactor the code at the end.Just give the error message in double quotes"
            },
        ]

        client = AzureOpenAI(
            azure_endpoint=config_class.AZURE_OPENAI_ENDPOINT,
            api_key=config_class.AZURE_OPENAI_API_KEY,
            api_version=config_class.AZURE_API_VERSION
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            max_tokens=4000,
            messages=conversation
        )
        return response.choices[0].message.content
    except Exception as e:
        data = {
            "error": error,
            "code": code
        }
        handle_exception("Error in error to msg python function", data, e, traceback.print_exc(), error_code=0)
