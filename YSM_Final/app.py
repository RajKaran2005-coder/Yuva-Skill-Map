from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import json
import os
import urllib.request
import urllib.error
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Optional .env support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

# Change this in production
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "CHANGE_THIS_SECRET_KEY"
)

DB = "database.db"

ADMIN_EMAIL = "admin@yuva.com"
ADMIN_PASSWORD = "admin123"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

# You can change this in .env if required.
# Example:
# OPENAI_MODEL=gpt-5.6
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6").strip()


# =========================================================
# SUBJECTS
# =========================================================

SUBJECTS = {
    "B.Tech": [
        "Programming / C / C++",
        "Python",
        "Java",
        "Data Structures & Algorithms",
        "DBMS",
        "Operating Systems",
        "Computer Networks",
        "Web Development",
        "AI / ML",
        "Cyber Security",
        "Cloud Computing",
        "Software Engineering"
    ],

    "B.E.": [
        "Programming",
        "Data Structures & Algorithms",
        "DBMS",
        "Operating Systems",
        "Computer Networks",
        "Web Development",
        "AI / ML",
        "Cyber Security",
        "Cloud Computing",
        "Software Engineering"
    ],

    "BCA": [
        "Programming in C",
        "C++ / Java",
        "Python",
        "Data Structures",
        "DBMS",
        "Operating Systems",
        "Computer Networks",
        "Web Development",
        "Software Engineering",
        "Cyber Security",
        "Cloud Computing",
        "Artificial Intelligence"
    ],

    "B.Sc.": [
        "Mathematics",
        "Statistics",
        "Physics",
        "Chemistry",
        "Computer Science",
        "Programming",
        "Data Analysis",
        "Python",
        "Database Fundamentals"
    ],

    "BBA": [
        "Principles of Management",
        "Business Economics",
        "Financial Management",
        "Marketing Management",
        "Human Resource Management",
        "Business Communication",
        "Business Analytics",
        "Entrepreneurship",
        "Business Law",
        "Statistics"
    ],

    "B.Com": [
        "Financial Accounting",
        "Business Economics",
        "Business Law",
        "Corporate Accounting",
        "Cost Accounting",
        "Taxation",
        "Auditing",
        "Business Management",
        "Statistics",
        "Financial Management"
    ],

    "BA": [
        "English",
        "Hindi",
        "History",
        "Political Science",
        "Sociology",
        "Geography",
        "Economics",
        "Psychology",
        "Public Administration",
        "Philosophy",
        "Education"
    ],

    "B.Voc": [
        "Communication Skills",
        "Computer Fundamentals",
        "Programming",
        "Database Fundamentals",
        "Web Development",
        "Digital Marketing",
        "Entrepreneurship",
        "Data Analysis",
        "Industry Skills"
    ],

    "Other Bachelor's Degree": [
        "Communication Skills",
        "Computer Fundamentals",
        "Digital Skills",
        "Problem Solving",
        "Data Analysis",
        "Programming Basics",
        "Career Skills",
        "Entrepreneurship"
    ]
}


# =========================================================
# BRANCHES
# =========================================================

BRANCHES = [
    "Computer Science & Engineering",
    "Information Technology",
    "Artificial Intelligence & Machine Learning",
    "Artificial Intelligence & Data Science",
    "Data Science",
    "Cyber Security",
    "Electronics & Communication Engineering",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Biotechnology",
    "Business Administration",
    "Commerce",
    "Science",
    "Arts",
    "Other"
]


# =========================================================
# ASSESSMENTS
# =========================================================

