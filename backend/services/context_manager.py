# context_manager.py - FIXED VERSION

from typing import List, Dict, Any
import json
import re

class ContextManager:
    def __init__(self, max_context_length: int = 10):
        self.max_context_length = max_context_length
   
    def prepare_context_for_llm(self, history: List[str], current_input: str, tool_name: str = None) -> List[Dict[str, str]]:
        """
        Prepare consistent context for all LLM calls with smart context selection
        """
        messages = []
       
        # Add system message with tool-specific instructions
        system_content = self._get_system_message(tool_name)
        messages.append({"role": "system", "content": system_content})
       
        # Smart context selection based on tool
        if tool_name == "search":
            # For search: intelligently select context that maintains topic continuity
            context_history = self._get_smart_search_context(history, current_input)
        else:
            # Other tools: use full context (last 10 messages)
            context_history = history[-self.max_context_length:] if len(history) > self.max_context_length else history
       
        # Add conversation history
        for i, msg in enumerate(context_history):
            role = "user" if i % 2 == 0 else "assistant"
            messages.append({"role": role, "content": msg})
       
        # Add current input
        if current_input.strip():
            messages.append({"role": "user", "content": current_input})
       
        return messages

    def _get_smart_search_context(self, history: List[str], current_input: str) -> List[str]:
        """
        Intelligently select context for search tool to maintain topic continuity
        while respecting rate limits
        """
        if len(history) <= 4:
            return history
        
        # Strategy: Include topic-establishing messages + recent context
        context_messages = []
        
        # 1. Find the most recent topic-establishing user message (questions, topics)
        topic_message = None
        topic_index = -1
        
        # Look for substantial user messages that establish topics
        for i in range(len(history) - 2, -1, -2):  # Go backwards through user messages
            msg = history[i].strip()
            if (len(msg.split()) > 3 and 
                (msg.endswith('?') or 
                 any(keyword in msg.lower() for keyword in ['about', 'explain', 'what', 'how', 'why', 'tell me']) or
                 len(msg) > 20)):
                topic_message = msg
                topic_index = i
                break
        
        # 2. Include the topic message and its response if found
        if topic_message and topic_index >= 0:
            context_messages.extend([topic_message])
            if topic_index + 1 < len(history):
                context_messages.append(history[topic_index + 1])  # Assistant's response
        
        # 3. Add the most recent 2 exchanges (4 messages) for immediate context
        recent_context = history[-4:] if len(history) >= 4 else history
        
        # Avoid duplicating messages
        for msg in recent_context:
            if msg not in context_messages:
                context_messages.append(msg)
        
        # Ensure we don't exceed 6 messages total (reasonable for search)
        return context_messages[-6:]

    def _get_system_message(self, tool_name: str) -> str:
        """
        Get appropriate system message based on tool
        """
        base_prompt = (
            "You are SynthesisTalk, an intelligent research assistant. "
            "Maintain conversation context and provide helpful, accurate responses. "
            "Always refer to previous messages when relevant and ask for clarification if needed."
        )
       
        tool_specific = {
            "search": (
                "Focus on the current research topic from our conversation. "
                "Use the conversation context to understand what the user is researching. "
                "If the user's search query is brief, expand it based on our discussion context. "
                "Provide relevant search queries that build on our ongoing research conversation."
            ),
            "summarize": "Provide clear, structured summaries while maintaining context from previous discussion.",
            "clarify": "Explain concepts clearly while referencing previous conversation context when relevant.",
            "visualize": "Generate visualization data based on the research insights from our conversation.",
            "react_agent": "Use the ReAct approach while maintaining awareness of our ongoing research discussion.",
            "qa": "Answer questions using chain-of-thought reasoning while considering our conversation history."
        }
       
        if tool_name and tool_name in tool_specific:
            return f"{base_prompt}\n\nSpecific task: {tool_specific[tool_name]}"
       
        return base_prompt

    def format_tool_input(self, history: List[str], user_input: str, tool_name: str) -> str:
        """
        Format input appropriately for each tool with context awareness
        """
        if tool_name == "visualize":
            # For visualize, use the last assistant response if no user input
            if not user_input.strip() and history:
                for i in range(len(history) - 1, -1, -1):
                    if i % 2 == 1:  # assistant's message
                        return history[i]
            return user_input or "Generate visualization from our discussion"
       
        elif tool_name == "search":
            # FIXED: Enhanced search input formatting with context awareness
            if user_input.strip():
                # If user provides input, enhance it with context if it's too brief
                if len(user_input.split()) <= 2 and history:
                    # Find recent topic context
                    context_topic = self._extract_current_topic(history)
                    if context_topic:
                        enhanced_query = f"{user_input} {context_topic}"
                        return enhanced_query
                return user_input
            else:
                # If no input, infer from context
                if history:
                    topic = self._extract_current_topic(history)
                    if topic:
                        return f"search for more information about {topic}"
                return "Please provide a search query"
       
        else:
            # For other tools, use input as-is
            return user_input

    def _extract_current_topic(self, history: List[str]) -> str:
        """
        Extract the current research topic from conversation history
        """
        # Look for the most recent substantial user question or topic
        for i in range(len(history) - 2, -1, -2):  # Go backwards through user messages
            msg = history[i].strip()
            if len(msg.split()) > 3:
                # Extract key terms (remove common words)
                words = msg.lower().split()
                filtered_words = [w for w in words if w not in ['what', 'how', 'why', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'can', 'could', 'would', 'should', 'tell', 'me', 'you', 'i', 'we', 'they']]
                if filtered_words:
                    return ' '.join(filtered_words[:4])  # Take first 4 meaningful words
        
        return ""

    def get_conversation_summary(self, history: List[str]) -> str:
        """
        Get a brief summary of the conversation for context
        """
        if not history:
            return "No previous conversation"
        
        # Find main topics discussed
        topics = []
        for i in range(0, len(history), 2):  # User messages
            if i < len(history):
                msg = history[i].strip()
                if len(msg.split()) > 3:
                    topic = self._extract_key_terms(msg)
                    if topic:
                        topics.append(topic)
        
        if topics:
            return f"Discussing: {', '.join(topics[:3])}"
        return "General conversation"

    def _extract_key_terms(self, text: str) -> str:
        """
        Extract key terms from a message
        """
        # Simple keyword extraction
        important_words = []
        words = text.lower().split()
        
        for word in words:
            word = re.sub(r'[^a-zA-Z]', '', word)  # Remove punctuation
            if (len(word) > 3 and 
                word not in ['what', 'how', 'why', 'when', 'where', 'would', 'could', 'should', 'about', 'explain', 'tell']):
                important_words.append(word)
        
        return ' '.join(important_words[:2]) if important_words else ""