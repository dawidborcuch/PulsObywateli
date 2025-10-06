# PulsObywateli

Obywatelska platforma sondażowo-informacyjna do śledzenia i oceniania projektów ustaw w Polsce oraz głosowania w sondażach dotyczących polityków i tematów społecznych.

## 🎯 Cel projektu

Budowanie świadomości obywatelskiej poprzez ułatwienie dostępu do informacji o pracach Sejmu oraz pokazywanie rzeczywistych nastrojów społecznych.

## 🛠 Technologie

- **Backend**: Python + Django REST Framework
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Baza danych**: PostgreSQL
- **API**: Integracja z API Sejmu RP
- **Hosting**: Docker + VPS

## 🚀 Szybki start

### Wymagania
- Docker i Docker Compose
- Node.js 18+ (dla rozwoju frontend)
- Python 3.9+ (dla rozwoju backend)

### Uruchomienie

```bash
# Klonowanie repozytorium
git clone <repo-url>
cd PulsObywateli

# Uruchomienie z Docker
docker-compose up --build

# Lub rozwój lokalny
# Backend
cd backend
pip install -r requirements.txt
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

## 📁 Struktura projektu

```
PulsObywateli/
├── backend/                 # Django REST API
│   ├── apps/
│   │   ├── accounts/       # Zarządzanie użytkownikami
│   │   ├── bills/          # Projekty ustaw
│   │   ├── polls/          # Sondaże
│   │   └── comments/       # System komentarzy
│   ├── config/             # Konfiguracja Django
│   └── requirements.txt
├── frontend/               # Next.js aplikacja
│   ├── components/         # Komponenty React
│   ├── pages/             # Strony aplikacji
│   ├── styles/            # Style CSS
│   └── package.json
├── docker-compose.yml      # Konfiguracja Docker
└── README.md
```

## 🧩 Funkcjonalności MVP

- ✅ Automatyczne pobieranie projektów ustaw z API Sejmu RP
- ✅ System głosowania na projekty ustaw
- ✅ Sondaże polityczne z wykresami
- ✅ System kont użytkowników
- ✅ Ranking poparcia
- ✅ System komentarzy
- ✅ Panel administratora

## 📊 API Endpoints

### Projekty ustaw
- `GET /api/bills/` - Lista projektów ustaw
- `GET /api/bills/{id}/` - Szczegóły projektu
- `POST /api/bills/{id}/vote/` - Głosowanie

### Sondaże
- `GET /api/polls/` - Lista sondaży
- `POST /api/polls/{id}/vote/` - Głosowanie w sondażu

### Użytkownicy
- `POST /api/auth/register/` - Rejestracja
- `POST /api/auth/login/` - Logowanie
- `GET /api/users/profile/` - Profil użytkownika

## 🔧 Rozwój

### Backend
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm run dev
```

## 📝 Licencja

MIT License

