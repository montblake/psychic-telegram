from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Mapped
from typing import List, Optional
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy setup
Base = declarative_base()

class Chapter(Base):
    __tablename__ = 'chapters'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    paragraphs = relationship("Paragraph", back_populates="chapter")
    
class Paragraph(Base):
    __tablename__ = 'paragraphs'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    index_within_chapter = Column(Integer)
    chapter_id = Column(Integer, ForeignKey('chapters.id'))
    chapter = relationship("Chapter", back_populates="paragraphs")



engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

#Get all chapters
@app.get("/chapters/")
async def get_chapters():
    session = Session()
    try:
        chapters = session.query(Chapter).all()
        return chapters
    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    finally:
        session.close()

@app.get("/chapters/{chapter_id}/paragraphs/")
async def get_paragraphs(chapter_id: int):
    session = Session()
    try:
        # Get all paragraphs for a chapter
        # paragraphs should be ordered by index_within_chapter
        paragraphs = session.query(Paragraph).filter(Paragraph.chapter_id == chapter_id).order_by(Paragraph.index_within_chapter).all()
        return paragraphs
    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    finally:
        session.close()

# Endpoint to upload and process the file
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    session = Session()
    try:

        # Create new chapter with title === file 
        # you will need to get the id of the chapter to add to the paragraphs
        new_chapter = Chapter(title=file.filename.partition('.')[0])
        session.add(new_chapter)
        session.commit()
        

        # Async reading of the file
        content = await file.read()
        print("CONTENT", content)
        readable_content = content.decode()
        print("READABLE CONTENT", readable_content)
        paragraphs = readable_content.split('\n\n')  # Assuming each paragraph is separated by two newlines

        # Create new paragraph for each paragraph in the file
        for index, para in enumerate(paragraphs):
            new_para = Paragraph(content=para, index_within_chapter=index, chapter_id=new_chapter.id)
            session.add(new_para)

        session.commit()
    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    finally:
        session.close()

    return {"message": f"File '{file.filename}' processed successfully"}

# Endpoint to check if server is online
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<html><body><h1>Hi, Friends.</h1><p>This is weird.</p></body></html>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
