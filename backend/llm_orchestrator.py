from typing import Dict, Any, Tuple, List, Optional
import os
from openai import OpenAI
import json
import re
import time

from .knowledge_base import KnowledgeBase

class LLMOrchestrator:
    """
    Orchestrates the LLM interactions, managing conversation flow,
    intent recognition, and knowledge base lookups.
    """
    
    def __init__(self, knowledge_base: KnowledgeBase):
        """
        Initialize the LLM orchestrator.
        
        Parameters:
        - knowledge_base: Instance of KnowledgeBase for retrieving supplement information
        """
        self.knowledge_base = knowledge_base
        
        # Initialize OpenAI client
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.client = OpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4o"  # Default to gpt-4o
        
        # System prompts
        self.base_system_prompt = """
You are a helpful, knowledgeable Longevity Health Agent specializing in longevity medicine.

Your goal is to understand the user's health concerns and goals, then provide evidence-based recommendations 
on supplements, lifestyle changes, and general health practices that could help them.

Important guidelines:
1. ALWAYS include appropriate medical disclaimers when giving health advice.
2. Be clear about the level of scientific evidence supporting each recommendation.
3. When recommending supplements, include dosage information, potential side effects, and contraindications.
4. Encourage users to consult with healthcare professionals before starting any new health regimen.
5. Avoid making exaggerated claims or promises about health outcomes.
6. Be respectful, empathetic, and professional in your tone.
7. Do not diagnose conditions or prescribe medications.
8. When relevant, include referral links for recommended supplements using the format provided in the knowledge base.

For each response, try to:
1. Acknowledge the user's concerns or questions
2. Provide evidence-based information and context
3. Give clear, actionable recommendations when appropriate
4. Include relevant disclaimers
"""

    def process_message(
        self, user_message: str, session_context: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Process a user message and generate a response with recommendations.
        
        Parameters:
        - user_message: The user's input message
        - session_context: The current session context with conversation history
        
        Returns:
        - response: The generated text response
        - recommendations: Any structured recommendations data (supplements, etc.)
        """
        # Check if OpenAI API key is available
        if not self.openai_api_key:
            return (
                "I'm sorry, but I'm not currently configured to process messages. "
                "Please contact support to set up the OpenAI API integration.",
                None
            )
        
        try:
            # Extract conversation history from session context
            conversation_history = session_context.get("messages", [])
            
            # Identify health goals and concerns from the user message
            detected_goals = self._detect_health_goals(user_message, conversation_history)
            
            # If we detected new goals, add them to the session
            if detected_goals and "identified_goals" in session_context:
                for goal in detected_goals:
                    if goal not in session_context["identified_goals"]:
                        session_context["identified_goals"].append(goal)
            
            # Retrieve relevant supplements and protocols from knowledge base
            relevant_supplements = []
            if detected_goals:
                for goal in detected_goals:
                    supplements = self.knowledge_base.get_supplements_for_goal(goal)
                    relevant_supplements.extend(supplements)
            
            # Construct the full prompt with conversation history and any relevant knowledge
            messages = self._construct_llm_prompt(user_message, conversation_history, relevant_supplements)
            
            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            # Parse recommendations from the response
            recommendations = self._extract_recommendations(response_text, relevant_supplements)
            
            return response_text, recommendations
            
        except Exception as e:
            # Return an error message if something goes wrong
            error_msg = f"I apologize, but I encountered an error processing your request: {str(e)}"
            return error_msg, None
    
    def _detect_health_goals(self, message: str, conversation_history: List[Dict[str, str]]) -> List[str]:
        """
        Identify health goals from the user's message.
        
        Parameters:
        - message: The user's input message
        - conversation_history: Previous messages in the conversation
        
        Returns:
        - List of identified health goals
        """
        # For V0, we'll use a simple approach with the LLM to identify goals
        try:
            # Construct a prompt specifically for goal detection
            full_conversation = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-5:] if msg['role'] in ['user', 'assistant']
            ])
            
            detection_prompt = [
                {"role": "system", "content": 
                    "You are an AI assistant that identifies health goals and concerns from user messages. "
                    "Extract specific health goals like weight loss, longevity, muscle gain, hair loss, "
                    "sleep improvement, energy enhancement, mental clarity, etc. "
                    "Respond with a JSON array of identified goals, using lowercase with spaces. "
                    "If no goals are identified, return an empty array."
                },
                {"role": "user", "content": 
                    f"Based on this conversation and the latest message, identify the health goals:\n\n"
                    f"Conversation history:\n{full_conversation}\n\n"
                    f"Latest message: {message}\n\n"
                    f"Return ONLY a JSON array of goals, nothing else. Example: [\"weight loss\", \"hair regrowth\"]"
                }
            ]
            
            # Call LLM with response_format for JSON
            response = self.client.chat.completions.create(
                model=self.model,
                messages=detection_prompt,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the response to extract goals
            result_text = response.choices[0].message.content
            try:
                result_json = json.loads(result_text)
                if "goals" in result_json and isinstance(result_json["goals"], list):
                    return result_json["goals"]
                elif isinstance(result_json, list):
                    return result_json
                else:
                    # Try to find an array in the response
                    match = re.search(r'\[.*?\]', result_text)
                    if match:
                        possible_array = match.group(0)
                        return json.loads(possible_array)
                    return []
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract goals with simple pattern matching
                goals = []
                common_goals = [
                    "weight loss", "longevity", "anti aging", "muscle gain", 
                    "hair loss", "sleep", "energy", "mental clarity", 
                    "stress reduction", "immune support"
                ]
                for goal in common_goals:
                    if goal in message.lower() or goal in full_conversation.lower():
                        goals.append(goal)
                return goals
                
        except Exception as e:
            print(f"Error in goal detection: {str(e)}")
            return []
    
    def _construct_llm_prompt(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]],
        relevant_supplements: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Construct the full prompt for the LLM.
        
        Parameters:
        - user_message: The latest user message
        - conversation_history: Previous messages in the conversation
        - relevant_supplements: List of relevant supplements from the knowledge base
        
        Returns:
        - List of message dictionaries for the OpenAI API
        """
        # Start with the system prompt
        system_prompt = self.base_system_prompt
        
        # Add relevant supplement information to the system prompt if available
        if relevant_supplements:
            supplements_info = "\n\nRelevant supplements from knowledge base:\n"
            for supplement in relevant_supplements:
                supplements_info += f"- {supplement['name']}: {supplement['description']}\n"
                supplements_info += f"  Typical dosage: {supplement['dosage']}\n"
                supplements_info += f"  Referral link: {supplement['referral_link']}\n\n"
            
            system_prompt += supplements_info
        
        # Construct the messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (limit to last 10 messages to avoid token limits)
        for msg in conversation_history[-10:]:
            if msg["role"] in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        return messages
    
    def _extract_recommendations(
        self, response_text: str, available_supplements: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured recommendations from the LLM response.
        
        Parameters:
        - response_text: The LLM-generated response text
        - available_supplements: List of relevant supplements from the knowledge base
        
        Returns:
        - Dictionary of structured recommendations, or None if none found
        """
        # For V0, we'll do a simple extraction of mentioned supplements
        if not available_supplements:
            return None
            
        recommended_supplements = []
        
        for supplement in available_supplements:
            supplement_name = supplement["name"].lower()
            if supplement_name in response_text.lower():
                recommended_supplements.append({
                    "name": supplement["name"],
                    "referral_link": supplement["referral_link"],
                    "dosage": supplement["dosage"]
                })
        
        if recommended_supplements:
            return {
                "supplements": recommended_supplements,
                "timestamp": int(time.time())
            }
        
        return None
