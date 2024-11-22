import logging
import os
import re
import json
import traceback
import requests

from openai.lib.azure import AzureOpenAI

import config
import base64
from VERTEX_CODE.EGPT_AI_Predict import calling_claude35, get_predict_response, longer_code_response
from VERTEX_CODE.prompt_storage import get_difference_explanation_prompts, get_feedback_refactor_prompts, get_predictAPI_prompt, get_test_cases_prompt, typescript_prompts
from utils.utils import num_tokens_from_string, handle_exception, get_coding_standards
from VERTEX_CODE.EGPT_AI import stream_inference
from Enums.Enum_data import StatusCodes
from config import JavascriptConfig

from anthropic import AnthropicVertex



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')


def refactor_code_improved(original_code, changes):
    try:
        print(f"Suggestions: {changes}")
        # Split the original code into lines for easier processing
        lines = original_code.split('\n')

        # Apply each change
        for change in changes:
            for original, updated in change.items():
                # Replace or remove lines that exactly match the key
                lines = [updated if line.strip() == original.strip() else line for line in lines]

        # Remove any potential empty lines left after removals
        lines = [line for line in lines if line.strip() != ""]

        # Join the lines back into a single string
        refactored_code = '\n'.join(lines)
        print("Refactored Code", refactored_code)
        return refactored_code
    except Exception as e:
        data = {
            "original code (truncated)": original_code[:20],
            "changes": changes
        }
        handle_exception("Error while authorizing github user", data, e, traceback.print_exc(), error_code=0)


def apply_diff(original_code, diff):
    """
    Applies diff changes to the original code.
    Parameters:
    - original_code: A string containing the original code.
    - diff: A JSON-like dictionary containing the diff changes.
    Returns:
    - A string representing the new code after applying the diff changes.
    """
    try:
        # Split the original code into a list of lines
        lines = original_code.split('\n')
        print('lines took')

        # Apply removals
        for change in diff['changes']:
            # Since we're directly modifying the list, calculate adjustments for line numbers
            adjustment = 0
            for line_number in change['removed']:
                # Convert string line numbers to integers and adjust for previous deletions
                real_line_number = int(line_number) - 1 - adjustment
                if 0 <= real_line_number < len(lines):
                    del lines[real_line_number]
                    adjustment += 1
        print('removal done')
        # Apply additions
        for change in diff['changes']:
            for line_number, content in sorted(change['added'].items(), key=lambda x: int(x[0])):
                # Insert new lines at the specified positions
                real_line_number = int(line_number) - 1
                if real_line_number >= len(lines):
                    # If the line number exceeds the length, append to the end
                    lines.append(content)
                else:
                    lines.insert(real_line_number, content)
        print('addition done')
        # Join the lines back into a single string
        new_code = '\n'.join(lines)
        return new_code
    except Exception as e:
        data = {
            "original code (truncated)": original_code[:20],
            "difference": diff
        }
        handle_exception("Error while refactoring for big file using diff", data, e, traceback.print_exc(),
                         error_code=0)


# def perform_refactoring(file_path):
#     MAX_RETRIES = 2
#     try:
#         with open(file_path, 'r', encoding='utf-8-sig') as file:
#             code = file.read()
#         total_input_tokens = num_tokens_from_string(code, "cl100k_base")
#         # insted of line we need to check for tokens and get more than 3500 tokens
#         if total_input_tokens >= 3500:
#             print(f'Token Count is {total_input_tokens}')
#             with open(file_path, "r", encoding='utf-8-sig') as file:
#                 code_content = file.read()
#             lines = code_content.split('\n')
#             lines_with_numbers = []
#             for i in range(len(lines)):
#                 lines_with_numbers.append(f"{i + 1} {lines[i]}")
#             code_with_line_num = '\n'.join(lines_with_numbers)