ASSESSMENTS = {
    "B.Tech": [
        (1, "Programming", "Which data type stores whole numbers in Python?",
         ["int", "float", "string", "boolean"], "int"),

        (2, "Web Development", "Which language structures web pages?",
         ["HTML", "CSS", "SQL", "Python"], "HTML"),

        (3, "Database", "Which SQL command retrieves data?",
         ["SELECT", "DELETE", "DROP", "REMOVE"], "SELECT"),

        (4, "DSA", "Which data structure follows LIFO?",
         ["Queue", "Stack", "Array", "Tree"], "Stack"),

        (5, "DSA", "Which data structure follows FIFO?",
         ["Stack", "Queue", "Graph", "Heap"], "Queue"),

        (6, "Operating Systems", "Which is an operating system?",
         ["Linux", "HTML", "MySQL", "Git"], "Linux"),

        (7, "Computer Networks", "What does IP stand for?",
         ["Internet Protocol", "Internal Program", "Internet Process", "Input Protocol"],
         "Internet Protocol"),

        (8, "OOP", "Which concept hides internal implementation details?",
         ["Encapsulation", "Inheritance", "Compilation", "Iteration"],
         "Encapsulation"),

        (9, "Cyber Security", "Which is a good security practice?",
         ["Share OTP", "Reuse passwords", "Use strong unique passwords", "Disable updates"],
         "Use strong unique passwords"),

        (10, "Cloud Computing", "Which is a cloud platform?",
         ["AWS", "HTML", "CSS", "Git"], "AWS"),

        (11, "Version Control", "Which tool is widely used for version control?",
         ["Git", "Excel", "PowerPoint", "Paint"], "Git"),

        (12, "AI/ML", "Machine Learning is a branch of which field?",
         ["Artificial Intelligence", "Accounting", "Networking", "Operating Systems"],
         "Artificial Intelligence"),

        (13, "Software Engineering",
         "What should be done before coding a large project?",
         ["Requirements analysis", "Skip planning", "Delete tests", "Guess requirements"],
         "Requirements analysis"),

        (14, "Programming", "Which is a programming language?",
         ["Java", "HTML", "CSS", "JSON"], "Java"),

        (15, "Career",
         "Which helps most with software placements?",
         ["Only certificates", "Projects + skills + practice", "Only marks", "Avoid practice"],
         "Projects + skills + practice")
    ],

    "B.E.": [
        (1, "Engineering Basics", "Which unit measures electrical resistance?",
         ["Ohm", "Watt", "Volt", "Ampere"], "Ohm"),

        (2, "Programming", "Which data structure follows LIFO?",
         ["Queue", "Stack", "Tree", "Graph"], "Stack"),

        (3, "Mathematics", "Derivative of x² is?",
         ["2x", "x", "x²", "2"], "2x"),

        (4, "Computer Fundamentals", "CPU stands for?",
         ["Central Processing Unit", "Computer Personal Unit",
          "Central Program Utility", "Control Processing User"],
         "Central Processing Unit"),

        (5, "Problem Solving",
         "What should you do first with a complex problem?",
         ["Break it into smaller parts", "Guess", "Ignore it", "Copy code"],
         "Break it into smaller parts"),

        (6, "Engineering Science", "SI unit of power is?",
         ["Watt", "Joule", "Newton", "Pascal"], "Watt"),

        (7, "Programming", "Which is a programming language?",
         ["C++", "HTML", "CSS", "JSON"], "C++"),

        (8, "Networks",
         "Which device forwards packets between networks?",
         ["Router", "Monitor", "Keyboard", "Printer"], "Router"),

        (9, "Database", "Which command retrieves SQL data?",
         ["SELECT", "DELETE", "DROP", "REMOVE"], "SELECT"),

        (10, "OOP",
         "Which OOP concept allows reuse through parent-child classes?",
         ["Inheritance", "Iteration", "Parsing", "Indexing"],
         "Inheritance"),

        (11, "Cyber Security", "Which is safest?",
         ["Strong unique passwords", "Share OTP",
          "Use unknown links", "Disable updates"],
         "Strong unique passwords"),

        (12, "Software Engineering", "What is testing used for?",
         ["Finding defects", "Writing emails",
          "Buying hardware", "Designing logos"],
         "Finding defects"),

        (13, "Data",
         "Which structure stores key-value pairs in Python?",
         ["Dictionary", "Tuple", "String", "Float"],
         "Dictionary"),

        (14, "Career", "Which improves employability?",
         ["Projects and practical skills", "Only attendance",
          "No practice", "Avoid teamwork"],
         "Projects and practical skills"),

        (15, "Engineering",
         "Which skill is common across engineering careers?",
         ["Problem solving", "Ignoring data",
          "Avoiding communication", "No documentation"],
         "Problem solving")
    ],

    "BCA": [
        (1, "Programming", "Which is a programming language?",
         ["Java", "HTML", "CSS", "JSON"], "Java"),

        (2, "Web Development", "Which language structures web pages?",
         ["HTML", "CSS", "SQL", "Python"], "HTML"),

        (3, "Database", "Which SQL command retrieves data?",
         ["SELECT", "DELETE", "DROP", "REMOVE"], "SELECT"),

        (4, "DSA", "Which data structure follows LIFO?",
         ["Queue", "Stack", "Array", "Tree"], "Stack"),

        (5, "Python", "Which type stores decimal numbers?",
         ["float", "int", "str", "bool"], "float"),

        (6, "Operating Systems", "Which is an operating system?",
         ["Linux", "HTML", "Git", "MySQL"], "Linux"),

        (7, "Networks", "What does HTTP relate to?",
         ["Web communication", "Image editing",
          "Accounting", "Hardware repair"],
         "Web communication"),

        (8, "OOP", "Which concept bundles data and methods?",
         ["Encapsulation", "Sorting", "Routing", "Indexing"],
         "Encapsulation"),

        (9, "Cyber Security", "Which practice is safest?",
         ["Use strong unique passwords", "Share OTP",
          "Reuse passwords", "Disable updates"],
         "Use strong unique passwords"),

        (10, "Cloud", "Which is a cloud platform?",
         ["AWS", "CSS", "Excel", "Git"], "AWS"),

        (11, "Version Control",
         "Which tool manages source code versions?",
         ["Git", "Paint", "Word", "Calculator"], "Git"),

        (12, "AI", "AI stands for?",
         ["Artificial Intelligence", "Automated Internet",
          "Advanced Input", "Application Interface"],
         "Artificial Intelligence"),

        (13, "Software Engineering",
         "What helps maintain code quality?",
         ["Testing", "Skipping tests",
          "No documentation", "Random changes"],
         "Testing"),

        (14, "Problem Solving", "Before coding, you should?",
         ["Understand the problem", "Guess",
          "Skip requirements", "Avoid testing"],
         "Understand the problem"),

        (15, "Career",
         "Which combination is useful for BCA placements?",
         ["Coding + DSA + projects", "Only certificates",
          "Only theory", "No practice"],
         "Coding + DSA + projects")
    ],

    "B.Sc.": [
        (1, "Science", "Which is the SI unit of force?",
         ["Newton", "Watt", "Volt", "Ohm"], "Newton"),

        (2, "Mathematics", "Derivative of x² is?",
         ["2x", "x", "x²", "2"], "2x"),

        (3, "Statistics", "Mean is calculated as?",
         ["Sum divided by count", "Maximum only",
          "Minimum only", "Product divided by count"],
         "Sum divided by count"),

        (4, "Physics", "Speed is distance divided by?",
         ["Time", "Mass", "Force", "Energy"], "Time"),

        (5, "Chemistry", "What is H₂O commonly called?",
         ["Water", "Hydrogen", "Oxygen", "Salt"], "Water"),

        (6, "Computer Science", "Which is a programming language?",
         ["Python", "HTML", "CSS", "SQL"], "Python"),

        (7, "Data Analysis",
         "Which is commonly used for data analysis?",
         ["Python", "Paint", "PowerPoint", "Notepad"],
         "Python"),

        (8, "Statistics", "Median represents?",
         ["Middle value", "Largest value",
          "Smallest value", "Sum"],
         "Middle value"),

        (9, "Biology", "Which organ pumps blood?",
         ["Heart", "Liver", "Lung", "Kidney"], "Heart"),

        (10, "Scientific Method",
         "What comes before testing a hypothesis?",
         ["Formulating a hypothesis", "Ignoring evidence",
          "Changing results", "Skipping observation"],
         "Formulating a hypothesis"),

        (11, "Research",
         "Which source is generally best for academic research?",
         ["Peer-reviewed paper", "Random post",
          "Unverified message", "Anonymous comment"],
         "Peer-reviewed paper"),

        (12, "Environment",
         "Which gas is a major greenhouse gas?",
         ["Carbon dioxide", "Helium", "Neon", "Argon"],
         "Carbon dioxide"),

        (13, "Problem Solving",
         "A good scientific approach uses?",
         ["Evidence and reasoning", "Guesswork only",
          "No measurement", "No testing"],
         "Evidence and reasoning"),

        (14, "Computer Skills",
         "Which format is commonly used for tabular data?",
         ["CSV", "MP3", "PNG", "MP4"], "CSV"),

        (15, "Career",
         "Which helps science graduates?",
         ["Subject knowledge + practical skills",
          "Only certificates", "No projects", "Avoid research"],
         "Subject knowledge + practical skills")
    ],

    "BBA": [
        (1, "Management", "What is the main purpose of planning?",
         ["Set goals and actions", "Avoid decisions",
          "Increase confusion", "Skip resources"],
         "Set goals and actions"),

        (2, "Marketing",
         "The 4Ps include Product, Price, Place and?",
         ["Promotion", "People only", "Profit", "Planning"],
         "Promotion"),

        (3, "Finance", "Revenue means?",
         ["Income from business activities", "Only expenses",
          "Tax only", "Loan only"],
         "Income from business activities"),

        (4, "HR", "HR mainly deals with?",
         ["People and employees", "Machines only",
          "Buildings", "Inventory only"],
         "People and employees"),

        (5, "Economics",
         "Demand generally falls when price rises, other things equal. This is?",
         ["Law of demand", "Law of supply", "GDP", "Inflation"],
         "Law of demand"),

        (6, "Accounting", "Assets are?",
         ["Resources owned/controlled by business",
          "Only expenses", "Only debts", "Only sales"],
         "Resources owned/controlled by business"),

        (7, "Entrepreneurship", "An entrepreneur primarily?",
         ["Creates and manages a venture",
          "Avoids risk completely", "Only studies theory",
          "Never makes decisions"],
         "Creates and manages a venture"),

        (8, "Business Communication",
         "A professional email should be?",
         ["Clear and concise", "Unclear",
          "All caps", "Without subject"],
         "Clear and concise"),

        (9, "Business Law", "A contract generally requires?",
         ["Agreement between parties", "Only a logo",
          "Only a phone call", "No consent"],
         "Agreement between parties"),

        (10, "Leadership", "A good leader should?",
         ["Communicate and motivate", "Avoid feedback",
          "Ignore team", "Never delegate"],
         "Communicate and motivate"),

        (11, "Strategy",
         "SWOT stands for Strengths, Weaknesses, Opportunities and?",
         ["Threats", "Targets", "Teams", "Trends"],
         "Threats"),

        (12, "Operations",
         "Operations management focuses on?",
         ["Efficient processes", "Only advertising",
          "Only recruitment", "Only taxation"],
         "Efficient processes"),

        (13, "Analytics",
         "Business analytics helps organizations?",
         ["Make data-informed decisions", "Avoid data",
          "Remove reports", "Ignore customers"],
         "Make data-informed decisions"),

        (14, "Ethics", "Business ethics concerns?",
         ["Right and responsible conduct", "Only profit",
          "Only advertising", "Only accounting"],
         "Right and responsible conduct"),

        (15, "Career",
         "Useful BBA career preparation includes?",
         ["Communication + business skills + internships",
          "Only certificates", "No practical work",
          "Avoid teamwork"],
         "Communication + business skills + internships")
    ],

    "B.Com": [
        (1, "Accounting", "Assets are?",
         ["Resources owned/controlled by business",
          "Only expenses", "Only liabilities", "Only sales"],
         "Resources owned/controlled by business"),

        (2, "Accounting",
         "Which statement shows financial position?",
         ["Balance Sheet", "Sales invoice",
          "Attendance sheet", "Advertisement"],
         "Balance Sheet"),

        (3, "Economics", "GDP measures?",
         ["Value of final goods and services",
          "Only imports", "Only taxes", "Only wages"],
         "Value of final goods and services"),

        (4, "Finance", "Profit equals?",
         ["Revenue minus expenses", "Assets plus expenses",
          "Sales plus liabilities", "Tax minus sales"],
         "Revenue minus expenses"),

        (5, "Taxation", "GST is a?",
         ["Goods and Services Tax", "General Sales Trade",
          "Government Service Tariff", "Goods Supply Transfer"],
         "Goods and Services Tax"),

        (6, "Auditing", "Auditing mainly examines?",
         ["Financial records and controls",
          "Only advertisements", "Only employees", "Only buildings"],
         "Financial records and controls"),

        (7, "Business Law", "A contract is primarily an?",
         ["Agreement enforceable by law", "Advertisement",
          "Invoice only", "Email signature"],
         "Agreement enforceable by law"),

        (8, "Cost Accounting", "Cost accounting helps determine?",
         ["Cost of products/services", "Only market share",
          "Only tax rates", "Only salaries"],
         "Cost of products/services"),

        (9, "Management", "Planning involves?",
         ["Setting objectives and actions", "Ignoring goals",
          "Avoiding resources", "Removing controls"],
         "Setting objectives and actions"),

        (10, "Marketing", "Promotion is part of?",
         ["Marketing mix", "Balance sheet",
          "Auditing", "Tax return"],
         "Marketing mix"),

        (11, "Banking", "A bank deposit account is used to?",
         ["Safely hold money", "Only calculate tax",
          "Only advertise", "Issue shares automatically"],
         "Safely hold money"),

        (12, "Statistics", "Mean equals?",
         ["Sum divided by number of observations",
          "Largest value", "Smallest value", "Middle value always"],
         "Sum divided by number of observations"),

        (13, "Economics", "Inflation means?",
         ["General rise in prices", "Fall in all prices",
          "Only wage increase", "Only tax decrease"],
         "General rise in prices"),

        (14, "Business Communication",
         "A formal report should be?",
         ["Structured and evidence-based", "Random",
          "Without headings", "Only images"],
         "Structured and evidence-based"),

        (15, "Career",
         "Useful B.Com preparation includes?",
         ["Accounting + Excel/data skills + communication",
          "Only certificates", "No practice", "Avoid internships"],
         "Accounting + Excel/data skills + communication")
    ],

    "BA": [
        (1, "English", "Choose the correct sentence.",
         ["She goes to college every day.",
          "She go to college every day.",
          "She going college every day.",
          "She gone to college every day."],
         "She goes to college every day."),

        (2, "History", "Who founded the Maurya Empire?",
         ["Chandragupta Maurya", "Ashoka", "Akbar", "Harsha"],
         "Chandragupta Maurya"),

        (3, "Political Science",
         "The Constitution of India came into effect on?",
         ["26 January 1950", "15 August 1947",
          "26 November 1949", "2 October 1950"],
         "26 January 1950"),

        (4, "Geography", "Which is the longest river in India?",
         ["Ganga", "Yamuna", "Narmada", "Godavari"], "Ganga"),

        (5, "Sociology", "Sociology is the study of?",
         ["Society and social relationships", "Stars",
          "Chemical reactions", "Computer networks"],
         "Society and social relationships"),

        (6, "Economics", "GDP measures?",
         ["Value of final goods and services",
          "Only taxes", "Only exports", "Only population"],
         "Value of final goods and services"),

        (7, "Psychology", "Psychology mainly studies?",
         ["Mind and behaviour", "Rocks", "Markets only", "Computers"],
         "Mind and behaviour"),

        (8, "Philosophy", "Ethics is concerned with?",
         ["Moral principles", "Weather",
          "Accounting", "Programming"],
         "Moral principles"),

        (9, "Public Administration",
         "Public administration mainly concerns?",
         ["Implementation of government policies",
          "Only private sales", "Only literature", "Only sports"],
         "Implementation of government policies"),

        (10, "Education", "Pedagogy refers to?",
         ["Methods and practice of teaching", "Economic growth",
          "Map making", "Taxation"],
         "Methods and practice of teaching"),

        (11, "English Literature", "A novel is generally?",
         ["A long fictional prose narrative", "A scientific formula",
          "A legal contract", "A map"],
         "A long fictional prose narrative"),

        (12, "Indian History",
         "The Quit India Movement began in?",
         ["1942", "1857", "1919", "1947"], "1942"),

        (13, "Indian Polity",
         "India is described by the Constitution as a?",
         ["Sovereign Socialist Secular Democratic Republic",
          "Monarchy", "Military state", "Colonial state"],
         "Sovereign Socialist Secular Democratic Republic"),

        (14, "Current Awareness",
         "Which skill is important for humanities careers?",
         ["Communication and critical thinking",
          "Only coding", "Only accounting", "Avoid reading"],
         "Communication and critical thinking"),

        (15, "Career",
         "Useful BA career preparation includes?",
         ["Subject knowledge + communication + digital skills",
          "Only certificates", "No reading", "Avoid writing"],
         "Subject knowledge + communication + digital skills")
    ],

    "B.Voc": [
        (1, "Communication", "Effective professional communication should be?",
         ["Clear and concise", "Confusing",
          "Unstructured", "Only informal"],
         "Clear and concise"),

        (2, "Digital Skills", "Which is used to store tabular data?",
         ["Spreadsheet", "MP3 player", "Image editor", "Video player"],
         "Spreadsheet"),

        (3, "Computer Fundamentals", "CPU stands for?",
         ["Central Processing Unit", "Computer Personal Unit",
          "Central Program Utility", "Control Processing User"],
         "Central Processing Unit"),

        (4, "Programming", "Which is a programming language?",
         ["Python", "HTML", "CSS", "JSON"], "Python"),

        (5, "Database", "Which command retrieves SQL data?",
         ["SELECT", "DELETE", "DROP", "REMOVE"], "SELECT"),

        (6, "Web Development", "Which language structures web pages?",
         ["HTML", "CSS", "SQL", "Python"], "HTML"),

        (7, "Entrepreneurship", "An entrepreneur creates?",
         ["A venture or business opportunity", "Only reports",
          "Only exams", "Only advertisements"],
         "A venture or business opportunity"),

        (8, "Data Analysis", "Which is commonly used for data analysis?",
         ["Excel", "Paint", "Calculator only", "Music player"],
         "Excel"),

        (9, "Problem Solving",
         "First step in solving a practical problem is?",
         ["Understand the problem", "Guess",
          "Ignore users", "Skip requirements"],
         "Understand the problem"),

        (10, "Cyber Security", "A strong password should be?",
         ["Unique and hard to guess", "Shared publicly",
          "Same everywhere", "Only your name"],
         "Unique and hard to guess"),

        (11, "Career Skills", "Internships help students gain?",
         ["Practical experience", "Only attendance",
          "Only marks", "No skills"],
         "Practical experience"),

        (12, "Teamwork", "Good teamwork requires?",
         ["Communication and cooperation", "No communication",
          "Only one person", "Avoiding feedback"],
         "Communication and cooperation"),

        (13, "Cloud", "AWS is an example of?",
         ["Cloud platform", "Text editor",
          "Database language", "Operating system"],
         "Cloud platform"),

        (14, "Version Control", "Git is used for?",
         ["Version control", "Photo editing",
          "Accounting", "Video playback"],
         "Version control"),

        (15, "Career",
         "A good vocational portfolio should show?",
         ["Projects and practical skills",
          "Only certificates", "No work", "Only personal photos"],
         "Projects and practical skills")
    ],

    "Other Bachelor's Degree": [
        (1, "Communication", "Professional communication should be?",
         ["Clear and concise", "Confusing",
          "Unstructured", "Only informal"],
         "Clear and concise"),

        (2, "Digital Skills",
         "Which tool is commonly used for documents?",
         ["Microsoft Word", "MP3 player", "Camera", "Music app"],
         "Microsoft Word"),

        (3, "Computer Fundamentals", "CPU stands for?",
         ["Central Processing Unit", "Computer Personal Unit",
          "Central Program Utility", "Control Processing User"],
         "Central Processing Unit"),

        (4, "Problem Solving",
         "What should you do first with a complex problem?",
         ["Break it into smaller parts", "Guess",
          "Ignore it", "Copy blindly"],
         "Break it into smaller parts"),

        (5, "Data Skills",
         "Which is a common spreadsheet application?",
         ["Microsoft Excel", "Paint", "VLC", "Notepad only"],
         "Microsoft Excel"),

        (6, "Internet Skills", "Which is a web browser?",
         ["Chrome", "Excel", "PowerPoint", "Photoshop"],
         "Chrome"),

        (7, "Cyber Security", "Which practice is safest?",
         ["Use strong unique passwords", "Share OTP",
          "Reuse passwords", "Disable updates"],
         "Use strong unique passwords"),

        (8, "Career Skills", "Which improves employability?",
         ["Skills and projects", "Only certificates",
          "No practice", "Avoid teamwork"],
         "Skills and projects"),

        (9, "Communication", "Active listening means?",
         ["Paying attention and understanding",
          "Interrupting constantly",
          "Ignoring the speaker", "Checking only messages"],
         "Paying attention and understanding"),

        (10, "Critical Thinking", "Critical thinking relies on?",
         ["Evidence and reasoning", "Rumours",
          "Guesswork", "No analysis"],
         "Evidence and reasoning"),

        (11, "Teamwork", "Effective teams need?",
         ["Communication and cooperation", "No communication",
          "Only one member", "No goals"],
         "Communication and cooperation"),

        (12, "Entrepreneurship", "Entrepreneurship involves?",
         ["Creating value and managing a venture",
          "Avoiding all decisions", "Only studying",
          "Only applying for jobs"],
         "Creating value and managing a venture"),

        (13, "Digital Literacy",
         "Which is a cloud storage service?",
         ["Google Drive", "Paint", "Calculator", "Notepad"],
         "Google Drive"),

        (14, "Professional Skills", "A good resume should be?",
         ["Relevant and concise", "Very long and unrelated",
          "Without skills", "Only photos"],
         "Relevant and concise"),

        (15, "Career", "A strong career plan includes?",
         ["Goals + skills + practical experience",
          "Only marks", "No goals", "Avoid learning"],
         "Goals + skills + practical experience")
    ]
}


