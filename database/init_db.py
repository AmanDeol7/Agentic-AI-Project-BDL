import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, PromptTemplate

def get_database_url():
    """Get database URL from environment or use default SQLite path"""
    db_path = os.environ.get('DB_PATH', 'sqlite:///database/agentic_assistant.db')
    return db_path

def init_db():
    """Initialize the database and create tables"""
    db_url = get_database_url()
    
    # Create database directory if it doesn't exist
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create engine and tables
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add default user if not exists
    default_user = session.query(User).filter_by(username="default").first()
    if not default_user:
        default_user = User(username="default")
        session.add(default_user)
        session.commit()
    
    # Add default prompt templates if not exists
    code_template = session.query(PromptTemplate).filter_by(
        user_id=default_user.id, agent_type="code_agent"
    ).first()
    
    if not code_template:
        default_code_template = """
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
        
        Context information:
        {% if documents %}
        Available documents:
        {% for doc in documents %}
        - {{ doc.filename }} ({{ doc.file_type }})
        {% endfor %}
        {% endif %}
        
        {% if conversation_history %}
        Relevant conversation history:
        {% for message in conversation_history %}
        {{ message.role }}: {{ message.content }}
        {% endfor %}
        {% endif %}
        """
        
        session.add(PromptTemplate(
            user_id=default_user.id,
            name="Default Code Template",
            agent_type="code_agent",
            template=default_code_template
        ))
    
    doc_template = session.query(PromptTemplate).filter_by(
        user_id=default_user.id, agent_type="doc_agent"
    ).first()
    
    if not doc_template:
        default_doc_template = """
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
        
        Context information:
        {% if documents %}
        Available documents:
        {% for doc in documents %}
        - {{ doc.filename }} ({{ doc.file_type }})
        {% endfor %}
        {% endif %}
        
        {% if conversation_history %}
        Relevant conversation history:
        {% for message in conversation_history %}
        {{ message.role }}: {{ message.content }}
        {% endfor %}
        {% endif %}
        """
        
        session.add(PromptTemplate(
            user_id=default_user.id,
            name="Default Document Template",
            agent_type="doc_agent",
            template=default_doc_template
        ))
    
    session.commit()
    session.close()
    
    return engine

def get_db_session():
    """Get a database session"""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")