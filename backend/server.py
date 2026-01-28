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
    # Clear existing data to allow updates
    await db.emotions.delete_many({})
    await db.moods.delete_many({})
    await db.guidances.delete_many({})
    
    # Check if chapters data exists
    existing_chapters = await db.chapters.count_documents({})
    
    if existing_chapters > 0:
        logger.info("Chapters data already exists, re-initializing emotions, moods, and guidances")
    else:
        logger.info("Initializing all data")
    
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
        },
        {
            "_id": "joy",
            "name_english": "Joy",
            "name_sanskrit": "आनंद (Ananda)",
            "description": "When you feel content, peaceful, or grateful for life's blessings",
            "icon": "😊"
        },
        {
            "_id": "doubt",
            "name_english": "Doubt",
            "name_sanskrit": "संशय (Sanshaya)",
            "description": "When you question your faith, beliefs, or the path you're on",
            "icon": "🤔"
        },
        {
            "_id": "pride",
            "name_english": "Pride",
            "name_sanskrit": "अहंकार (Ahamkara)",
            "description": "When you feel superior, self-important, or overly confident",
            "icon": "😤"
        },
        {
            "_id": "desire",
            "name_english": "Desire",
            "name_sanskrit": "काम (Kama)",
            "description": "When you experience strong cravings, wants, or material attachments",
            "icon": "🤲"
        },
        {
            "_id": "envy",
            "name_english": "Envy",
            "name_sanskrit": "ईर्ष्या (Irshya)",
            "description": "When you compare yourself to others or feel jealous of their fortune",
            "icon": "😒"
        },
        {
            "_id": "despair",
            "name_english": "Despair",
            "name_sanskrit": "निराशा (Nirasha)",
            "description": "When you feel hopeless, defeated, or without direction in life",
            "icon": "😞"
        }
    ]
    
    # Sample moods for each emotion
    moods = [
        # Fear moods (6 total)
        {"_id": "fear_future", "emotion_id": "fear", "name": "Fear of the Future", "description": "Worried about what tomorrow will bring"},
        {"_id": "fear_death", "emotion_id": "fear", "name": "Fear of Death", "description": "Anxious about mortality and the unknown"},
        {"_id": "fear_failure", "emotion_id": "fear", "name": "Fear of Failure", "description": "Afraid of not being good enough"},
        {"_id": "fear_illness", "emotion_id": "fear", "name": "Fear of Illness", "description": "Worried about health and disease"},
        {"_id": "fear_abandonment", "emotion_id": "fear", "name": "Fear of Being Alone", "description": "Afraid of losing loved ones"},
        {"_id": "fear_change", "emotion_id": "fear", "name": "Fear of Change", "description": "Scared of life's transitions"},
        
        # Anger moods (6 total)
        {"_id": "anger_injustice", "emotion_id": "anger", "name": "Anger at Injustice", "description": "Upset about unfair treatment"},
        {"_id": "anger_self", "emotion_id": "anger", "name": "Anger at Myself", "description": "Frustrated with my own actions"},
        {"_id": "anger_world", "emotion_id": "anger", "name": "Anger at the World", "description": "Mad at how things are"},
        {"_id": "anger_betrayal", "emotion_id": "anger", "name": "Anger at Betrayal", "description": "Hurt by broken trust"},
        {"_id": "anger_powerless", "emotion_id": "anger", "name": "Anger at Helplessness", "description": "Frustrated by inability to help"},
        {"_id": "anger_disrespect", "emotion_id": "anger", "name": "Anger at Disrespect", "description": "Offended by lack of regard"},
        
        # Grief moods (6 total)
        {"_id": "grief_loss", "emotion_id": "grief", "name": "Loss of a Loved One", "description": "Missing someone who has passed"},
        {"_id": "grief_change", "emotion_id": "grief", "name": "Loss of What Was", "description": "Mourning how things used to be"},
        {"_id": "grief_health", "emotion_id": "grief", "name": "Loss of Health", "description": "Struggling with physical decline"},
        {"_id": "grief_dream", "emotion_id": "grief", "name": "Loss of a Dream", "description": "Mourning unfulfilled hopes"},
        {"_id": "grief_relationship", "emotion_id": "grief", "name": "Loss of Relationship", "description": "Grieving a ended connection"},
        {"_id": "grief_youth", "emotion_id": "grief", "name": "Loss of Youth", "description": "Sadness about aging"},
        
        # Confusion moods (6 total)
        {"_id": "confusion_purpose", "emotion_id": "confusion", "name": "Lost About Purpose", "description": "Unsure why I am here"},
        {"_id": "confusion_choice", "emotion_id": "confusion", "name": "Unable to Decide", "description": "Don't know what to do"},
        {"_id": "confusion_meaning", "emotion_id": "confusion", "name": "Questioning Meaning", "description": "Wondering if life has meaning"},
        {"_id": "confusion_identity", "emotion_id": "confusion", "name": "Lost Sense of Self", "description": "Not sure who I am anymore"},
        {"_id": "confusion_direction", "emotion_id": "confusion", "name": "No Clear Path", "description": "Don't know where to go"},
        {"_id": "confusion_values", "emotion_id": "confusion", "name": "Conflicting Beliefs", "description": "Torn between different values"},
        
        # Detachment moods (6 total)
        {"_id": "detachment_loneliness", "emotion_id": "detachment", "name": "Feeling Alone", "description": "Disconnected from others"},
        {"_id": "detachment_emptiness", "emotion_id": "detachment", "name": "Inner Emptiness", "description": "Nothing brings joy anymore"},
        {"_id": "detachment_world", "emotion_id": "detachment", "name": "Withdrawn from Life", "description": "Don't care about worldly things"},
        {"_id": "detachment_numb", "emotion_id": "detachment", "name": "Feeling Numb", "description": "Can't feel emotions anymore"},
        {"_id": "detachment_apathy", "emotion_id": "detachment", "name": "Lost Interest", "description": "Nothing seems important"},
        {"_id": "detachment_tired", "emotion_id": "detachment", "name": "Weary of Life", "description": "Exhausted from living"},
        
        # Joy moods (6 total)
        {"_id": "joy_gratitude", "emotion_id": "joy", "name": "Feeling Grateful", "description": "Thankful for life's blessings"},
        {"_id": "joy_peace", "emotion_id": "joy", "name": "Inner Peace", "description": "Content and at ease with life"},
        {"_id": "joy_acceptance", "emotion_id": "joy", "name": "Accepting What Is", "description": "At peace with how things are"},
        {"_id": "joy_serenity", "emotion_id": "joy", "name": "Deep Serenity", "description": "Calm amidst life's storms"},
        {"_id": "joy_connection", "emotion_id": "joy", "name": "Spiritual Connection", "description": "Feeling close to the divine"},
        {"_id": "joy_wisdom", "emotion_id": "joy", "name": "Blessed with Wisdom", "description": "Understanding life's lessons"},
        
        # Doubt moods (6 total)
        {"_id": "doubt_faith", "emotion_id": "doubt", "name": "Questioning Faith", "description": "Unsure if God exists or cares"},
        {"_id": "doubt_teachings", "emotion_id": "doubt", "name": "Doubting the Path", "description": "Wondering if these teachings are true"},
        {"_id": "doubt_self", "emotion_id": "doubt", "name": "Doubting Myself", "description": "Not sure if I'm doing things right"},
        {"_id": "doubt_goodness", "emotion_id": "doubt", "name": "Doubting Goodness", "description": "Questioning if good prevails"},
        {"_id": "doubt_purpose", "emotion_id": "doubt", "name": "Doubting Life's Purpose", "description": "Wondering if anything matters"},
        {"_id": "doubt_karma", "emotion_id": "doubt", "name": "Doubting Justice", "description": "Questioning if actions have consequences"},
        
        # Pride moods (6 total)
        {"_id": "pride_achievement", "emotion_id": "pride", "name": "Pride in Success", "description": "Feeling superior due to accomplishments"},
        {"_id": "pride_knowledge", "emotion_id": "pride", "name": "Pride in Knowledge", "description": "Thinking I know more than others"},
        {"_id": "pride_status", "emotion_id": "pride", "name": "Pride in Position", "description": "Feeling important due to my status"},
        {"_id": "pride_appearance", "emotion_id": "pride", "name": "Pride in Appearance", "description": "Vain about how I look"},
        {"_id": "pride_virtue", "emotion_id": "pride", "name": "Pride in Righteousness", "description": "Feeling morally superior"},
        {"_id": "pride_independence", "emotion_id": "pride", "name": "Pride in Self-Sufficiency", "description": "Refusing to need anyone"},
        
        # Desire moods (6 total)
        {"_id": "desire_wealth", "emotion_id": "desire", "name": "Craving Wealth", "description": "Strong desire for money and possessions"},
        {"_id": "desire_pleasure", "emotion_id": "desire", "name": "Seeking Pleasure", "description": "Always wanting more enjoyment"},
        {"_id": "desire_control", "emotion_id": "desire", "name": "Need to Control", "description": "Wanting things to go my way"},
        {"_id": "desire_recognition", "emotion_id": "desire", "name": "Craving Recognition", "description": "Wanting praise and attention"},
        {"_id": "desire_comfort", "emotion_id": "desire", "name": "Attached to Comfort", "description": "Avoiding any discomfort"},
        {"_id": "desire_security", "emotion_id": "desire", "name": "Craving Security", "description": "Needing guarantees and certainty"},
        
        # Envy moods (6 total)
        {"_id": "envy_success", "emotion_id": "envy", "name": "Envying Others' Success", "description": "Jealous of what others have achieved"},
        {"_id": "envy_happiness", "emotion_id": "envy", "name": "Envying Others' Joy", "description": "Wishing I had their peace and happiness"},
        {"_id": "envy_fortune", "emotion_id": "envy", "name": "Envying Others' Fortune", "description": "Comparing my life unfavorably to theirs"},
        {"_id": "envy_youth", "emotion_id": "envy", "name": "Envying the Young", "description": "Wishing I had their energy and time"},
        {"_id": "envy_family", "emotion_id": "envy", "name": "Envying Others' Families", "description": "Jealous of their relationships"},
        {"_id": "envy_health", "emotion_id": "envy", "name": "Envying Others' Health", "description": "Wishing I had their vitality"},
        
        # Despair moods (6 total)
        {"_id": "despair_effort", "emotion_id": "despair", "name": "Feeling It's Pointless", "description": "Nothing I do seems to matter"},
        {"_id": "despair_alone", "emotion_id": "despair", "name": "No One Understands", "description": "Feeling isolated in my struggles"},
        {"_id": "despair_future", "emotion_id": "despair", "name": "No Hope for Tomorrow", "description": "Can't see things getting better"},
        {"_id": "despair_burden", "emotion_id": "despair", "name": "Too Heavy to Bear", "description": "Life feels overwhelming"},
        {"_id": "despair_mistakes", "emotion_id": "despair", "name": "Haunted by Regrets", "description": "Can't forgive past errors"},
        {"_id": "despair_meaning", "emotion_id": "despair", "name": "Life Feels Meaningless", "description": "Everything seems empty"}
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
        },
        {
            "_id": "guidance_joy_gratitude",
            "mood_id": "joy_gratitude",
            "title": "Offer Your Joy to the Divine",
            "verse_reference": "Bhagavad Gita 9.26",
            "sanskrit_verse": "पत्रं पुष्पं फलं तोयं यो मे भक्त्या प्रयच्छति।\nतदहं भक्त्युपहृतमश्नामि प्रयतात्मनः॥",
            "english_translation": "Whoever offers Me with devotion a leaf, a flower, a fruit, or water - I accept that offering of love from the pure-hearted.",
            "guidance_text": "Your gratitude is itself a form of worship. Krishna teaches that the simplest offering, given with love, reaches the divine. When you feel thankful, recognize that joy as a gift. Share it, express it, and let it deepen your connection to all that sustains you."
        },
        {
            "_id": "guidance_joy_peace",
            "mood_id": "joy_peace",
            "title": "The Peace Beyond Understanding",
            "verse_reference": "Bhagavad Gita 2.71",
            "sanskrit_verse": "विहाय कामान्यः सर्वान्पुमांश्चरति निःस्पृहः।\nनिर्ममो निरहङ्कारः स शान्तिमधिगच्छति॥",
            "english_translation": "One who has given up all desires for sense gratification, who lives free from desires, who has given up all sense of proprietorship and is devoid of false ego—he alone can attain real peace.",
            "guidance_text": "True peace comes not from having everything, but from wanting nothing beyond what is. Your contentment reflects spiritual maturity. Krishna honors this state as the foundation of lasting happiness. Cherish this peace and let it guide your choices."
        },
        {
            "_id": "guidance_joy_acceptance",
            "mood_id": "joy_acceptance",
            "title": "Equanimity in All Circumstances",
            "verse_reference": "Bhagavad Gita 2.48",
            "sanskrit_verse": "योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।\nसिद्ध्यसिद्ध्योः समो भूत्वा समत्वं योग उच्यते॥",
            "english_translation": "Perform your duty with a steady mind, O Arjuna, abandoning attachment to success and failure. Such equanimity is called yoga.",
            "guidance_text": "Acceptance is not resignation—it is wisdom. By accepting what is, you free yourself from the burden of constant resistance. Krishna teaches that equanimity in both joy and sorrow is the mark of a yogi. This acceptance allows you to act with clarity and purpose."
        },
        {
            "_id": "guidance_doubt_faith",
            "mood_id": "doubt_faith",
            "title": "Faith Destroys Doubt",
            "verse_reference": "Bhagavad Gita 4.40",
            "sanskrit_verse": "अज्ञश्चाश्रद्दधानश्च संशयात्मा विनश्यति।\nनायं लोकोऽस्ति न परो न सुखं संशयात्मनः॥",
            "english_translation": "But ignorant and faithless persons who doubt the revealed scriptures do not attain God consciousness. For the doubting soul there is happiness neither in this world nor in the next.",
            "guidance_text": "Doubt is natural, but dwelling in it brings suffering. Krishna acknowledges that faith requires courage—believing in what cannot be proven. Your questioning shows you are thinking deeply. Now take the next step: choose faith and see where it leads. Experience will dissolve doubt better than argument."
        },
        {
            "_id": "guidance_doubt_teachings",
            "mood_id": "doubt_teachings",
            "title": "Test the Teachings Through Practice",
            "verse_reference": "Bhagavad Gita 18.73",
            "sanskrit_verse": "अर्जुन उवाच\nनष्टो मोहः स्मृतिर्लब्धा त्वत्प्रसादान्मयाच्युत।\nस्थितोऽस्मि गतसन्देहः करिष्ये वचनं तव॥",
            "english_translation": "Arjuna said: My illusion has been destroyed and I have gained understanding through Your grace. I am now firm and free from doubt, and I will act according to Your instruction.",
            "guidance_text": "Arjuna also doubted at first—his transformation came through listening and practicing. Don't expect to understand everything immediately. Apply what resonates, observe the results in your life. The Gita's truth reveals itself through sincere practice, not mere intellectual study."
        },
        {
            "_id": "guidance_doubt_self",
            "mood_id": "doubt_self",
            "title": "Trust Your Inner Wisdom",
            "verse_reference": "Bhagavad Gita 6.5",
            "sanskrit_verse": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
            "english_translation": "Elevate yourself through the power of your mind, and not degrade yourself, for the mind can be the friend and also the enemy of the self.",
            "guidance_text": "Self-doubt weakens you. Krishna teaches that you have the power to lift yourself up or bring yourself down. When you doubt, remember: you have within you the same divine spark that powers all creation. Act with what wisdom you have, and trust that you will learn as you go."
        },
        {
            "_id": "guidance_pride_achievement",
            "mood_id": "pride_achievement",
            "title": "You Are Not the Doer",
            "verse_reference": "Bhagavad Gita 3.27",
            "sanskrit_verse": "प्रकृतेः क्रियमाणानि गुणैः कर्माणि सर्वशः।\nअहङ्कारविमूढात्मा कर्ताहमिति मन्यते॥",
            "english_translation": "All actions are performed by the modes of material nature, but the soul deluded by false ego thinks, 'I am the doer.'",
            "guidance_text": "Your achievements came through a combination of effort, circumstances, support from others, and forces beyond your control. Krishna reminds us that ego makes us think 'I did this alone.' Recognize your role, but also honor all that made success possible. Gratitude dissolves pride."
        },
        {
            "_id": "guidance_pride_knowledge",
            "mood_id": "pride_knowledge",
            "title": "True Knowledge Brings Humility",
            "verse_reference": "Bhagavad Gita 13.8",
            "sanskrit_verse": "अमानित्वमदम्भित्वमहिंसा क्षान्तिरार्जवम्।\nआचार्योपासनं शौचं स्थैर्यमात्मविनिग्रहः॥",
            "english_translation": "Humility, modesty, nonviolence, tolerance, simplicity, approaching a bona fide spiritual master, cleanliness, steadiness, self-control—these are the qualities of true knowledge.",
            "guidance_text": "If knowledge makes you proud, you have not truly understood. Real wisdom makes one humble, because it reveals how much remains unknown. The wise person knows that all knowledge comes from a source beyond themselves. Let your learning inspire reverence, not arrogance."
        },
        {
            "_id": "guidance_pride_status",
            "mood_id": "pride_status",
            "title": "All Positions Are Temporary",
            "verse_reference": "Bhagavad Gita 2.14",
            "sanskrit_verse": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
            "english_translation": "The contact of the senses with their objects, O son of Kunti, gives rise to heat and cold, pleasure and pain. These are temporary and come and go like seasons. Learn to endure them.",
            "guidance_text": "Status, like all worldly things, is fleeting. The position you hold today may be gone tomorrow. Krishna teaches that what matters is not your title, but your character and actions. Don't identify with your role—you are far more than any position you occupy."
        },
        {
            "_id": "guidance_desire_wealth",
            "mood_id": "desire_wealth",
            "title": "Desire Leads to Endless Suffering",
            "verse_reference": "Bhagavad Gita 2.62-63",
            "sanskrit_verse": "ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते।\nसङ्गात्सञ्जायते कामः कामात्क्रोधोऽभिजायते॥",
            "english_translation": "While contemplating the objects of the senses, a person develops attachment for them. From attachment comes desire, and from desire arises anger.",
            "guidance_text": "The more you focus on what you want, the more enslaved you become. Krishna warns that desire is never satisfied—fulfilling one only creates another. True wealth is contentment. Ask yourself: what do you truly need? Freedom comes not from having more, but from wanting less."
        },
        {
            "_id": "guidance_desire_pleasure",
            "mood_id": "desire_pleasure",
            "title": "Temporary Pleasures Bring Lasting Pain",
            "verse_reference": "Bhagavad Gita 5.22",
            "sanskrit_verse": "ये हि संस्पर्शजा भोगा दुःखयोनय एव ते।\nआद्यन्तवन्तः कौन्तेय न तेषु रमते बुधः॥",
            "english_translation": "The pleasures that arise from contact with sense objects are sources of misery and have a beginning and an end. The wise, O son of Kunti, do not rejoice in them.",
            "guidance_text": "Pleasures derived from the senses seem sweet at first, but they fade quickly, leaving you empty and wanting more. Krishna teaches that the wise find joy within, not in fleeting sensations. Seek lasting contentment through spiritual practice, not temporary thrills."
        },
        {
            "_id": "guidance_desire_control",
            "mood_id": "desire_control",
            "title": "Surrender Control to Find Peace",
            "verse_reference": "Bhagavad Gita 18.66",
            "sanskrit_verse": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।\nअहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
            "english_translation": "Abandon all varieties of dharma and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
            "guidance_text": "The need to control everything is exhausting and ultimately impossible. Krishna invites you to release this burden. Do your part with sincerity, but trust the larger process. Surrender doesn't mean giving up—it means acting without the anxiety of trying to control everything."
        },
        {
            "_id": "guidance_envy_success",
            "mood_id": "envy_success",
            "title": "Each Has Their Own Path",
            "verse_reference": "Bhagavad Gita 3.35",
            "sanskrit_verse": "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।\nस्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥",
            "english_translation": "It is better to perform one's own duty imperfectly than to perform another's duty perfectly. It is better to die doing one's own duty; another's duty is fraught with danger.",
            "guidance_text": "Comparing yourself to others is a trap. Their path is not yours. Krishna teaches that you must walk your own road, however humble it may seem. Your journey has unique meaning. Envy blinds you to your own gifts and the special contribution only you can make."
        },
        {
            "_id": "guidance_envy_happiness",
            "mood_id": "envy_happiness",
            "title": "Rejoice in Others' Good Fortune",
            "verse_reference": "Bhagavad Gita 12.13-14",
            "sanskrit_verse": "अद्वेष्टा सर्वभूतानां मैत्रः करुण एव च।\nनिर्ममो निरहङ्कारः समदुःखसुखः क्षमी॥",
            "english_translation": "One who is not envious but is a kind friend to all, who does not think himself a proprietor, who is free from false ego and equal in both happiness and distress—such a person is very dear to Me.",
            "guidance_text": "Another person's joy does not diminish yours. Krishna values those who can celebrate others' happiness without jealousy. Practice wishing well for those you envy—it will free you. Remember, their contentment doesn't block yours. There is enough grace for everyone."
        },
        {
            "_id": "guidance_envy_fortune",
            "mood_id": "envy_fortune",
            "title": "Your Journey Unfolds as It Should",
            "verse_reference": "Bhagavad Gita 18.46",
            "sanskrit_verse": "यतः प्रवृत्तिर्भूतानां येन सर्वमिदं ततम्।\nस्वकर्मणा तमभ्यर्च्य सिद्धिं विन्दति मानवः॥",
            "english_translation": "By performing one's own duty, worshiping the Lord from whom all beings have come and by whom the whole universe is pervaded, a person attains perfection.",
            "guidance_text": "You see only a snapshot of others' lives, not their struggles or sorrows. Krishna reminds you that each person's karma unfolds uniquely. Instead of coveting what others have, focus on fulfilling your own purpose. Your path leads somewhere meaningful, even if you can't see it yet."
        },
        {
            "_id": "guidance_despair_effort",
            "mood_id": "despair_effort",
            "title": "No Effort Is Ever Wasted",
            "verse_reference": "Bhagavad Gita 2.40",
            "sanskrit_verse": "नेहाभिक्रमनाशोऽस्ति प्रत्यवायो न विद्यते।\nस्वल्पमप्यस्य धर्मस्य त्रायते महतो भयात्॥",
            "english_translation": "In this endeavor there is no loss or diminution, and even a little advancement on this path can protect one from the most dangerous fear.",
            "guidance_text": "When you feel nothing matters, remember Krishna's promise: no sincere effort is ever lost. Even small acts of dharma accumulate. You may not see results immediately, but every right action plants seeds. The universe wastes nothing. Your efforts matter, even when results are invisible."
        },
        {
            "_id": "guidance_despair_alone",
            "mood_id": "despair_alone",
            "title": "The Divine Witness Sees All",
            "verse_reference": "Bhagavad Gita 13.23",
            "sanskrit_verse": "उपद्रष्टानुमन्ता च भर्ता भोक्ता महेश्वरः।\nपरमात्मेति चाप्युक्तो देहेऽस्मिन्पुरुषः परः॥",
            "english_translation": "Yet in this body there is another, the transcendent Lord, who is the supreme observer, the permitter, the supporter, the experiencer, and the ultimate controller, called the Supersoul.",
            "guidance_text": "You are never truly alone in your suffering. Krishna reveals that the divine presence within witnesses every moment of your struggle. Your pain is seen, your effort is known. This presence understands you completely, even when no human does. Find comfort in this eternal companionship."
        },
        {
            "_id": "guidance_despair_future",
            "mood_id": "despair_future",
            "title": "Darkness Precedes Dawn",
            "verse_reference": "Bhagavad Gita 2.69",
            "sanskrit_verse": "या निशा सर्वभूतानां तस्यां जागर्ति संयमी।\nयस्यां जाग्रति भूतानि सा निशा पश्यतो मुनेः॥",
            "english_translation": "What is night for all beings is the time of awakening for the self-controlled; and the time of awakening for all beings is night for the introspective sage.",
            "guidance_text": "When you cannot see hope, it doesn't mean there is none. Sometimes the darkest hour comes before transformation. Krishna teaches that the wise see differently than others—what seems like an ending may be a beginning. Hold on. Continue doing what is right. The dawn you cannot yet see is coming."
        },
        {
            "_id": "guidance_fear_failure",
            "mood_id": "fear_failure",
            "title": "Success and Failure Are the Same",
            "verse_reference": "Bhagavad Gita 2.48",
            "sanskrit_verse": "योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।\nसिद्ध्यसिद्ध्योः समो भूत्वा समत्वं योग उच्यते॥",
            "english_translation": "Perform your duty with a steady mind, abandoning attachment to success and failure. Such equanimity is called yoga.",
            "guidance_text": "Fear of failure paralyzes action. Krishna teaches that true success lies not in outcomes, but in performing your duty with sincerity. When you are equally poised in success and failure, you are free to act courageously. Do your best and accept the result with grace. This is the way of the yogi."
        },
        {
            "_id": "guidance_anger_world",
            "mood_id": "anger_world",
            "title": "Accept What Cannot Be Changed",
            "verse_reference": "Bhagavad Gita 2.14",
            "sanskrit_verse": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
            "english_translation": "The contact of the senses with their objects, O son of Kunti, gives rise to heat and cold, pleasure and pain. These are temporary and come and go like seasons. Learn to endure them.",
            "guidance_text": "The world will not always meet your expectations, and anger at this reality only increases suffering. Krishna teaches acceptance—not resignation, but understanding that change is constant and universal. Channel your energy toward what you can influence: your own actions and responses. Peace comes from accepting the world as it is while working toward what it can become."
        },
        {
            "_id": "guidance_anger_self",
            "mood_id": "anger_self",
            "title": "Uplift Yourself, Don't Condemn",
            "verse_reference": "Bhagavad Gita 6.5",
            "sanskrit_verse": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
            "english_translation": "Elevate yourself through the power of your mind, and not degrade yourself, for the mind can be the friend and also the enemy of the self.",
            "guidance_text": "Self-directed anger is self-destruction. Krishna teaches that you must be your own ally, not your enemy. Yes, you have made mistakes—everyone does. Learn from them and move forward. Treat yourself with the same kindness you would offer a dear friend who is struggling. You deserve your own compassion."
        },
        {
            "_id": "guidance_grief_change",
            "mood_id": "grief_change",
            "title": "Change is the Nature of Life",
            "verse_reference": "Bhagavad Gita 2.27",
            "sanskrit_verse": "जातस्य हि ध्रुवो मृत्युर्ध्रुवं जन्म मृतस्य च।\nतस्मादपरिहार्येऽर्थे न त्वं शोचितुमर्हसि॥",
            "english_translation": "For one who has taken birth, death is certain; and for one who has died, birth is certain. Therefore, you should not lament over the inevitable.",
            "guidance_text": "The way things were cannot remain forever—this is the law of existence. Krishna teaches that change, though painful, is natural and necessary. Honor what you had, but do not resist life's flow. Even as you grieve, new possibilities are emerging. The essence of what you loved remains, transformed but not lost."
        },
        {
            "_id": "guidance_grief_health",
            "mood_id": "grief_health",
            "title": "The Body Changes, the Soul Remains",
            "verse_reference": "Bhagavad Gita 2.13",
            "sanskrit_verse": "देहिनोऽस्मिन्यथा देहे कौमारं यौवनं जरा।\nतथा देहान्तरप्राप्तिर्धीरस्तत्र न मुह्यति॥",
            "english_translation": "Just as the embodied soul continuously passes through childhood, youth, and old age, similarly, at the time of death, the soul passes into another body. The wise are not deluded by this.",
            "guidance_text": "Physical decline is difficult to accept, but Krishna reminds us that the body is temporary while the soul endures. You are more than your physical form. Find new ways to contribute and connect that honor your current state. Wisdom and presence do not diminish with age—they often deepen. Your value is not measured by physical strength."
        },
        {
            "_id": "guidance_confusion_choice",
            "mood_id": "confusion_choice",
            "title": "Act with What You Know Now",
            "verse_reference": "Bhagavad Gita 3.19",
            "sanskrit_verse": "तस्मादसक्तः सततं कार्यं कर्म समाचर।\nअसक्तो ह्याचरन्कर्म परमाप्नोति पूरुषः॥",
            "english_translation": "Therefore, without attachment, constantly perform actions which are duty, for by performing actions without attachment, one attains the Supreme.",
            "guidance_text": "Indecision often masks fear of making the wrong choice. Krishna teaches that action, even imperfect, is better than paralysis. Make the best decision you can with what you know now. Learn as you go. Most paths lead somewhere worthwhile when walked with sincerity. The important thing is to move forward."
        },
        {
            "_id": "guidance_confusion_meaning",
            "mood_id": "confusion_meaning",
            "title": "Meaning is Created Through Action",
            "verse_reference": "Bhagavad Gita 3.20",
            "sanskrit_verse": "कर्मणैव हि संसिद्धिमास्थिता जनकादयः।\nलोकसंग्रहमेवापि संपश्यन्कर्तुमर्हसि॥",
            "english_translation": "King Janaka and others attained perfection through action alone. You should also perform your duty with a view to guide people and for the welfare of society.",
            "guidance_text": "Life's meaning is not found by thinking alone—it emerges through doing. Krishna teaches that purpose reveals itself in service and action. Instead of seeking a grand meaning, begin with small acts of kindness and duty. Meaning accumulates in how you treat others and fulfill your responsibilities. Do good, and purpose will follow."
        },
        {
            "_id": "guidance_detachment_emptiness",
            "mood_id": "detachment_emptiness",
            "title": "Fill Emptiness with the Divine",
            "verse_reference": "Bhagavad Gita 9.22",
            "sanskrit_verse": "अनन्याश्चिन्तयन्तो मां ये जनाः पर्युपासते।\nतेषां नित्याभियुक्तानां योगक्षेमं वहाम्यहम्॥",
            "english_translation": "To those who are constantly devoted and who worship Me with love, I give the understanding by which they can come to Me.",
            "guidance_text": "The emptiness you feel is the soul's longing for connection with something greater. Krishna promises that those who turn to the Divine with devotion will find fulfillment. What worldly pleasures once filled, they no longer can. This void is an invitation—fill it not with more possessions or distractions, but with spiritual practice, prayer, and service. The Divine fills all emptiness."
        },
        {
            "_id": "guidance_detachment_world",
            "mood_id": "detachment_world",
            "title": "Be in the World, Not of It",
            "verse_reference": "Bhagavad Gita 5.10",
            "sanskrit_verse": "ब्रह्मण्याधाय कर्माणि सङ्गं त्यक्त्वा करोति यः।\nलिप्यते न स पापेन पद्मपत्रमिवाम्भसा॥",
            "english_translation": "One who performs duties without attachment, dedicating actions to the Supreme, is not tainted by sin, just as a lotus leaf is untouched by water.",
            "guidance_text": "Feeling disconnected from the world can be wisdom, not loneliness. Krishna uses the lotus as example—it grows in water but remains dry. Engage with life fully, but don't let it pull you under. Your spiritual nature transcends worldly affairs. Participate in the world while remaining centered in your true self."
        },
        # New guidance entries for additional moods
        {
            "_id": "guidance_fear_illness",
            "mood_id": "fear_illness",
            "title": "The Body is Temporary, Spirit Eternal",
            "verse_reference": "Bhagavad Gita 2.22",
            "sanskrit_verse": "वासांसि जीर्णानि यथा विहाय नवानि गृह्णाति नरोऽपराणि।\nतथा शरीराणि विहाय जीर्णान्यन्यानि संयाति नवानि देही॥",
            "english_translation": "As a person sheds worn-out garments and wears new ones, likewise, at the time of death, the soul casts off worn-out bodies and enters new ones.",
            "guidance_text": "Illness reminds us of our body's fragility, but Krishna teaches that your true self is beyond illness. The body may weaken, but the soul remains untouched. Use this time to deepen your spiritual practice. Health comes and goes, but your eternal nature endures. Fear not the body's changes—honor the spirit within."
        },
        {
            "_id": "guidance_fear_abandonment",
            "mood_id": "fear_abandonment",
            "title": "The Divine Never Abandons You",
            "verse_reference": "Bhagavad Gita 9.31",
            "sanskrit_verse": "कौन्तेय प्रतिजानीहि न मे भक्तः प्रणश्यति॥",
            "english_translation": "O son of Kunti, declare it boldly that My devotee never perishes.",
            "guidance_text": "People may come and go, but the Divine presence remains constant. Krishna promises that those who remember the Divine are never truly alone. Cultivate this inner relationship—it cannot be lost through distance or death. Even if everyone leaves, you carry within you an eternal companion who knows and loves you completely."
        },
        {
            "_id": "guidance_fear_change",
            "mood_id": "fear_change",
            "title": "Change is Life's Constant Teacher",
            "verse_reference": "Bhagavad Gita 2.14",
            "sanskrit_verse": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
            "english_translation": "The contact of the senses with their objects gives rise to heat and cold, pleasure and pain. These are temporary and come and go. Learn to endure them, O Bharata.",
            "guidance_text": "Change is inevitable—resisting it only increases suffering. Krishna teaches that all circumstances are temporary, like seasons. Winter becomes spring, sorrow becomes joy. Trust in life's rhythms. What feels like an ending may be a new beginning. Face change with courage, knowing that your adaptable spirit has survived all previous transitions."
        },
        {
            "_id": "guidance_anger_betrayal",
            "mood_id": "anger_betrayal",
            "title": "Betrayal Cannot Touch Your Soul",
            "verse_reference": "Bhagavad Gita 5.18",
            "sanskrit_verse": "विद्याविनयसम्पन्ने ब्राह्मणे गवि हस्तिनि।\nशुनि चैव श्वपाके च पण्डिताः समदर्शिनः॥",
            "english_translation": "The truly wise, with the eyes of knowledge, see equally the learned sage, the cow, the elephant, the dog, and the person of low birth.",
            "guidance_text": "Betrayal wounds deeply, but Krishna teaches that others' actions reflect their character, not your worth. Your true self remains untarnished. Let this experience teach you wisdom without hardening your heart. Forgiveness doesn't excuse their action—it frees you from carrying the burden of their wrong. Protect yourself wisely, but don't let bitterness poison your spirit."
        },
        {
            "_id": "guidance_anger_powerless",
            "mood_id": "anger_powerless",
            "title": "Your Duty is to Act, Not Control Results",
            "verse_reference": "Bhagavad Gita 2.47",
            "sanskrit_verse": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।\nमा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
            "english_translation": "You have the right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself to be the cause of the results, nor be attached to inaction.",
            "guidance_text": "Helplessness arises when we feel responsible for outcomes we cannot control. Krishna liberates us from this burden—your power lies in sincere effort, not guaranteed results. Do what you can with love and skill, then release attachment to how it unfolds. This is not giving up; it's wisdom. You are not powerless—you have the power that matters: the power to act rightly."
        },
        {
            "_id": "guidance_anger_disrespect",
            "mood_id": "anger_disrespect",
            "title": "Your Worth Is Not Defined by Others",
            "verse_reference": "Bhagavad Gita 12.18-19",
            "sanskrit_verse": "समः शत्रौ च मित्रे च तथा मानापमानयोः।\nशीतोष्णसुखदुःखेषु समः सङ्गविवर्जितः॥",
            "english_translation": "One who is equal toward friend and foe, in honor and dishonor, in heat and cold, happiness and distress—such a person is very dear to Me.",
            "guidance_text": "Disrespect stings because we seek validation from others. Krishna teaches that the wise remain steady whether praised or criticized. Your value is inherent, not dependent on others' recognition. Those who disrespect you reveal their own limitations, not yours. Stand in your dignity without needing their approval. True respect comes from self-respect."
        },
        {
            "_id": "guidance_grief_dream",
            "mood_id": "grief_dream",
            "title": "New Dreams Await Beyond the Old",
            "verse_reference": "Bhagavad Gita 2.69",
            "sanskrit_verse": "या निशा सर्वभूतानां तस्यां जागर्ति संयमी।\nयस्यां जाग्रति भूतानि सा निशा पश्यतो मुनेः॥",
            "english_translation": "What is night for all beings is the time of awakening for the self-controlled; and the time of awakening for all beings is night for the introspective sage.",
            "guidance_text": "When a dream dies, it feels like losing a part of yourself. Krishna teaches that endings create space for transformation. Perhaps that dream was preparing you for something greater. Grieve what you hoped for, then look with new eyes. Life has dreams for you that you haven't imagined yet. Trust that closed doors lead to open horizons."
        },
        {
            "_id": "guidance_grief_relationship",
            "mood_id": "grief_relationship",
            "title": "Love Transcends Physical Presence",
            "verse_reference": "Bhagavad Gita 2.23",
            "sanskrit_verse": "नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः।\nन चैनं क्लेदयन्त्यापो न शोषयति मारुतः॥",
            "english_translation": "Weapons cannot cut the soul, fire cannot burn it, water cannot wet it, and wind cannot dry it.",
            "guidance_text": "Relationships may end in form, but the love shared leaves eternal marks on the soul. Krishna teaches that true connection transcends physical presence. What you learned and how you grew through that relationship remains forever. Honor the ending, but know that real love never truly ends—it transforms. Carry forward the gifts that relationship gave you."
        },
        {
            "_id": "guidance_grief_youth",
            "mood_id": "grief_youth",
            "title": "Age Brings Wisdom's Greater Gifts",
            "verse_reference": "Bhagavad Gita 2.13",
            "sanskrit_verse": "देहिनोऽस्मिन्यथा देहे कौमारं यौवनं जरा।\nतथा देहान्तरप्राप्तिर्धीरस्तत्र न मुह्यति॥",
            "english_translation": "Just as the embodied soul continuously passes through childhood, youth, and old age, similarly, at the time of death, the soul passes into another body. The wise are not deluded by this.",
            "guidance_text": "Youth's energy fades, but something deeper emerges—wisdom, perspective, and peace. Krishna reminds us that all bodies age; the soul does not. What you've gained in understanding and character far exceeds what you've lost in physical vitality. Your youth served its purpose. Now embrace the richness that only age can bring. The best of you is timeless."
        },
        {
            "_id": "guidance_confusion_identity",
            "mood_id": "confusion_identity",
            "title": "Your True Self is Beyond Roles",
            "verse_reference": "Bhagavad Gita 2.20",
            "sanskrit_verse": "न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः।\nअजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥",
            "english_translation": "The soul is never born and never dies. It is unborn, eternal, ever-existing, and primeval. The soul is not slain when the body is slain.",
            "guidance_text": "You may have lost your roles—worker, spouse, parent—but these were never your true identity. Krishna reveals that your essence is eternal consciousness, beyond all labels. When external identities fall away, the authentic self emerges. This confusion is actually awakening. Who are you beyond what you do or how others see you? Discover this, and you find unshakeable peace."
        },
        {
            "_id": "guidance_confusion_direction",
            "mood_id": "confusion_direction",
            "title": "Follow Dharma, the Path Appears",
            "verse_reference": "Bhagavad Gita 3.35",
            "sanskrit_verse": "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।\nस्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥",
            "english_translation": "It is better to perform one's own duty imperfectly than to perform another's duty perfectly. It is better to die doing one's own duty; another's duty is fraught with danger.",
            "guidance_text": "Not knowing which way to go can be paralyzing. Krishna teaches that your path reveals itself when you follow dharma—right action in this moment. Don't wait for perfect clarity. Take the next right step, even if you can't see the full journey. Your path finds you when you walk with integrity. Direction emerges from movement, not from standing still."
        },
        {
            "_id": "guidance_confusion_values",
            "mood_id": "confusion_values",
            "title": "Root Your Values in the Eternal",
            "verse_reference": "Bhagavad Gita 9.30",
            "sanskrit_verse": "अपि चेत्सुदुराचारो भजते मामनन्यभाक्।\nसाधुरेव स मन्तव्यः सम्यग्व्यवसितो हि सः॥",
            "english_translation": "Even if the most sinful person resolves to worship Me with exclusive devotion, that person is to be considered saintly, for their resolve is properly placed.",
            "guidance_text": "Conflicting values create inner turmoil. Krishna offers clarity: root yourself in the Divine, and lesser conflicts resolve. When you align with eternal principles—truth, compassion, service—situational confusions fall away. Not all values are equal. Prioritize spiritual truth above social convention, inner integrity above external approval. This hierarchy brings peace."
        },
        {
            "_id": "guidance_detachment_numb",
            "mood_id": "detachment_numb",
            "title": "Feel to Heal, Then Transcend",
            "verse_reference": "Bhagavad Gita 6.20-21",
            "sanskrit_verse": "यत्रोपरमते चित्तं निरुद्धं योगसेवया।\nयत्र चैवात्मनात्मानं पश्यन्नात्मनि तुष्यति॥",
            "english_translation": "When the mind, restrained by the practice of yoga, attains quietude, and when, seeing the Self by the Self, one is satisfied in the Self alone.",
            "guidance_text": "Numbness often protects us from overwhelming pain. Krishna teaches that true detachment is not numbness—it's profound peace after fully experiencing emotion. Don't rush past your feelings. Acknowledge them, then release them. Meditation can help you feel without being consumed. Real equanimity includes all emotions, holding them lightly. You're not broken—you're protecting yourself. Healing restores feeling."
        },
        {
            "_id": "guidance_detachment_apathy",
            "mood_id": "detachment_apathy",
            "title": "Apathy is Not Wisdom",
            "verse_reference": "Bhagavad Gita 3.8",
            "sanskrit_verse": "नियतं कुरु कर्म त्वं कर्म ज्यायो ह्यकर्मणः।\nशरीरयात्रापि च ते न प्रसिद्ध्येदकर्मणः॥",
            "english_translation": "Perform your prescribed duties, for action is better than inaction. Without work, even the maintenance of your physical body would not be possible.",
            "guidance_text": "Apathy masquerades as detachment but leads to stagnation. Krishna doesn't teach withdrawal from life—he teaches engaged action without attachment to results. Do what is yours to do, not because you care about results, but because it is right. Purpose returns when you act, even without passion. Movement creates meaning. Begin with small duties, and interest will follow."
        },
        {
            "_id": "guidance_detachment_tired",
            "mood_id": "detachment_tired",
            "title": "Rest in the Divine, Then Rise Again",
            "verse_reference": "Bhagavad Gita 6.17",
            "sanskrit_verse": "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।\nयुक्तस्वप्नावबोधस्य योगो भवति दुःखहा॥",
            "english_translation": "For one who is moderate in eating and recreation, regulated in work, and proper in sleep and wakefulness, yoga destroys all sorrows.",
            "guidance_text": "Life-weariness signals that you've been carrying too much for too long. Krishna teaches balance—rest is not weakness, it's wisdom. Give yourself permission to step back and replenish. You don't have to keep fighting. Sometimes the bravest thing is to rest, trusting that life continues. Surrender your exhaustion to the Divine. When you're ready, strength will return."
        },
        {
            "_id": "guidance_joy_serenity",
            "mood_id": "joy_serenity",
            "title": "Serenity is Your Natural State",
            "verse_reference": "Bhagavad Gita 5.21",
            "sanskrit_verse": "बाह्यस्पर्शेष्वसक्तात्मा विन्दत्यात्मनि यत्सुखम्।\nस ब्रह्मयोगयुक्तात्मा सुखमक्षयमश्नुते॥",
            "english_translation": "One who is not attached to external sense pleasures realizes happiness in the Self. Engaging in meditation, such a person enjoys unlimited happiness.",
            "guidance_text": "The serenity you feel is not a temporary mood—it's a glimpse of your true nature. Krishna teaches that lasting peace comes from within, not from circumstances. Circumstances change, but the peace within remains steady. Cherish this state and remember it during storms. You've tasted what lies at your core: unchanging, divine tranquility. Meditation deepens this connection."
        },
        {
            "_id": "guidance_joy_connection",
            "mood_id": "joy_connection",
            "title": "Divine Connection is Your Birthright",
            "verse_reference": "Bhagavad Gita 10.8",
            "sanskrit_verse": "अहं सर्वस्य प्रभवो मत्तः सर्वं प्रवर्तते।\nइति मत्वा भजन्ते मां बुधा भावसमन्विताः॥",
            "english_translation": "I am the source of all creation. Everything emanates from Me. The wise who know this perfectly worship Me with loving devotion.",
            "guidance_text": "The connection you feel is real and sacred. Krishna confirms that the Divine dwells within and all around. This feeling of union is your soul recognizing its source. Nurture this relationship through prayer, meditation, and service. You're not imagining it—you're awakening to the truth. All separation is illusion; connection is reality."
        },
        {
            "_id": "guidance_joy_wisdom",
            "mood_id": "joy_wisdom",
            "title": "Wisdom Brings Lasting Joy",
            "verse_reference": "Bhagavad Gita 4.38",
            "sanskrit_verse": "न हि ज्ञानेन सदृशं पवित्रमिह विद्यते।\nतत्स्वयं योगसंसिद्धः कालेनात्मनि विन्दति॥",
            "english_translation": "In this world, there is nothing as purifying as divine knowledge. One who is perfected in yoga discovers this within the Self in due course of time.",
            "guidance_text": "The joy of understanding life's deeper truths surpasses all other pleasures. Krishna honors wisdom as the highest purifier. Your insights are hard-won treasures—share them with humility. True wisdom doesn't inflate the ego; it dissolves it. You see clearly now what confusion once obscured. Use this clarity to guide yourself and others with compassion."
        },
        {
            "_id": "guidance_doubt_goodness",
            "mood_id": "doubt_goodness",
            "title": "Goodness Prevails in the End",
            "verse_reference": "Bhagavad Gita 4.7-8",
            "sanskrit_verse": "यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।\nअभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥",
            "english_translation": "Whenever there is a decline in righteousness and a rise in unrighteousness, O Bharata, at that time I manifest Myself.",
            "guidance_text": "Evil may seem to triumph temporarily, but Krishna promises that Divine justice ultimately prevails. Goodness endures beyond individual lifetimes. Your task is not to control the world's moral arc but to remain steadfast in your own integrity. Be the goodness you wish to see. Trust that righteousness has power beyond what appears. Your good actions matter eternally."
        },
        {
            "_id": "guidance_doubt_purpose",
            "mood_id": "doubt_purpose",
            "title": "Your Existence Has Divine Purpose",
            "verse_reference": "Bhagavad Gita 7.6",
            "sanskrit_verse": "एतद्योनीनि भूतानि सर्वाणीत्युपधारय।\nअहं कृत्स्नस्य जगतः प्रभवः प्रलयस्तथा॥",
            "english_translation": "Understand that all living beings are born from these two natures. I am the source of the entire creation, and into Me it all dissolves.",
            "guidance_text": "If you exist, you have purpose—this is Krishna's teaching. You are not an accident but an expression of Divine will. Your purpose may be hidden, but it's real. Often purpose reveals itself through small daily choices, not grand revelations. Live with integrity, serve where you can, and purpose unfolds naturally. Trust that your life matters in the cosmic design."
        },
        {
            "_id": "guidance_doubt_karma",
            "mood_id": "doubt_karma",
            "title": "Every Action Bears Fruit",
            "verse_reference": "Bhagavad Gita 4.17",
            "sanskrit_verse": "कर्मणो ह्यपि बोद्धव्यं बोद्धव्यं च विकर्मणः।\nअकर्मणश्च बोद्धव्यं गहना कर्मणो गतिः॥",
            "english_translation": "The true nature of action is difficult to understand. You must understand what is action, what is wrong action, and what is inaction.",
            "guidance_text": "Karma's workings are subtle and span lifetimes—don't expect immediate results. Krishna teaches that every action has consequences, though they may not be visible now. Good actions plant seeds that sprout in their time. Don't let delayed justice make you cynical. Live righteously not for reward but because it is right. Universal law is patient but certain."
        },
        {
            "_id": "guidance_pride_appearance",
            "mood_id": "pride_appearance",
            "title": "Beauty Fades, Character Endures",
            "verse_reference": "Bhagavad Gita 2.14",
            "sanskrit_verse": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।\nआगमापायिनोऽनित्यास्तांस्तितिक्षस्व भारत॥",
            "english_translation": "The contact of the senses with their objects gives rise to heat and cold, pleasure and pain. These are temporary and come and go. Learn to endure them.",
            "guidance_text": "Physical beauty is fleeting—time spares no one. Krishna teaches that all sensory experiences, including beauty, are temporary. What you see in the mirror today will change. Invest in qualities that aging enhances: wisdom, kindness, and spiritual depth. True attractiveness radiates from within. Vanity blinds you to your real value, which is timeless."
        },
        {
            "_id": "guidance_pride_virtue",
            "mood_id": "pride_virtue",
            "title": "True Virtue Needs No Announcement",
            "verse_reference": "Bhagavad Gita 17.14",
            "sanskrit_verse": "देवद्विजगुरुप्राज्ञपूजनं शौचमार्जवम्।\nब्रह्मचर्यमहिंसा च शारीरं तप उच्यते॥",
            "english_translation": "Worship of the gods, the priests, the spiritual teacher, and the wise; purity, straightforwardness, celibacy, and non-violence—these are said to be the austerity of the body.",
            "guidance_text": "If you feel righteous compared to others, examine your heart. Krishna teaches that true virtue is humble and doesn't need recognition. Moral pride is spiritual poison—it separates you from others and from God. Everyone struggles; everyone fails. Your goodness should inspire compassion, not superiority. The truly righteous never think themselves so."
        },
        {
            "_id": "guidance_pride_independence",
            "mood_id": "pride_independence",
            "title": "We Are All Interdependent",
            "verse_reference": "Bhagavad Gita 3.20",
            "sanskrit_verse": "कर्मणैव हि संसिद्धिमास्थिता जनकादयः।\nलोकसंग्रहमेवापि संपश्यन्कर्तुमर्हसि॥",
            "english_translation": "King Janaka and others attained perfection through action alone. You should also perform your duty with a view to guide people and for the welfare of society.",
            "guidance_text": "No one succeeds alone—we all depend on countless others. Krishna teaches that we're woven together in mutual service. Your independence is an illusion built on others' help. Accepting help is not weakness; it's wisdom. Vulnerability connects us. The truly strong know when to lean on others. Pride isolates; humility binds us in love."
        },
        {
            "_id": "guidance_desire_recognition",
            "mood_id": "desire_recognition",
            "title": "Seek the Divine's Recognition Alone",
            "verse_reference": "Bhagavad Gita 6.1",
            "sanskrit_verse": "श्रीभगवानुवाच।\nअनाश्रितः कर्मफलं कार्यं कर्म करोति यः।\nस संन्यासी च योगी च न निरग्निर्न चाक्रियः॥",
            "english_translation": "The Supreme Lord said: One who performs duties without depending on the fruits of actions is a renunciate and a yogi, not one who has merely renounced fire or activities.",
            "guidance_text": "Craving others' approval makes you their slave. Krishna teaches that true fulfillment comes from acting rightly, regardless of recognition. The Divine sees all your efforts, acknowledged or not. Work for this audience of One. When you stop performing for human applause, you find freedom. Your worth doesn't depend on being seen; it simply is."
        },
        {
            "_id": "guidance_desire_comfort",
            "mood_id": "desire_comfort",
            "title": "Growth Lies Beyond Comfort",
            "verse_reference": "Bhagavad Gita 6.5",
            "sanskrit_verse": "उद्धरेदात्मनात्मानं नात्मानमवसादयेत्।\nआत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
            "english_translation": "Elevate yourself through the power of your mind, and not degrade yourself, for the mind can be the friend and also the enemy of the self.",
            "guidance_text": "Attachment to comfort stunts your growth. Krishna teaches that spiritual progress requires discipline and occasional discomfort. Your comfort zone is both haven and prison. Step beyond it regularly. Challenge yourself with small austerities—not for punishment but for strength. The soul expands through stretching. Comfort has its place, but it should not rule your life."
        },
        {
            "_id": "guidance_desire_security",
            "mood_id": "desire_security",
            "title": "True Security Lies in the Divine",
            "verse_reference": "Bhagavad Gita 9.22",
            "sanskrit_verse": "अनन्याश्चिन्तयन्तो मां ये जनाः पर्युपासते।\nतेषां नित्याभियुक्तानां योगक्षेमं वहाम्यहम्॥",
            "english_translation": "To those who are constantly devoted and who worship Me with love, I give the understanding by which they can come to Me.",
            "guidance_text": "No worldly circumstance guarantees security—everything changes. Krishna promises that those devoted to the Divine are cared for. Real security isn't controlling circumstances; it's trusting that you'll be okay regardless of what happens. Build your foundation on faith, not bank accounts or insurance policies. When you rest in the Divine, uncertainty becomes adventure, not threat."
        },
        {
            "_id": "guidance_envy_youth",
            "mood_id": "envy_youth",
            "title": "Every Age Has Its Blessings",
            "verse_reference": "Bhagavad Gita 2.13",
            "sanskrit_verse": "देहिनोऽस्मिन्यथा देहे कौमारं यौवनं जरा।\nतथा देहान्तरप्राप्तिर्धीरस्तत्र न मुह्यति॥",
            "english_translation": "Just as the embodied soul continuously passes through childhood, youth, and old age, similarly, at the time of death, the soul passes into another body. The wise are not deluded by this.",
            "guidance_text": "Youth has energy; age has wisdom. Krishna teaches that all life stages serve their purpose. Don't envy what you've outgrown. The young face struggles you've survived; you possess gifts they haven't earned. Each age offers unique treasures. Celebrate your season of life rather than coveting another's. Your value deepens with time, it doesn't diminish."
        },
        {
            "_id": "guidance_envy_family",
            "mood_id": "envy_family",
            "title": "Find Family in Spiritual Community",
            "verse_reference": "Bhagavad Gita 6.32",
            "sanskrit_verse": "आत्मौपम्येन सर्वत्र समं पश्यति योऽर्जुन।\nसुखं वा यदि वा दुःखं स योगी परमो मतः॥",
            "english_translation": "One who sees happiness and distress equally in all beings, comparing them to oneself, is considered the highest yogi, O Arjuna.",
            "guidance_text": "Family comes in many forms. Krishna teaches that spiritual kinship can be stronger than blood relations. If you lack biological family, create chosen family through deep friendships and spiritual community. Your capacity to love and be loved isn't limited to genetics. Look around—family may be closer than you think, just not in expected forms. Open your heart to connection."
        },
        {
            "_id": "guidance_envy_health",
            "mood_id": "envy_health",
            "title": "Honor Your Body's Unique Journey",
            "verse_reference": "Bhagavad Gita 3.35",
            "sanskrit_verse": "श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।\nस्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥",
            "english_translation": "It is better to perform one's own duty imperfectly than to perform another's duty perfectly. It is better to die doing one's own duty; another's duty is fraught with danger.",
            "guidance_text": "Every body has its karma, its unique challenges. Krishna teaches that comparing your health to others' brings only suffering. Work with the body you have, not the one you wish you had. Adapt, adjust, find new ways to participate in life. Your spirit is unlimited, even if your body has limits. Health isn't virtue—how you respond to your circumstances is."
        },
        {
            "_id": "guidance_despair_burden",
            "mood_id": "despair_burden",
            "title": "Share Your Burden with the Divine",
            "verse_reference": "Bhagavad Gita 18.66",
            "sanskrit_verse": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।\nअहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
            "english_translation": "Abandon all varieties of dharma and just surrender unto Me. I shall deliver you from all sinful reactions. Do not fear.",
            "guidance_text": "When life feels too heavy, Krishna invites you to surrender. You weren't meant to carry everything alone. Share your burden through prayer, asking the Divine to help you carry what you cannot bear. Surrender isn't giving up—it's acknowledging your limits and trusting in something greater. Even the strongest need support. Let divine grace lighten your load."
        },
        {
            "_id": "guidance_despair_mistakes",
            "mood_id": "despair_mistakes",
            "title": "Learn from the Past, Live in the Present",
            "verse_reference": "Bhagavad Gita 4.36-37",
            "sanskrit_verse": "अपि चेदसि पापेभ्यः सर्वेभ्यः पापकृत्तमः।\nसर्वं ज्ञानप्लवेनैव वृजिनं सन्तरिष्यसि॥",
            "english_translation": "Even if you are the most sinful of all sinners, you will cross over the ocean of sin by the boat of divine knowledge.",
            "guidance_text": "Regret keeps you imprisoned in the past. Krishna promises that no mistake is beyond redemption. Learn from errors, make amends where possible, then release them. Your past doesn't define your future unless you let it. Forgiveness begins with forgiving yourself. You are more than your worst moments. Every day offers a chance to begin again with wisdom earned from what went before."
        },
        {
            "_id": "guidance_despair_meaning",
            "mood_id": "despair_meaning",
            "title": "Meaning Emerges Through Service",
            "verse_reference": "Bhagavad Gita 12.20",
            "sanskrit_verse": "ये तु धर्म्यामृतमिदं यथोक्तं पर्युपासते।\nश्रद्दधाना मत्परमा भक्तास्तेऽतीव मे प्रियाः॥",
            "english_translation": "Those who follow this eternal path of dharma with faith, regarding Me as their supreme goal, are very dear to Me.",
            "guidance_text": "Meaninglessness is the soul's cry for purpose. Krishna teaches that meaning isn't found through analysis but through devotion and service. Stop searching and start serving. Help someone today, however small the act. Meaning accumulates in caring for others and connecting with the Divine. You don't find purpose; you create it through love in action. Begin where you are."
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
    
    # Always insert emotions, moods, and guidances (since we cleared them)
    await db.emotions.insert_many(emotions)
    await db.moods.insert_many(moods)
    await db.guidances.insert_many(guidances)
    logger.info("Emotions, moods, and guidance data initialized")
    
    if existing_chapters == 0:
        await db.chapters.insert_many(chapters)
        logger.info("Chapters data initialized")
    
    logger.info("Sample data initialization complete")

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