#             # print('code content here', code_with_line_num)
#             # print('code content', code_content)
#             for _ in range(MAX_RETRIES):
#                 egpt_resp = stream_inference(code_with_line_num, 'csharpchunk')
#                 # print('egpt_ res', egpt_resp)
#                 if egpt_resp:
#                     text_response = egpt_resp
#                     # print("Received text response from stream_inference:", text_response)
#                     if  '```json' not in text_response:
#                         print("JSON not found in the text response.")
#                         #return code_content, 200
#                         continue

#                     json_code_start = '```json'
#                     json_code_end = '```'
#                     start_index = text_response.find(json_code_start) + len(json_code_start)
#                     end_index = text_response.find(json_code_end, start_index)

#                     if start_index == -1 or end_index == -1:
#                         print("JSON code block not found in the text response.")
#                         # return "JSON code block not found in response."
#                         continue

#                     json_response = text_response[start_index:end_index].strip()
#                     print("Extracted JSON response from text:", json_response)

#                     try:
#                         changes_array = json.loads(json_response)
#                     except json.JSONDecodeError:
#                         print("Error decoding JSON response.")
#                         # return "Error decoding JSON response."
#                         continue

#                     # print("Parsed JSON into Changes Array:", changes_array)

#                     updated_code = apply_diff(code_content, changes_array)
#                     print("Applied differences to code.",updated_code)
#                     return updated_code, StatusCodes.SUCCESS.value
#             # else:
#             #     return {"message": "Sorry, we aren't able to help you right now, try again after some time."}, 400
#         else:
#             print('less than 600')
#             with open(file_path, "r", encoding='utf-8-sig') as file:
#                 code_content = file.read()
#             # print('code cintn', code_content)
#             lines = code_content.split('\n')
#             lines_with_numbers = []
#             for i in range(len(lines)):
#                 lines_with_numbers.append(f"{i + 1} {lines[i]}")
#             code_with_line_num = '\n'.join(lines_with_numbers)

#             # print('code content with line number : \n\n')
#             # print(code_with_line_num)

#             for _ in range(MAX_RETRIES):
#                 egpt_resp = stream_inference(code_with_line_num)
#                 if egpt_resp:
#                     extracted_code_match = re.search(r'```csharp([\s\S]+?)```', egpt_resp)
#                     if extracted_code_match:
#                         generated_code = extracted_code_match.group(1)
#                         print("Extracted", generated_code)
#                         return generated_code, StatusCodes.SUCCESS.value

#         if egpt_resp:
#             print("egpt-response",egpt_resp)
#             return {"message":egpt_resp}, StatusCodes.NO_WORK_REQUIRED.value
#         else:
#             return {"message": "Sorry, we aren't able to help you right now, try again after some time."}, StatusCodes.EMPTY_RESPONSE
#     except Exception as e:
#         # TODO add exceptional handling
#         return {"message": str(e)}, StatusCodes.INTERNAL_SERVER_ERROR.value



# def fun(code_content, file_path):
#     payload = {
#             "branch": "harshit-testing-2",
#             "repo name": "fo-auto-ai-backend",
#             "code to refactor": [
#                 {
#                     "code": code_content,
#                     "file path": file_path,
#                 }
#             ],
#             "organization": "Techolution",
#             "project name": "javascript",
#             "Authorization": base64.b64encode(JavascriptConfig.TOKEN.encode()).decode(),
#             "codeRefactorTokenLimit": 1500
#         }

#     print("payload", payload)

#     response = requests.post(JavascriptConfig.LONG_CODE_REFACTOR_API,
#                                      headers = {'Content-Type': 'application/json'},
#                                      data=json.dumps(payload))
#     print("response frmo APi\n", response.text)
#     print(response.status_code)
#     return response.text, response.status_code


