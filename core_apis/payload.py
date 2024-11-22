import requests
def process_payload(payload, token, organization):
    processed_json = {}
    print("Payload provided \n ", payload)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if organization == "techolution":
        print("Pull Request: ", payload['pull_request']['url'])
        pull_req_url = payload['pull_request']['url']
        comments_url = payload['pull_request']['url'] + "/comments"
    else:
        print("Pull Request: ", payload['pull_request_url'])
        pull_req_url = payload['pull_request_url']
        comments_url = payload['pull_request_url'] + "/comments"
    pr_response = requests.get(pull_req_url, headers=headers)
    pr_data = pr_response.json()

    comments_response = requests.get(comments_url, headers=headers)
    comments_data = comments_response.json()

    feedback = {}
    for comment in comments_data:
        path = comment["path"]
        body = comment["body"]
        line = comment["line"]

        if path not in feedback:
            feedback[path] = {}

        feedback[path][body] = str(line)

    feedback = [feedback]

    processed_json['repo_name'] = pr_data['head']['repo']['name']
    processed_json['source_branch'] = pr_data['base']['ref']
    processed_json['ai_branch'] = pr_data['head']['ref']
    processed_json['feedback'] = feedback

    print("Processed Json", processed_json)

    return processed_json