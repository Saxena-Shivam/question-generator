import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Structured subject and chapter data
subjects = [
    {
        "subject_name": "Mathematics",
        "subject_code": "ma",
        "chapters_by_class": {
            6: ["Knowing Our Numbers", "Whole Numbers", "Integers"],
            7: ["Integers", "Fractions and Decimals", "Data Handling", "Algebra", "Perimeter and Area"],
            8: ["Linear Equations", "Understanding Quadrilaterals", "Mensuration"],
            9: ["Number Systems", "Polynomials", "Coordinate Geometry", "Linear Equations in Two Variables"],
            10: ["Real Numbers", "Pair of Linear Equations", "Quadratic Equations", "Statistics"]
        }
    },
    {
        "subject_name": "Science",
        "subject_code": "sc",
        "chapters_by_class": {
            6: ["Food: Where Does It Come From?", "Components of Food", "Separation of Substances"],
            7: ["Nutrition in Plants", "Nutrition in Animals", "Heat", "Motion and Time", "Electricity"],
            8: ["Crop Production", "Microorganisms", "Force and Pressure"],
            9: ["Matter in Our Surroundings", "Atoms and Molecules", "The Fundamental Unit of Life"],
            10: ["Chemical Reactions", "Acids, Bases and Salts", "Life Processes"]
        }
    },
    {
        "subject_name": "Social Science",
        "subject_code": "ss",
        "chapters_by_class": {
            6: ["Understanding Diversity", "Local Government", "Maps"],
            7: ["Democracy and Equality", "India's Neighbours", "State Government"],
            8: ["The Indian Constitution", "Judiciary", "Natural Resources"],
            9: ["Democratic Politics", "Climate", "Nazism and the Rise of Hitler"],
            10: ["Federalism", "Sectors of the Indian Economy", "Nationalism in India"]
        }
    }
]

# MongoDB Setup
load_dotenv("D:/Project-ARC/Question_Paper_Generator/.env")
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
collection = client["Textbooks"]["content"]

docs = []

