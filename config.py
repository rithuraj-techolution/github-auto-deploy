import json
import os
import traceback

import google
from google.cloud import secretmanager_v1

from utils.utils import handle_exception

env = os.environ.get('ENV', 'dev')
# PROJECT_ID = os.environ.get('PROJECT_ID')
PROJECT_ID = "lumbar-poc"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/rithurajnambiar/Documents/demo-setup/credentials.json"
#for local env
# PROJECT_ID = 'sylvan-dev'


# EGPT URLs
POST_URL = "https://dev-84lumber-ai.techo.camp/api/chat/streamResponsePost"
GET_URL = "https://dev-84lumber-ai.techo.camp/api/chat/streamResponseGet"
REFACTOR_FUNC_NAME = "csharpcoderefactorer"
UNITTEST_FUNC_NAME = "charpmstest"


# Compiler URLs
COMPILER_UPLOAD_FILE = "https://dev-appmod.techo.camp/compiler/upload_code"
COMPILER_RUN_COMMAND = "https://dev-appmod.techo.camp/compiler/run_cmd_on_compiler"




# MAIN Egpt configeration
# "For main refactoring: -> csharprefactor
# (https://sylvan-ai.techo.camp/dashboard?name=csharprefactor&organizationName=sylvan&tabIndex=0)"
# "For mainUnit Test cases -> csharptestcase
# (https://sylvan-ai.techo.camp/dashboard?name=csharptestcase&organizationName=sylvan&tabIndex=0)"

# POST_URL = "https://sylvan-ai.techo.camp/api/chat/streamResponsePost"
# GET_URL = "https://sylvan-ai.techo.camp/api/chat/streamResponseGet"
# REFACTOR_FUNC_NAME = "csharprefactor"
# UNITTEST_FUNC_NAME = "csharptestcase"


def get_secret_value(secret_name: str):
    """
    Getting values from cloud secret manager
    Args:
        secret_name (str): The name of the secret.
    Returns:
        str: The secret value.
    """
    return ""
    client = secretmanager_v1.SecretManagerServiceClient()
    secret_name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    try:
        response = client.access_secret_version(request={"name": secret_name})
        secret_value = response.payload.data.decode("UTF-8")
        return secret_value
    except google.api_core.exceptions.PermissionDenied as e:
        data = {"secret name": secret_name}
        handle_exception("Permission denied while accessing secret", data, e, traceback.print_exc())
        return None
    except google.api_core.exceptions.DeadlineExceeded as e:
        data = {"secret name": secret_name}
        handle_exception("Deadline exceeded while accessing secret", data, e, traceback.print_exc())
        return None
    except google.api_core.exceptions.GoogleAPICallError as e:
        data = {"secret name": secret_name}
        handle_exception("Error making API call to Secret Manager", data, e, traceback.print_exc())
        return None
    except Exception as e:
        data = {"secret name": secret_name}
        handle_exception("Unexpected error occured while getting data from secret manager", data, e, traceback.print_exc())
        return None

class CConfig:
    """
    C configuration class.
    """
    TOKEN = ""
    REPO_NAME = ''
    BASE_PATH = f'D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{REPO_NAME}'
    AUTH_URL = ""
    GIT_USERNAME = "harshit-rathore3"
    GIT_EMAIL = "harshit.rathore@techolution.com"
    ORGANIZATION = ""
    FILE_EXTENSIONS = [".c"]


    @classmethod
    def set_creds(cls, repo_name: str, token: str, organization: str) -> None:
        """
        Set credentials.
        Args:
            repo_name (str): The name of the repository.
        """
        cls.REPO_NAME = repo_name
        cls.BASE_PATH = f'D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{repo_name}'
        cls.ORGANIZATION = organization
        cls.TOKEN = token
        cls.GIT_CLONE_URLS = [f"https://{cls.TOKEN}@github.com/{organization}/{repo_name}.git"]


    AZURE_API_TYPE = "azure"
    AZURE_API_BASE="https://wu-oai-appmod.openai.azure.com/"
    AZURE_API_VERSION="2023-05-15"
    AZURE_OPENAI_API_KEY="ad60d67257f8435f905039712b0cd748"
    AZURE_OPENAI_ENDPOINT="https://wu-oai-appmod.openai.azure.com/"


