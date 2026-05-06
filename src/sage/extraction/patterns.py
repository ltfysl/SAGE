"""Shared patterns for entity extraction."""
import re

# Known person names (from generator)
KNOWN_NAMES = {
    "Latif","Arno","Chen","Diana","Elena","Fatima","Gabriel","Hiroshi","Ingrid",
    "Jamal","Keiko","Luis","Maria","Nadia","Omar","Priya","Quan","Rosa","Samir",
    "Tanya","Uma","Viktor","Wei","Ximena","Yuki","Zara","Akira","Bianca","Carlos",
    "Dmitri","Esther","Francois","Grace","Hassan","Iris","Jin","Kalani","Leila",
    "Marcus","Naomi","Olga","Pablo","Qiana","Rafael","Serena","Theo","Umar",
    "Valentina","Winston","Xi","Yara","Zayn","Amara","Bodhi","Camila","Dario",
    "Esme","Felix","Giulia","Haruki","Imran","Juno","Kofi","Lucia","Matteo",
    "Noor","Orion","Petra","Quinn","Raj","Sofia","Tobias","Ursula","Vince",
    "Willa","Xander","Yuna","Zeke",
}

# Non-name words that start with capital letters in stories
STOP_WORDS = {"Question","How","What","Who","Which","Whose","Somewhere","Someone",
              "The","A","Footsteps","Raindrops","Question:","Somewhere,","A"}

# Object plurals and singulars
PLURALS = ["coins","books","apples","marbles","cards","candies","pencils",
           "stickers","cookies","shells","stones","beads","tokens","berries",
           "seeds","buttons","keys","rings","pebbles","leaves"]
SINGULARS = ["coin","book","apple","marble","card","candy","pencil","sticker",
             "cookie","shell","stone","bead","token","berry","seed","button",
             "key","ring","pebble","leaf"]

# Build object lookup: any form -> canonical plural
OBJECT_LOOKUP = {}
for p in PLURALS:
    OBJECT_LOOKUP[p] = p
for i, s in enumerate(SINGULARS):
    if i < len(PLURALS):
        OBJECT_LOOKUP[s] = PLURALS[i]
# Irregular mappings
OBJECT_LOOKUP["leaves_irregular"] = "leaves"

# Verb sets for classification
SET_VERBS = {"has","owns","holds","possesses","is holding","has exactly"}
ADD_VERBS = {"finds","discovers","gains","collects","earns","picks up",
             "receives","gets","takes"}
SUB_VERBS = {"spends","uses","consumes","loses","drops","misplaces",
             "gives away","parts with","accidentally loses"}
GIVE_VERBS = {"gives","hands","passes","offers","transfers","sends"}
BUY_VERBS = {"buys","purchases","pays"}
SELL_VERBS = {"sells"}
RECEIVE_VERBS = {"receives","gets","takes","is given"}

# Compiled regex patterns
NUMBER_RE = re.compile(r'\b(\d+)\b')
NAME_RE = re.compile(r'\b([A-Z][a-z]+)\b')
TO_RE = re.compile(r'\bto\s+([A-Z][a-z]+)')
FROM_RE = re.compile(r'\bfrom\s+([A-Z][a-z]+)')
BY_RE = re.compile(r'\bby\s+([A-Z][a-z]+)')
FOR_RE = re.compile(r'\bfor\s+(\d+)\s+(\w+)')
PAYS_RE = re.compile(r'\b(pays?)\s+([A-Z][a-z]+)\s+for', re.IGNORECASE)

# Question patterns for extracting query target
QUESTION_PATTERNS = [
    re.compile(r'\bdoes\s+([A-Z][a-z]+)\s+have'),
    re.compile(r'\bis\s+([A-Z][a-z]+)\s+holding'),
    re.compile(r'\bwith\s+([A-Z][a-z]+)\b'),
    re.compile(r'\bremain\s+with\s+([A-Z][a-z]+)'),
    re.compile(r"([A-Z][a-z]+)'s\s+"),
    re.compile(r'\bend\s+up\s+with\s+([A-Z][a-z]+)'),
    re.compile(r'\bleft\s+with\s+([A-Z][a-z]+)'),
    re.compile(r'\bdoes\s+([A-Z][a-z]+)\s+possess'),
    re.compile(r'\bdoes\s+([A-Z][a-z]+)\s+end'),
]
