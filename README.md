# 2D Shape Side Matching

A web application to find the best-fitting match for a 2D shape from a database of other shapes using computer vision and a weighted Levenshtein algorithm.

---

## Tech Stack

- **Frontend**: Next.js (React), TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, OpenCV
- **Database**: PostgreSQL with pgvector extension
- **Containerization**: Docker

---

## How to Run Locally

### 1. Start the Database

Ensure Docker Desktop is running, then start the PostgreSQL container.

```bash
docker-compose up -d
```

### 2. Set Up and Run the Backend

Navigate to the `backend` directory in a terminal.

```bash
# Create and activate the virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with initial images
python -m app.scripts.seed_db

# Run the server
uvicorn app.main:app --reload
```

The backend will be running on `http://localhost:8000`.

### 3. Set Up and Run the Frontend

Navigate to the `frontend` directory in a separate terminal.

```bash
npm install

npm run dev
```

The frontend will be accessible at `http://localhost:3000`.

---

### Author

- **Name**: Lutfi Hakim Yusra
- **NIM**: 13523084