# Backward compatibility
Q = ASSESSMENTS["B.Tech"]


def get_questions(user):
    degree = user["degree"] if user else ""
    return ASSESSMENTS.get(
        degree,
        ASSESSMENTS["Other Bachelor's Degree"]
    )


# =========================================================
# CAREER MAP
# =========================================================

CAREER = {
    "Web Development": (
        "Web Developer",
        ["HTML", "CSS", "JavaScript", "Git",
         "Frontend framework", "Backend basics", "Projects"]
    ),

    "Programming": (
        "Software Developer",
        ["One programming language", "OOP", "DSA",
         "Git", "Projects", "Interview practice"]
    ),

    "DSA": (
        "Software Engineer / SDE Track",
        ["DSA", "OOP", "Problem Solving",
         "Coding practice", "Projects", "Interview practice"]
    ),

    "Cyber Security": (
        "Cyber Security Analyst",
        ["Networking", "Linux", "Security fundamentals",
         "OWASP basics", "Security practice", "Projects"]
    ),

    "Cloud": (
        "Cloud / DevOps Track",
        ["Linux", "Networking", "Cloud fundamentals",
         "Docker", "CI/CD", "Projects"]
    ),

    "AI/ML": (
        "AI/ML Beginner Track",
        ["Python", "Statistics", "NumPy/Pandas",
         "ML fundamentals", "Projects"]
    ),

    "Database": (
        "Backend / Database Developer",
        ["SQL", "Database design", "Backend language",
         "APIs", "Projects"]
    ),

    "Version Control": (
        "Software Developer",
        ["Git", "GitHub", "Branching",
         "Collaboration", "Projects"]
    ),

    "Problem Solving": (
        "Software Developer",
        ["DSA", "Problem Solving", "OOP",
         "Projects", "Interview practice"]
    ),

    "Computer Science": (
        "IT / Software Track",
        ["Programming", "DSA", "OS",
         "DBMS", "Networks", "Projects"]
    ),

    "Career": (
        "Career Readiness Track",
        ["Communication", "Aptitude", "Projects",
         "Resume", "Interview practice"]
    ),

    "English": (
        "Content / Communication Track",
        ["English communication", "Writing",
         "Literature", "Digital content", "Presentation"]
    ),

    "History": (
        "History / Research Track",
        ["History research", "Writing",
         "Archives", "Critical thinking", "Communication"]
    ),

    "Political Science": (
        "Public Policy / Civil Services Track",
        ["Indian Polity", "Current affairs",
         "Public administration", "Writing", "Communication"]
    ),

    "Geography": (
        "Geography / GIS Track",
        ["Geography", "GIS basics", "Environment",
         "Data interpretation", "Research"]
    ),

    "Sociology": (
        "Social Research Track",
        ["Sociology", "Research methods",
         "Data interpretation", "Writing", "Communication"]
    ),

    "Economics": (
        "Economics / Finance Track",
        ["Microeconomics", "Macroeconomics",
         "Statistics", "Excel", "Data analysis"]
    ),

    "Psychology": (
        "Psychology / HR Track",
        ["Psychology", "Research methods",
         "Communication", "Counselling basics", "HR skills"]
    ),

    "Philosophy": (
        "Teaching / Research Track",
        ["Logic", "Critical thinking",
         "Research", "Writing", "Communication"]
    ),

    "Public Administration": (
        "Public Administration / Civil Services Track",
        ["Governance", "Public policy",
         "Current affairs", "Writing", "Communication"]
    ),

    "Education": (
        "Teaching / Education Track",
        ["Pedagogy", "Communication",
         "Lesson planning", "Child development",
         "Digital teaching"]
    ),

    "Management": (
        "Management Track",
        ["Management", "Communication",
         "Leadership", "Marketing", "Business analytics"]
    ),

    "Marketing": (
        "Marketing Track",
        ["Marketing", "Digital marketing",
         "Communication", "Analytics", "Projects"]
    ),

    "Accounting": (
        "Accounting / Finance Track",
        ["Accounting", "Excel", "Taxation",
         "Auditing", "Financial analysis"]
    ),

    "Finance": (
        "Finance Track",
        ["Financial management", "Accounting",
         "Excel", "Analysis", "Communication"]
    ),

    "Science": (
        "Science / Research Track",
        ["Subject knowledge", "Statistics",
         "Research", "Data analysis", "Projects"]
    ),

    "Mathematics": (
        "Data / Analytics Track",
        ["Mathematics", "Statistics", "Python",
         "Data analysis", "Problem solving"]
    ),

    "Statistics": (
        "Data Analytics Track",
        ["Statistics", "Excel", "Python",
         "Data visualization", "Research"]
    ),

    "Physics": (
        "Physics / Research Track",
        ["Physics", "Mathematics", "Lab skills",
         "Research", "Data analysis"]
    ),

    "Chemistry": (
        "Chemistry / Research Track",
        ["Chemistry", "Lab skills", "Research",
         "Data analysis", "Safety"]
    )
}


