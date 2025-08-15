import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from app.extractors.json_extractor import JsonExtractor
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

class MetadataValidator:
    """
    The system prompt for the metadata validation task.
    we will send {system_prompt_metadata} as the system prompt to the model.
    and this class will be used to validate the response from the model.
    """
    def __init__(self, text: str = None, column_names: list = None, raise_on_error: bool = True):
        self._column_names        = column_names
        self._general_description = None
        self._column_descriptions = None
        for json_object in JsonExtractor(text).objects:
            try:
                if self.validate_json(json_object):
                    return
            except Exception as e:
                pass
        self._general_description = None
        self._column_descriptions = None
        if raise_on_error:
            raise ValueError("No valid metadata found in the provided text.")
    
    def isvalid(self) -> bool:
        """
        Check if the metadata is valid.
        Returns True if valid, False otherwise.
        """
        if not self._general_description or not self._column_descriptions:
            return False
        return True
    
    @property
    def general_description(self) -> str:
        """
        Get the general description of the metadata.
        This is a placeholder for the actual implementation.
        """
        return self._general_description
    
    @property
    def column_descriptions(self) -> list: 
        """
        Get the column descriptions of the metadata.
        This is a placeholder for the actual implementation.
        """
        if not self._column_descriptions:
            return []
        return self._column_descriptions
    
    def uniform_column_name(self, column_name: str) -> str:
        """
        Convert the column name to a uniform format.
        This is a placeholder for the actual implementation.
        """
        if not isinstance(column_name, str) or not column_name.strip():
            return ""
        column_name = column_name.strip().lower()
        for c in "\r\n\t\v\f ":
            column_name = column_name.replace(c, " ")
        while "  " in column_name:
            column_name = column_name.replace("  ", " ")
        return column_name.strip()
        
    def similarity(self, str1: str, str2: str) -> float:
        """
        Calculate the similarity between two strings.
        This is a placeholder for the actual implementation.
        returns a float value between 0 and 1, where 1 means identical.
        """
        str1 = self.uniform_column_name(str1)
        str2 = self.uniform_column_name(str2)
        if str1 == str2:
            return 1.0
        str1 = str1.replace("_", "")
        str2 = str2.replace("_", "")
        if str1 == str2:
            return 0.9
        str1 = str1.replace(" ", "")
        str2 = str2.replace(" ", "")
        if str1 == str2:
            return 0.85
        # try:
        #     vectorizer = TfidfVectorizer().fit_transform([str1, str2])
        #     vectors    = vectorizer.toarray()
        #     csim       = cosine_similarity(vectors)
        #     return csim[0, 1]
        # except ValueError:
        #     return 0.0
        return 0.0
    
    def update_descriptions(self, general_description: str, column_descriptions: dict) -> None:
        self._general_description = None
        self._column_descriptions = None
        _general_description      = general_description
        _column_descriptions      = [None] * len(self._column_names)
        if not general_description or not column_descriptions:
            raise ValueError("Invalid metadata provided. General description and column descriptions are required.")
        if not isinstance(general_description, str):
            raise ValueError("Invalid general description provided. It should be a string.")
        if not isinstance(column_descriptions, dict):
            raise ValueError("Invalid column descriptions provided. It should be a dictionary.")
        if not general_description.strip():
            raise ValueError("Invalid general description provided. It should not be empty.")
        for step in range(len(self._column_names)):
            for key, val in column_descriptions.items():
                if self.similarity(key, self._column_names[step]) > 0.8:
                    if _column_descriptions[step] is not None:
                        raise ValueError(f"Duplicate column description found for {self._column_names[step]}")
                    _column_descriptions[step] = {self._column_names[step] : val}
                    break
        for item in _column_descriptions:
            if not item:
                raise ValueError("Invalid column description found. Each column description should be a dictionary with one key-value pair.")
        self._general_description = _general_description
        self._column_descriptions = _column_descriptions
        return True

    def validate_json(self, json_object: dict) -> bool:
        """
        Validate the JSON object against the expected structure.
        """
        general_description       = None
        column_descriptions       = None
        self._general_description = None
        self._column_descriptions = None
        for key, val in json_object.items():
            if "general" in key.lower():
                general_description = val
            elif "column" in key.lower():
                column_descriptions = val
        return self.update_descriptions(general_description, column_descriptions)
    
class DescriptionValidator:
    """
    The system prompt for the metadata validation task.
    we will send {system_prompt_metadata} as the system prompt to the model.
    and this class will be used to validate the response from the model.
    """
    def __init__(self, text: str = None, raise_on_error: bool = True):
        self._general_description = None
        for json_object in JsonExtractor(text).objects:
            try:
                if self.validate_json(json_object):
                    return
            except Exception as e:
                pass
        self._general_description = None
        if raise_on_error:
            raise ValueError("No valid metadata found in the provided text.")

    def isvalid(self) -> bool:
        """
        Check if the metadata is valid.
        Returns True if valid, False otherwise.
        """
        if self._general_description:
            return True
        return False

    @property
    def general_description(self) -> str:
        """
        Get the general description of the metadata.
        This is a placeholder for the actual implementation.
        """
        return self._general_description

    def validate_json(self, json_object: dict) -> bool:
        """
        Validate the JSON object against the expected structure.
        """
        self._general_description = None
        for key, val in json_object.items():
            if "general" in key.lower():
                self._general_description = val
                return True
        return False