def long_code_refactor():
    data = None

    def store_data(my_data):
        nonlocal data
        data = my_data
    
    def rlef_api_call(branch, code_content, file_path, auth_token, code_refactor_token_limit):

        print("See i have this data", data)
        payload = {
            "branch": branch,
            "repo name": data["repo_name"],
            "code to refactor": [
                {
                    "code": code_content,
                    "file path": file_path,
                }
            ],
            "organization": data["organization"],
            "project name": "javascript",
            "Authorization": base64.b64encode(auth_token.encode()).decode(),
            "codeRefactorTokenLimit": code_refactor_token_limit
        }

        print("payload", payload)

        response = requests.post(JavascriptConfig.LONG_CODE_REFACTOR_API,
                                        headers = {'Content-Type': 'application/json'},
                                        data=json.dumps(payload))
        print("response frmo APi\n", response.text)
        print(response.status_code)
        return response.text, response.status_code

        

        # async with aiohttp.ClientSession() as session:
        #     async with session.post(JavascriptConfig.LONG_CODE_REFACTOR_API,
        #                             headers = {'Content-Type': 'application/json'},
        #                              data=json.dumps(payload)) as response:
        #         return await response.text(), response.status

    long_code_refactor.store_data = store_data
    long_code_refactor.rlef_api_call = rlef_api_call

long_code_refactor() # intentionaly calling function



# def long_code_refactor(data, code_content, file_path, auth_token, code_reafactor_token_limit):
#     payload = {
#         "branch": data["branch"],
#         "repo name": data["repo_name"],
#         "code to refactor": [
#             {
#                 "code": code_content,
#                 "file path": file_path,
#             }
#         ],
#         "organization": data["organization"],
#         "project name": "javascript",
#         "Authorization": base64.b64encode(auth_token.encode()),
#         "codeRefactorTokenLimit": code_reafactor_token_limit
#     }
#     print(payload)

#     res = requests.post(JavascriptConfig.LONG_CODE_REFACTOR_API, data=payload)


#     print("the res that I got")
#     print(res)
#     print(res.status_code)

#     input()


#     if res.status_code == StatusCodes.SUCCESS.value:
#         json_output = res.json()
#         return {"status": "succes"}, StatusCodes.SKIP_PIPELINE.value
#     else:
#         return code_content, StatusCodes.EMPTY_RESPONSE.value


