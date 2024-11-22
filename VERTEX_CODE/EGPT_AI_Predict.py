import json
import time
import uuid
import requests
import  traceback
from Enums.Enum_data import StatusCodes
from utils.AssistantUtils import AssistantConfig
from utils.utils import handle_exception
def get_predict_response(user_prompt, system_prompt, assistant_name):

    try:
        MAX_RETRIES = 2
        for _ in range(MAX_RETRIES):
            assistant_config = AssistantConfig(assistant_name)
            URL = "https://dev-84lumber-ai.techo.camp/predict"
            request_id = "requestId-" + str(uuid.uuid4())
            predict_payload = json.dumps({
                "conciergeId": "fc462861-5fd8-4224-ab95-1869639b421c",
                "conciergeName": assistant_name,
                "organizationId": "d73b4e26-10f0-4f57-8b11-5a6e33c632b1",
                "organizationName": "84lumber",
                "guestId": f"84lumber-{assistant_name}-49153af4-667a-4784-b671-62eda2106503",
                "userId": "52b1256d-3f84-4aac-83bd-1736fc5bcd11",
                "userName": "parinayseth",
                "assistant_type": "code_converter",
                "question": user_prompt,
                "prompt": system_prompt,
                "referenceDocsCount": 3,
                "proposals_file": "",
                "proposals_section": "",
                "images": {},
                "model_names": {
                    assistant_config.model_org: assistant_config.model_type
                },
                "confidenceScoreThreshold": 70,
                "chatHistory": [],
                "modelType": assistant_config.model_org,
                "pinecone_index": f"84lumber-{assistant_name}",
                "databaseType":assistant_config.databasetype,
                f"database_index": f"84lumber-{assistant_name}",
                "isCoPilotOn": True,
                "requestId": request_id,
                "chatLowConfidenceMessage": "Sorry we aren't able to help you with this question at this time. "
                                            "Contact us for further assistance.",
                "autoai": assistant_config.auto_ai,
                "documentRetrieval": assistant_config.documentRetrieval,
                "answerEvaluation": assistant_config.answerEvaluation,
                "bestAnswer": assistant_config.bestAnswer,
                "metadata": {
                    "userName": "parinayseth",
                    "userEmailId": "parinay.seth@techolution.com"
                },
                "source": assistant_config.source,
                "target": assistant_config.target,
                "evaluationCriteria": {},
                "isRESTrequest": False,
                "isStreamResponseOn": False,
                "isSpt":False
            })

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", URL, headers=headers, data=predict_payload)

            # print("response", response.text)
            if response.status_code == 200:
                print("AI-Response - ", response.text)
                response_text = json.loads(response.text)
                # print("AI-Response - ", response_text)
                response_extracted = response_text['Answer']
                if response_text:
                    return response_extracted
            
        return {
            "message": "Sorry, we aren't able to help you right now, try again after some time."}, StatusCodes.INTERNAL_SERVER_ERROR.value


    except Exception as e:
        handle_exception("Error while getting response from AI", {}, e, traceback.print_exc(),error_code=0)




def generate_response_claude35(system_prompt, chat_history, max_retries=5):
    """Generate a response using Claude 3.5 with retry logic.

    Args:
        system_prompt (str): The system prompt to send to the model.
        chat_history (list): A list of message dictionaries representing the conversation history.
        max_retries (int, optional): The maximum number of retry attempts. Defaults to 3.

    Returns:
        dict: The response from Claude 3.5, or an error dictionary in case of failure.
    """
    from anthropic import AnthropicVertex
    from config import PROJECT_ID
    import json
    import time  

    anthropic_client = AnthropicVertex(region="europe-west1", project_id=PROJECT_ID)
    attempt = 0
    delay = 2  

    while attempt < max_retries:
        try:
            # Claude API Call
            message = anthropic_client.messages.create(
                system=system_prompt,
                model="claude-3-5-sonnet@20240620",
                max_tokens=4096,
                temperature=0.2,
                messages=chat_history,
            )
            response = message.model_dump_json(indent=2)
            response_dictionary = json.loads(response)
            return response_dictionary['content'][0]['text']
        except Exception as e:
            attempt += 1
            print(f"Anthropic API Call Error (Attempt {attempt}): ", e)

            if attempt >= max_retries:
                print("Max retries reached. Returning error.")
                return {"error": f"Failed after {max_retries} attempts: {str(e)}"}

            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff



    
