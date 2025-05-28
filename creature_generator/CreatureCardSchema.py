from pydantic import BaseModel
from typing import List, Optional, Literal
import enum

class Name(BaseModel):
    rus: str
    eng: str

class rusSize(enum.Enum):
    tiny = "Крошечный"
    small = "Маленький"
    medium = "Средний"
    large = "Большой"
    huge = "Огромный"
    gargantuan = "Громадный"

class engSize(enum.Enum):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large"
    huge = "huge"
    gargantuan = "gargantuan"

class cellSize(enum.Enum):
    tiny = "1/4 клетки"
    small = "1 клетка"
    medium = "1 клетка"
    large = "2x2 клетки"
    huge = "3x3 клетки"
    gargantuan = "4x4 клетки или больше"

class Size(BaseModel):
    rus: rusSize
    eng: engSize
    cell: cellSize

class CreatureType(enum.Enum):
    aberration = "аберрация"
    beast = "зверь"
    celestial = "небожитель"
    construct = "конструкт"
    dragon = "дракон"
    elemental = "элементаль"
    fey = "фея"
    fiend = "исчадие"
    giant = "великан"
    humanoid = "гуманоид"
    monstrosity = "монстр"
    plant = "растение"
    undead = "нежить"
    ooze = "слизь"
    swarm_of_tiny_beasts = "стая крошечных зверей"

class Type(BaseModel):
    name: CreatureType

class Alignment(enum.Enum):
    lawful_good = "законно-добрый"
    neutral_good = "нейтрально-добрый"
    chaotic_good = "хаотично-добрый"
    lawful_neutral = "законно-нейтральный"
    true_neutral = "нейтральный"
    chaotic_neutral = "хаотично-нейтральный"
    lawful_evil = "законно-злой"
    neutral_evil = "нейтрально-злой"
    chaotic_evil = "хаотично-злой"
    unaligned = "без мировоззрения"

class ArmorName(enum.Enum):
    no_armor = "нет доспеха"
    natural_armor = "природный доспех"
    "доспех мага"
    padded = "стёганый"
    leather = "кожаный"
    studded_leather = "клёпаный кожаный"
    hide = "шкурный"
    chain_shirt = "кольчужная рубаха"
    scale_mail = "чешуйчатый"
    breastplate = "кираса"
    half_plate = "полулаты"
    ring_mail = "кольчатый"
    chain_mail = "кольчуга"
    splint = "наборный"
    plate = "латы"
    other_armor = "другой"
    shield = "щит"

class ArmorType(enum.Enum):
    armor = "armor"
    shield =  "shield"

class Armor(BaseModel):
    name: ArmorName
    type: ArmorType

class HitPoints(BaseModel):
    average: int
    formula: str
    sign: str
    bonus: int
    text: Optional[str]

class Speed(BaseModel):
    value: int

class AbilityScores(BaseModel):
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int

class SavingThrow(BaseModel):
    name: str
    shortName: str
    value: int
    additional: Optional[str]

class Skill(BaseModel):
    name: str
    value: int
    additional: Optional[str]

class Sense(BaseModel):
    name: str
    value: int
    additional: Optional[str]

class Senses(BaseModel):
    passivePerception: str
    senses: List[Sense]

class Feature(BaseModel):
    name: str
    value: str

class LegendaryAction(BaseModel):
    name: str
    value: str

class Legendary(BaseModel):
    list: List[LegendaryAction]
    count: int
    description: str

class LairInfo(BaseModel):
    action: str
    effect: str
    description: str

class CreatureCard(BaseModel):
    name: Name
    size: Size
    type: Type
    challengeRating:  Literal[
        "—", "0", "1/8", "1/4", "1/2", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"
    ]
    experience: int
    proficiencyBonus: str
    alignment: Alignment
    armorClass: int
    armors: Optional[List[Armor]]
    hits: HitPoints
    speed: List[Speed]
    ability: AbilityScores
    savingThrows: Optional[List[SavingThrow]]
    skills: Optional[List[Skill]]
    senses: Senses
    languages: Optional[List[str]]
    feats: Optional[List[Feature]]
    actions: Optional[List[Feature]]
    legendary: Optional[Legendary]
    description: Optional[str]
    reactions: Optional[List[Feature]]
    armorText: Optional[str]
    damageImmunities: Optional[List[str]]
    damageResistances: Optional[List[str]]
    conditionImmunities: Optional[List[str]]
    bonusActions: Optional[List[Feature]]
    environment: Optional[List[str]]
    damageVulnerabilities: Optional[List[str]]
    lair: Optional[LairInfo]
    mysticalActions: Optional[List[Feature]]