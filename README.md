# 🤖 MAVERIK AI

<p align="center">
  
</p>

<p align="center">
  <strong>Your AI Operating System for Windows.</strong>
</p>

<p align="center">
  An intelligent desktop assistant that understands natural language, executes real computer tasks, manages files, launches applications, controls windows, and helps you work faster using AI.
</p>

---

## 🚀 Overview

Maverik AI is a next-generation desktop AI assistant built for Windows 11.

Unlike traditional AI chatbots, Maverik doesn't just answer questions—it performs real actions on your computer.

Simply type or speak a command, and Maverik understands your intent using **Google Gemini 2.5**, then executes the requested task through a secure backend.

Examples:

- Open Chrome
- Launch VS Code
- Create a folder called AI Projects
- Search YouTube for React tutorials
- Read my notes.txt
- Send an email with my resume
- Take a screenshot
- Show CPU usage

Maverik bridges conversational AI with desktop automation.

---

# ✨ Features

## 💬 AI Assistant

- Natural language conversations
- Gemini 2.5 reasoning
- Coding assistance
- Explanations
- Writing assistance
- AI-powered responses

---

## 🎙 Voice Assistant

- Voice commands
- Push-to-talk
- Speech recognition
- Text-to-speech
- Voice feedback
- Voice status indicators

---

## 🌐 Website Launcher

Open websites instantly.

Supported examples:

- Google
- YouTube
- GitHub
- LinkedIn
- Gmail
- ChatGPT
- Claude
- Perplexity
- Reddit
- Spotify
- Amazon
- Netflix
- WhatsApp Web
- Discord
- Canva
- Figma
- Google Drive
- Google Docs
- Google Sheets
- Google Slides

Supports search commands like:

- Search Google for FastAPI
- Search YouTube for Python
- Search GitHub for React Projects

---

## 🖥 Application Launcher

Launch installed applications using natural language.

Examples:

- Microsoft Word
- Microsoft Excel
- Microsoft PowerPoint
- Google Chrome
- Microsoft Edge
- Visual Studio Code
- Codex
- Trae
- Microsoft Copilot
- Microsoft Store
- Lenovo Vantage
- Photos
- Paint
- Calculator
- Settings
- Notepad
- File Explorer
- Task Manager
- Control Panel
- PC Manager
- Smart Connect

---

## 📂 Folder Management

- Open folders
- Create folders
- Rename folders
- Delete folders
- Move folders
- Copy folders
- Search folders

---

## 📄 File Management

- Create files
- Open files
- Read files
- Write files
- Append text
- Rename files
- Delete files
- Move files
- Copy files
- Search files

---

## 🔍 Search Everything

Search your entire computer using natural language.

Examples:

- Find my resume
- Find DBMS notes
- Find all PDF files
- Find Python files
- Find PowerPoint presentations
- Find images
- Find videos
- Find React projects

Supports searching across all available drives.

---

## 📝 Notepad Automation

- Open Notepad
- Write text
- Append text
- Save notes
- Read saved notes

---

## 📧 Email Assistant

- Draft emails
- AI-generated emails
- Send emails
- Attach files
- Preview before sending

---

## 🪟 Window Management

- Minimize windows
- Maximize windows
- Restore windows
- Close applications
- Switch windows
- Arrange windows
- Tile windows
- Cascade windows
- Side-by-side layouts

---

## 📊 Live System Dashboard

Real-time monitoring:

- CPU Usage
- RAM Usage
- Disk Usage
- Battery
- Network Status
- Current Time
- Current Date
- System Uptime

---

## 📋 Clipboard Manager

- View clipboard
- Copy text
- Save clipboard
- Clear clipboard

---

## 📥 Downloads Manager

- Open Downloads
- View recent downloads
- Organize downloads
- Remove unwanted installers

---

## ⭐ Favorites

Save frequently used:

- Websites
- Applications
- Files
- Folders

---

## 📜 Command History

Stores:

- Previous commands
- Execution time
- Results
- Task history

---

## ⚙ Settings

- Gemini API Configuration
- Voice Settings
- Permissions
- Theme
- History
- System Information

---

# 🛠 Technology Stack

## Frontend

- React
- TypeScript
- Tailwind CSS
- Framer Motion
- Lucide Icons

## Backend

- Python
- FastAPI
- Uvicorn

## Database

- SQLite

## AI

- Google Gemini 2.5 Flash

## Voice

- Web Speech API
- Gemini Text-to-Speech

---

# 🏗 Architecture

```
User
      │
      ▼
 React Frontend
      │
      ▼
 FastAPI Backend
      │
      ▼
 Gemini 2.5
(Intent Detection)
      │
      ▼
 Command Router
      │
      ▼
 Tool Registry
      │
      ▼
 Windows Automation
      │
      ▼
 Execution Result
      │
      ▼
 User Interface
```

---

# 📁 Project Structure

```
maverik-ai/

├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── api/
│   ├── tools/
│   ├── services/
│   ├── models/
│   ├── database/
│   ├── utils/
│   └── main.py
│
├── assets/
│
├── docs/
│
├── tests/
│
├── .env.example
├── requirements.txt
├── README.md
└── LICENSE
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/maverik-ai.git
```

Navigate into the project

```bash
cd maverik-ai
```

Install backend dependencies

```bash
pip install -r requirements.txt
```

Install frontend dependencies

```bash
npm install
```

Create environment variables

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Start backend

```bash
uvicorn main:app --reload
```

Start frontend

```bash
npm run dev
```

---

# 💡 Example Commands

```
Open Chrome

Open VS Code

Create folder AI Projects

Create file app.py

Read notes.txt

Search Google for FastAPI

Search YouTube for React

Find my resume

Take screenshot

Show CPU usage

Open Downloads

Open Word

Start a 25 minute timer

Send an email to professor@example.com

Open Chrome and VS Code side by side
```

---

# 🔒 Security

- Local-first architecture
- API keys stored securely
- No hardcoded credentials
- Confirmation before destructive actions
- Permission-aware execution
- Safe command routing

---

# 🎯 Roadmap

### Version 1.0

- AI Chat
- Voice Assistant
- File Management
- Folder Management
- Website Launcher
- Application Launcher
- Search Everything
- Window Management
- Email Assistant
- System Dashboard

### Version 1.1

- OCR
- PDF Understanding
- Clipboard Intelligence
- Browser Automation
- Workflow Automation

### Version 2.0

- Persistent Memory
- Multi-Agent Support
- Local LLM Support
- Plugin System
- AI Workflows
- Autonomous Task Execution

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you find Maverik AI useful, consider giving the repository a ⭐ on GitHub.

It helps the project grow and motivates future development.

---

<p align="center">
Built with ❤️ using React, FastAPI, Python, and Google Gemini.
</p>
