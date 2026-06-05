"""
Generates a professional PDF report for SignSpeak project.
Run: python generate_pdf.py
Output: documents/SignSpeak_Complete_Explanation.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "documents", "SignSpeak_Complete_Explanation.pdf")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# ─── Color Palette ────────────────────────────────────────────────────────────
PURPLE      = colors.HexColor("#7C3AED")
PURPLE_DARK = colors.HexColor("#5B21B6")
PURPLE_LIGHT= colors.HexColor("#EDE9FE")
GREEN       = colors.HexColor("#10B981")
DARK_BG     = colors.HexColor("#0F172A")
LIGHT_TEXT  = colors.HexColor("#F8FAFC")
BODY_TEXT   = colors.HexColor("#1E293B")
MUTED       = colors.HexColor("#64748B")
BORDER      = colors.HexColor("#E2E8F0")
YELLOW_BG   = colors.HexColor("#FFFBEB")
YELLOW_BORDER=colors.HexColor("#F59E0B")
RED_BG      = colors.HexColor("#FFF1F2")
RED_BORDER  = colors.HexColor("#EF4444")
BLUE_BG     = colors.HexColor("#EFF6FF")
BLUE_BORDER = colors.HexColor("#3B82F6")

# ─── Styles ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

style_cover_title = ParagraphStyle("cover_title", fontSize=30, fontName="Helvetica-Bold",
    textColor=LIGHT_TEXT, alignment=TA_CENTER, spaceAfter=12, leading=38)
style_cover_sub = ParagraphStyle("cover_sub", fontSize=14, fontName="Helvetica",
    textColor=colors.HexColor("#C4B5FD"), alignment=TA_CENTER, spaceAfter=6)
style_cover_small = ParagraphStyle("cover_small", fontSize=11, fontName="Helvetica",
    textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER)

style_h1 = ParagraphStyle("h1", fontSize=20, fontName="Helvetica-Bold",
    textColor=PURPLE, spaceAfter=8, spaceBefore=20, borderPad=4)
style_h2 = ParagraphStyle("h2", fontSize=15, fontName="Helvetica-Bold",
    textColor=DARK_BG, spaceAfter=6, spaceBefore=14,
    borderLeftWidth=4, borderLeftColor=PURPLE, borderLeftPadding=8,
    borderPadding=(0,0,0,10))
style_h3 = ParagraphStyle("h3", fontSize=12, fontName="Helvetica-Bold",
    textColor=PURPLE_DARK, spaceAfter=4, spaceBefore=10)
style_body = ParagraphStyle("body", fontSize=10, fontName="Helvetica",
    textColor=BODY_TEXT, alignment=TA_JUSTIFY, spaceAfter=6, leading=16)
style_body_bold = ParagraphStyle("body_bold", fontSize=10, fontName="Helvetica-Bold",
    textColor=BODY_TEXT, spaceAfter=4)
style_code = ParagraphStyle("code", fontSize=9, fontName="Courier",
    textColor=PURPLE_DARK, backColor=PURPLE_LIGHT, borderPad=6,
    spaceAfter=8, leading=14, leftIndent=12, rightIndent=12)
style_note = ParagraphStyle("note", fontSize=9, fontName="Helvetica-Oblique",
    textColor=MUTED, spaceAfter=6, leftIndent=16)
style_label = ParagraphStyle("label", fontSize=9, fontName="Helvetica-Bold",
    textColor=PURPLE)
style_toc = ParagraphStyle("toc", fontSize=10, fontName="Helvetica",
    textColor=BODY_TEXT, spaceAfter=3, leftIndent=12)


def rule():
    return HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10, spaceBefore=4)


def section_title(text):
    return [Paragraph(text, style_h1), rule()]


def sub_title(text):
    return [Spacer(1, 4), Paragraph(text, style_h2)]


def sub_sub_title(text):
    return [Paragraph(text, style_h3)]


def body(text):
    return Paragraph(text, style_body)


def bold(text):
    return Paragraph(text, style_body_bold)


def code_block(text):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), style_code)


def note(text):
    return Paragraph(f"💡 {text}", style_note)


def spacer(h=0.3):
    return Spacer(1, h * cm)


def info_box(text, bg=BLUE_BG, border=BLUE_BORDER, icon="ℹ"):
    data = [[Paragraph(f"<b>{icon}</b>", ParagraphStyle("ic", fontSize=12, textColor=border)),
             Paragraph(text, ParagraphStyle("ib", fontSize=9, textColor=BODY_TEXT, leading=14))]]
    t = Table(data, colWidths=[0.6*cm, 14.4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("BOX", (0,0), (-1,-1), 1, border),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


def make_table(headers, rows, col_widths=None):
    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle("th", fontSize=9, fontName="Helvetica-Bold",
                       textColor=LIGHT_TEXT)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ParagraphStyle("td", fontSize=9, fontName="Helvetica",
                               textColor=BODY_TEXT, leading=13)) for c in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), PURPLE),
        ("BACKGROUND", (0,1), (-1,-1), colors.white),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PURPLE_LIGHT]),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    return t


# ─── Build the Document ───────────────────────────────────────────────────────
story = []

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
    title="SignSpeak — Complete Project Explanation",
    author="SignSpeak Team",
)

def cover_page(canvas, doc):
    canvas.saveState()
    # Dark gradient cover
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # Purple accent bar at top
    canvas.setFillColor(PURPLE)
    canvas.rect(0, A4[1]-8, A4[0], 8, fill=1, stroke=0)
    # Purple accent bar at bottom
    canvas.rect(0, 0, A4[0], 8, fill=1, stroke=0)
    canvas.restoreState()

# ─── COVER PAGE ───────────────────────────────────────────────────────────────
story.append(Spacer(1, 5*cm))
story.append(Paragraph("✋ SignSpeak", style_cover_title))
story.append(Paragraph("Complete Project Explanation", style_cover_sub))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("AI-Powered Sign Language Translation System", style_cover_small))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("From Beginning to End — Every Detail Explained", style_cover_small))
story.append(Spacer(1, 3*cm))

cover_table_data = [
    ["Technology Stack", "React (Vite) · FastAPI · TensorFlow · SQLite · MediaPipe"],
    ["Deployment",       "Vercel (Frontend) · Railway (Backend + AI Model)"],
    ["Repository",       "github.com/ngoh-remy/signspeak2"],
    ["AI Model",         "LSTM Neural Network · 50 Signs · 1,662 features/frame"],
    ["Lifecycle",        "MLLC + SDLC (Merged at Deployment)"],
    ["Methodology",      "Agile Iterative Development"],
]
ct = Table(cover_table_data, colWidths=[5*cm, 10*cm])
ct.setStyle(TableStyle([
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTNAME", (1,0), (1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 10),
    ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#C4B5FD")),
    ("TEXTCOLOR", (1,0), (1,-1), colors.HexColor("#E2E8F0")),
    ("LINEBELOW", (0,0), (-1,-2), 0.5, colors.HexColor("#334155")),
    ("LEFTPADDING", (0,0), (-1,-1), 0),
    ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
]))
story.append(ct)
story.append(PageBreak())

# ─── SECTION 1: What Is SignSpeak ─────────────────────────────────────────────
story.extend(section_title("1. What Is SignSpeak?"))
story.append(body(
    "SignSpeak is a full-stack, AI-powered web application that translates sign language gestures "
    "into text and spoken audio in real time using only a standard webcam. Think of it like Google "
    "Translate, but instead of typing words, you perform hand signs in front of your camera. The "
    "application watches your movements, recognizes the sign, and instantly writes the word on screen "
    "and reads it out loud."
))
story.append(spacer())
story.append(body(
    "It is a complete, production-ready product — not just a script or demo. It includes a live website "
    "hosted on the cloud, a secure user account system, a sign dictionary, a sentence builder that "
    "accumulates multiple signs, bilingual support (English and French), dark and light mode, and "
    "persistent translation history saved to a database."
))
story.append(spacer())
story.append(info_box(
    "Live at: https://signspeak2.vercel.app · Backend: https://signspeak2-production.up.railway.app",
    bg=PURPLE_LIGHT, border=PURPLE, icon="🌐"
))
story.append(spacer())

# ─── SECTION 2: The Problem ───────────────────────────────────────────────────
story.extend(section_title("2. The Problem We Are Solving"))
story.append(body(
    "People who are deaf or hard of hearing communicate primarily through sign language. However, "
    "the vast majority of the general population does not understand sign language, creating a "
    "daily communication barrier. Existing solutions — such as human interpreters — are expensive, "
    "not always available, and cannot scale to millions of people."
))
story.append(spacer())
story.append(body(
    "SignSpeak proposes a technological bridge: an AI that can watch a person signing and "
    "automatically convert those gestures into words that anyone can read or hear, accessible "
    "from any modern web browser with a camera."
))
story.append(spacer())

# ─── SECTION 3: Lifecycles ────────────────────────────────────────────────────
story.extend(section_title("3. The Lifecycles We Followed"))
story.append(body(
    "Because SignSpeak is both an AI system AND a web application, we could not follow a single "
    "lifecycle. We merged two independent lifecycles that ran in parallel and joined together at "
    "the deployment stage."
))
story.append(spacer())

story.extend(sub_title("3.1 The Machine Learning Lifecycle (MLLC)"))
story.append(body("This lifecycle governs the AI brain of the application:"))
story.append(spacer(0.2))
lifecycle_data = [
    ["Phase", "What We Did"],
    ["1. Problem Definition", "Define the goal: translate ASL gestures to text in real time."],
    ["2. Data Acquisition", "Record MP4 videos for 50 signs (4 videos per sign)."],
    ["3. Data Preprocessing", "Run MediaPipe on every video to extract 1,662 coordinates per frame."],
    ["4. Model Training", "Train an LSTM neural network on the preprocessed keypoint data."],
    ["5. Model Evaluation", "Measure accuracy and loss, generate training graphs."],
    ["6. Deployment", "Push model.h5 to the Railway cloud server."],
    ["7. Monitoring", "Tune the confidence threshold in real-world testing."],
]
story.append(make_table(lifecycle_data[0], lifecycle_data[1:], col_widths=[5*cm, 10*cm]))
story.append(spacer())

story.extend(sub_title("3.2 The Software Development Lifecycle (SDLC)"))
story.append(body("This lifecycle governs the website infrastructure:"))
story.append(spacer(0.2))
sdlc_data = [
    ["Phase", "What We Did"],
    ["1. Planning", "Define features: auth, translate, dictionary, history, bilingual UI."],
    ["2. System Design", "Design database schema, API endpoints, UI pages, and routing."],
    ["3. Implementation", "Write React frontend, FastAPI backend, and SQLite database code."],
    ["4. Testing", "Write unit, integration, and end-to-end tests."],
    ["5. Deployment", "Deploy frontend to Vercel, backend to Railway via Docker."],
    ["6. Maintenance", "Fix bugs, add dark/light mode, polish mobile responsiveness."],
]
story.append(make_table(sdlc_data[0], sdlc_data[1:], col_widths=[5*cm, 10*cm]))
story.append(spacer())
story.append(info_box(
    "The Merge Point: When we embedded model.h5 from the MLLC into the FastAPI backend "
    "of the SDLC via inference.py, the two lifecycles became one unified system.",
    bg=YELLOW_BG, border=YELLOW_BORDER, icon="⚡"
))
story.append(spacer())

# ─── SECTION 4: Methodology ───────────────────────────────────────────────────
story.extend(section_title("4. The Methodology: Agile Iterative Development"))
story.append(body(
    "Our overarching management methodology is Agile. Instead of the old 'Waterfall' approach "
    "(plan everything → build everything → test at the very end), we worked in short, repeated "
    "cycles. Each cycle produced a working, testable, and deployable piece of software."
))
story.append(spacer())
story.append(body(
    "Every push to GitHub represents one completed Agile sprint. The CI/CD (Continuous Integration / "
    "Continuous Deployment) pipelines on Vercel and Railway ensured that every approved change went "
    "live automatically within minutes."
))
story.append(spacer())

# ─── SECTION 5: Project Structure ────────────────────────────────────────────
story.extend(section_title("5. Project Structure Overview"))
struct_data = [
    ["Folder / File", "Role"],
    ["Ai_model/", "The AI brain — data, preprocessing, training, and inference"],
    ["Ai_model/SL/", "Raw MP4 video dataset (organized by sign name)"],
    ["Ai_model/keypoints/", "Preprocessed .npy files (30×1,662 arrays per video)"],
    ["Ai_model/preprocess.py", "Converts raw videos into numerical keypoint arrays"],
    ["Ai_model/train.py", "Builds and trains the LSTM neural network"],
    ["Ai_model/inference.py", "Real-time prediction engine used by the backend"],
    ["Ai_model/model.h5", "The trained AI brain file (6.7 MB)"],
    ["Ai_model/labels.json", "Ordered list of 50 sign names the model knows"],
    ["backend/", "The server — handles requests, authentication, and WebSocket"],
    ["backend/main.py", "FastAPI app + the WebSocket real-time recognition endpoint"],
    ["backend/routes.py", "All HTTP REST API endpoints (auth, signs, history)"],
    ["backend/auth.py", "Security: bcrypt password hashing + JWT token management"],
    ["backend/database.py", "SQLite database connection using SQLAlchemy ORM"],
    ["backend/models/models.py", "Database table definitions (Users, TranslationHistory)"],
    ["backend/Dockerfile", "Container recipe for Railway cloud deployment"],
    ["frontend/src/", "The user interface — everything the user sees in the browser"],
    ["frontend/src/App.jsx", "Main app entry point with page routing"],
    ["frontend/src/api.js", "API helper that automatically attaches JWT tokens"],
    ["frontend/src/index.css", "Global design system (colors, fonts, dark/light mode)"],
    ["frontend/src/context/AuthContext.jsx", "Global state (user, theme, language)"],
    ["frontend/src/pages/Translate.jsx", "The core translation engine page (WebSocket)"],
    ["frontend/src/pages/Dictionary.jsx", "Browse all 50 supported signs"],
    ["railway.toml", "Railway deployment configuration"],
]
story.append(make_table(struct_data[0], struct_data[1:], col_widths=[7*cm, 8*cm]))
story.append(PageBreak())

# ─── SECTION 6: The AI Model ──────────────────────────────────────────────────
story.extend(section_title("6. Part 1 — The AI Model"))

story.extend(sub_title("6.1 Phase 1: Data Collection"))
story.append(body(
    "The raw dataset is stored in Ai_model/SL/. Each subdirectory represents one sign (e.g., "
    "SL/hello/, SL/thank you/). Inside each folder are 4 short MP4 video files of a person "
    "performing that sign. The 50 signs cover everyday communication: greetings, emotions, "
    "family members, medical terms, and common verbs."
))
story.append(spacer(0.2))
story.append(info_box(
    "Limitation: Professional AI models require 50–200 videos per sign. With 4 videos per sign, "
    "the model works well for clear, consistent signs but may struggle with variations in lighting, "
    "angle, or speed. This is a dataset size constraint, not a flaw in the system architecture.",
    bg=YELLOW_BG, border=YELLOW_BORDER, icon="⚠"
))
story.append(spacer())

story.extend(sub_title("6.2 Phase 2: Data Preprocessing (preprocess.py)"))
story.append(body(
    "Instead of feeding raw video pixels into the neural network (which would require massive amounts "
    "of data and computation), we use Google's MediaPipe Holistic library to extract a mathematical "
    "'skeleton' from every frame."
))
story.append(spacer(0.2))
story.extend(sub_sub_title("How MediaPipe Works"))
story.append(body(
    "MediaPipe scans each video frame and finds the exact pixel coordinates of body and hand joints. "
    "It outputs X, Y, and Z coordinates for:"
))
mp_data = [
    ["Body Part", "Landmarks", "Values Each", "Total Numbers"],
    ["Body Pose", "33 joints", "4 (x, y, z, visibility)", "132"],
    ["Face", "468 points", "3 (x, y, z)", "1,404 (zeroed out)"],
    ["Left Hand", "21 joints", "3 (x, y, z)", "63"],
    ["Right Hand", "21 joints", "3 (x, y, z)", "63"],
    ["TOTAL PER FRAME", "—", "—", "1,662 numbers"],
]
story.append(make_table(mp_data[0], mp_data[1:], col_widths=[4*cm, 3.5*cm, 4*cm, 3.5*cm]))
story.append(spacer(0.3))
story.append(body(
    "The face landmarks are included but set to zero. This focuses the model exclusively on "
    "hand and arm movements — the parts that actually change between signs."
))
story.append(spacer(0.2))
story.extend(sub_sub_title("Standardizing Video Length"))
story.append(body(
    "Every video must produce exactly 30 frames to be a valid input to the neural network. "
    "If a video is shorter than 30 frames, zero arrays are appended (padding). "
    "If it is longer, 30 frames are evenly sampled across the entire duration."
))
story.append(spacer(0.2))
story.append(body(
    "Output: Each video becomes a .npy (NumPy array) file of shape (30, 1662) — "
    "30 frames, each with 1,662 numerical features. These are saved in the keypoints/ folder."
))
story.append(spacer())

story.extend(sub_title("6.3 Phase 3: Model Building & Training (train.py)"))
story.extend(sub_sub_title("Why LSTM?"))
story.append(body(
    "A sign is a movement over time — not a frozen snapshot. Standard neural networks have no "
    "memory: they treat each input independently. LSTM (Long Short-Term Memory) networks were "
    "specifically invented for sequential data. They maintain internal memory cells that carry "
    "information from earlier frames to later ones."
))
story.append(spacer(0.2))
story.append(body(
    "Example: LSTM sees Frame 1 (hand at rest), Frame 8 (hand moving up), Frame 15 (hand "
    "waving), Frame 30 (hand returning). It combines all this information to conclude: 'hello'."
))
story.append(spacer(0.2))
story.extend(sub_sub_title("Model Architecture"))
arch_data = [
    ["Layer", "Type", "Size", "Purpose"],
    ["1", "LSTM", "64 units", "Learns low-level temporal movements (early frames)"],
    ["2", "BatchNormalization", "—", "Stabilizes and speeds up training"],
    ["3", "Dropout 30%", "—", "Randomly disables neurons to prevent memorization"],
    ["4", "LSTM", "128 units", "Learns higher-level sign patterns across all 30 frames"],
    ["5", "BatchNormalization", "—", "Stabilizes training"],
    ["6", "Dropout 30%", "—", "Further prevents overfitting"],
    ["7", "Dense (ReLU)", "64 units", "Combines learned features into a classification signal"],
    ["8", "Dropout 50%", "—", "Final regularization"],
    ["9", "Dense (Softmax)", "50 units", "Outputs a probability (0–1) for each of the 50 signs"],
]
story.append(make_table(arch_data[0], arch_data[1:], col_widths=[1*cm, 4.5*cm, 2.5*cm, 7*cm]))
story.append(spacer(0.3))
story.extend(sub_sub_title("Training Process"))
story.append(body(
    "The 200 total samples (50 signs × 4 videos) are split: 80% for training, 20% for testing. "
    "The model trains for up to 100 epochs. Three callbacks monitor training automatically:"
))
story.append(spacer(0.2))
cb_data = [
    ["Callback", "Purpose"],
    ["ModelCheckpoint", "Saves the best model whenever validation accuracy improves"],
    ["EarlyStopping (patience=20)", "Stops training if accuracy stalls for 20 epochs in a row"],
    ["ReduceLROnPlateau", "Halves the learning rate when training plateaus"],
]
story.append(make_table(cb_data[0], cb_data[1:], col_widths=[6*cm, 9*cm]))
story.append(spacer(0.3))
story.append(body(
    "Output: The best trained model is saved as model.h5 — a 6.7 MB file containing all learned "
    "weights. Training also generates accuracy.png and loss.png charts in training_results/."
))
story.append(spacer())

story.extend(sub_title("6.4 Phase 4: Real-Time Inference (inference.py)"))
story.append(body(
    "inference.py is the real-time engine. It loads model.h5 once when the server starts and then "
    "processes every camera frame sent through the WebSocket."
))
story.append(spacer(0.2))
story.append(body("Step-by-step flow for each camera frame received:"))
steps = [
    "Decode the JPEG bytes into a pixel array using OpenCV.",
    "Run MediaPipe Holistic on the pixel array to extract 1,662 coordinates.",
    "Add the coordinates to a rolling buffer (deque) of maximum size 30.",
    "If the buffer has fewer than 30 frames, send back a 'processing' message to the frontend.",
    "When the buffer reaches 30 frames, convert it to shape (1, 30, 1662) and run the LSTM model.",
    "The model outputs 50 probability values. Find the highest one.",
    "If the highest probability exceeds 0.05 (5%), return the corresponding sign label.",
    "Clear the buffer so the next sign starts from frame 0.",
]
for i, step in enumerate(steps, 1):
    story.append(body(f"<b>{i}.</b> {step}"))
story.append(spacer())
story.append(info_box(
    "Key settings: SEQUENCE_LENGTH=30 (frames per prediction), "
    "CONFIDENCE_THRESHOLD=0.05 (lowered to ensure output with small dataset), "
    "SIMULATION_MODE=False (always uses the real AI model).",
    bg=BLUE_BG, border=BLUE_BORDER, icon="⚙"
))
story.append(PageBreak())

# ─── SECTION 7: Backend ───────────────────────────────────────────────────────
story.extend(section_title("7. Part 2 — The Backend Server"))
story.append(body(
    "The backend is a Python web server built with FastAPI. It runs 24/7 on Railway's cloud "
    "infrastructure and does three things: serves the AI model's predictions via WebSocket, "
    "manages user accounts via REST API, and stores translation history in a SQLite database."
))
story.append(spacer())

story.extend(sub_title("7.1 The Database"))
story.append(body(
    "SQLite is used for the database — a file-based system that requires no separate server. "
    "SQLAlchemy (an ORM) lets us interact with the database using Python classes instead of "
    "raw SQL queries. Two tables are defined:"
))
story.append(spacer(0.2))
story.extend(sub_sub_title("users table"))
u_data = [
    ["Column", "Type", "Purpose"],
    ["id", "Integer (PK)", "Auto-incrementing unique identifier"],
    ["username", "String (unique)", "The user's display name"],
    ["email", "String (unique)", "Login email address"],
    ["hashed_password", "String", "bcrypt-encrypted password (plain text is never stored)"],
    ["is_active", "Boolean", "Whether the account is enabled"],
    ["created_at", "DateTime", "When the account was created"],
]
story.append(make_table(u_data[0], u_data[1:], col_widths=[3.5*cm, 4*cm, 7.5*cm]))
story.append(spacer(0.3))
story.extend(sub_sub_title("translation_history table"))
h_data = [
    ["Column", "Type", "Purpose"],
    ["id", "Integer (PK)", "Unique record identifier"],
    ["user_id", "Integer (FK)", "Links to the user who performed the sign"],
    ["sign_label", "String", "The recognized sign word (e.g., 'hello')"],
    ["confidence", "Float", "Model confidence score (0.0 to 1.0)"],
    ["session_id", "String (UUID)", "Groups signs from the same camera session"],
    ["created_at", "DateTime", "When the sign was recognized"],
]
story.append(make_table(h_data[0], h_data[1:], col_widths=[3.5*cm, 4*cm, 7.5*cm]))
story.append(spacer())

story.extend(sub_title("7.2 Security & Authentication"))
story.extend(sub_sub_title("Password Hashing (bcrypt)"))
story.append(body(
    "We never store a user's plain-text password. When you register with 'mypassword', bcrypt "
    "transforms it into a scrambled string like '$2b$12$K9d7GjX...'. Even if someone steals "
    "the entire database file, they cannot reverse-engineer the original password from this hash."
))
story.append(spacer(0.2))
story.extend(sub_sub_title("JWT Tokens (JSON Web Tokens)"))
story.append(body(
    "After successful login, the server creates a signed JWT token and sends it to the browser. "
    "The browser stores this token in localStorage and sends it with every API request in the "
    "'Authorization: Bearer <token>' header. The server verifies the cryptographic signature "
    "instantly — without querying the database — making authentication fast and stateless."
))
story.append(spacer())

story.extend(sub_title("7.3 The REST API Endpoints"))
api_data = [
    ["Method", "Endpoint", "Purpose"],
    ["GET", "/api/health", "Check if the server is running"],
    ["POST", "/api/auth/register", "Create a new user account"],
    ["POST", "/api/auth/login", "Log in and receive a JWT token"],
    ["GET", "/api/auth/me", "Get the current logged-in user's info"],
    ["POST", "/api/auth/forgot-password", "Request a password reset link"],
    ["POST", "/api/auth/reset-password", "Complete password reset with token"],
    ["GET", "/api/signs", "Get all 50 supported signs (with search)"],
    ["GET", "/api/history", "Get the user's translation history"],
    ["DELETE", "/api/history", "Clear the user's translation history"],
]
story.append(make_table(api_data[0], api_data[1:], col_widths=[2.5*cm, 5*cm, 7.5*cm]))
story.append(spacer())

story.extend(sub_title("7.4 The WebSocket Real-Time Engine"))
story.append(body(
    "Normal HTTP (request-response) is too slow for real-time video. WebSocket creates a "
    "persistent, two-way connection that stays open — like a phone call instead of letters. "
    "The frontend sends one JPEG frame every 100ms (10 FPS). The server processes each frame "
    "through MediaPipe + LSTM and pushes the result back the instant it's ready."
))
story.append(spacer(0.2))
ws_data = [
    ["Message Type", "Direction", "Content"],
    ["connected", "Server → Browser", "Confirms WebSocket is open and AI model is ready"],
    ["processing", "Server → Browser", "Frame count update: {frames_buffered: N, frames_needed: 30}"],
    ["recognition", "Server → Browser", "Sign result: {sign: 'hello', confidence: 0.15}"],
    ["JPEG bytes", "Browser → Server", "Raw image bytes of the current camera frame"],
]
story.append(make_table(ws_data[0], ws_data[1:], col_widths=[3.5*cm, 4*cm, 7.5*cm]))
story.append(PageBreak())

# ─── SECTION 8: Frontend ─────────────────────────────────────────────────────
story.extend(section_title("8. Part 3 — The Frontend (User Interface)"))

story.extend(sub_title("8.1 Technology Stack"))
tech_data = [
    ["Technology", "Role"],
    ["React (Vite)", "JavaScript UI framework for building interactive components"],
    ["React Router", "Handles navigation between pages without full page reloads"],
    ["Lucide React", "Icon library used throughout the interface"],
    ["Vanilla CSS", "Custom styling — no Bootstrap or Tailwind, full design control"],
    ["Web Speech API", "Browser built-in API for text-to-speech audio output"],
    ["WebSocket API", "Browser built-in API for real-time server communication"],
    ["MediaDevices API", "Browser built-in API for accessing the webcam"],
]
story.append(make_table(tech_data[0], tech_data[1:], col_widths=[5*cm, 10*cm]))
story.append(spacer())

story.extend(sub_title("8.2 Application Routing"))
route_data = [
    ["URL", "Page", "Requires Login?"],
    ["/", "Landing (Home page)", "No"],
    ["/login", "Login form", "No"],
    ["/register", "Registration form", "No"],
    ["/forgot-password", "Password reset request", "No"],
    ["/reset-password", "Password reset form", "No"],
    ["/dictionary", "Browse all 50 signs", "No"],
    ["/translate", "Live AI translation engine", "No (history requires login)"],
]
story.append(make_table(route_data[0], route_data[1:], col_widths=[4*cm, 7*cm, 4*cm]))
story.append(spacer())

story.extend(sub_title("8.3 The AuthContext (Global State Manager)"))
story.append(body(
    "AuthContext uses React's Context API to share data across all components without prop drilling. "
    "It stores the logged-in user object, the current theme (dark/light), and the active language "
    "(en/fr). It also provides login(), logout(), register(), toggleTheme(), and changeLanguage() "
    "functions that any component can call. All preferences are persisted in localStorage so they "
    "survive page refreshes."
))
story.append(spacer())

story.extend(sub_title("8.4 The Translate Page — Core Engine"))
story.append(body(
    "Translate.jsx is the heart of the application (477 lines). It orchestrates everything:"
))
translate_feats = [
    "Requests webcam access using navigator.mediaDevices.getUserMedia()",
    "Draws each video frame onto a hidden HTML <canvas> element every 100ms",
    "Exports the canvas as a JPEG blob and sends it through the WebSocket",
    "Listens for server messages and updates the UI state (OFFLINE / CONNECTING / READY / PROCESSING)",
    "Displays the 'Capturing Gestures: X / 30 frames' progress bar",
    "Accumulates recognized signs into the Sentence Builder",
    "Reads each recognized word aloud using window.speechSynthesis (text-to-speech)",
    "Fetches and displays the user's past translations from the database",
    "Supports switching between front and rear cameras on mobile devices",
]
for feat in translate_feats:
    story.append(body(f"• {feat}"))
story.append(spacer())

story.extend(sub_title("8.5 The Design System (index.css)"))
story.append(body(
    "All colors, fonts, and spacing are defined once as CSS custom properties (variables) in "
    "index.css. Every component uses these variables (e.g., var(--bg-base)) instead of hardcoded "
    "values. This is what makes the dark/light mode toggle work instantly across the entire app:"
))
story.append(spacer(0.2))
story.append(body(
    "When the user clicks the Sun/Moon icon, toggleTheme() sets data-theme='light' on the root "
    "<html> element. This triggers the :root[data-theme='light'] CSS block, which overrides all "
    "background and text color variables. Since every component references these variables, the "
    "entire application re-themes with a single attribute change — no page reload needed."
))
story.append(PageBreak())

# ─── SECTION 9: Integration ──────────────────────────────────────────────────
story.extend(section_title("9. Part 4 — How It All Connects"))
story.append(body(
    "This is the most important section. Let's trace a sign from your webcam to the spoken word:"
))
story.append(spacer(0.2))
flow_data = [
    ["Step", "Component", "What Happens"],
    ["1", "Your Webcam", "Captures a video frame every 100 milliseconds"],
    ["2", "Translate.jsx (React)", "Draws the frame onto a hidden canvas, exports as JPEG blob"],
    ["3", "WebSocket connection", "Raw JPEG bytes are sent to the Railway server over WSS"],
    ["4", "main.py (FastAPI)", "Receives bytes, calls recognizer.process_frame(frame_bytes)"],
    ["5", "inference.py", "Decodes JPEG → runs MediaPipe → extracts 1,662 coordinates"],
    ["6", "inference.py buffer", "Coordinates added to buffer (deque maxlen=30)"],
    ["7", "inference.py model", "When buffer=30: feeds (1,30,1662) array into model.h5 LSTM"],
    ["8", "model.h5 output", "Returns probability array [0.15, 0.03, 0.08, ...] for 50 signs"],
    ["9", "inference.py threshold", "Finds max probability. If >0.05: returns ('hello', 0.15)"],
    ["10", "main.py", "Builds JSON response, saves to database (if user logged in)"],
    ["11", "WebSocket response", "JSON sent back to browser: {type:'recognition', sign:'hello'}"],
    ["12", "Translate.jsx", "Updates UI with the word, appends to Sentence Builder"],
    ["13", "Web Speech API", "Browser reads 'hello' out loud using text-to-speech"],
    ["14", "Buffer cleared", "inference.py resets buffer to 0 — cycle begins again"],
]
story.append(make_table(flow_data[0], flow_data[1:], col_widths=[1.2*cm, 4*cm, 9.8*cm]))
story.append(spacer())
story.append(info_box(
    "Total round-trip time: approximately 3 seconds per sign (30 frames × 100ms per frame). "
    "The WebSocket stays open for the entire session — no reconnection needed between signs.",
    bg=BLUE_BG, border=BLUE_BORDER, icon="⏱"
))
story.append(PageBreak())

# ─── SECTION 10: Deployment ──────────────────────────────────────────────────
story.extend(section_title("10. Part 5 — Deployment"))

story.extend(sub_title("10.1 Frontend → Vercel"))
story.append(body(
    "Vercel is a cloud platform specialized for hosting web applications. Our React code lives "
    "in the frontend/ folder on GitHub. Vercel is connected to our repository. Every time we "
    "push to the main branch, Vercel automatically builds the React app (npm run build) and "
    "deploys the new version globally within 60 seconds. The result is available at "
    "https://signspeak2.vercel.app."
))
story.append(spacer())

story.extend(sub_title("10.2 Backend + AI Model → Railway (Docker)"))
story.append(body(
    "Railway runs server applications. Our Python backend and AI model are deployed using Docker. "
    "A Dockerfile is a recipe that tells Railway exactly how to build the environment:"
))
story.append(spacer(0.2))
docker_steps = [
    "Start with a clean Python 3.11 Linux environment (python:3.11-slim)",
    "Install system dependencies that OpenCV and MediaPipe require (libgl1, libglib2.0-0)",
    "Copy and install all Python packages from backend/requirements.txt",
    "Copy the Ai_model/ folder (including the 6.7 MB model.h5 file)",
    "Copy the backend/ source code",
    "Start the server: uvicorn main:app --host 0.0.0.0 --port $PORT",
]
for i, step in enumerate(docker_steps, 1):
    story.append(body(f"<b>{i}.</b> {step}"))
story.append(spacer(0.2))
story.append(body(
    "railway.toml configures Railway to use the Dockerfile, monitor /api/health for uptime, "
    "and restart automatically on failure. Like Vercel, Railway auto-deploys on every GitHub push."
))
story.append(spacer())

# ─── SECTION 11: Testing ─────────────────────────────────────────────────────
story.extend(section_title("11. Part 6 — Testing"))
test_data = [
    ["Test Level", "Tool", "What It Tests", "Example"],
    ["Unit", "pytest", "Individual functions in isolation",
     "hash_password() returns a bcrypt string; extract_keypoints() returns shape (1662,)"],
    ["Integration", "FastAPI TestClient", "Multiple components working together",
     "POST /api/auth/register returns 200 + JWT; GET /api/history without token returns 401"],
    ["End-to-End", "React Testing Library", "Full user flows in the browser",
     "User fills registration form → clicks Submit → is redirected to /translate"],
]
story.append(make_table(test_data[0], test_data[1:], col_widths=[2.5*cm, 3.5*cm, 4.5*cm, 4.5*cm]))
story.append(spacer())

# ─── SECTION 12: Key Concepts ────────────────────────────────────────────────
story.extend(section_title("12. Key Technical Concepts Explained Simply"))

concepts = [
    ("MediaPipe", "A Google library that detects the exact position of hand joints, body pose, "
     "and face landmarks in a camera frame in milliseconds. We use it to convert video pixels "
     "into clean numerical coordinates, making the AI's job much simpler."),
    ("LSTM Neural Network", "A type of neural network with built-in 'memory'. Unlike standard "
     "networks that treat each input independently, LSTM remembers what happened in previous "
     "frames when processing the current frame — essential for understanding movements over time."),
    ("WebSocket", "A persistent two-way connection between browser and server (like a phone call, "
     "not a letter exchange). Allows the server to push results to the browser the instant they "
     "are ready, enabling real-time streaming."),
    ("JWT Token", "A signed digital certificate issued after login. The browser stores it and "
     "sends it with every request. The server verifies the signature without a database lookup — "
     "fast, secure, and stateless."),
    ("bcrypt", "A one-way password transformation. The original password cannot be recovered "
     "from the hash. Even if the database is stolen, user passwords remain safe."),
    ("Docker", "A way to package an application with all its dependencies into a portable container. "
     "Our Dockerfile ensures the server runs identically on Railway's Linux cloud as on a local machine."),
    ("CORS", "Cross-Origin Resource Sharing — a browser security rule that blocks web pages from "
     "calling APIs on different domains by default. Our backend adds special headers to explicitly "
     "allow the Vercel frontend to make requests to the Railway backend."),
    ("SQLAlchemy ORM", "Object-Relational Mapper — lets us write Python classes instead of raw SQL. "
     "Safer (prevents SQL injection), more readable, and easier to maintain."),
]

for name, explanation in concepts:
    story.extend(sub_sub_title(name))
    story.append(body(explanation))
    story.append(spacer(0.2))

story.append(PageBreak())

# ─── SECTION 13: Accuracy ────────────────────────────────────────────────────
story.extend(section_title("13. Accuracy & Current Limitations"))
acc_data = [
    ["Metric", "Value"],
    ["Number of signs supported", "50"],
    ["Training videos per sign", "4"],
    ["Total training samples", "~200 sequences"],
    ["AI model file size", "6.7 MB"],
    ["Frames per prediction window", "30"],
    ["Real-time latency", "~3 seconds per sign"],
    ["Confidence threshold", "0.05 (5%)"],
    ["Typical output confidence", "15%–30%"],
]
story.append(make_table(acc_data[0], acc_data[1:], col_widths=[8*cm, 7*cm]))
story.append(spacer())
story.append(info_box(
    "The low confidence is a dataset size issue, not an architecture issue. The system "
    "infrastructure (WebSocket pipeline, cloud deployment, user authentication, database) "
    "all work perfectly. Adding 40+ videos per sign would dramatically improve accuracy.",
    bg=YELLOW_BG, border=YELLOW_BORDER, icon="📊"
))
story.append(spacer())

# ─── SECTION 14: Summary ─────────────────────────────────────────────────────
story.extend(section_title("14. Summary for the Jury"))

story.append(body(
    "In one sentence: SignSpeak is a real, deployed, AI-powered web application that translates "
    "sign language into text and speech in real time, built end-to-end from raw video data "
    "collection through neural network training to global cloud deployment."
))
story.append(spacer())

summary_data = [
    ["Aspect", "Our Approach"],
    ["Lifecycles", "Merged MLLC (Machine Learning) + SDLC (Software Development)"],
    ["Methodology", "Agile Iterative Development with CI/CD auto-deployment"],
    ["AI Architecture", "LSTM Neural Network (sequential gesture recognition)"],
    ["Feature Extraction", "Google MediaPipe Holistic (1,662 coordinates per frame)"],
    ["Backend Framework", "FastAPI (Python) with WebSocket real-time streaming"],
    ["Frontend Framework", "React (Vite) with React Router and Vanilla CSS"],
    ["Security", "bcrypt password hashing + JWT authentication tokens"],
    ["Database", "SQLite via SQLAlchemy ORM"],
    ["Deployment", "Vercel (frontend) + Railway/Docker (backend + AI model)"],
    ["Testing", "Unit + Integration + End-to-End test suites"],
    ["Extras", "Dark/Light mode, Bilingual (EN/FR), Mobile responsive, Text-to-speech"],
]
story.append(make_table(summary_data[0], summary_data[1:], col_widths=[5*cm, 10*cm]))
story.append(spacer())

story.append(info_box(
    "What makes this project stand out: (1) It is not a simulation — the AI is real and live. "
    "(2) Anyone can use it right now at signspeak2.vercel.app. "
    "(3) It follows professional-grade engineering practices end-to-end. "
    "(4) It demonstrates a complete, production-ready MLOps pipeline.",
    bg=PURPLE_LIGHT, border=PURPLE, icon="⭐"
))

# Build the PDF
doc.build(story, onFirstPage=cover_page, onLaterPages=lambda c,d: None)
print(f"\nPDF generated successfully!\nLocation: {OUTPUT}\n")