# Loop over each subject and class
for subject in subjects:
    subject_name = subject["subject_name"]
    chapters_by_class = subject["chapters_by_class"]

    for class_level, chapters in chapters_by_class.items():
        for chapter in chapters:
            topic_code = chapter
            print(f"Processing Class {class_level}, Subject: {subject_name}, Topic: {topic_code}")

            # Default placeholder content
            textbook_content = f"This chapter titled '{topic_code}' from Class {class_level} {subject_name} covers fundamental concepts necessary for deeper understanding in this subject."

            # Mathematics content
            if subject_name == "Mathematics":
                if topic_code == "Knowing Our Numbers":
                    textbook_content = "Introduces large numbers up to millions, place value system, estimation techniques, and comparing numbers. Includes practical applications like reading bus/train timetables."
                elif topic_code == "Whole Numbers":
                    textbook_content = "Covers properties of whole numbers (closure, commutative, associative), number line representation, patterns in numbers, and basic operations with word problems."
                elif topic_code == "Integers":
                    textbook_content = "Introduces negative numbers, their representation on number line, ordering, and operations (addition, subtraction) with real-life examples like temperature and elevation."
                elif topic_code == "Fractions and Decimals":
                    textbook_content = "Covers types of fractions, equivalent fractions, operations with fractions, decimal representation, and conversion between fractions and decimals with measurement applications."
                elif topic_code == "Data Handling":
                    textbook_content = "Teaches data collection, organization (tally marks, frequency tables), representation (bar graphs, pictographs), and interpretation including averages (mean)."
                elif topic_code == "Algebra":
                    textbook_content = "Introduces variables, expressions, equations, and simple formulas. Covers solving one-step equations with practical applications like perimeter formulas."
                elif topic_code == "Perimeter and Area":
                    textbook_content = "Calculates perimeter and area of rectangles, squares, triangles, and composite shapes. Introduces units of measurement and conversion between units."
                elif topic_code == "Linear Equations":
                    textbook_content = "Solves linear equations in one variable with applications to practical problems. Covers transposition method and verification of solutions."
                elif topic_code == "Understanding Quadrilaterals":
                    textbook_content = "Classifies quadrilaterals (trapezium, parallelogram, rectangle, rhombus, square), their properties, angle sum property, and types of polygons."
                elif topic_code == "Mensuration":
                    textbook_content = "Calculates area of trapezium, quadrilateral, polygon; surface area and volume of cube, cuboid, cylinder with real-world applications."
                elif topic_code == "Number Systems":
                    textbook_content = "Covers real numbers, irrational numbers, decimal expansions, operations on real numbers, laws of exponents for real numbers with proofs."
                elif topic_code == "Polynomials":
                    textbook_content = "Defines polynomials, degrees, types (linear, quadratic, cubic), zeros of polynomials, factorization using identities, and algebraic identities."
                elif topic_code == "Coordinate Geometry":
                    textbook_content = "Introduces Cartesian system, plotting points in plane, distance formula, section formula (internal division), and applications to geometric problems."
                elif topic_code == "Linear Equations in Two Variables":
                    textbook_content = "Solves pairs of linear equations graphically and algebraically (substitution, elimination), with word problems on ages, mixtures, etc."
                elif topic_code == "Real Numbers":
                    textbook_content = "Covers Euclid's division lemma and algorithm, fundamental theorem of arithmetic, irrationality proofs (e.g., √2), and decimal expansions."
                elif topic_code == "Pair of Linear Equations":
                    textbook_content = "Solves systems of equations algebraically (substitution, elimination, cross-multiplication), consistency, and graphical interpretation."
                elif topic_code == "Quadratic Equations":
                    textbook_content = "Standard form of quadratic equations, solutions by factorization, completing square, quadratic formula, discriminant, and nature of roots."
                elif topic_code == "Statistics":
                    textbook_content = "Calculates mean, median, mode of grouped and ungrouped data, cumulative frequency, ogives, and measures of central tendency applications."

            # Science content
            elif subject_name == "Science":
                if topic_code == "Food: Where Does It Come From?":
                    textbook_content = "Classifies food sources into plant-based (cereals, pulses, vegetables) and animal-based (milk, eggs, meat). Explains food chains and interdependence."
                elif topic_code == "Components of Food":
                    textbook_content = "Identifies nutrients (carbohydrates, proteins, fats, vitamins, minerals), their sources, functions, deficiency diseases, and balanced diet concepts."
                elif topic_code == "Separation of Substances":
                    textbook_content = "Methods of separation: handpicking, sieving, winnowing, sedimentation, decantation, filtration, evaporation, condensation, and chromatography."
                elif topic_code == "Nutrition in Plants":
                    textbook_content = "Photosynthesis process (chlorophyll, sunlight, CO2), modes of nutrition (autotrophic, heterotrophic), parasitic plants, and insectivorous plants."
                elif topic_code == "Nutrition in Animals":
                    textbook_content = "Human digestive system (mouth, esophagus, stomach, intestines), digestion process, ruminants, amoeba's food vacuole, and balanced diet."
                elif topic_code == "Heat":
                    textbook_content = "Concepts of temperature, thermometers (clinical, laboratory), heat transfer (conduction, convection, radiation), conductors and insulators."
                elif topic_code == "Motion and Time":
                    textbook_content = "Defines speed, uniform/non-uniform motion, measurement of time (pendulum, stopwatch), speed calculation, distance-time graphs."
                elif topic_code == "Electricity":
                    textbook_content = "Electric circuits (cell, bulb, switch), conductors/insulators, heating effect of current, electromagnets, and electrical safety measures."
                elif topic_code == "Crop Production":
                    textbook_content = "Agricultural practices: soil preparation, sowing, irrigation, weeding, harvesting, storage. Modern methods: fertilizers, pesticides, crop rotation."
                elif topic_code == "Microorganisms":
                    textbook_content = "Classification (bacteria, fungi, protozoa, algae, viruses), beneficial uses (medicine, food, environment), harmful effects (diseases, food spoilage)."
                elif topic_code == "Force and Pressure":
                    textbook_content = "Contact/non-contact forces, pressure calculation, atmospheric pressure, applications (hydraulic systems, suction cups), and fluid pressure."
                elif topic_code == "Matter in Our Surroundings":
                    textbook_content = "States of matter, interconversion (melting, boiling, sublimation), evaporation factors, and kinetic theory of matter applications."
                elif topic_code == "Atoms and Molecules":
                    textbook_content = "Laws of chemical combination, atomic theory, molecular mass, mole concept, writing chemical formulas, and molecular structures."
                elif topic_code == "The Fundamental Unit of Life":
                    textbook_content = "Cell structure (plasma membrane, nucleus, cytoplasm), organelles, differences between plant/animal cells, and cell division basics."
                elif topic_code == "Chemical Reactions":
                    textbook_content = "Types of reactions (combination, decomposition, displacement, double displacement), oxidation-reduction, corrosion, and rancidity."
                elif topic_code == "Acids, Bases and Salts":
                    textbook_content = "pH scale, indicators (litmus, turmeric, phenolphthalein), neutralization reactions, preparation and uses of common salts."
                elif topic_code == "Life Processes":
                    textbook_content = "Nutrition (autotrophic, heterotrophic), human respiration, transportation (blood, lymph), excretion (kidneys, nephrons) in living organisms."

            # Social Science content
            elif subject_name == "Social Science":
                if topic_code == "Understanding Diversity":
                    textbook_content = "Explores India's linguistic, religious, and cultural diversity through case studies (Ladakh vs. Kerala). Discusses unity in diversity and prejudice."
                elif topic_code == "Local Government":
                    textbook_content = "Structure of rural (Gram Panchayat, Panchayat Samiti) and urban (Municipalities, Municipal Corporations) local governance with functions."
                elif topic_code == "Maps":
                    textbook_content = "Components of maps (scale, direction, symbols), types (physical, political, thematic), and reading contour lines for elevation."
                elif topic_code == "Democracy and Equality":
                    textbook_content = "Principles of democracy (equality, justice), struggles for equality (civil rights movement), and Indian constitutional values."
                elif topic_code == "India's Neighbours":
                    textbook_content = "Geographical, cultural, economic relations with Pakistan, China, Nepal, Bhutan, Bangladesh, Sri Lanka, and Myanmar."
                elif topic_code == "State Government":
                    textbook_content = "Structure (Legislative Assembly, Council), roles (CM, Governor), law-making process, and comparison with central government functions."
                elif topic_code == "The Indian Constitution":
                    textbook_content = "Key features (federalism, parliamentary system, fundamental rights), historical background, and constitutional amendments process."
                elif topic_code == "Judiciary":
                    textbook_content = "Hierarchy of courts (Supreme, High, District), judicial review, PILs, and role in protecting fundamental rights and constitution."
                elif topic_code == "Natural Resources":
                    textbook_content = "Classification (renewable/non-renewable), conservation methods (water harvesting, afforestation), and sustainable development goals."
                elif topic_code == "Democratic Politics":
                    textbook_content = "Features of democracy (free elections, rule of law), challenges to democracy, and role of political parties and electoral competition."
                elif topic_code == "Climate":
                    textbook_content = "Factors affecting India's climate (latitude, altitude, monsoon winds), seasonal patterns, and climate change impacts."
                elif topic_code == "Nazism and the Rise of Hitler":
                    textbook_content = "Post-WWI Germany, Hitler's propaganda, Nazi ideology (racial hierarchy), Holocaust, and consequences of Nazi rule."
                elif topic_code == "Federalism":
                    textbook_content = "Division of powers (Union, State, Concurrent Lists), decentralization (73rd/74th Amendments), and special status provisions."
                elif topic_code == "Sectors of the Indian Economy":
                    textbook_content = "Primary (agriculture), secondary (manufacturing), tertiary (services) sectors; organized vs unorganized sectors; employment patterns."
                elif topic_code == "Nationalism in India":
                    textbook_content = "Non-Cooperation Movement, Civil Disobedience Movement, role of Gandhi, participation of different groups, and impact of colonialism."

            docs.append({
                "class": class_level,
                "subject_name": subject_name,
                "topic": topic_code,
                "textbook": textbook_content
            })

# Insert into DB
if docs:
    collection.insert_many(docs)
    print(f"✅ Inserted {len(docs)} textbook content documents.")
else:
    print("❌ No textbook content found to insert.")

client.close()