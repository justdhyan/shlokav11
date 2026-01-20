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
        # Keep _id as-is if it's already int or string, otherwise convert ObjectId to string
        if isinstance(obj['_id'], (int, str)):
            pass  # Keep as-is
        else:
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
    
    class Config:
        populate_by_name = True

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
    
    # Sample chapters (all 18 chapters of Bhagavad Gita)
    chapters = [
        {
            "_id": 1,
            "chapter_number": 1,
            "name_english": "Arjuna's Dilemma",
            "name_sanskrit": "अर्जुनविषादयोग (Arjuna Vishada Yoga)",
            "description": "The first chapter describes how Arjuna, overwhelmed by grief and moral confusion on the battlefield, refuses to fight.",
            "key_teaching": "This chapter sets the stage for Krishna's teachings by showing Arjuna's spiritual crisis - a universal human experience of doubt and despair.",
            "verses": [
                {
                    "verse_number": "1.30",
                    "sanskrit": "निमित्तानि च पश्यामि विपरीतानि केशव।",
                    "english": "I see omens of evil, O Krishna. I do not see any good in killing my kinsmen in battle."
                }
            ]
        },
        {
            "_id": 2,
            "chapter_number": 2,
            "name_english": "The Eternal Reality of the Soul",
            "name_sanskrit": "सांख्ययोग (Sankhya Yoga)",
            "description": "Krishna explains the eternal nature of the soul and introduces the concepts of dharma and karma yoga.",
            "key_teaching": "The soul is eternal and indestructible. Focus on your duty without attachment to results.",
            "verses": [
                {
                    "verse_number": "2.20",
                    "sanskrit": "न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः।",
                    "english": "The soul is never born and never dies. It is unborn, eternal, ever-existing, and primeval."
                },
                {
                    "verse_number": "2.47",
                    "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
                    "english": "You have the right to perform your duty, but you are not entitled to the fruits of your actions."
                }
            ]
        },
        {
            "_id": 3,
            "chapter_number": 3,
            "name_english": "Path of Action",
            "name_sanskrit": "कर्मयोग (Karma Yoga)",
            "description": "Krishna explains the importance of selfless action and performing one's duty without desire for personal gain.",
            "key_teaching": "Perform your duties as an offering to the Divine, without attachment to outcomes.",
            "verses": [
                {
                    "verse_number": "3.19",
                    "sanskrit": "तस्मादसक्तः सततं कार्यं कर्म समाचर।",
                    "english": "Therefore, without attachment, constantly perform actions which are duty, for by performing actions without attachment, one attains the Supreme."
                }
            ]
        },
        {
            "_id": 4,
            "chapter_number": 4,
            "name_english": "Path of Knowledge",
            "name_sanskrit": "ज्ञानयोग (Jnana Yoga)",
            "description": "Krishna reveals the divine nature of his incarnations and the liberating power of spiritual knowledge.",
            "key_teaching": "Knowledge of the true self and the divine nature destroys all karma and leads to liberation.",
            "verses": [
                {
                    "verse_number": "4.7",
                    "sanskrit": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।",
                    "english": "Whenever there is a decline in righteousness and rise in unrighteousness, O Arjuna, at that time I manifest myself on earth."
                }
            ]
        },
        {
            "_id": 5,
            "chapter_number": 5,
            "name_english": "Path of Renunciation",
            "name_sanskrit": "सन्न्यासयोग (Sannyasa Yoga)",
            "description": "Krishna explains that both renunciation and selfless service lead to liberation, but selfless service is superior.",
            "key_teaching": "True renunciation is not abandoning action, but performing action without selfish desire.",
            "verses": [
                {
                    "verse_number": "5.10",
                    "sanskrit": "ब्रह्मण्याधाय कर्माणि सङ्गं त्यक्त्वा करोति यः।",
                    "english": "One who performs their duty without attachment, surrendering results unto the Supreme, is unaffected by sin."
                }
            ]
        },
        {
            "_id": 6,
            "chapter_number": 6,
            "name_english": "Path of Meditation",
            "name_sanskrit": "ध्यानयोग (Dhyana Yoga)",
            "description": "Krishna describes the practice of meditation and the characteristics of a true yogi.",
            "key_teaching": "Through meditation and self-control, one can achieve peace and ultimately unite with the Divine.",
            "verses": [
                {
                    "verse_number": "6.5",
                    "sanskrit": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।",
                    "english": "Elevate yourself through the power of your mind, and not degrade yourself, for the mind can be the friend and also the enemy of the self."
                }
            ]
        },
        {
            "_id": 7,
            "chapter_number": 7,
            "name_english": "Knowledge and Wisdom",
            "name_sanskrit": "ज्ञानविज्ञानयोग (Jnana Vijnana Yoga)",
            "description": "Krishna explains his divine nature and how he pervades all of creation.",
            "key_teaching": "Understanding that God is both the material and spiritual essence of all existence.",
            "verses": [
                {
                    "verse_number": "7.8",
                    "sanskrit": "रसोऽहमप्सु कौन्तेय प्रभास्मि शशिसूर्ययोः।",
                    "english": "I am the taste in water, O son of Kunti, and I am the light of the sun and moon."
                }
            ]
        },
        {
            "_id": 8,
            "chapter_number": 8,
            "name_english": "Path to the Supreme",
            "name_sanskrit": "अक्षरब्रह्मयोग (Aksara Brahma Yoga)",
            "description": "Krishna explains how to attain Him through constant remembrance, especially at the time of death.",
            "key_teaching": "Whatever one remembers at the time of death, one attains that state.",
            "verses": [
                {
                    "verse_number": "8.7",
                    "sanskrit": "तस्मात्सर्वेषु कालेषु मामनुस्मर युध्य च।",
                    "english": "Therefore, remember Me at all times and fight. With mind and intellect fixed on Me, you will surely come to Me."
                }
            ]
        },
        {
            "_id": 9,
            "chapter_number": 9,
            "name_english": "Royal Knowledge",
            "name_sanskrit": "राजविद्याराजगुह्ययोग (Raja Vidya Raja Guhya Yoga)",
            "description": "Krishna reveals the most confidential knowledge about devotion and His divine nature.",
            "key_teaching": "God accepts even the smallest offering made with love and devotion.",
            "verses": [
                {
                    "verse_number": "9.26",
                    "sanskrit": "पत्रं पुष्पं फलं तोयं यो मे भक्त्या प्रयच्छति।",
                    "english": "Whoever offers Me with devotion a leaf, a flower, a fruit, or water - I accept that offering of love from the pure-hearted."
                }
            ]
        },
        {
            "_id": 10,
            "chapter_number": 10,
            "name_english": "Divine Manifestations",
            "name_sanskrit": "विभूतियोग (Vibhuti Yoga)",
            "description": "Krishna describes His divine manifestations and how He pervades the entire universe.",
            "key_teaching": "God is present in all that is excellent, powerful, and beautiful in creation.",
            "verses": [
                {
                    "verse_number": "10.20",
                    "sanskrit": "अहमात्मा गुडाकेश सर्वभूताशयस्थितः।",
                    "english": "I am the Self, O Arjuna, seated in the hearts of all beings. I am the beginning, the middle, and also the end of all beings."
                }
            ]
        },
        {
            "_id": 11,
            "chapter_number": 11,
            "name_english": "Vision of the Universal Form",
            "name_sanskrit": "विश्वरूपदर्शनयोग (Vishvarupa Darshana Yoga)",
            "description": "Krishna reveals His cosmic form to Arjuna, showing the magnificence of the entire universe in His body.",
            "key_teaching": "God encompasses all of existence - the creator, preserver, and destroyer of all.",
            "verses": [
                {
                    "verse_number": "11.54",
                    "sanskrit": "भक्त्या त्वनन्यया शक्य अहमेवंविधोऽर्जुन।",
                    "english": "Only by undivided devotion can I be known and seen in this form, O Arjuna, and entered into."
                }
            ]
        },
        {
            "_id": 12,
            "chapter_number": 12,
            "name_english": "Path of Devotion",
            "name_sanskrit": "भक्तियोग (Bhakti Yoga)",
            "description": "Krishna explains that the path of devotion is the most direct way to reach Him.",
            "key_teaching": "Devotion to God with love and surrender is the highest path.",
            "verses": [
                {
                    "verse_number": "12.8",
                    "sanskrit": "मय्येव मन आधत्स्व मयि बुद्धिं निवेशय।",
                    "english": "Fix your mind on Me alone and let your intellect dwell upon Me. Thereafter you will live in Me without doubt."
                }
            ]
        },
        {
            "_id": 13,
            "chapter_number": 13,
            "name_english": "Field and Knower of the Field",
            "name_sanskrit": "क्षेत्रक्षेत्रज्ञविभागयोग (Kshetra Kshetrajna Vibhaga Yoga)",
            "description": "Krishna explains the distinction between the physical body (field) and the soul (knower of the field).",
            "key_teaching": "Understanding the difference between the body and the eternal soul is true knowledge.",
            "verses": [
                {
                    "verse_number": "13.2",
                    "sanskrit": "क्षेत्रज्ञं चापि मां विद्धि सर्वक्षेत्रेषु भारत।",
                    "english": "Know Me to be the Knower of the field in all fields, O Arjuna. Knowledge of the field and its Knower is true knowledge."
                }
            ]
        },
        {
            "_id": 14,
            "chapter_number": 14,
            "name_english": "Three Modes of Nature",
            "name_sanskrit": "गुणत्रयविभागयोग (Gunatraya Vibhaga Yoga)",
            "description": "Krishna explains the three gunas (modes of nature): sattva (goodness), rajas (passion), and tamas (ignorance).",
            "key_teaching": "Understanding the three gunas helps one transcend material nature and attain liberation.",
            "verses": [
                {
                    "verse_number": "14.5",
                    "sanskrit": "सत्त्वं रजस्तम इति गुणाः प्रकृतिसम्भवाः।",
                    "english": "Goodness, passion, and ignorance - these three modes born of nature bind the eternal soul to the body."
                }
            ]
        },
        {
            "_id": 15,
            "chapter_number": 15,
            "name_english": "The Supreme Person",
            "name_sanskrit": "पुरुषोत्तमयोग (Purushottama Yoga)",
            "description": "Krishna describes the imperishable tree of material existence and how to attain the supreme abode.",
            "key_teaching": "God is beyond both the perishable and imperishable, the Supreme Person who sustains all.",
            "verses": [
                {
                    "verse_number": "15.7",
                    "sanskrit": "ममैवांशो जीवलोके जीवभूतः सनातनः।",
                    "english": "The living entities in this world are My eternal fragmented parts, but bound by material nature, they struggle with the six senses including the mind."
                }
            ]
        },
        {
            "_id": 16,
            "chapter_number": 16,
            "name_english": "Divine and Demonic Natures",
            "name_sanskrit": "दैवासुरसम्पद्विभागयोग (Daivasura Sampad Vibhaga Yoga)",
            "description": "Krishna contrasts divine and demonic qualities, explaining which lead to liberation and which to bondage.",
            "key_teaching": "Cultivate divine qualities like truthfulness, compassion, and humility; avoid demonic qualities like pride, anger, and arrogance.",
            "verses": [
                {
                    "verse_number": "16.3",
                    "sanskrit": "तेजः क्षमा धृतिः शौचमद्रोहो नातिमानिता।",
                    "english": "Vigor, forgiveness, fortitude, purity, absence of hatred, and absence of pride - these are the qualities of those endowed with divine nature."
                }
            ]
        },
        {
            "_id": 17,
            "chapter_number": 17,
            "name_english": "Three Divisions of Faith",
            "name_sanskrit": "श्रद्धात्रयविभागयोग (Shraddhatraya Vibhaga Yoga)",
            "description": "Krishna explains how faith manifests according to one's nature and the three types of faith.",
            "key_teaching": "Faith aligned with goodness leads to divinity; faith in passion or ignorance leads to bondage.",
            "verses": [
                {
                    "verse_number": "17.3",
                    "sanskrit": "सत्त्वानुरूपा सर्वस्य श्रद्धा भवति भारत।",
                    "english": "The faith of all beings conforms to their mental disposition, O Arjuna. A person is known by the faith they hold."
                }
            ]
        },
        {
            "_id": 18,
            "chapter_number": 18,
            "name_english": "Liberation through Renunciation",
            "name_sanskrit": "मोक्षसंन्यासयोग (Moksha Sannyasa Yoga)",
            "description": "The final chapter summarizes all the teachings and emphasizes complete surrender to God.",
            "key_teaching": "Surrender all actions to God, perform your duty without attachment, and you will attain liberation.",
            "verses": [
                {
                    "verse_number": "18.66",
                    "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।",
                    "english": "Abandon all varieties of dharma and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear."
                },
                {
                    "verse_number": "18.78",
                    "sanskrit": "यत्र योगेश्वरः कृष्णो यत्र पार्थो धनुर्धरः।",
                    "english": "Wherever there is Krishna, the Lord of Yoga, and Arjuna, the wielder of the bow, there will be fortune, victory, prosperity, and morality."
                }
            ]
        }
    ]
    
    # Insert data
    await db.emotions.insert_many(emotions)
    await db.moods.insert_many(moods)
    await db.guidances.insert_many(guidances)
    await db.chapters.insert_many(chapters)
    
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

@api_router.get("/chapters")
async def get_chapters():
    """Get all chapters of Bhagavad Gita"""
    chapters = await db.chapters.find().sort("chapter_number", 1).to_list(100)
    return [str_id(c) for c in chapters]

@api_router.get("/chapters/{chapter_number}")
async def get_chapter(chapter_number: int):
    """Get a specific chapter by number"""
    chapter = await db.chapters.find_one({"chapter_number": chapter_number})
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return str_id(chapter)

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
