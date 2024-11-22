"""docstring"""
import traceback
import base64

from flask import Blueprint, request, make_response
from flask_restx import Api, Resource, fields

from HelperClasses.main import project_mapping
from Enums.Enum_data import StatusCodes
from core_apis.payload import process_payload
from utils.utils import handle_exception

api = Api()

# Create a blueprint for your API routes
name = Blueprint('name', __name__, url_prefix='/name')
name_api = Api(name, version="1.0", title="name", description="Description of the project")
namens = name_api.namespace('name', description='Description of the namespace')

nested_model = api.model('NestedModel', {
    'nested_field': fields.String(description='Nested Field'),
})
main_model = api.model('MainModel', {
    'field1': fields.String(description='Field 1'),
    'nested': fields.Nested(nested_model),
})


@namens.route('/git_pr_refactor_unittest')
class New(Resource):
    """
    NewResource class for handling HTTP requests.
    """

    # @name_api.expect(main_model, validate=True)
    def post(self):
        """
        Handle POST request.
        Returns:
            Response object: Response to the client.
        """
        try:
            json_payload = request.get_json()
            pat = request.headers.get("Authorization")
            flow = request.headers.get("Flow")
            # repo_name = request.headers.get("Repo")
            project_name = request.headers.get("project").lower()
            organization = request.headers.get("organization")
            read_me = request.headers.get("readme", "False")

            data = {}
            pat = pat.replace("Basic ", "")
            decoded_token = base64.b64decode(pat).decode('utf-8')
            decoded_token = decoded_token.replace(":", "")

            print(f"Flow: {flow}, Project: {project_name}, Organization: {organization}, PAT: {decoded_token}")
            if flow == "normal":
                commit_id = json_payload['head']['sha']
                branch_name = json_payload["head"]["ref"]
                repo_name = json_payload["head"]["repo"]["name"]
                user_name = json_payload["user"]["login"]
                commit_message = json_payload['body'] if 'body' in json_payload and json_payload['body'] else json_payload['title'] if 'title' in json_payload else ""
                default_branch = json_payload['base']['ref']
                pull_request_number = json_payload['number']

                data["pat"] = decoded_token
                data["repo_name"] = repo_name
                data["branch"] = branch_name
                data["commit id"] = commit_id
                data["commit msg"] = commit_message
                data["organization"] = organization
                data["user_name"] = user_name
                data["default_branch"] = default_branch
                data['pull_request_number'] = pull_request_number
                data['readme'] = read_me
            elif flow == "feedback":
                processed_payload = process_payload(json_payload, decoded_token, organization)
                data["pat"] = decoded_token
                data["repo_name"] = processed_payload['repo_name']
                data['source_branch'] = processed_payload['source_branch']
                data['ai_branch'] = processed_payload['ai_branch']
                data["feedback"] = processed_payload['feedback']
                data["organization"] = organization

                print("data got", data)
            print("data", data)
            # input()

            return project_mapping[project_name](data, flow)
        except Exception as e:
            data_msg = {"json data": data}
            handle_exception("Error while getting data from json input", data_msg, e, traceback.print_exc(),
                             error_code=0)
            return make_response({"status": "FAILED", "status message": str(e)},
                                 StatusCodes.INTERNAL_SERVER_ERROR.value)


@namens.route("/js_long_code_refactor_later")
class longCodeRefactorJS(Resource):
    """
    """

    def post(self):
        """
        """
        try:
            json_payload = request.get_json()
            pat = request.headers.get("Authorization")

            
            pat = pat.replace("Basic ", "")
            decoded_token = base64.b64decode(pat).decode('utf-8')
            decoded_token = decoded_token.replace(":", "")

            data = {}
            data["pat"] = decoded_token
            data["branch"] = json_payload.get("branch")
            data["repo_name"] = json_payload.get("repo name")
            data["refactored code"] = json_payload.get("refactored code")
            data["organization"] = json_payload.get("organization")
            project_name = json_payload.get("project name").lower()

            print(data)

            if not all(value for value in data.values()):
                return make_response({"status": "failed", "msg": "Please provide all the parameters and headers while calling API"},
                                      StatusCodes.WRONG_PAYLOAD_DATA.value)
            else:
                return project_mapping[project_name](data, flow="long_code_refactor")

        except Exception as e:
            data_msg = {"json data": data}
            handle_exception("Error while getting data from json input in long code refactoring in js", 
                             data_msg, e, traceback.print_exc(), error_code=0)
            return make_response({"status": "FAILED", "status message": str(e)},
                                 StatusCodes.INTERNAL_SERVER_ERROR.value)

from Languages.C import fun
@namens.route("/sample")
class longCodeRefactorJS(Resource):
    """
    """
    def post(self):
        fun()
        return make_response({"status": "success"}, StatusCodes.SUCCESS.value)