# =========================================================
# DATABASE
# =========================================================

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    c = conn()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            degree TEXT NOT NULL,
            branch TEXT NOT NULL,
            course TEXT NOT NULL,
            subjects TEXT NOT NULL,
            batch TEXT NOT NULL,
            semester TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            score INTEGER,
            total INTEGER,
            percentage REAL,
            level TEXT,
            recommendation TEXT,
            roadmap TEXT,
            category_scores TEXT,
            answers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cols = [
        row[1]
        for row in c.execute(
            "PRAGMA table_info(results)"
        ).fetchall()
    ]

    if "answers" not in cols:
        c.execute(
            "ALTER TABLE results ADD COLUMN answers TEXT"
        )

    c.commit()
    c.close()


# =========================================================
# AUTH DECORATORS
# =========================================================

def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if session.get("user_id"):
            return f(*a, **k)
        return redirect(url_for("login"))

    return w


def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        if session.get("admin"):
            return f(*a, **k)
        return redirect(url_for("admin_login"))

    return w


# =========================================================
# ASSESSMENT ANALYSIS
# =========================================================

def analyze(ans, questions):
    scores = {}
    score = 0

    for i, cat, text, opts, correct in questions:
        scores.setdefault(cat, 0)

        if ans.get(str(i)) == correct:
            score += 1
            scores[cat] += 1

    total = len(questions)

    if total == 0:
        return (
            0,
            0,
            "Beginner",
            "Please complete the assessment.",
            "Communication → Digital skills → Projects",
            {}
        )

    pct = round(score / total * 100, 1)

    if pct >= 80:
        level = "Excellent"
    elif pct >= 60:
        level = "Strong"
    elif pct >= 40:
        level = "Developing"
    else:
        level = "Beginner"

    top = max(scores, key=scores.get) if scores else "Career"

    career, roadmap = CAREER.get(
        top,
        (
            "Career Exploration",
            [
                "Communication",
                "Digital skills",
                "Projects",
                "Internships"
            ]
        )
    )

    recommendation = (
        f"Your strongest assessed area is {top}. "
        f"A suitable direction to explore is {career}."
    )

    return (
        score,
        pct,
        level,
        recommendation,
        " → ".join(roadmap),
        scores
    )