def calling_claude35(system_prompt, user_prompt):
    try:
        
        chat_history = []
        chat_history.append({"role": "user", "content": user_prompt})
        
        response = generate_response_claude35(system_prompt, chat_history)
        return response
    except Exception as e:
        return None
        
        
    
    
    
def longer_code_response(system_prompt, user_prompt, delimeters):
    try:
        original_user_prompt = user_prompt

        chat_history = []
        chat_history.append({"role": "user", "content": user_prompt})
        
        count = 0
        max_iterations = 20
        loop = True
        all_responses = []
        while loop and count < max_iterations:
            try:
        
                claude_response = generate_response_claude35(system_prompt, chat_history)
                print("claude_response: \n ", claude_response)
                
                if claude_response == "**Sorry from AI":
                        print("Delimeter not present in response")
                        user_prompt = original_user_prompt
                else:
                    # Append to chat_history
                    chat_history.append({
                        "role": "assistant",
                        "content": claude_response
                    })

                    all_responses.append(claude_response)

                    print("-" * 100)
                    
                    
                    time.sleep(3)

                    check = is_code_complete(claude_response, delimeters)
                    print("is_code_complete", check)

                    if check:
                        print("Code is complete")
                        loop = False
                    else:
                        print("Code is not complete")
                        
                        user_prompt = f"Continue modifying the code from the last complete line of code you generated previously, including the last two lines for context. Ensure there is an overlap with the previous output with the same indentation, but do not start with ```{delimeters}. When the entire code is migrated, make sure it ends with ```. When continuing the code, do not include any introductory or explanatory text; start directly with the code."
                        chat_history.append({"role": "user", "content": user_prompt})

                count += 1

            except KeyboardInterrupt:
                loop = False
                break
            
            
        # now generatation explanation call:
        try:
            chat_history.append({"role": "user", "content": "rovide short crisp bullet points explaining the changes done (provide line numbers or other references to make it easy for reviewers to cross-check the changes). Output Must in $$$summary$$$ delimiters"})
            claude_response = generate_response_claude35(system_prompt, chat_history)
            print("claude_response: \n ", claude_response)
            
            explanations = extract_explanation(claude_response)
            
        except Exception as e:
            print("Error while generating explanation", e)
            return None, StatusCodes.INTERNAL_SERVER_ERROR.value
            
            
            
            
            
        responses = store_code_responses(all_responses, delimeter=delimeters)
        # print(f"responess are (truncated) --------- {responses[:50]}")
        def combine_code_snippets(snippets):
            if len(snippets) == 1:
                return snippets[0]
            combined_code = snippets[0]

            for i in range(1, len(snippets)):
                combined_code = combine_two_snippets(combined_code, snippets[i])

            return combined_code

        def combine_two_snippets(first, second):
            first = first.rstrip()
            second = second.lstrip()

            max_overlap_len = min(len(first), len(second))

            for overlap_len in range(max_overlap_len, 0, -1):
                if first.endswith(second[:overlap_len]):
                    return first + second[overlap_len:]

            # No overlap found, concatenate directly
            return first + second
        

        combined_code = combine_code_snippets(responses)
        combined_code = check_code_ending(combined_code)

        
        print(f"Final code is \n {combined_code}")
        print(f"Final explanation is \n {explanations}")
        
        return combined_code, explanations,  StatusCodes.SUCCESS.value
    except Exception as e:
        handle_exception("Error while getting response from AI", {}, e, traceback.print_exc(),error_code=0)
        return None, StatusCodes.INTERNAL_SERVER_ERROR.value


# def is_code_complete(output, delimeter):
#     """
#     Checks if both the code section and summary are complete, handling multi-part responses.
#     Code delimiters: ```python (start) and ``` (end)
#     Summary delimiters: $$$summary (start) and $$$ (end)
    
