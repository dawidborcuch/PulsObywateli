"""
Management command do tworzenia przykładowych danych testowych
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.bills.models import Bill, BillVote
from apps.polls.models import Poll, PollVote
from apps.comments.models import Comment
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Tworzy przykładowe dane testowe'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Liczba użytkowników do utworzenia'
        )
        parser.add_argument(
            '--bills',
            type=int,
            default=20,
            help='Liczba projektów ustaw do utworzenia'
        )
        parser.add_argument(
            '--polls',
            type=int,
            default=10,
            help='Liczba sondaży do utworzenia'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        bills_count = options['bills']
        polls_count = options['polls']
        
        self.stdout.write('Tworzę przykładowe dane testowe...')
        
        # Tworzenie użytkowników
        self.create_users(users_count)
        
        # Tworzenie projektów ustaw
        self.create_bills(bills_count)
        
        # Tworzenie sondaży
        self.create_polls(polls_count)
        
        # Tworzenie głosów i komentarzy
        self.create_votes_and_comments()
        
        self.stdout.write(
            self.style.SUCCESS('Przykładowe dane zostały utworzone pomyślnie!')
        )

    def create_users(self, count):
        """Tworzy przykładowych użytkowników"""
        self.stdout.write(f'Tworzenie {count} użytkowników...')
        
        for i in range(count):
            user, created = User.objects.get_or_create(
                email=f'user{i+1}@example.com',
                defaults={
                    'username': f'user{i+1}',
                    'nickname': f'Użytkownik{i+1}',
                    'first_name': f'Imię{i+1}',
                    'last_name': f'Nazwisko{i+1}',
                }
            )
            if created:
                user.set_password('password123')
                user.save()

    def create_bills(self, count):
        """Tworzy przykładowe projekty ustaw"""
        self.stdout.write(f'Tworzenie {count} projektów ustaw...')
        
        bill_titles = [
            'Ustawa o ochronie środowiska',
            'Ustawa o edukacji',
            'Ustawa o służbie zdrowia',
            'Ustawa o transporcie publicznym',
            'Ustawa o mieszkalnictwie',
            'Ustawa o energii odnawialnej',
            'Ustawa o cyfryzacji',
            'Ustawa o kulturze',
            'Ustawa o sporcie',
            'Ustawa o turystyce',
            'Ustawa o bezpieczeństwie',
            'Ustawa o pracy',
            'Ustawa o emeryturach',
            'Ustawa o podatkach',
            'Ustawa o sądownictwie',
        ]
        
        statuses = ['draft', 'submitted', 'in_committee', 'first_reading', 'second_reading', 'third_reading', 'passed', 'rejected']
        authors_list = [
            'Klub Parlamentarny Prawo i Sprawiedliwość',
            'Klub Parlamentarny Koalicja Obywatelska',
            'Klub Parlamentarny Lewica',
            'Klub Parlamentarny Polska 2050',
            'Klub Parlamentarny Konfederacja',
            'Klub Parlamentarny Kukiz\'15',
        ]
        
        for i in range(count):
            title = random.choice(bill_titles)
            if i > len(bill_titles) - 1:
                title = f'{title} (wersja {i//len(bill_titles) + 1})'
            
            bill, created = Bill.objects.get_or_create(
                number=f'U/{i+1}/2024',
                defaults={
                    'title': title,
                    'description': f'Projekt ustawy dotyczący {title.lower()}. Projekt ma na celu poprawę sytuacji w danej dziedzinie poprzez wprowadzenie nowych regulacji prawnych.',
                    'authors': random.choice(authors_list),
                    'submission_date': timezone.now().date() - timedelta(days=random.randint(1, 365)),
                    'status': random.choice(statuses),
                    'source_url': f'https://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=PROJEKTY_USTAW&id={i+1}',
                    'is_featured': random.choice([True, False]),
                    'tags': random.choice(['środowisko', 'edukacja', 'zdrowie', 'transport', 'mieszkalnictwo', 'energia', 'cyfryzacja', 'kultura', 'sport', 'turystyka']),
                }
            )

    def create_polls(self, count):
        """Tworzy przykładowe sondaże"""
        self.stdout.write(f'Tworzenie {count} sondaży...')
        
        poll_titles = [
            'Czy popierasz wprowadzenie bezpłatnej komunikacji publicznej?',
            'Czy jesteś za zwiększeniem nakładów na służbę zdrowia?',
            'Czy popierasz wprowadzenie 4-dniowego tygodnia pracy?',
            'Czy jesteś za zwiększeniem wieku emerytalnego?',
            'Czy popierasz legalizację marihuany?',
            'Czy jesteś za zwiększeniem podatków dla najbogatszych?',
            'Czy popierasz wprowadzenie bezpłatnych obiadów w szkołach?',
            'Czy jesteś za zwiększeniem nakładów na obronność?',
            'Czy popierasz wprowadzenie bezpłatnych leków dla seniorów?',
            'Czy jesteś za zwiększeniem nakładów na kulturę?',
        ]
        
        poll_types = ['political', 'social', 'economic', 'other']
        
        for i in range(count):
            title = random.choice(poll_titles)
            if i > len(poll_titles) - 1:
                title = f'{title} (edycja {i//len(poll_titles) + 1})'
            
            options = [
                'Zdecydowanie tak',
                'Raczej tak',
                'Nie mam zdania',
                'Raczej nie',
                'Zdecydowanie nie'
            ]
            
            poll, created = Poll.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'Sondaż dotyczący {title.lower()}. Twoja opinia jest dla nas ważna!',
                    'poll_type': random.choice(poll_types),
                    'options': options,
                    'start_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'end_date': timezone.now() + timedelta(days=random.randint(1, 60)),
                    'is_featured': random.choice([True, False]),
                    'tags': random.choice(['transport', 'zdrowie', 'praca', 'emerytury', 'narkotyki', 'podatki', 'edukacja', 'obronność', 'kultura']),
                }
            )

    def create_votes_and_comments(self):
        """Tworzy przykładowe głosy i komentarze"""
        self.stdout.write('Tworzenie głosów i komentarzy...')
        
        users = list(User.objects.all())
        bills = list(Bill.objects.all())
        polls = list(Poll.objects.all())
        
        # Głosy na projekty ustaw
        for bill in bills:
            voters = random.sample(users, random.randint(5, min(50, len(users))))
            for user in voters:
                vote_choice = random.choice(['support', 'against', 'neutral'])
                BillVote.objects.get_or_create(
                    user=user,
                    bill=bill,
                    defaults={'vote': vote_choice}
                )
        
        # Głosy w sondażach
        for poll in polls:
            voters = random.sample(users, random.randint(10, min(100, len(users))))
            for user in voters:
                selected_option = random.choice(poll.options)
                PollVote.objects.get_or_create(
                    user=user,
                    poll=poll,
                    defaults={'selected_option': selected_option}
                )
        
        # Komentarze do projektów ustaw
        comment_texts = [
            'Bardzo dobry projekt, popieram w pełni!',
            'Nie zgadzam się z tym rozwiązaniem.',
            'Ciekawe podejście, ale wymaga dopracowania.',
            'Świetny pomysł, czekam na realizację.',
            'To może być problematyczne w praktyce.',
            'Dobry kierunek, ale za mało ambitne.',
            'Wreszcie ktoś pomyślał o tym problemie!',
            'To może być zbyt kosztowne.',
            'Popieram, ale z pewnymi zastrzeżeniami.',
            'Nie jestem przekonany do tego rozwiązania.',
        ]
        
        for bill in bills:
            commenters = random.sample(users, random.randint(2, min(20, len(users))))
            for user in commenters:
                Comment.objects.get_or_create(
                    user=user,
                    bill=bill,
                    defaults={
                        'content': random.choice(comment_texts),
                    }
                )

