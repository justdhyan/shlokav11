from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper function to convert ObjectId to string
def str_id(obj):
    if obj and '_id' in obj:
        obj['_id'] = str(obj['_id'])
    return obj

# Define Models
class Emotion(BaseModel):
    id: str = Field(alias="_id")
    name_english: str
    name_sanskrit: str
    description: str
    icon: str

class Mood(BaseModel):
    id: str = Field(alias="_id")
    emotion_id: str
    name: str
    description: str

class Guidance(BaseModel):
    id: str = Field(alias="_id")
    mood_id: str
    title: str
    verse_reference: str  # e.g., "Bhagavad Gita 2.47"
    sanskrit_verse: str
    english_translation: str
    guidance_text: str

class BookmarkCreate(BaseModel):
    guidance_id: str

class Chapter(BaseModel):
    id: int = Field(alias="_id")
    chapter_number: int
    name_english: str
    name_sanskrit: str
    description: str
    key_teaching: str
    verses: List[dict]  # List of sample verses

# Initialize sample data
@app.on_event("startup")
async def startup_db():
    # Check if data already exists
    existing_emotions = await db.emotions.count_documents({})
    if existing_emotions > 0:
        logger.info("Sample data already exists")
        return
    
    # Sample emotions
    emotions = [
        {
            "_id": "fear",
            "name_english": "Fear",
            "name_sanskrit": "भय (Bhaya)",
            "description": "When you feel afraid, anxious, or worried about the future",
            "icon": "😰"
        },
        {
            "_id": "anger",
            "name_english": "Anger",
            "name_sanskrit": "क्रोध (Krodha)",
            "description": "When you feel frustrated, irritated, or filled with rage",
            "icon": "😠"
        },
        {
            "_id": "grief",
            "name_english": "Grief",
            "name_sanskrit": "शोक (Shoka)",
            "description": "When you feel sad, lost, or mourning a loss",
            "icon": "😢"
        },
        {
            "_id": "confusion",
            "name_english": "Confusion",
            "name_sanskrit": "मोह (Moha)",
            "description": "When you feel uncertain, lost, or unable to decide",
            "icon": "😕"
        },
        {
            "_id": "detachment",
            "name_english": "Detachment",
            "name_sanskrit": "वैराग्य (Vairagya)",
            "description": "When you feel disconnected, empty, or without purpose",
            "icon": "😶"
        }
    ]
    
    # Sample moods for each emotion
    moods = [
        # Fear moods
        {"_id": "fear_future", "emotion_id": "fear", "name": "Fear of the Future", "description": "Worried about what tomorrow will bring"},
        {"_id": "fear_death", "emotion_id": "fear", "name": "Fear of Death", "description": "Anxious about mortality and the unknown"},
        {"_id": "fear_failure", "emotion_id": "fear", "name": "Fear of Failure", "description": "Afraid of not being good enough"},
        
        # Anger moods
        {"_id": "anger_injustice", "emotion_id": "anger", "name": "Anger at Injustice", "description": "Upset about unfair treatment"},
        {"_id": "anger_self", "emotion_id": "anger", "name": "Anger at Myself", "description": "Frustrated with my own actions"},
        {"_id": "anger_world", "emotion_id": "anger", "name": "Anger at the World", "description": "Mad at how things are"},
        
        # Grief moods
        {"_id": "grief_loss", "emotion_id": "grief", "name": "Loss of a Loved One", "description": "Missing someone who has passed"},
        {"_id": "grief_change", "emotion_id": "grief", "name": "Loss of What Was", "description": "Mourning how things used to be"},
        {"_id": "grief_health", "emotion_id": "grief", "name": "Loss of Health", "description": "Struggling with physical decline"},
        
        # Confusion moods
        {"_id": "confusion_purpose", "emotion_id": "confusion", "name": "Lost About Purpose", "description": "Unsure why I am here"},
        {"_id": "confusion_choice", "emotion_id": "confusion", "name": "Unable to Decide", "description": "Don't know what to do"},
        {"_id": "confusion_meaning", "emotion_id": "confusion", "name": "Questioning Meaning", "description": "Wondering if life has meaning"},
        
        # Detachment moods
        {"_id": "detachment_loneliness", "emotion_id": "detachment", "name": "Feeling Alone", "description": "Disconnected from others"},
        {"_id": "detachment_emptiness", "emotion_id": "detachment", "name": "Inner Emptiness", "description": "Nothing brings joy anymore"},
        {"_id": "detachment_world", "emotion_id": "detachment", "name": "Withdrawn from Life", "description": "Don't care about worldly things"}
    ]
    
    # Sample guidance (with authentic Bhagavad Gita verses)
    guidances = [
        {
            "_id": "guidance_fear_future",
            "mood_id": "fear_future",
            "title": "Focus on Your Duty, Not Results",
            "verse_reference": "Bhagavad Gita 2.47",
            "sanskrit_verse": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
            "english_translation": "You have the right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself to be the cause of the results, nor be attached to inaction.",
            "guidance_text": "Krishna teaches that worry about tomorrow comes from attachment to results. Do your duty today with care, but release anxiety about outcomes. The future is shaped by present action, not by worry. Your power lies in what you do now, not in controlling what comes next."
        },
        {
            "_id": "guidance_fear_death",
            "mood_id": "fear_death",
            "title": "The Soul is Eternal",
            "verse_reference": "Bhagavad Gita 2.20",
            "sanskrit_verse": "न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः।\nअजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥",
            "english_translation": "The soul is never born and never dies. It is unborn, eternal, ever-existing, and primeval. The soul is not slain when the body is slain.",
            "guidance_text": "Death is only the body changing form, like removing old clothes. Your true self—the soul—is eternal and cannot be destroyed. Understanding this truth brings peace. What you truly are has always existed and will always exist."
        },
        {
            "_id": "guidance_anger_injustice",
            "mood_id": "anger_injustice",
            "title": "Anger Destroys Wisdom",
            "verse_reference": "Bhagavad Gita 2.63",
            "sanskrit_verse": "क्रोधाद्भवति संमोहः संमोहात्स्मृतिविभ्रमः।\nस्मृतिभ्रंशाद् बुद्धिनाशो बुद्धिनाशात्प्रणश्यति॥",
            "english_translation": "From anger comes delusion; from delusion, confusion of memory; from confusion of memory, loss of intelligence; and from loss of intelligence, one perishes.",
            "guidance_text": "When we see injustice, anger is natural. But Krishna warns that unchecked anger clouds our judgment and leads to more suffering. Channel your sense of justice into wise action, not destructive rage. True strength lies in responding with clarity, not reacting in fury."
        },
        {
            "_id": "guidance_grief_loss",
            "mood_id": "grief_loss",
            "title": "All Beings Follow Nature's Way",
            "verse_reference": "Bhagavad Gita 2.27",
            "sanskrit_verse": "जातस्य हि ध्रुवो मृत्युर्ध्रुवं जन्म मृतस्य च।\nतस्मादपरिहार्येऽर्थे न त्वं शोचितुमर्हसि॥",
            "english_translation": "For one who has taken birth, death is certain; and for one who has died, birth is certain. Therefore, you should not lament over the inevitable.",
            "guidance_text": "Your grief honors the love you shared. Krishna does not ask you to stop feeling—he acknowledges that loss is part of life's cycle. Allow yourself to grieve, but know that your loved one's journey continues. What was real in your relationship—the love—remains eternal."
        },
        {
            "_id": "guidance_confusion_purpose",
            "mood_id": "confusion_purpose",
            "title": "Surrender to the Divine Will",
            "verse_reference": "Bhagavad Gita 18.66",
            "sanskrit_verse": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।\nअहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
            "english_translation": "Abandon all varieties of dharma and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
            "guidance_text": "When you cannot see the path, trust that there is a larger design. Your purpose unfolds not through perfect understanding, but through sincere effort and faith. Do your best each day, and trust that the divine guides those who are open to guidance."
        },
        {
            "_id": "guidance_detachment_loneliness",
            "mood_id": "detachment_loneliness",
            "title": "You Are Never Alone",
            "verse_reference": "Bhagavad Gita 9.29",
            "sanskrit_verse": "समोऽहं सर्वभूतेषु न मे द्वेष्योऽस्ति न प्रियः।\nये भजन्ति तु मां भक्त्या मयि ते तेषु चाप्यहम्॥",
            "english_translation": "I am equal to all beings; none are hateful or dear to Me. But those who worship Me with devotion are in Me, and I am in them.",
            "guidance_text": "Loneliness comes from feeling separate. Krishna reveals that the divine presence dwells within you and all beings. You are connected to everything through this universal spirit. Even in solitude, you are held by something greater than yourself."
        }
    ]
    
    # Insert data
    await db.emotions.insert_many(emotions)
    await db.moods.insert_many(moods)
    await db.guidances.insert_many(guidances)
    
    logger.info("Sample data initialized successfully")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "SHLOKA API - Bhagavad Gita Guidance by Emotion"}

@api_router.get("/emotions", response_model=List[Emotion])
async def get_emotions():
    """Get all emotions"""
    emotions = await db.emotions.find().to_list(100)
    return [str_id(e) for e in emotions]

@api_router.get("/moods/{emotion_id}", response_model=List[Mood])
async def get_moods(emotion_id: str):
    """Get all moods for a specific emotion"""
    moods = await db.moods.find({"emotion_id": emotion_id}).to_list(100)
    if not moods:
        raise HTTPException(status_code=404, detail="No moods found for this emotion")
    return [str_id(m) for m in moods]

@api_router.get("/guidance/{mood_id}", response_model=Guidance)
async def get_guidance(mood_id: str):
    """Get guidance for a specific mood"""
    guidance = await db.guidances.find_one({"mood_id": mood_id})
    if not guidance:
        raise HTTPException(status_code=404, detail="Guidance not found for this mood")
    return str_id(guidance)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
