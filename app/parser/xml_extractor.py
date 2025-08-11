import re
import json
from typing import List, Dict, Any, Optional

class XmlExtractor:
    """
    A class to extract XML-like tags and their content from text.
    Specifically designed to parse <agent_call> and <answer> tags from responses.
    """

    def __init__(self, text: str = ""):
        self._text = text
        if text:
            self._agent_calls = self.extract_agent_calls(text)
            self._answer = self.extract_answer(text)
        else:
            self._agent_calls = []
            self._answer = None

    @property
    def agent_calls(self) -> List[Dict[str, Any]]:
        """Returns the list of extracted agent call objects."""
        return self._agent_calls

    @property
    def answer(self) -> Optional[str]:
        """Returns the extracted answer content."""
        return self._answer

    def has_agent_calls(self) -> bool:
        """Check if the text contains any agent calls."""
        return len(self._agent_calls) > 0

    @staticmethod
    def extract_answer(text: str) -> Optional[str]:
        """
        Extract content from <answer> tags.
        Returns the text content inside the first <answer></answer> block.
        """
        text = str(text).strip()
        if not text:
            return None
        
        pattern = r'<answer>(.*?)</answer>'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def extract_answers(text: str) -> List[str]:
        """
        Extract all content from <answer> tags.
        Returns a list of text content from all <answer></answer> blocks.
        """
        text = str(text).strip()
        if not text:
            return []
        
        pattern = r'<answer>(.*?)</answer>'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        return [match.strip() for match in matches if match.strip()]

    @staticmethod
    def extract_agent_calls(text: str) -> List[Dict[str, Any]]:
        """
        Extract and parse <agent_call> blocks from text.
        Each block should contain JSON with agent, dataset, and question.
        
        Returns a list of dictionaries with parsed agent call parameters.
        """
        text = str(text).strip()
        if not text:
            return []
        
        # Find all <agent_call> blocks
        pattern = r'<agent_call>(.*?)</agent_call>'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        agent_calls = []
        for match_content in matches:
            try:
                # Clean up the JSON content
                json_content = match_content.strip()
                
                # Parse the JSON
                call_data = json.loads(json_content)
                
                # Validate required fields
                if all(key in call_data for key in ['agent', 'dataset', 'question']):
                    agent_calls.append({
                        'agent': call_data['agent'],
                        'dataset': call_data['dataset'],
                        'question': call_data['question']
                    })
                else:
                    print(f"Warning: Invalid agent call missing required fields: {call_data}")
                    
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse agent call JSON: {match_content[:100]}... Error: {e}")
                continue
            except Exception as e:
                print(f"Warning: Error processing agent call: {e}")
                continue
        
        return agent_calls

    @staticmethod
    def create_agent_answer_block(content: str, dataset: str = None, error: str = None) -> str:
        """
        Create an <agent_answer> block with the provided content.
        
        Args:
            content: The answer content from data expert
            dataset: Optional dataset identifier
            error: Optional error message if data extraction failed
        """
        if error:
            answer_content = f"Error extracting data from {dataset}: {error}"
        else:
            answer_content = content
        
        return f"<agent_answer>\n{answer_content}\n</agent_answer>"