import requests
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    
    def __init__(self, base_url: str = None, model: str = None, timeout: int = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT
    
    def chat(self, messages: list[dict], model: str = None) -> str:
        """Send a chat request to Ollama.
        
        Args:
            messages: list of {'role': str, 'content': str}
            model: optional model override
            
        Returns:
            The assistant's response text
        """
        url = f'{self.base_url}/api/chat'
        payload = {
            'model': model or self.model,
            'messages': messages,
            'stream': False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get('message', {}).get('content', '')
        except requests.exceptions.ConnectionError:
            logger.error(f'Cannot connect to Ollama at {self.base_url}')
            raise ConnectionError(
                f'Cannot connect to Ollama at {self.base_url}. '
                'Please ensure Ollama is running (ollama serve).'
            )
        except requests.exceptions.Timeout:
            logger.error('Ollama request timed out')
            raise TimeoutError(
                f'Ollama request timed out after {self.timeout}s. '
                'The model may be loading or the query may be too complex.'
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f'Model "{self.model}" not found. '
                    f'Please run: ollama pull {self.model}'
                )
            logger.error(f'Ollama HTTP error: {e}')
            raise
    
    def generate(self, prompt: str, model: str = None) -> str:
        """Send a generate request to Ollama."""
        url = f'{self.base_url}/api/generate'
        payload = {
            'model': model or self.model,
            'prompt': prompt,
            'stream': False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get('response', '')
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f'Cannot connect to Ollama at {self.base_url}. '
                'Please ensure Ollama is running.'
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(f'Ollama request timed out after {self.timeout}s.')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f'Model "{self.model}" not found.')
            raise
    
    def check_model(self, model: str = None) -> bool:
        """Check if a model is available in Ollama."""
        try:
            models = self.list_models()
            target = model or self.model
            # Check both exact name and name without tag
            for m in models:
                name = m.get('name', '')
                if name == target or name.split(':')[0] == target.split(':')[0]:
                    return True
            return False
        except Exception:
            return False
    
    def list_models(self) -> list[dict]:
        """List available Ollama models."""
        url = f'{self.base_url}/api/tags'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except Exception as e:
            logger.error(f'Failed to list Ollama models: {e}')
            return []
    
    def is_available(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            response = requests.get(f'{self.base_url}/api/tags', timeout=5)
            return response.status_code == 200
        except Exception:
            return False
