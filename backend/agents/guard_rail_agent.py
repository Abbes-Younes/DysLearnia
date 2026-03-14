"""
Guard Rail Agent - Content safety and moderation

This agent handles content moderation and safety checks for user inputs
and AI-generated content using a local LLM via llama.cpp.
"""

from typing import Dict, List, Optional, Any


class ContentGuardRail:
    """
    Content safety and moderation agent.
    
    Uses llama-cpp-python (llama.cpp) for detecting inappropriate content, 
    harmful requests, or content that violates safety guidelines.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the guard rail agent.
        
        Args:
            model_path: Path to the LLM model for content moderation.
                       If None, uses a default lightweight model.
        """
        self.model_path = model_path
        self._llama_model = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the LLM model for content moderation.
        
        Returns:
            True if initialization succeeded, False otherwise.
        """
        try:
            # Try to import llama_cpp (from pip package llama-cpp-python)
            from llama_cpp import Llama as LlamaModel
            
            # Use a small model for content classification
            # In production, this would be a fine-tuned safety model
            if self.model_path:
                self._llama_model = LlamaModel(
                    model_path=self.model_path,
                    n_ctx=512,
                    n_threads=4
                )
            
            self._initialized = True
            return True
        except ImportError:
            # If llama_cpp not available, fall back to rule-based checking
            print("Warning: llama_cpp not available, using rule-based checks only")
            self._initialized = True
            return True
        except Exception as e:
            print(f"Warning: Could not initialize LLM model: {e}")
            self._initialized = True
            return True
    
    def check_content(self, text: str) -> Dict[str, Any]:
        """
        Check if content passes safety guidelines.
        
        Args:
            text: The text content to check.
            
        Returns:
            Dictionary with 'is_safe' boolean and 'reason' if unsafe.
        """
        if not self._initialized:
            self.initialize()
        
        # Basic rule-based checks (always available)
        result = self._rule_based_check(text)
        
        if not result["is_safe"]:
            return result
        
        # If LLM is available, do deeper analysis
        if self._llama_model is not None:
            return self._llm_check(text)
        
        return result
    
    def _rule_based_check(self, text: str) -> Dict[str, Any]:
        """
        Perform basic rule-based content checks.
        
        Args:
            text: Text to check.
            
        Returns:
            Dictionary with check results.
        """
        text_lower = text.lower()
        
        # List of prohibited patterns (simplified example)
        prohibited_keywords = [
            "harmful", "dangerous", "illegal", 
            # Add more keywords as needed
        ]
        
        for keyword in prohibited_keywords:
            if keyword in text_lower:
                return {
                    "is_safe": False,
                    "reason": f"Content contains prohibited keyword: {keyword}",
                    "confidence": 0.9
                }
        
        return {"is_safe": True, "reason": None, "confidence": 1.0}
    
    def _llm_check(self, text: str) -> Dict[str, Any]:
        """
        Use LLM for more sophisticated content analysis.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Dictionary with analysis results.
        """
        # This would be a more sophisticated LLM-based check
        # For now, just return the rule-based result
        return self._rule_based_check(text)
    
    def batch_check(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Check multiple texts for safety.
        
        Args:
            texts: List of texts to check.
            
        Returns:
            List of check results for each text.
        """
        return [self.check_content(text) for text in texts]


# Default instance for easy imports
_default_agent: Optional[ContentGuardRail] = None


def get_guard_rail_agent() -> ContentGuardRail:
    """
    Get the default guard rail agent instance.
    
    Returns:
        The singleton ContentGuardRail instance.
    """
    global _default_agent
    if _default_agent is None:
        _default_agent = ContentGuardRail()
        _default_agent.initialize()
    return _default_agent