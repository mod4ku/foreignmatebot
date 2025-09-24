<h1 align="center">🎓Bot for searching study buddy</h1>

<p align="center">
   <img src="https://img.shields.io/badge/python-_3.13-red" alt="Версия Python">
</p>

## 📖About the Project

A Telegram bot designed to help people find friends who are going to study abroad. The bot facilitates connections between users by offering profile creation and matching features.

## 💡Features

*   Profile Creation & Editing: Users can create and edit their profiles (exams, countries, descriptions).
*   Profile Search: Ability to search and view other users' profiles.
*   Likes: Users can express interest in other profiles.
*   Data Validation: Validates user-input data (name, age, country, exam scores, etc.) to ensure correctness and security.
*   Logging: Logs all critical bot actions for easier debugging and monitoring.

## 💻Technology Stack

Asynchronous Frameworks & HTTP Clients
* Aiogram (3.21.0): Asynchronous framework for building Telegram bots with FSM (Finite State Machine) support.
* Aiohttp (3.12.14): Asynchronous HTTP client/server for API interactions and web requests.
* Aiohappyeyeballs (2.6.1): Optimizes connections for IPv6/IPv4 compatibility.

Database Management
* SQLAlchemy (2.0.41): ORM for interacting with relational databases (supports async via asyncpg/aiomysql).
* Asyncpg (0.30.0): Asynchronous driver for PostgreSQL.
* Aiomysql (0.2.0): Asynchronous client for MySQL/MariaDB.
* Redis (6.2.0): Storage for caching and temporary data (sessions, task queues).

Data Validation & Configuration
* Pydantic (2.11.7): Data validation and serialization/deserialization.
* Pydantic-settings (2.10.1): Manages app configuration via environment variables.
* Python-dotenv (1.1.1): Loads environment variables from .env files.

Helper Libraries
* Aiofiles (24.1.0): Asynchronous file operations.
* Geonamescache (2.0.0): Geographic data (countries, cities) for localization.
* Magic-filter (1.0.12): Simplified filtering syntax for Aiogram.
* Propcache (0.3.2): Property caching for objects.

Networking Utilities
* Multidict (6.6.3), Yarl (1.20.1): URL and HTTP header handling.
* Hiredis (3.2.1): High-performance Redis parser.
  
System Dependencies
* Greenlet (3.2.3):  Lightweight coroutines for async operations.
* Certifi (2025.7.9): SSL certificates for secure connections.


## 📥Installation

1.  Clone the repository:
    ``git clone https://github.com/mod4ku/foreignmatebote.git``
    
2.  Install requirements:
    ``pip install -r requirements.txt``
    
3.  Create a .env file in the project root and add the required environment variables:
   ```
    BOT_TOKEN=your_bot_token
    ADMIN_IDS=your_id
    BOT_NAME=bot_name
    IMGUR_BASE_URL=https://i.imgur.com/tBlNjDE.png
    DEFAULT_PROFILE_IMAGE=data/default-img.png
   ```
## 🚀Launch
```
python main.py
```
## ⛓️Link
*   [ForeignMatebot](https://t.me/foreignmatebot)

## 🛠Developer

*   [mod4ku](https://github.com/mod4ku)
