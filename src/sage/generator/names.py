"""Names for synthetic world people."""

# A diverse set of names for synthetic data generation
NAMES = [
    "Latif", "Arno", "Chen", "Diana", "Elena", "Fatima", "Gabriel",
    "Hiroshi", "Ingrid", "Jamal", "Keiko", "Luis", "Maria", "Nadia",
    "Omar", "Priya", "Quan", "Rosa", "Samir", "Tanya", "Uma", "Viktor",
    "Wei", "Ximena", "Yuki", "Zara", "Akira", "Bianca", "Carlos",
    "Dmitri", "Esther", "Francois", "Grace", "Hassan", "Iris", "Jin",
    "Kalani", "Leila", "Marcus", "Naomi", "Olga", "Pablo", "Qiana",
    "Rafael", "Serena", "Theo", "Umar", "Valentina", "Winston", "Xi",
    "Yara", "Zayn", "Amara", "Bodhi", "Camila", "Dario", "Esme",
    "Felix", "Giulia", "Haruki", "Imran", "Juno", "Kofi", "Lucia",
    "Matteo", "Noor", "Orion", "Petra", "Quinn", "Raj", "Sofia",
    "Tobias", "Ursula", "Vince", "Willa", "Xander", "Yuna", "Zeke",
]

# Common object types for synthetic stories
OBJECT_TYPES = [
    "coins", "books", "apples", "marbles", "cards", "candies",
    "pencils", "stickers", "cookies", "shells", "stones", "beads",
    "tokens", "berries", "seeds", "buttons", "keys", "rings",
    "pebbles", "leaves",
]

# Object types that are singular
SINGULAR_OBJECTS = [
    "coin", "book", "apple", "marble", "card", "candy",
    "pencil", "sticker", "cookie", "shell", "stone", "bead",
    "token", "berry", "seed", "button", "key", "ring",
    "pebble", "leaf",
]

# Mapping from plural to singular
PLURAL_TO_SINGULAR = dict(zip(OBJECT_TYPES, SINGULAR_OBJECTS))


def get_singular(obj_type: str) -> str:
    """Get singular form of an object type."""
    return PLURAL_TO_SINGULAR.get(obj_type, obj_type)