class PythonConfig:
    """
    Python configuration class.
    """
    TOKEN = ""
    REPO_NAME = ''
    BASE_PATH = f'D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{REPO_NAME}'
    GIT_CLONE_URLS = [f"https://{TOKEN}@github.com/harshit-rathore3/{REPO_NAME}.git"]
    AUTH_URL = ""
    GIT_USERNAME = "harshit-rathore3"
    GIT_EMAIL = "harshit.rathore@techolution.com"
    ORGANIZATION = ""
    FILE_EXTENSIONS = [".py"]


    @classmethod
    def set_creds(cls, repo_name: str, token: str, organization: str) -> None:
        """
        Set credentials.
        Args:
            repo_name (str): The name of the repository.
        """
        cls.REPO_NAME = repo_name
        cls.BASE_PATH = f'D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{repo_name}'
        cls.ORGANIZATION = organization
        cls.TOKEN = token
        cls.GIT_CLONE_URLS = [f"https://{cls.TOKEN}@github.com/{organization}/{repo_name}.git"]

    AZURE_API_TYPE = "azure"
    AZURE_API_BASE="https://wu-oai-appmod.openai.azure.com/"
    AZURE_API_VERSION="2023-05-15"
    AZURE_OPENAI_API_KEY="ad60d67257f8435f905039712b0cd748"
    AZURE_OPENAI_ENDPOINT="https://wu-oai-appmod.openai.azure.com/"

class JavascriptConfig:
    """
    JavaScript configuration class
    """
    TOKEN = ""
    REPO_NAME = ""
    BASE_PATH = f"D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{REPO_NAME}"
    GIT_CLONE_URLS = [f"https://{TOKEN}@github.com/harshit-rathore3/{REPO_NAME}.git"]
    AUTH_URL = ""
    GIT_USERNAME = "harshit-rathore3"
    GIT_EMAIL = "harshit.rathore@techolution.com"
    ORGANIZATION = ""
    LONG_CODE_REFACTOR_API = "https://autoai-backend-exjsxe2nda-uc.a.run.app/javascriptParser/refactorCode"
    FILE_EXTENSIONS = [".js"]


    @classmethod
    def set_creds(cls, repo_name: str, token: str, organization: str) -> None:
        """
        Set credentials.
        Args:
            repo_name (str): The name of the repository.
        """
        cls.REPO_NAME = repo_name
        cls.BASE_PATH = f"D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{repo_name}"
        cls.TOKEN = token
        cls.ORGANIZATION = organization
        cls.GIT_CLONE_URLS = [f"https://{cls.TOKEN}@github.com/{organization}/{repo_name}.git"]
    
    AZURE_API_TYPE = "azure"
    AZURE_API_BASE="https://wu-oai-appmod.openai.azure.com/"
    AZURE_API_VERSION="2023-05-15"
    AZURE_OPENAI_API_KEY="ad60d67257f8435f905039712b0cd748"
    AZURE_OPENAI_ENDPOINT="https://wu-oai-appmod.openai.azure.com/"



class TypescriptConfig:
    """
    JavaScript configuration class
    """
    TOKEN = ""
    REPO_NAME = ""
    BASE_PATH = f"D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{REPO_NAME}"
    GIT_CLONE_URLS = [f"https://{TOKEN}@github.com/harshit-rathore3/{REPO_NAME}.git"]
    AUTH_URL = ""
    GIT_USERNAME = "parinaysethtecholution"
    GIT_EMAIL = "parinay.seth@techolution.com"
    ORGANIZATION = ""
    FILE_EXTENSIONS = [".ts", ".tsx"]

    @classmethod
    def set_creds(cls, repo_name: str, token: str, organization: str) -> None:
        """
        Set credentials.
        Args:
            repo_name (str): The name of the repository.
        """
        cls.REPO_NAME = repo_name
        cls.BASE_PATH = f"D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{repo_name}"
        cls.TOKEN = token
        cls.ORGANIZATION = organization
        cls.GIT_CLONE_URLS = [f"https://{cls.TOKEN}@github.com/{organization}/{repo_name}.git"]
    
    AZURE_API_TYPE = "azure"
    AZURE_API_BASE="https://wu-oai-appmod.openai.azure.com/"
    AZURE_API_VERSION="2023-05-15"
    AZURE_OPENAI_API_KEY="ad60d67257f8435f905039712b0cd748"
    AZURE_OPENAI_ENDPOINT="https://wu-oai-appmod.openai.azure.com/"
    



