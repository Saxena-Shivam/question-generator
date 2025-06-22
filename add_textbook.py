import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
with open(r'd:\Project-ARC\Question_Paper_Generator\textbook.json', encoding='utf-8') as f:
    data = json.load(f)
# Load environment variables
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
# Get the MongoDB URI from the environment
mongo_uri = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(mongo_uri)
collection = client["Textbooks"]["content"]
docs = []

for subject_block in data:
    class_level = subject_block["class"]
    subject_name = subject_block["subject"]
    for topic_block in subject_block["topics"]:
        topic_code = topic_block["topic"]

        # Generate textbook content based on subject and topic code
        if subject_name == "Mathematics":
            if topic_code == "a":
                textbook_content = (
                    "Basic arithmetic involves the fundamental operations of addition, subtraction, multiplication, and division. "
                    "Addition combines numbers to find their total, while subtraction finds the difference between numbers. "
                    "Multiplication is repeated addition, and division is splitting into equal parts. "
                    "Understanding these operations is essential for all mathematical concepts."
                )
            elif topic_code == "b":
                textbook_content = (
                    "Fractions represent parts of a whole. A fraction has a numerator (top number) and denominator (bottom number). "
                    "Proper fractions have numerators smaller than denominators, while improper fractions have numerators equal to or larger than denominators. "
                    "Equivalent fractions represent the same value (e.g., 1/2 = 2/4). Fractions can be added, subtracted, multiplied, and divided with specific rules."
                )
            elif topic_code == "c":
                textbook_content = (
                    "Geometry studies shapes, sizes, and positions of figures. Basic elements include points, lines, and angles. "
                    "Polygons are closed shapes with straight sides (triangles, quadrilaterals, pentagons, etc.). "
                    "Circles are round shapes where all points are equidistant from the center. "
                    "Angles are measured in degrees: acute (<90°), right (90°), obtuse (>90°), and straight (180°)."
                )
            elif topic_code == "d":
                textbook_content = (
                    "Decimals are numbers with whole and fractional parts separated by a decimal point. "
                    "Place values extend right of the decimal: tenths, hundredths, thousandths, etc. "
                    "Decimals can be added, subtracted, multiplied, and divided like whole numbers, aligning decimal points for operations. "
                    "Fractions can be converted to decimals by dividing numerator by denominator."
                )
            elif topic_code == "e":
                textbook_content = (
                    "Measurement involves quantifying physical quantities using standard units. "
                    "Length is measured in meters/centimeters, weight in kilograms/grams, and volume in liters/milliliters. "
                    "Time is measured in seconds, minutes, hours. Temperature in Celsius or Fahrenheit. "
                    "The metric system uses base-10 conversions (e.g., 100 cm = 1 m)."
                )
            else:
                textbook_content = f"Mathematics topic {topic_code} content."
        elif subject_name == "Biology":
            if topic_code == "f":
                textbook_content = (
                    "Biology is the study of living organisms. All living things are made of cells, the basic unit of life. "
                    "Organisms obtain energy (nutrition), grow, respond to stimuli, reproduce, and adapt to their environment. "
                    "Living things are classified into five kingdoms: Monera, Protista, Fungi, Plantae, and Animalia."
                )
            elif topic_code == "g":
                textbook_content = (
                    "The human body has several interconnected systems. The skeletal system provides structure and protection. "
                    "The muscular system enables movement. The circulatory system transports blood with oxygen and nutrients. "
                    "The respiratory system exchanges gases. The digestive system breaks down food. "
                    "The nervous system controls and coordinates body activities through the brain, spinal cord, and nerves."
                )
            elif topic_code == "h":
                textbook_content = (
                    "Plants are autotrophs that produce food through photosynthesis using chlorophyll in their leaves. "
                    "Roots anchor plants and absorb water/nutrients. Stems provide support and transport materials. "
                    "Leaves are the main photosynthetic organs. Flowers contain reproductive structures. "
                    "Plants reproduce sexually (seeds) or asexually (vegetative propagation)."
                )
            elif topic_code == "i":
                textbook_content = (
                    "Animals are classified based on characteristics. Vertebrates have backbones (fish, amphibians, reptiles, birds, mammals). "
                    "Invertebrates lack backbones (insects, spiders, worms, mollusks). "
                    "Mammals are warm-blooded with hair/fur and produce milk. Birds have feathers and lay eggs. "
                    "Reptiles are cold-blooded with scales. Amphibians live in water and land. Fish live in water with gills."
                )
            elif topic_code == "j":
                textbook_content = (
                    "An ecosystem includes living organisms and their physical environment interacting as a system. "
                    "Producers (plants) make food. Consumers (animals) eat other organisms. Decomposers break down dead matter. "
                    "Food chains show energy transfer. Biodiversity refers to variety of life in an area. "
                    "Human activities can impact ecosystems positively (conservation) or negatively (pollution)."
                )
            else:
                textbook_content = f"Biology topic {topic_code} content."
        elif subject_name == "Social Studies":
            if topic_code == "k":
                textbook_content = (
                    "Ancient civilizations laid foundations for modern society. Mesopotamia (Tigris-Euphrates) developed writing (cuneiform) and laws. "
                    "Ancient Egypt built pyramids and developed hieroglyphics along the Nile. "
                    "The Indus Valley civilization had planned cities like Mohenjo-Daro. "
                    "Ancient China invented paper and gunpowder. Greece developed democracy and Rome created a vast empire with advanced engineering."
                )
            elif topic_code == "l":
                textbook_content = (
                    "Medieval India (8th-18th century) saw the Delhi Sultanate and Mughal Empire. "
                    "The Mughals (Babur, Akbar, Shah Jahan) built architectural marvels like the Taj Mahal. "
                    "Regional kingdoms like Vijayanagara and Cholas flourished in the south. "
                    "The Bhakti and Sufi movements promoted spiritual harmony. "
                    "Sher Shah Suri introduced administrative reforms and built the Grand Trunk Road."
                )
            elif topic_code == "m":
                textbook_content = (
                    "Geography studies Earth's landscapes, environments, and relationships between people and places. "
                    "Maps represent Earth's surface using symbols, scales, and projections. "
                    "Latitude (parallels) measures distance north/south of the Equator. "
                    "Longitude (meridians) measures east/west of the Prime Meridian. "
                    "Physical geography studies landforms, while human geography examines human activities."
                )
            elif topic_code == "n":
                textbook_content = (
                    "The Indian Constitution is the supreme law adopted on January 26, 1950. "
                    "Dr. B.R. Ambedkar chaired the drafting committee. It establishes India as a sovereign, socialist, secular, democratic republic. "
                    "The Preamble outlines justice, liberty, equality, and fraternity as goals. "
                    "It provides fundamental rights, directive principles, and establishes federal structure with parliamentary democracy."
                )
            elif topic_code == "o":
                textbook_content = (
                    "India is the world's largest democracy with a parliamentary system. "
                    "The President is head of state, while the Prime Minister leads the government. "
                    "Parliament consists of Lok Sabha (people's representatives) and Rajya Sabha (state representatives). "
                    "State governments mirror the central structure. Local governments include municipalities and panchayats. "
                    "Elections are conducted by the independent Election Commission."
                )
            else:
                textbook_content = f"Social Studies topic {topic_code} content."
        else:
            textbook_content = f"Textbook content for {subject_name} class {class_level}, topic {topic_code}."

        docs.append({
            "class": class_level,
            "subject_name": subject_name,
            "topic": topic_code,
            "textbook": textbook_content
        })

if docs:
    collection.insert_many(docs)
    print(f"✅ Inserted {len(docs)} textbook content documents with coded topics.")
else:
    print("No topics found to insert.")