#     Also handles the case where only summary end is present, indicating
#     code was completed earlier and summary is now complete.
#     """
#     code_start =f"```{delimeter}"
#     code_end = "```"
#     has_code_start = code_start in output
#     has_code_end = code_end in output.split(code_start)[-1] if has_code_start else False

#     summary_start = "$$$summary"
#     summary_end = "$$$"
#     has_summary_start = summary_start in output
#     has_summary_end = summary_end in output.split(summary_start)[-1] if has_summary_start else False

#     # Case 1: Both code and summary are complete in this part
#     if has_code_start and has_code_end and has_summary_start and has_summary_end:
#         return True

#     # Case 2: Only summary end is present, indicating code was completed earlier
#     # and summary is now complete
#     if not has_code_start and not has_code_end and not has_summary_start and has_summary_end:
#         return True

#     if not code_end and has_summary_start and has_summary_end:
#         return True
    
#     return False




# def store_code_responses(responses, delimeter):
#     """
#     Processes each response, stores the code in an array, and extracts explanations marked by $$$summary and $$$.
#     """
#     stored_code = []
#     explanations = []
#     current_code = []
    
#     for response in responses:
#         # Extract code
#         code_start = response.find(f'```{delimeter}')
#         if code_start != -1:
#             code_end = response.find('```', code_start + len(f'```{delimeter}'))
#             if code_end != -1:
#                 code = response[code_start + len(f'```{delimeter}'):code_end].strip()
#                 stored_code.append(code)
#             else:
#                 current_code.append(response[code_start + len(f'```{delimeter}'):].strip())
#         elif current_code:
#             code_end = response.find('```')
#             if code_end != -1:
#                 current_code.append(response[:code_end].strip())
#                 stored_code.append('\n'.join(current_code))
#                 current_code = []
#             else:
#                 current_code.append(response.strip())
        
#         # Extract explanation
#         explanation_start = response.find('$$$summary')
#         if explanation_start != -1:
#             explanation_end = response.find('$$$', explanation_start + 10)
#             if explanation_end != -1:
#                 explanation = response[explanation_start + 10:explanation_end].strip()
#                 explanations.append(explanation)
    
#     if current_code:
#         stored_code.append('\n'.join(current_code))
    
#     return stored_code, "\n".join(explanations)


def is_code_complete(output, delimeter="python"):
    """
    Checks if the upgraded code section is complete based on the presence of the summary indicator $$$.
    """
    print("delimeter--------- here", delimeter)
    has_code_start = f'```{delimeter}' in output
    has_code_end = '```' in output.split(f'```{delimeter}')[-1] if has_code_start else False
    has_summary = '$$$' in output
    
    return (has_code_start and has_code_end) or has_summary


def store_code_responses(responses, delimeter):
    """
    Processes each response and stores the code in an array based on the specified logic.
    """
    stored_code = []
    first_response = True

    for response in responses:
        if first_response:
            first_response = False
            if is_code_complete(response, delimeter=delimeter):
                # Store code between "```c" and "```"
                start_index = response.find(f'```{delimeter}') + len(f'```{delimeter}')
                end_index = response.find('```', start_index)
                stored_code.append(response[start_index:end_index].strip())
            else:
                # Store code after "```c"
                start_index = response.find(f'```{delimeter}') + len(f'```{delimeter}')
                stored_code.append(response[start_index:].strip())
        else:
            if is_code_complete(response, delimeter=delimeter):
                # Store code before delimiter "```"
                end_index = response.find('```')
                stored_code.append(response[:end_index].strip())
            else:
                # Store the whole content
                stored_code.append(response.strip())
    
    return stored_code


def extract_explanation(response):
    """
    Extracts the explanation from the response based on the presence of the summary indicator $$$.
    """
    explanation_start = response.find('$$$summary')
    if explanation_start != -1:
        explanation_end = response.find('$$$', explanation_start + 10)
        if explanation_end != -1:
            explanation = response[explanation_start + 10:explanation_end].strip()
            return explanation
    return ""

def check_code_ending(code):
    if code.endswith("```"):
        code = code[:-3]
    return code