# =========================================================
# LOCAL AI FALLBACK
# =========================================================

def local_ai_answer(question, language="en", context=None):
    """
    Local fallback.

    This function is used when:
    - API key is missing
    - API credits are exhausted
    - API returns 429
    - API model is unavailable
    - API request times out
    - Any unexpected API error happens
    """

    q = (question or "").lower()

    # Hindi / Hinglish friendly answers
    if any(x in q for x in [
        "dsa",
        "data structure",
        "array",
        "linked list",
        "stack",
        "queue"
    ]):
        if language == "hi":
            return (
                "DSA data ko efficiently store aur process karne ka tarika hai. "
                "Start arrays aur strings se karo, phir linked list, stack, queue, "
                "trees aur graphs padho. Roz 1-2 problems practice karo."
            )

        return (
            "DSA is about choosing efficient ways to store data and solve problems. "
            "Start with arrays and strings, then learn linked lists, stacks, queues, "
            "trees and graphs. Practice 1–2 problems regularly."
        )

    if any(x in q for x in [
        "python",
        "java",
        "c++",
        "c language",
        "programming",
        "coding"
    ]):
        if language == "hi":
            return (
                "Programming ke liye pehle ek language properly seekho. "
                "Python ya Java se start kar sakte ho. Variables, conditions, "
                "loops, functions, OOP aur phir DSA padho. Har topic ke baad "
                "small programs banao."
            )

        return (
            "For programming, first learn one language properly. "
            "You can start with Python or Java. Learn variables, conditions, "
            "loops, functions and OOP, then move to DSA. Build small programs "
            "after each topic."
        )

    if any(x in q for x in [
        "career",
        "job",
        "placement",
        "developer",
        "software"
    ]):
        if language == "hi":
            return (
                "Software career ke liye programming fundamentals, DSA, Git, "
                "projects, communication aur interview practice important hain. "
                "Ek time par ek skill par focus karo aur projects ke through practice karo."
            )

        return (
            "For a software career, focus on programming fundamentals, DSA, Git, "
            "projects, communication and interview practice. Learn one skill at "
            "a time and apply it through projects."
        )

    if any(x in q for x in [
        "web",
        "html",
        "css",
        "javascript",
        "website"
    ]):
        if language == "hi":
            return (
                "Web development ke liye HTML → CSS → JavaScript sequence follow karo. "
                "Uske baad Git, frontend framework aur backend basics seekho. "
                "Ek responsive website project zaroor banao."
            )

        return (
            "For web development, follow HTML → CSS → JavaScript. "
            "Then learn Git, a frontend framework and backend basics. "
            "Build at least one responsive website project."
        )

    if any(x in q for x in [
        "cyber",
        "security",
        "hacking",
        "network"
    ]):
        if language == "hi":
            return (
                "Cyber Security ke liye pehle networking, Linux aur security fundamentals "
                "seekho. Uske baad OWASP basics aur safe security labs par practice karo."
            )

        return (
            "For Cyber Security, start with networking, Linux and security fundamentals. "
            "Then learn OWASP basics and practice in safe, authorized labs."
        )

    if any(x in q for x in [
        "cloud",
        "aws",
        "devops"
    ]):
        if language == "hi":
            return (
                "Cloud/DevOps ke liye Linux aur networking se start karo. "
                "Phir cloud fundamentals, Docker, CI/CD aur deployment projects seekho."
            )

        return (
            "For Cloud/DevOps, start with Linux and networking. "
            "Then learn cloud fundamentals, Docker, CI/CD and deployment projects."
        )

    if language == "hi":
        return (
            "Main YSM Career Mentor hoon. Aap programming, DSA, Web Development, "
            "Cyber Security, Cloud, projects, assessment ya career roadmap ke baare "
            "mein question pooch sakte ho. Main step-by-step explain karunga."
        )

    return (
        "I am the YSM Career Mentor. You can ask me about programming, DSA, "
        "Web Development, Cyber Security, Cloud, projects, assessment or career "
        "roadmaps. I will explain things step by step."
    )


