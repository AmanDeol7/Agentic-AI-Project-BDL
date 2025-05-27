"""
Manager for handling prompt templates.
"""
from typing import Dict, List, Any, Optional
from jinja2 import Template

class TemplateManager:
    """Manager for prompt templates with database integration."""
    
    def __init__(self, db_manager=None):
        """
        Initialize the template manager.
        
        Args:
            db_manager: Database manager for template storage
        """
        self.db_manager = db_manager
        
        # Default templates as fallback
        self.default_templates = {
            "code_agent": """
            You are a specialized Code Assistant that helps users generate high-quality code.
            
            You have these capabilities:
            1. Generate code based on user requirements
            2. Explain code functionality
            3. Debug and improve existing code
            4. Work with data from uploaded files
            
            When generating code:
            - Write clean, well-documented code
            - Include comments explaining complex logic
            - Follow best practices for the language
            - Provide explanations of how the code works
            """,
            
            "doc_agent": """
            You are a specialized Document Assistant that helps users understand and extract information from documents.
            
            You have these capabilities:
            1. Answer questions about document content
            2. Summarize documents
            3. Extract specific information from documents
            4. Compare information across multiple documents
            
            When working with documents:
            - Provide accurate information based on document content
            - Cite relevant sections when providing information
            - Maintain proper context when summarizing
            - Be clear about information that is not in the documents
            """
        }
    
    def get_template_for_user(self, user_id: str, agent_type: str) -> str:
        """
        Get template for a specific user and agent type.
        
        Args:
            user_id: User ID to get template for
            agent_type: Type of agent ("code_agent" or "doc_agent")
            
        Returns:
            Template string
        """
        if not self.db_manager:
            return self.default_templates.get(agent_type, "")
            
        # Try to get the template from the database
        try:
            user = self.db_manager.get_or_create_user(user_id)
            templates = self.db_manager.get_user_templates(user.id, agent_type)
            
            if templates:
                # Return the first template (we could also provide a way to select specific templates)
                return templates[0].template
                
        except Exception as e:
            print(f"Error getting template: {e}")
            
        # Fallback to default template
        return self.default_templates.get(agent_type, "")
    
    def save_template(self, user_id: str, name: str, agent_type: str, template: str, template_id: Optional[int] = None) -> bool:
        """
        Save a template to the database.
        
        Args:
            user_id: User ID to save template for
            name: Template name
            agent_type: Type of agent ("code_agent" or "doc_agent")
            template: Template string
            template_id: Optional ID for updating existing template
            
        Returns:
            Success status
        """
        if not self.db_manager:
            return False
            
        try:
            user = self.db_manager.get_or_create_user(user_id)
            template = self.db_manager.create_or_update_template(
                user.id, name, agent_type, template, template_id
            )
            return template is not None
        except Exception as e:
            print(f"Error saving template: {e}")
            return False
    
    def render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """
        Render a template with context data.
        
        Args:
            template_str: Template string
            context: Context data for rendering
            
        Returns:
            Rendered template
        """
        template = Template(template_str)
        return template.render(**context)