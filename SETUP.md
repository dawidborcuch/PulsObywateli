# Instrukcja uruchomienia PulsObywateli

## 🚀 Szybki start z Docker

### Wymagania
- Docker i Docker Compose
- Git

### Kroki uruchomienia

1. **Sklonuj repozytorium**
```bash
git clone <repo-url>
cd PulsObywateli
```

2. **Uruchom aplikację**
```bash
docker-compose up --build
```

3. **Utwórz superużytkownika Django**
```bash
docker-compose exec backend python manage.py createsuperuser
```

4. **Utwórz przykładowe dane (opcjonalnie)**
```bash
docker-compose exec backend python manage.py create_sample_data --users 50 --bills 20 --polls 10
```

5. **Otwórz aplikację**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin panel: http://localhost:8000/admin/

## 🛠 Rozwój lokalny

### Backend (Django)

1. **Przygotuj środowisko**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

2. **Skonfiguruj bazę danych**
```bash
# Utwórz plik .env w katalogu backend/
echo "DEBUG=1" > .env
echo "SECRET_KEY=your-secret-key-here" >> .env
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pulsobywateli" >> .env
```

3. **Uruchom migracje**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Utwórz superużytkownika**
```bash
python manage.py createsuperuser
```

5. **Uruchom serwer**
```bash
python manage.py runserver
```

### Frontend (Next.js)

1. **Zainstaluj zależności**
```bash
cd frontend
npm install
```

2. **Uruchom serwer deweloperski**
```bash
npm run dev
```

## 📊 Zarządzanie danymi

### Pobieranie projektów ustaw (podejście hybrydowe)

**ZALECANE: Hybrydowy scraper (API Sejmu + Gov.pl)**

```bash
# Pobierz projekty z API Sejmu i gov.pl (najlepsze dane)
docker-compose exec backend python manage.py fetch_hybrid_bills --limit 100

# Pobierz projekty z konkretnej kadencji i roku
docker-compose exec backend python manage.py fetch_hybrid_bills --term 10 --year 2025 --limit 50

# Wymuś aktualizację istniejących projektów
docker-compose exec backend python manage.py fetch_hybrid_bills --force --limit 100
```

**Alternatywnie: API Sejmu (tylko dane strukturalne)**

```bash
# Pobierz projekty ustaw z API Sejmu (kadencja 10)
docker-compose exec backend python manage.py fetch_sejm_api_bills --term 10 --limit 100

# Pobierz z konkretnej kadencji
docker-compose exec backend python manage.py fetch_sejm_api_bills --term 9 --limit 50
```

**Alternatywnie: Gov.pl (tylko dane gov.pl)**

```bash
# Pobierz najnowsze projekty ustaw z gov.pl
docker-compose exec backend python manage.py fetch_sejm_bills --limit 100

# Pobierz projekty z konkretnego roku
docker-compose exec backend python manage.py fetch_gov_pl_bills --year 2025 --limit 50
```

### Tworzenie przykładowych danych

```bash
# Utwórz podstawowe dane testowe
docker-compose exec backend python manage.py create_sample_data

# Utwórz więcej danych
docker-compose exec backend python manage.py create_sample_data --users 100 --bills 50 --polls 20
```

## 🔧 Konfiguracja

### Zmienne środowiskowe

Utwórz plik `.env` w katalogu `backend/`:

```env
DEBUG=1
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@db:5432/pulsobywateli
REDIS_URL=redis://localhost:6379/0
```

### Konfiguracja bazy danych

Aplikacja używa PostgreSQL. W środowisku produkcyjnym skonfiguruj odpowiednie połączenie z bazą danych.

## 📱 API Endpoints

### Autentykacja
- `POST /api/auth/register/` - Rejestracja
- `POST /api/auth/login/` - Logowanie
- `POST /api/auth/logout/` - Wylogowanie
- `GET /api/auth/profile/` - Profil użytkownika

### Projekty ustaw
- `GET /api/bills/` - Lista projektów ustaw
- `GET /api/bills/{id}/` - Szczegóły projektu
- `POST /api/bills/{id}/vote/` - Głosowanie
- `GET /api/bills/stats/` - Statystyki

### Sondaże
- `GET /api/polls/` - Lista sondaży
- `GET /api/polls/{id}/` - Szczegóły sondażu
- `POST /api/polls/{id}/vote/` - Głosowanie w sondażu
- `GET /api/polls/stats/` - Statystyki sondaży

### Komentarze
- `GET /api/comments/bills/{bill_id}/` - Komentarze do projektu
- `POST /api/comments/bills/{bill_id}/` - Dodaj komentarz
- `GET /api/comments/{id}/` - Szczegóły komentarza

## 🐳 Docker

### Budowanie obrazów
```bash
docker-compose build
```

### Restart serwisów
```bash
docker-compose restart
```

### Logi
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Czyszczenie
```bash
docker-compose down -v
docker system prune -a
```

## 🧪 Testy

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend
npm test
```

## 📈 Monitoring

### Logi aplikacji
```bash
docker-compose logs -f
```

### Baza danych
```bash
docker-compose exec db psql -U postgres -d pulsobywateli
```

## 🚀 Wdrożenie produkcyjne

1. **Skonfiguruj zmienne środowiskowe produkcyjne**
2. **Ustaw DEBUG=False**
3. **Skonfiguruj domenę i SSL**
4. **Skonfiguruj backup bazy danych**
5. **Ustaw monitoring i logi**

## 🆘 Rozwiązywanie problemów

### Problem z połączeniem do bazy danych
```bash
docker-compose exec db psql -U postgres -c "SELECT 1;"
```

### Problem z migracjami
```bash
docker-compose exec backend python manage.py migrate --fake-initial
```

### Problem z cache
```bash
docker-compose exec backend python manage.py clear_cache
```

### Reset bazy danych
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