def perform_refactoring(data, file_path, assistant_name, approach="whole file",
                        changed_content="", file_extension=""):  # TODO : make this function generalized and remove un-necessary repetitive code
    MAX_RETRIES = 2
    try:
        repo_name = data["repo_name"]
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            code_content = file.read()
        egpt_resp = ""

        total_input_tokens = num_tokens_from_string(code_content, "cl100k_base")
        print("Tokens", total_input_tokens)
        lines = code_content.split('\n')
        lines_with_numbers = []
        for i in range(len(lines)):
            lines_with_numbers.append(f"{i + 1} {lines[i]}")
        code_with_line_num = '\n'.join(lines_with_numbers)
        user_coding_standards = get_coding_standards(repo_name)
        # print("Coding standards ====", user_coding_standards)
        print("file path", file_path)
        
        
        if file_extension == ".ts" or file_extension == ".tsx":
            updated_code, explanations_str, status_code =  longer_code_direct_call(changed_content, approach, total_input_tokens, code_with_line_num, user_coding_standards, assistant_name)    
            
            return updated_code, explanations_str, status_code

            
        if total_input_tokens >= 8000 or file_path=="BackendService\logger.js" or file_path=="BackendService/logger.js":
            if file_extension==".js":
                print("yeah going here")
                long_code_refactor.store_data(data)
                return "", "", StatusCodes.ACCEPTED.value
            else:
                for _ in range(MAX_RETRIES):
                    assistant = assistant_name[1]
                    prompt = f"""Original Code: \n    
                                    {code_with_line_num}
                                

                                    Changed Part: \n
                                    {changed_content}
                                    """
                    # print("Code",code_with_line_num)
                    # egpt_resp = stream_inference(code_with_line_num, temp)
                    system_prompt, user_prompt = get_predictAPI_prompt(assistant, prompt, user_coding_standards)
                    egpt_resp = calling_claude35(user_prompt=user_prompt, system_prompt=system_prompt)
                    if egpt_resp:
                        text_response = egpt_resp
                        # print("Received text response from stream_inference:", text_response)
                        if '```json' not in text_response:
                            print("JSON not found in the text response.")
                            # return code_content, 200
                            continue

                        json_code_start = '```json'
                        json_code_end = '```'
                        start_index = text_response.find(json_code_start) + len(json_code_start)
                        end_index = text_response.find(json_code_end, start_index)

                        if start_index == -1 or end_index == -1:
                            print("JSON code block not found in the text response.")
                            # return "JSON code block not found in response."
                            continue

                        json_response = text_response[start_index:end_index].strip()
                        # print("Extracted JSON response from text:", json_response)

                        try:
                            changes_array = json.loads(json_response)
                        except json.JSONDecodeError:
                            print("Error decoding JSON response.")
                            # return "Error decoding JSON response."
                            continue

                        # print("Parsed JSON into Changes Array:", changes_array)

                        updated_code = refactor_code_improved(code_content, changes_array)
                        # print("Applied differences to code.",updated_code)
                        return updated_code, "", StatusCodes.SUCCESS.value
        else:
            if approach == "changed content":
                print("Reached Changed Content")
                prompt = f"""Original Code: \n    
                                                {code_with_line_num}
                                                Changed Part: \n
                                                {changed_content}
                                                """
                print("Prompts Generated")
                # print(prompt)
                assistant = assistant_name[2]
                print("Assistant Received --- ",assistant)

                system_prompt, user_prompt = get_predictAPI_prompt(assistant_name=assistant, original_code=prompt, coding_standards=user_coding_standards)

                # print("System Prompt ---", system_prompt, "\n", "User_Prompt --- ", user_prompt)
                # egpt_resp = get_predict_response(user_prompt=user_prompt, system_prompt=system_prompt, assistant_name=assistant)
                egpt_resp = calling_claude35(user_prompt=user_prompt, system_prompt=system_prompt)
                print("EGPT Response --- ", egpt_resp)
                
                # egpt_resp = stream_inference(prompt, assistant)
                if egpt_resp:
                    extracted_code_match = re.search(r'```refactored([\s\S]+?)```', egpt_resp)
                    if extracted_code_match:
                        generated_code = extracted_code_match.group(1)
                        
                        
                        try:
                            changes_array = json.loads(generated_code)
                        except json.JSONDecodeError:
                            print("Error decoding JSON response.")
                            # return "Error decoding JSON response."
                        

                        # print("Parsed JSON into Changes Array:", changes_array)

                        updated_code = refactor_code_improved(code_content, changes_array)
                        
                        return updated_code,"", StatusCodes.SUCCESS.value
            else:
                print("Applying General Refactoring")
                for _ in range(MAX_RETRIES):
                    assistant = assistant_name[0]
                    system_prompt, user_prompt = get_predictAPI_prompt(assistant_name=assistant, original_code=code_with_line_num, coding_standards=user_coding_standards)
                    if file_extension == ".ts" or file_extension == ".tsx":
                        updated_code, status_code = longer_code_direct_call(system_prompt, user_prompt)
                        return updated_code, StatusCodes.SUCCESS.value
                    egpt_resp = calling_claude35(user_prompt=user_prompt, system_prompt=system_prompt)
                    print("EGPT Response --- ", egpt_resp)
                    # egpt_resp = stream_inference(code_with_line_num, assistant_name[0])
                    if egpt_resp:
                        # extracted_code_match = re.search(r'```python([\s\S]+?)```', egpt_resp)
                        extracted_code_match = re.search(r'```refactored([\s\S]+?)```', egpt_resp)
                        if extracted_code_match:
                            generated_code = extracted_code_match.group(1)
                            # print("Extracted", generated_code)
                            return generated_code, "", StatusCodes.SUCCESS.value

        if egpt_resp:
            return egpt_resp, "",  StatusCodes.NO_WORK_REQUIRED.value
        else:
            return {
                "message": "Sorry, we aren't able to help you right now, try again after some time."}, "" ,StatusCodes.EMPTY_RESPONSE.value

    except Exception as e:
        data = {
            "file_path": file_path,
            "assistant_name": assistant_name
        }
        handle_exception("Error while performing refactoring", data, e, traceback.print_exc(), error_code=0)