class DocumentConfig:
    """
    JavaScript configuration class
    """
    TOKEN = ""
    REPO_NAME = ""
    BASE_PATH = f"D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{REPO_NAME}"
    GIT_CLONE_URLS = [f"https://{TOKEN}@github.com/harshit-rathore3/{REPO_NAME}.git"]
    AUTH_URL = ""
    GIT_USERNAME = "parinaysethtecholution"
    GIT_EMAIL = "parinay.seth@techolution.com"
    ORGANIZATION = ""
    FILE_EXTENSIONS = [""]

    @classmethod
    def set_creds(cls, repo_name: str, token: str, organization: str) -> None:
        """
        Set credentials.
        Args:
            repo_name (str): The name of the repository.
        """
        cls.REPO_NAME = repo_name
        cls.BASE_PATH = f"D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{repo_name}"
        cls.TOKEN = token
        cls.ORGANIZATION = organization
        cls.GIT_CLONE_URLS = [f"https://{cls.TOKEN}@github.com/{organization}/{repo_name}.git"]
    
    AZURE_API_TYPE = "azure"
    AZURE_API_BASE="https://wu-oai-appmod.openai.azure.com/"
    AZURE_API_VERSION="2023-05-15"
    AZURE_OPENAI_API_KEY="ad60d67257f8435f905039712b0cd748"
    AZURE_OPENAI_ENDPOINT="https://wu-oai-appmod.openai.azure.com/"
    
    
    
class Config:
    """
    Configuration class.
    """
    TOKEN = ''
    REPO_NAME = ''
    BASE_PATH = f'C:\\app\\{REPO_NAME}'
    # BASE_PATH = f'C:\\Users\\techolution\\Documents\\sylvan-backend\\{REPO_NAME}'
    # BASE_PATH = f'D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{REPO_NAME}'
    # BASE_PATH= f"C:\\Users\\Parinay Seth\\Desktop\\Sylvan\\mainfiles\\sylvan-backend\\{REPO_NAME}"

    REFACTOR_BRANCH = get_secret_value(env+'_'+'REFACTOR_BRANCH')
    SOURCE_BRANCH = get_secret_value(env+'_''SOURCE_BRANCH')
    TEST_BRANCH = get_secret_value(env+'_'+'TEST_BRANCH')
    AUTH_USERNAME = get_secret_value(env+'_'+'AUTH_USERNAME')
    AUTH_URL = get_secret_value(env+'_'+'AUTH_URL') 
    GIT_USERNAME = get_secret_value(env+'_'+'GIT_USERNAME')

    @classmethod
    def set_repo_token(cls, repo_name, token):
        """
        Set repository token.
        Args:
            repo_name (str): The name of the repository.
            token (str): The token.
        """
        ORGANIZATION_NAME = get_secret_value(env+'_'+'ORG')
        PROJECT_NAME = get_secret_value(env+'_'+'PROJECT')
        GIT_CLONE_URL = F"https://{token}@dev.azure.com/{ORGANIZATION_NAME}/{PROJECT_NAME}/_git/{repo_name}"
        GIT_CLONE_URL_Shared = f"https://{token}@dev.azure.com/{ORGANIZATION_NAME}/{PROJECT_NAME}/_git/Shared"
        cls.REPO_NAME = repo_name
        cls.TOKEN = token
        cls.GIT_CLONE_URL = GIT_CLONE_URL
        cls.GIT_CLONE_URL_Shared = GIT_CLONE_URL_Shared
        cls.BASE_PATH = f'C:\\app\\{repo_name}'
        # cls.BASE_PATH = f'C:\\Users\\techolution\\Documents\\sylvan-backend\\{repo_name}'
        # cls.BASE_PATH = f'D:\\Techolution Projects\\Sylvan Stuff\\sylvan-backend\\{repo_name}'
        # cls.BASE_PATH= f"C:\\Users\\Parinay Seth\\Desktop\\Sylvan\\mainfiles\\sylvan-backend\\{repo_name}"

    # Azure OpenAI configuration and request
    AZURE_API_TYPE = get_secret_value("AZURE_API_TYPE")
    AZURE_API_BASE = get_secret_value("AZURE_API_BASE")
    AZURE_API_VERSION = get_secret_value("AZURE_API_VERSION")
    AZURE_OPENAI_API_KEY = get_secret_value("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = get_secret_value("AZURE_OPENAI_ENDPOINT")
