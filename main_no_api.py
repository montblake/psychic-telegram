from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, ValidationError

# Define SQLAlchemy ORM model
Base = declarative_base()
class Paragraph(Base):
    __tablename__ = 'paragraphs'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

# Create SQLite DB
engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Define Pydantic model for validation
class ParagraphModel(BaseModel):
    content: str

# Read Paragraphs from a text file
def read_paragraphs(path_object):
    with path_object.open('r', encoding='utf8') as file:
        return file.read().split('\n\n') # assumning input string has paragraphs separated by a blank line.
    
# Process and add paragraphs to the database
def add_paragraphs_to_db(paragraphs):
    for para in paragraphs:
        try:
            # Validate paragraph
            valid_paragraph = ParagraphModel(content=para)
            #Add to DB
            new_para = Paragraph(content=valid_paragraph.content)
            session.add(new_para)
        except ValidationError as e:
            print(f"Validation error: {e}")

    session.commit()

# Example usage
print("processing begun")
file_path = Path('./resources/bobby.txt')
print("file_path", file_path)
paragraphs = read_paragraphs(file_path)
print("paragraphs separated")
add_paragraphs_to_db(paragraphs)
print("processing complete")