def generate_unit_test(file_path, assistant_name):
    MAX_RETRIES = 2
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            code_content = file.read()
        lines = code_content.split('\n')
        lines_with_numbers = []
        for i in range(len(lines)):
            lines_with_numbers.append(f"{i + 1} {lines[i]}")
        code_with_line_num = '\n'.join(lines_with_numbers)
        filename = os.path.basename(file_path)
        prompt = f"{code_content}"

        for _ in range(MAX_RETRIES):
            system_prompt = get_test_cases_prompt(asssistant_name=assistant_name)
            egpt_resp = calling_claude35(user_prompt=prompt, system_prompt=system_prompt)
            if egpt_resp:
                extracted_code_match = re.search(r'```unittest([\s\S]+?)```', egpt_resp)
                if extracted_code_match:
                    generated_code = extracted_code_match.group(1)
                    # print("Extracted", generated_code)
                    return generated_code, StatusCodes.SUCCESS.value

        if egpt_resp:
            return egpt_resp, StatusCodes.NO_WORK_REQUIRED.value

        else:
            return {
                "message": "Sorry, we aren't able to help you right now, try again after some time."}, StatusCodes.EMPTY_RESPONSE.value

    except Exception as e:
        data = {
            "file_path": file_path,
            "assistant_name": assistant_name
        }
        handle_exception("Error while generating unit test case", data, e, traceback.print_exc(), error_code=0)


