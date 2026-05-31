# SignSpeak - Complete Project Documentation

Welcome to the SignSpeak documentation! This guide explains how the entire project works, broken down into simple, easy-to-understand concepts.

---

## 1. What is SignSpeak?
SignSpeak is a real-time sign language translation web application. It uses a computer's webcam to look at a user's hand gestures, uses Artificial Intelligence (AI) to figure out what sign they are making, and translates it into text on the screen. It also includes user accounts so people can save their translation history.

---

## 2. The Three Main Pieces
The project is divided into three separate but connected parts:
1. **The Frontend** (The website you see and interact with)
2. **The Backend** (The hidden server that manages data and accounts)
3. **The AI Model** (The brain that understands sign language)

---

## 3. The Frontend (User Interface)
**Technology Used:** React, Vite, JavaScript, CSS.
**Where it is hosted:** Vercel (`https://signspeak2.vercel.app`)

The frontend is the visual part of the application. 
- It contains the landing page, the login/register forms, and the actual translation camera interface.
- We used **React** to build reusable pieces (components) like buttons and forms.
- It accesses your webcam using the browser's built-in tools.
- When you log in or register, the Frontend sends a message to the Backend asking for permission.

---

## 4. The Backend (Server & Database)
**Technology Used:** Python, FastAPI, SQLite, SQLAlchemy.
**Where it is hosted:** Railway (`https://signspeak2-production.up.railway.app`)

The backend is like the central nervous system of the app. It runs continuously on a server waiting for requests from the frontend.
- **Database (SQLite):** It stores all user accounts securely (passwords are scrambled using a tool called `bcrypt` so even we can't read them) and saves translation histories.
- **REST API:** It provides endpoints (like `/api/auth/register`) that the frontend talks to when a user clicks a button.
- **WebSockets:** For real-time video translation, standard HTTP requests are too slow. We use WebSockets, which creates a continuous, lightning-fast two-way connection between the frontend and backend.

---

## 5. The AI Model (The Brain)
**Technology Used:** MediaPipe, TensorFlow, Keras.

The AI doesn't actually look at the raw video. That would be too slow. Instead, it works in two steps:
1. **MediaPipe (Hand Tracking):** Google's MediaPipe library scans the video frame and finds exactly 21 "landmarks" (joints and fingertips) on the human hand. It outputs the X, Y, and Z coordinates of these points.
2. **TensorFlow (Neural Network):** We take those 21 coordinates and feed them into our custom-trained Neural Network. The network has been trained on hundreds of examples of different signs. It looks at the coordinates, calculates the angles and distances, and guesses which word the sign represents (e.g., "Hello", "Thank You"). It also gives a "confidence" score (e.g., "I am 95% sure this is Hello"). Our current model achieves a high accuracy rate (typically ~95% or higher on the signs it has been trained on) by leveraging MediaPipe's precise spatial tracking combined with a deep learning classifier.

---

## 6. How Deployment Works (The Vercel & Railway Connection)
Getting the frontend and backend to talk to each other across the internet was the most complex part of the setup.

- **Vercel** hosts the Frontend files and delivers them to the user's browser.
- **Railway** hosts the Backend Python server inside a "Docker Container" (a mini virtual computer).
- **The CORS Problem:** Browsers have a security feature called CORS (Cross-Origin Resource Sharing) that blocks a website on one domain (Vercel) from talking to a server on a different domain (Railway) to prevent hackers. 
- **The Solution:** We wrote a custom piece of code on the Railway backend (called a CORS Middleware) that explicitly tells the browser: *"It is completely safe to accept data from the Vercel app."* 
- **Environment Variables:** The frontend needs to know where the backend lives. We stored the Railway URL in a secret variable called `VITE_API_URL` inside Vercel's dashboard. This allows the code to connect without hardcoding the URL into the public source code.

---

## 7. Things We Had to Download / Dependencies
To make all of this work, we relied on several open-source libraries:

**For the Backend (Python):**
- `fastapi` & `uvicorn`: To run the web server.
- `sqlalchemy`: To talk to the SQLite database without writing raw SQL code.
- `passlib` & `bcrypt`: To securely scramble and check passwords.
- `python-jose`: To generate secure "Tokens" (digital ID cards) when users log in.
- `mediapipe` & `tensorflow`: To run the AI model.
- `opencv-python`: To handle image and video data.

**For the Frontend (Node.js/React):**
- `react` & `react-dom`: The core framework for building the website.
- `react-router-dom`: To allow users to click links and change pages without the browser reloading.
- `lucide-react`: The library that provides the beautiful icons (like the Eye icon for passwords).
- `vite`: The tool that bundles all our code together and makes it fast.

---

## 8. Summary of the Data Flow
Here is exactly what happens when a user translates a sign:
1. User opens the app on Vercel.
2. The browser asks for camera permissions and turns on the webcam.
3. The frontend establishes a WebSocket connection to the Railway backend.
4. The browser takes a snapshot of the video and sends it to the backend.
5. The backend gives the image to MediaPipe to find the hand coordinates.
6. The coordinates are passed to TensorFlow, which guesses the word ("Hello").
7. The backend saves this translation into the database under the user's account.
8. The backend sends the word "Hello" back through the WebSocket.
9. The React frontend updates the screen to show "Hello" to the user.
*All of this happens in less than a tenth of a second!*
