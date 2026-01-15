# Culina

A Django web application for culinary management.

## Installation

### Prerequisites
- Python 3.8+
- pip
- Docker and Docker Compose

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd culina
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Docker Development

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Run migrations (in a new terminal):
```bash
docker-compose exec web python manage.py migrate
```

3. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

To stop the containers:
```bash
docker-compose down
```