def feedback_refactor(original_code, refactored_code, feedback, file_extention):
    # print("AI Code ", refactored_code)
    # LOCATION = "us-central1"  # or "europe-west4"
    # client = AnthropicVertex(region=LOCATION, project_id="lumbar-poc")

    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Parinay Seth\Desktop\Sylvan\refactor_sylvan\sylvan-backend\VERTEX_CODE\credentials.json"

    try:
        system_prompt = get_feedback_refactor_prompts(file_extention)
        conversation = f""" Original Code: \n {original_code} \n
                        Initial Refactored Code: \n  {refactored_code}
                        User Feedback: \n {feedback}"""
        MAX_RETRIES = 2
        for _ in range(MAX_RETRIES):
            # message = client.messages.create(
            #     system=system_prompt,
            #     model="claude-3-haiku@20240307",
            #     max_tokens=4096,
            #     temperature=0.0,
            #     messages=messages,
            # )
            # response = message.model_dump_json(indent=2)
            # response_dictionary = json.loads(response)

            URL = "https://dev-84lumber-ai.techo.camp/predict"

            predict_payload = json.dumps({
                "conciergeId": "fc462861-5fd8-4224-ab95-1869639b421c",
                "conciergeName": "generalcoderefactor",
                "organizationId": "d73b4e26-10f0-4f57-8b11-5a6e33c632b1",
                "organizationName": "84lumber",
                "guestId": "84lumber-generalcoderefactor-49153af4-667a-4784-b671-62eda2106503",
                "userId": "52b1256d-3f84-4aac-83bd-1736fc5bcd11",
                "userName": "parinayseth",
                "assistant_type": "code_converter",
                "question": conversation,
                "prompt": system_prompt,
                "referenceDocsCount": 3,
                "proposals_file": "",
                "proposals_section": "",
                "images": {},
                "model_names": {
                    "openai": "gpt-4-128k"
                },
                "confidenceScoreThreshold": 70,
                "chatHistory": [],
                "modelType": "openai",
                "pinecone_index": "84lumber-generalcoderefactor",
                "databaseType": "pinecone",
                "database_index": "84lumber-generalcoderefactor",
                "isCoPilotOn": True,
                "requestId": "requestId-2d5cf342-58fd-499b-973f-0376f6905c53",
                "chatLowConfidenceMessage": "Sorry we aren't able to help you with this question at this time. "
                                            "Contact us for further assistance.",
                "autoai": "65e5d428f82eb8a5e577e580",
                "documentRetrieval": "65e5d428f82eb84bd177e551",
                "answerEvaluation": "65e5d428f82eb8556577e55e",
                "bestAnswer": "65e5d428f82eb8441777e56f",
                "metadata": {
                    "userName": "parinayseth",
                    "userEmailId": "parinay.seth@techolution.com"
                },
                "source": "",
                "target": "",
                "evaluationCriteria": {},
                "isRESTrequest": False
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", URL, headers=headers, data=predict_payload)
            # print("response", response.text)
            if response.status_code == 200:
                response_text = json.loads(response.text)
                # print("AI-Response - ", response_text)
                response_extracted = response_text['Answer']
                if response_text:
                    code_start_point = "```refactored"
                    code_end_point = "```"
                    start_index = response_extracted.find(code_start_point) + len(code_start_point)
                    end_index = response_extracted.find(code_end_point, start_index)
                    if start_index != -1 and end_index != -1:
                        updated_code = response_extracted[start_index:end_index].strip()
                        # print("Extracted Code - ", updated_code)
                        return updated_code, StatusCodes.SUCCESS.value
            else:
                print("response", response.text)
        return {
            "message": "Sorry, we aren't able to help you right now, try again after some time."}, StatusCodes.INTERNAL_SERVER_ERROR.value


    except Exception as e:
        data = {
            "file_path": "file_path",
        }
        handle_exception("Error while refactoring code in feedback pipeline", data, e, traceback.print_exc(),
                         error_code=0)



def longer_code_direct_call(changed_content, approach, tokens, code_with_line_num, user_coding_standards, assistant_name):
    print("Typescript Longer Code Direct Call")
    # if approach == "changed content":
    #     prompt = f"""Original Code: \n {code_with_line_num} \n Changed Part: \ {changed_content}"""
    #     # print(prompt)
    #     assistant = assistant_name[1]
    #     print("Assistant Received --- ",assistant)
    #     system_prompt, user_prompt = typescript_prompts(assistant_name=assistant, original_code=prompt, coding_standards=user_coding_standards, )
    #     delimeters = ""
    # else:
    print(f"Appling General Refactoring for {tokens} input tokens file")
    assistant = assistant_name[0]
    print("Assistant Received --- ",assistant)
    if assistant_name == "generalcoderefactor":
        system_prompt, user_prompt = typescript_prompts(assistant_name=assistant, original_code=code_with_line_num, coding_standards=user_coding_standards)
    system_prompt, user_prompt = typescript_prompts(assistant_name=assistant, original_code=code_with_line_num, coding_standards=user_coding_standards)
    delimeters = "refactored"
    refactored_code, explanations_str, status_code = longer_code_response(system_prompt, user_prompt, delimeters)
    print("Refactored Code Generated")
    return refactored_code, explanations_str, status_code
        
        
        
        
def get_differnce_explanation(code_difference: str, path: str):
    try:
        
        logging.info("Getting Difference Explanation")
        
        with open(path, 'r', encoding='utf-8-sig') as file:
            original_code = file.read().splitlines()
        
        
        system_prompt, user_prompt = get_difference_explanation_prompts(original_code, code_difference)
        response = calling_claude35(user_prompt=user_prompt, system_prompt=system_prompt)
        logging.info("Response from EGPT AI")
        logging.info(response)
        if response:
            extracted_code_match = re.search(r'```json([\s\S]+?)```', response)
            if extracted_code_match:
                generated_code = extracted_code_match.group(1)
                generat_code_json = json.loads(generated_code)
                logging.info(f"Extracted Code - {generat_code_json}")
                logging.info(f"Data Type - {type(generat_code_json)}") 
                return generat_code_json, StatusCodes.SUCCESS.value
        
        return {
            "message": "Sorry, we aren't able to help you right now, try again after some time."}, StatusCodes.EMPTY_RESPONSE.value
    except Exception as e:
        data = {
            "file_path": path,
        }
        handle_exception("Error while getting difference explanation", data, e, traceback.print_exc(),
                         error_code=0)
        
        
        
        
            
            