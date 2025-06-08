# Calmindra – Phase One (In Progress)

This repository documents my ongoing development of **Calmindra**, an AI-powered mental health chatbot designed to detect emotional states and respond with supportive, empathetic dialogue.

## ✅ Work Completed So Far

- Set up **FastAPI** backend with `/chat/` endpoint
- Integrated Hugging Face Inference APIs:
  - Emotion classifier (automatically detects emotion from user input)
  - Response generator using `mistralai/Mistral-7B-Instruct-v0.1`
- Designed prompt format based on emotion-aware response
- Successfully tested real-time emotion detection and chat response locally
- Secured API keys via `.env` configuration

## 🛠️ Current Phase

This is **Phase One** of the project, focused entirely on backend and inference logic.

## 🚀 What's Next

- Fine-tune a dialogue model on empathetic conversations for better domain alignment
- Build a full **React-based frontend** for real-time chat UI
- Add journaling, feedback scoring, and long-term sentiment tracking
- Prepare the system for deployment on Hugging Face Spaces or a cloud backend

