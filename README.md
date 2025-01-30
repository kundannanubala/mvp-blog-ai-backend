# mvp-blog-ai-backend

Backend of Blog AI, consisting of services to handle RSS feeds management, user management, personalized blog generation, and pipelines facilitating communication among mentioned services.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This project is the backend for a Blog AI application. It manages RSS feeds, user data, and generates personalized blog content. The backend is built using FastAPI and includes various services for handling different aspects of the application.

## Features

- **RSS Feeds Management**: Parse and consolidate RSS feeds.
- **User Management**: Handle user data and preferences.
- **Blog Generation**: Generate personalized blog content.
- **Task Scheduling**: Schedule tasks using APScheduler.
- **Database Integration**: Use MongoDB for data storage.

## Tech Stack

- **FastAPI**: Web framework for building APIs.
- **MongoDB**: NoSQL database for storing data.
- **APScheduler**: Library for scheduling tasks.
- **Motor**: Async MongoDB driver.
- **Feedparser**: Library for parsing RSS feeds.
- **Pydantic**: Data validation and settings management.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mvp-blog-ai-backend.git
   cd mvp-blog-ai-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Environment Variables**:
   Create a `.env` file in the root directory and add the following variables:
   ```
   MONGODB_URI=your_mongodb_uri
   MONGODB_NAME=your_database_name
   ```

## Running the Project

1. **Start the FastAPI server**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

2. **Access the API**:
   Open your browser and go to `http://localhost:8000/docs` to view the interactive API documentation.

## API Endpoints

- **GET /xml/**: Fetch consolidated XML feeds.
- **POST /xml/add-urls**: Add new XML URLs to the database.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
