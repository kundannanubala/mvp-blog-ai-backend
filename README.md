# mvp-blog-ai-backend

Backend of Blog AI, consisting of services to handle RSS feeds management, user management, personalized blog generation, and pipelines facilitating communication among mentioned services.

## Frontend
https://github.com/Sachinbadi/Blogai-frontend/tree/kundannanubala

## Features

- RSS feed management
- User management
- Personalized blog generation
- Keyword extraction using AI models
- Image generation using Vertex AI

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB
- Google Cloud account with Vertex AI enabled
- AstraDB account

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/mvp-blog-ai-backend.git
   cd mvp-blog-ai-backend   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt   ```

   Reference:   ```plaintext:requirements.txt
   startLine: 1
   endLine: 57   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory and add the necessary environment variables. Refer to `core/config.py` for the required variables.

   Reference:   ```python:core/config.py
   startLine: 6
   endLine: 20   ```

### Running the Application

1. **Start the FastAPI server:**
   ```bash
   uvicorn app:app --reload   ```

   Reference:   ```python:app.py
   startLine: 58
   endLine: 60   ```

2. **Access the API:**

   Open your browser and go to `http://localhost:8000/docs` to access the Swagger UI for API documentation.

### Additional Setup

- **MongoDB:**

  Ensure MongoDB is running and accessible. Update the `MONGODB_URI` and `MONGODB_NAME` in your `.env` file.

- **Google Cloud:**

  Set up your Google Cloud credentials and ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is correctly set.

- **AstraDB:**

  Configure your AstraDB settings in the `.env` file.

## Usage

- **Generate Blog Posts:**

  Use the `/generate-blog` endpoint to create blog posts from specified articles.

  Reference:  ```python:api/blog.py
  startLine: 11
  endLine: 41  ```

- **Manage RSS Feeds:**

  Use the `/xml` endpoints to manage and fetch RSS feeds.

  Reference:  ```python:api/xml.py
  startLine: 16
  endLine: 52  ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
