class AssistantConfig:
    """A class to access configuration for different assistants.

    Attributes:
        assistant (str): The name of the assistant (e.g., "generalcoderefactor").
        documentRetrieval (str): The ID for document retrieval.
        answerEvaluation (str): The ID for answer evaluation.
        bestAnswer (str): The ID for the best answer.
        source (str): The source language (e.g., "python").
        target (str): The target language (e.g., "python").
        auto_ai (str): The ID for auto AI.
        model_org (str): The model organization (e.g., "openai").
        model_type (str): The model type (e.g., "gpt-4-128k").
    """

    def __init__(self, assistant):
        """
        Initializes the AssistantConfig object with the specified assistant.

        Args:
            assistant (str): The name of the assistant.
        """

        if assistant == "generalcoderefactor":
            self.documentRetrieval = "65e5d428f82ceb84bd177e551"
            self.answerEvaluation = "65e5d428f82eb8556577e55e"
            self.bestAnswer = "65e5d428f82eb8441777e56f"
            self.source = "python"
            self.target = "python"
            self.auto_ai = "65e5d428f82eb8a5e577e580"
            self.model_org = "google"
            self.model_type = "claude-3-sonnet"
            self.databasetype = "pinecone"

        elif assistant == "refactorchanged":
            self.documentRetrieval = "66449425ef7faeeaedce6989"
            self.answerEvaluation = "66449426ef7faeeaedce6992"
            self.bestAnswer = "66449426ef7faeeaedce699d"
            self.source = "python"
            self.target = "python"
            self.auto_ai = "66449426ef7faeeaedce69a6"
            self.model_org = "google"
            self.model_type = "claude-3-sonnet"
            self.databasetype = "alloydb"

        elif assistant == "coderefactordiff":
            self.documentRetrieval = "6634b1001c6b4122a8b42ca9"
            self.answerEvaluation = "6634b1001c6b4122a8b42cb2"
            self.bestAnswer = "6634b1001c6b4122a8b42cbb"
            self.source = "python"
            self.target = "python"
            self.auto_ai = "6634b1001c6b4122a8b42cc4"
            self.model_org = "google"
            self.model_type = "claude-3-sonnet"
            self.databasetype = "pinecone"


        else:
            raise ValueError(f"Unsupported assistant: {assistant}")