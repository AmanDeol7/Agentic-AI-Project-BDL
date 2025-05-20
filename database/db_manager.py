from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Session as ChatSession, Message, Document, PromptTemplate

class DatabaseManager:
    """Manager class for database operations"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    # User operations
    def get_or_create_user(self, username: str) -> User:
        """Get an existing user or create if not exists"""
        user = self.db_session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            self.db_session.add(user)
            self.db_session.commit()
        return user
    
    # Session operations
    def create_session(self, user_id: int, name: str) -> ChatSession:
        """Create a new chat session for a user"""
        session = ChatSession(user_id=user_id, name=name)
        self.db_session.add(session)
        self.db_session.commit()
        return session
    
    def get_session(self, session_id: int) -> ChatSession:
        """Get a session by ID"""
        return self.db_session.query(ChatSession).filter_by(id=session_id).first()
    
    def get_user_sessions(self, user_id: int) -> list:
        """Get all sessions for a user"""
        return self.db_session.query(ChatSession).filter_by(user_id=user_id).order_by(ChatSession.last_accessed.desc()).all()
    
    def update_session_access(self, session_id: int) -> None:
        """Update the last accessed timestamp for a session"""
        session = self.get_session(session_id)
        if session:
            session.last_accessed = datetime.utcnow()
            self.db_session.commit()
    
    # Message operations
    def add_message(self, session_id: int, role: str, content: str) -> Message:
        """Add a message to a session"""
        message = Message(session_id=session_id, role=role, content=content)
        self.db_session.add(message)
        self.db_session.commit()
        return message
    
    def get_session_messages(self, session_id: int) -> list:
        """Get all messages for a session"""
        return self.db_session.query(Message).filter_by(session_id=session_id).order_by(Message.created_at).all()
    
    # Document operations
    def add_document(self, session_id: int, filename: str, file_path: str, file_type: str) -> Document:
        """Add a document to a session"""
        document = Document(
            session_id=session_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type
        )
        self.db_session.add(document)
        self.db_session.commit()
        return document
    
    def get_session_documents(self, session_id: int) -> list:
        """Get all documents for a session"""
        return self.db_session.query(Document).filter_by(session_id=session_id).all()
    
    # Template operations
    def get_template(self, template_id: int) -> PromptTemplate:
        """Get a template by ID"""
        return self.db_session.query(PromptTemplate).filter_by(id=template_id).first()
    
    def get_user_templates(self, user_id: int, agent_type: str = None) -> list:
        """Get all templates for a user, optionally filtered by agent type"""
        query = self.db_session.query(PromptTemplate).filter_by(user_id=user_id)
        if agent_type:
            query = query.filter_by(agent_type=agent_type)
        return query.all()
    
    def create_or_update_template(self, user_id: int, name: str, agent_type: str, template: str, template_id: int = None) -> PromptTemplate:
        """Create a new template or update existing one"""
        if template_id:
            prompt_template = self.get_template(template_id)
            if prompt_template and prompt_template.user_id == user_id:
                prompt_template.name = name
                prompt_template.agent_type = agent_type
                prompt_template.template = template
                prompt_template.last_modified = datetime.utcnow()
            else:
                return None
        else:
            prompt_template = PromptTemplate(
                user_id=user_id,
                name=name,
                agent_type=agent_type,
                template=template
            )
            self.db_session.add(prompt_template)
        
        self.db_session.commit()
        return prompt_template
    
    def delete_template(self, template_id: int, user_id: int) -> bool:
        """Delete a template if it belongs to the user"""
        template = self.get_template(template_id)
        if template and template.user_id == user_id:
            self.db_session.delete(template)
            self.db_session.commit()
            return True
        return False