# =========================================================
# OPENAI API
# =========================================================

def call_openai(question, language, context, history):
    """
    Calls OpenAI API.

    Returns:
        answer, None
    OR:
        None, error_message
    """

    if not OPENAI_API_KEY:
        return None, "missing_api_key"

    lang_names = {
        "hi": "Hindi",
        "en": "English",
        "bn": "Bengali",
        "mr": "Marathi",
        "ta": "Tamil",
        "te": "Telugu",
        "gu": "Gujarati"
    }

    selected_language = lang_names.get(
        language,
        "English"
    )

    system = (
        f"You are YSM AI Career Mentor for a student. "
        f"Reply only in {selected_language}. "
        "Be encouraging, concise, educational and practical. "
        "Use the student's assessment context when relevant. "
        "Do not claim to be a human. "
        "Answer follow-up questions consistently. "
        f"Student context: {json.dumps(context, ensure_ascii=False)}"
    )

    messages = [
        {
            "role": "system",
            "content": system
        }
    ]

    for h in history[-8:]:
        if (
            isinstance(h, dict)
            and h.get("role") in ("user", "assistant")
            and h.get("content")
        ):
            messages.append({
                "role": h["role"],
                "content": h["content"]
            })

    messages.append({
        "role": "user",
        "content": question
    })

    payload = json.dumps({
        "model": OPENAI_MODEL,
        "input": messages,
        "store": False
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=payload,
        headers={
            "Authorization": "Bearer " + OPENAI_API_KEY,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=45
        ) as response:

            obj = json.loads(
                response.read().decode("utf-8")
            )

        answer = obj.get("output_text")

        if not answer:
            parts = []

            for item in obj.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        parts.append(
                            content.get("text", "")
                        )

            answer = "".join(parts).strip()

        if not answer:
            return None, "empty_response"

        return answer, None

    except urllib.error.HTTPError as e:

        try:
            detail = e.read().decode(
                "utf-8",
                errors="ignore"
            )
        except Exception:
            detail = ""

        # 429 = quota/rate limit
        if e.code == 429:
            return None, "quota_or_rate_limit"

        # Other OpenAI errors also go to fallback
        if e.code in (400, 401, 403, 404, 500, 502, 503):
            return None, f"api_error_{e.code}"

        return None, f"http_error_{e.code}"

    except urllib.error.URLError:
        return None, "network_error"

    except TimeoutError:
        return None, "timeout"

    except Exception:
        return None, "unknown_error"


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        d = {
            k: request.form.get(k, "").strip()
            for k in [
                "name",
                "email",
                "degree",
                "branch",
                "course",
                "batch",
                "semester"
            ]
        }

        pw = request.form.get("password", "")
        subs = request.form.getlist("subjects")

        if not all(d.values()) or not pw or not subs:
            return render_template(
                "register.html",
                error="Please fill all fields and select at least one subject.",
                degrees=list(SUBJECTS),
                branches=BRANCHES,
                subjects_map=SUBJECTS
            )

        if len(pw) < 6:
            return render_template(
                "register.html",
                error="Password must contain at least 6 characters.",
                degrees=list(SUBJECTS),
                branches=BRANCHES,
                subjects_map=SUBJECTS
            )

        c = conn()

        try:
            c.execute(
                """
                INSERT INTO users(
                    name,email,password,degree,branch,
                    course,subjects,batch,semester
                )
                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    d["name"],
                    d["email"].lower(),
                    generate_password_hash(pw),
                    d["degree"],
                    d["branch"],
                    d["course"],
                    json.dumps(subs),
                    d["batch"],
                    d["semester"]
                )
            )

            c.commit()

        except sqlite3.IntegrityError:

            c.close()

            return render_template(
                "register.html",
                error="Email already registered.",
                degrees=list(SUBJECTS),
                branches=BRANCHES,
                subjects_map=SUBJECTS
            )

        c.close()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template(
        "register.html",
        degrees=list(SUBJECTS),
        branches=BRANCHES,
        subjects_map=SUBJECTS
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        c = conn()

        u = c.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        c.close()

        if u and check_password_hash(
            u["password"],
            password
        ):

            session.clear()
            session["user_id"] = u["id"]

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    r = c.execute(
        """
        SELECT * FROM results
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    c.close()

    return render_template(
        "dashboard.html",
        user=u,
        latest=r
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    c.close()

    return render_template(
        "profile.html",
        user=u,
        subjects=json.loads(u["subjects"])
    )


# =========================================================
# ASSESSMENT
# =========================================================

@app.route("/assessment")
@login_required
def assessment():

    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    c.close()

    questions = get_questions(u)

    return render_template(
        "assessment.html",
        questions=questions,
        degree=u["degree"],
        course=u["course"]
    )


# =========================================================
# RESULT
# =========================================================

@app.route("/result", methods=["POST"])
@login_required
def result():

    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    c.close()

    questions = get_questions(u)

    ans = {
        str(i): request.form.get(f"q{i}")
        for i, *_ in questions
    }

    (
        score,
        pct,
        level,
        rec,
        road,
        cats
    ) = analyze(ans, questions)

    c = conn()

    c.execute(
        """
        INSERT INTO results(
            user_id,score,total,percentage,level,
            recommendation,roadmap,category_scores,answers
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            session["user_id"],
            score,
            len(questions),
            pct,
            level,
            rec,
            road,
            json.dumps(cats),
            json.dumps(ans)
        )
    )

    c.commit()

    rid = c.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    c.close()

    return redirect(
        url_for(
            "result_view",
            result_id=rid
        )
    )


# =========================================================
# RESULT VIEW
# =========================================================

@app.route("/result/<int:result_id>")
@login_required
def result_view(result_id):

    c = conn()

    r = c.execute(
        """
        SELECT
            r.*,
            u.name,
            u.degree,
            u.branch,
            u.course,
            u.subjects,
            u.batch,
            u.semester
        FROM results r
        JOIN users u ON u.id=r.user_id
        WHERE r.id=? AND r.user_id=?
        """,
        (
            result_id,
            session["user_id"]
        )
    ).fetchone()

    c.close()

    if not r:
        return redirect(
            url_for("dashboard")
        )

    categories = json.loads(
        r["category_scores"] or "{}"
    )

    saved_answers = json.loads(
        r["answers"] or "{}"
    )

    question_review = []

    for (
        i,
        cat,
        text,
        opts,
        correct
    ) in get_questions(r):

        selected = saved_answers.get(
            str(i)
        )

        question_review.append({
            "number": i,
            "category": cat,
            "text": text,
            "selected": selected,
            "correct": correct,
            "is_correct": selected == correct
        })

    ranked = sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top1 = (
        ranked[0][0]
        if ranked
        else "Career Skills"
    )

    top2 = (
        ranked[1][0]
        if len(ranked) > 1
        else top1
    )

    career_map_text = (
        f"Your assessment shows your strongest area is {top1}. "
        f"The suggested direction is based on this strength and "
        f"your selected course ({r['degree']}). "
        f"Use the roadmap below to build the missing skills step by step."
    )

    chart_text = (
        f"The chart compares your performance across assessment "
        f"categories. {top1} is currently your strongest area, "
        f"while {top2} is another area to keep developing. "
        f"Focus first on the lowest-scoring categories and practice "
        f"them regularly."
    )

    roadmap_text = (
        f"This roadmap starts from your {top1} strength and moves "
        f"toward practical career skills. Follow each step in order, "
        f"practice with small tasks, and build at least one project. "
        f"Your next goal is consistent improvement rather than trying "
        f"to learn everything at once."
    )

    return render_template(
        "result.html",
        result=r,
        categories=categories,
        subjects=json.loads(r["subjects"]),
        career_map_text=career_map_text,
        chart_text=chart_text,
        roadmap_text=roadmap_text,
        question_review=question_review
    )


# =========================================================
# AI CHAT
# =========================================================

@app.route("/api/ai-chat", methods=["POST"])
@login_required
def ai_chat():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        question = (
            data.get("message") or ""
        ).strip()

        language = (
            data.get("language")
            or "en"
        )

        context = (
            data.get("context")
            or {}
        )

        history = (
            data.get("history")
            or []
        )

        if not question:

            return {
                "answer": "Please enter a question.",
                "mode": "local"
            }, 200

        # -------------------------------------------------
        # FIRST TRY OPENAI
        # -------------------------------------------------

        answer, error = call_openai(
            question=question,
            language=language,
            context=context,
            history=history
        )

        if answer:

            return {
                "answer": answer,
                "mode": "openai"
            }, 200

        # -------------------------------------------------
        # AUTOMATIC FALLBACK
        # -------------------------------------------------

        fallback = local_ai_answer(
            question,
            language,
            context
        )

        # Never expose raw OpenAI error to the user.
        return {
            "answer": fallback,
            "mode": "local",
            "fallback": True
        }, 200

    except Exception:

        # Final safety fallback.
        return {
            "answer": local_ai_answer(
                request.form.get(
                    "message",
                    ""
                ),
                "en",
                {}
            ),
            "mode": "local",
            "fallback": True
        }, 200


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).lower()

        password = request.form.get(
            "password",
            ""
        )

        if (
            email == ADMIN_EMAIL
            and password == ADMIN_PASSWORD
        ):

            session.clear()
            session["admin"] = True

            return redirect(
                url_for("admin_dashboard")
            )

    return render_template(
        "admin_login.html",
        error=(
            "Invalid admin credentials."
            if request.method == "POST"
            else None
        )
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    c = conn()

    users = c.execute(
        "SELECT * FROM users ORDER BY id DESC"
    ).fetchall()

    results = c.execute(
        """
        SELECT r.*,u.name,u.email
        FROM results r
        JOIN users u ON u.id=r.user_id
        ORDER BY r.id DESC
        """
    ).fetchall()

    c.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        results=results
    )


# =========================================================
# ADMIN EDIT USER
# =========================================================

@app.route(
    "/admin/edit-user/<int:uid>",
    methods=["GET", "POST"]
)
@admin_required
def edit_user(uid):

    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()

    if not u:

        c.close()

        return redirect(
            url_for("admin_dashboard")
        )

    if request.method == "POST":

        d = {
            k: request.form.get(k, "").strip()
            for k in [
                "name",
                "email",
                "degree",
                "branch",
                "course",
                "batch",
                "semester"
            ]
        }

        subs = request.form.getlist(
            "subjects"
        )

        if not all(d.values()) or not subs:

            c.close()

            return render_template(
                "edit_user.html",
                user=u,
                error="Please fill all fields and select at least one subject.",
                degrees=list(SUBJECTS),
                branches=BRANCHES,
                subjects_map=SUBJECTS,
                selected_subjects=subs
            )

        try:

            c.execute(
                """
                UPDATE users
                SET
                    name=?,
                    email=?,
                    degree=?,
                    branch=?,
                    course=?,
                    subjects=?,
                    batch=?,
                    semester=?
                WHERE id=?
                """,
                (
                    d["name"],
                    d["email"].lower(),
                    d["degree"],
                    d["branch"],
                    d["course"],
                    json.dumps(subs),
                    d["batch"],
                    d["semester"],
                    uid
                )
            )

            c.commit()

        except sqlite3.IntegrityError:

            c.close()

            return render_template(
                "edit_user.html",
                user=u,
                error="That email is already used by another account.",
                degrees=list(SUBJECTS),
                branches=BRANCHES,
                subjects_map=SUBJECTS,
                selected_subjects=subs
            )

        c.close()

        return redirect(
            url_for("admin_dashboard")
        )

    selected = json.loads(
        u["subjects"]
    )

    c.close()

    return render_template(
        "edit_user.html",
        user=u,
        degrees=list(SUBJECTS),
        branches=BRANCHES,
        subjects_map=SUBJECTS,
        selected_subjects=selected
    )


# =========================================================
# ADMIN EDIT RESULT
# =========================================================

@app.route(
    "/admin/edit-result/<int:rid>",
    methods=["GET", "POST"]
)
@admin_required
def edit_result(rid):

    c = conn()

    r = c.execute(
        """
        SELECT r.*,u.name
        FROM results r
        JOIN users u ON u.id=r.user_id
        WHERE r.id=?
        """,
        (rid,)
    ).fetchone()

    if not r:

        c.close()

        return redirect(
            url_for("admin_dashboard")
        )

    if request.method == "POST":

        total = max(
            1,
            int(r["total"] or 15)
        )

        try:
            score = int(
                request.form.get(
                    "score",
                    0
                )
            )
        except ValueError:
            score = 0

        score = max(
            0,
            min(total, score)
        )

        pct = round(
            score / total * 100,
            1
        )

        if pct >= 80:
            level = "Excellent"
        elif pct >= 60:
            level = "Strong"
        elif pct >= 40:
            level = "Developing"
        else:
            level = "Beginner"

        recommendation = request.form.get(
            "recommendation",
            ""
        ).strip()

        roadmap = request.form.get(
            "roadmap",
            ""
        ).strip()

        c.execute(
            """
            UPDATE results
            SET
                score=?,
                percentage=?,
                level=?,
                recommendation=?,
                roadmap=?
            WHERE id=?
            """,
            (
                score,
                pct,
                level,
                recommendation,
                roadmap,
                rid
            )
        )

        c.commit()
        c.close()

        return redirect(
            url_for("admin_dashboard")
        )

    c.close()

    return render_template(
        "edit_result.html",
        result=r
    )


# =========================================================
# ADMIN DELETE USER
# =========================================================

@app.route(
    "/admin/delete-user/<int:uid>",
    methods=["POST"]
)
@admin_required
def delete_user(uid):

    c = conn()

    c.execute(
        "DELETE FROM results WHERE user_id=?",
        (uid,)
    )

    c.execute(
        "DELETE FROM users WHERE id=?",
        (uid,)
    )

    c.commit()
    c.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN DELETE RESULT
# =========================================================

@app.route(
    "/admin/delete-result/<int:rid>",
    methods=["POST"]
)
@admin_required
def delete_result(rid):

    c = conn()

    c.execute(
        "DELETE FROM results WHERE id=?",
        (rid,)
    )

    c.commit()
    c.close()

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    init()

    print("----------------------------------------")
    print("Yuva Skill Map starting...")
    print("Open: http://127.0.0.1:5000/")
    print("----------------------------------------")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )