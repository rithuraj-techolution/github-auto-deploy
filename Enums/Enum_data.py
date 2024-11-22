
from enum import Enum


class StatusCodes(Enum):
    """
    Enum class for status codes.
    """
    # success responses
    SUCCESS = 200
    SKIP_PIPELINE = 201
    ACCEPTED = 202
    COMPILE_ERROR = 205
    NO_WORK_REQUIRED = 207

    # client error responses
    INVALID_OR_EXPIRED_TOKEN = 403
    WRONG_PAYLOAD_DATA = 405

    # server error responses
    INTERNAL_SERVER_ERROR = 500
    EMPTY_RESPONSE = 503


class PythonAssistants(Enum):
    """
    Enum class for Python assistants.
    """
    # Python assistants
    UNITTEST = "pythonunitcases"
    # REFACTOR = "pythonrefactor"
    REFACTOR = ["generalcoderefactor", "coderefactordiff", "refactorchanged"]
    FILE_EXTENSIONS = [".py"]


class JavascriptAssistants(Enum):
    """
    Enum class for JavaScript assistants.
    """
    UNITTEST = "jstest"

    REFACTOR = ["generalcoderefactor", "coderefactordiff", "refactorchanged"]
    FILE_EXTENSIONS = [".js"]


class CAssistant(Enum):
    """
    Enum class for C assistants.
    """
    UNITTEST = "TEST"
    REFACTOR = ["REFACTOR1"]
    COMPILER = "c-compiler-3889"
    FILE_EXTENSIONS = [".c"]


class TypescriptAssistants(Enum):
    """
    Enum class for TypeScript assistants.
    """
    UNITTEST = "tsunittest"
    REFACTOR = ["generalcoderefactor"]
    FILE_EXTENSIONS = [".ts", ".tsx"]
