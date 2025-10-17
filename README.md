# PulsObywateli

Platforma do śledzenia i oceniania projektów ustaw w Polsce.

## Konfiguracja

### 1. Klonowanie repozytorium
```bash
git clone <repository-url>
cd PulsObywateli
```

### 2. Konfiguracja zmiennych środowiskowych

Utwórz plik `.env` w głównym katalogu projektu:

```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

**UWAGA**: Plik `.env` jest już dodany do `.gitignore` i nie będzie commitowany do repozytorium.

### 3. Uruchomienie aplikacji

```bash
docker compose up -d
```

Aplikacja będzie dostępna pod adresami:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Nginx: http://localhost:80

### 4. Zatrzymanie aplikacji

```bash
docker compose down
```

## Funkcje

- **Projekty ustaw**: Przeglądanie i głosowanie na projekty ustaw
- **Analiza AI**: Automatyczna analiza projektów ustaw przez AI
- **Głosowania kworum**: Obsługa specjalnych głosowań kworum w Sejmie
- **Wyniki głosowań**: Szczegółowe wyniki głosowań posłów
- **Sondaże**: Ankiety społeczne
- **Ranking**: Statystyki wsparcia projektów

## Struktura projektu

```
├── backend/          # Django REST API
├── frontend/         # Next.js aplikacja
├── docker-compose.yml # Konfiguracja Docker
├── .env              # Zmienne środowiskowe (lokalne)
├── .env.example      # Wzorzec zmiennych środowiskowych
└── README.md         # Ten plik
```

## Bezpieczeństwo

- Klucze API są przechowywane w zmiennych środowiskowych
- Plik `.env` jest ignorowany przez Git
- Używaj `.env.example` jako wzorca dla innych deweloperów