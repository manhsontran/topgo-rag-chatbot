"""
Ollama LLM client for local language model inference
"""
import requests
from typing import Dict, List, Optional
import json


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize Ollama client
        
        Args:
            base_url: Base URL for Ollama API
            model: Model name (llama2, mistral, etc.)
        """
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False
    ) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            
        Returns:
            Generated text response
        """
        # Build full prompt with system prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                if stream:
                    # Handle streaming response
                    result = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            result += data.get('response', '')
                    return result
                else:
                    # Handle non-streaming response
                    data = response.json()
                    return data.get('response', '')
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timeout. Please try again."
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Chat with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Generated response
        """
        # Convert messages to prompt format
        prompt = ""
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt = f"{content}\n\n{prompt}"
            elif role == 'user':
                prompt += f"\n\nUser: {content}"
            elif role == 'assistant':
                prompt += f"\n\nAssistant: {content}"
        
        prompt += "\n\nAssistant:"
        
        return self.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )


def test_ollama():
    """Test Ollama connection and models"""
    print("🔍 Testing Ollama Connection...")
    print("=" * 80)
    
    client = OllamaClient()
    
    # Check connection
    print("\n1. Checking connection...")
    if client.check_connection():
        print("   ✅ Ollama is running!")
    else:
        print("   ❌ Ollama is not running!")
        print("   💡 Start Ollama:")
        print("      - Windows: Start Ollama app")
        print("      - Linux/Mac: ollama serve")
        return
    
    # List models
    print("\n2. Available models:")
    models = client.list_models()
    if models:
        for model in models:
            print(f"   ✅ {model}")
    else:
        print("   ⚠️  No models found!")
        print("   💡 Pull a model:")
        print("      ollama pull llama2")
        return
    
    # Test generation
    print("\n3. Testing generation...")
    response = client.generate(
        prompt="Hello! Please introduce yourself in one sentence.",
        temperature=0.7,
        max_tokens=100
    )
    print(f"   Response: {response[:200]}...")
    
    print("\n" + "=" * 80)
    print("✅ Ollama test complete!")


if __name__ == "__main__":
    test_ollama()
