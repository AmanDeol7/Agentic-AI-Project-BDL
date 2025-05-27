import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.models import Base, User, PromptTemplate, Session as ChatSession, Message, Document
from config.app_config import DATABASE_URL

def get_database_url() -> str:
    return DATABASE_URL

def init_db(engine=None) -> any:
    if engine is None:
        db_url = get_database_url()
        if db_url.startswith("sqlite:///"):
            if db_url.startswith("sqlite:///./"):
                db_file_path = db_url.replace("sqlite:///./", "", 1)
                db_file_path = os.path.join(os.getcwd(), db_file_path)
            elif db_url.startswith("sqlite:///"):
                db_file_path = db_url.replace("sqlite:///", "", 1)
                if not os.path.isabs(db_file_path):
                    db_file_path = os.path.join(PROJECT_ROOT, db_file_path)
            db_dir = os.path.dirname(db_file_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created database directory: {db_dir}")
        engine = create_engine(db_url)

    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created.")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db: SQLAlchemySession = SessionLocal()

    try:
        default_username = "default_user"
        default_user = db.query(User).filter_by(username=default_username).first()
        if not default_user:
            default_user = User(username=default_username)
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            print(f"Created default user: {default_username} (ID: {default_user.id})")
        else:
            print(f"Default user '{default_username}' (ID: {default_user.id}) already exists.")

        default_templates = [
            {
                "name": "Default Code Agent Template",
                "agent_type": "code_agent",
                "template": """You are a helpful and proficient AI Code Assistant.
Your primary goal is to generate accurate, efficient, and well-documented code based on the user's requirements.

User's request:
{{ user_query }}

{% if documents %}
You have access to the following documents:
{% for doc in documents %}
- {{ doc.filename }} ({{ doc.file_type }})
{% endfor %}
Please use their content if relevant.
{% endif %}

{% if conversation_history %}
Recent conversation:
{{ conversation_history }}
{% endif %}

Please provide the code solution. If necessary, also provide a brief explanation of your code.
Format the code within appropriate markdown code blocks (e.g., ```python ... ```).
""",
                "is_default": True,
            },
            {
                "name": "Default Document Agent Template",
                "agent_type": "doc_agent",
                "template": """You are an intelligent AI Document Assistant.
Your task is to analyze the provided documents and answer user questions, summarize content, or extract information.

User's request:
{{ user_query }}

{% if documents %}
You are working with the following documents:
{% for doc in documents %}
- {{ doc.filename }} ({{ doc.file_type }})
{% endfor %}
Base your answers strictly on the content of these documents.
{% else %}
No documents are currently loaded. Please ask the user to upload documents for analysis.
{% endif %}

{% if conversation_history %}
Recent conversation:
{{ conversation_history }}
{% endif %}

Please provide a clear and concise response. If quoting from a document, indicate the source if possible.
""",
                "is_default": True,
            },
        ]

        for temp_data in default_templates:
            existing_template = (
                db.query(PromptTemplate)
                .filter_by(
                    user_id=default_user.id,
                    agent_type=temp_data["agent_type"],
                    name=temp_data["name"],
                    is_default=True
                )
                .first()
            )
            if not existing_template:
                new_template = PromptTemplate(
                    user_id=default_user.id,
                    name=temp_data["name"],
                    agent_type=temp_data["agent_type"],
                    template=temp_data["template"],
                    is_default=temp_data["is_default"],
                )
                db.add(new_template)
                print(f"Added default template: '{temp_data['name']}' for user '{default_username}'")
        db.commit()
        print("Default data checked/populated.")

    except Exception as e:
        db.rollback()
        print(f"Error during database initialization: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    return engine

def get_db_session(engine=None) -> SQLAlchemySession:
    if engine is None:
        engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

if __name__ == "__main__":
    print("Initializing database...")
    main_engine = init_db()
    if main_engine:
        print(f"Database initialized successfully using URL: {str(main_engine.url)}")
    else:
        print("Database initialization failed.")
