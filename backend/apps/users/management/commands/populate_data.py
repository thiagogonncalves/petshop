"""
Command to populate database with fake data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserRole
from apps.clients.models import Client
from apps.pets.models import Pet
from apps.products.models import Category, Product
from apps.services.models import Service
from apps.scheduling.models import Appointment
from apps.sales.models import Sale, SaleItem
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with fake data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            SaleItem.objects.all().delete()
            Sale.objects.all().delete()
            Appointment.objects.all().delete()
            Pet.objects.all().delete()
            Client.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            Service.objects.all().delete()
            User.objects.exclude(is_superuser=True).delete()
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        self.stdout.write('Creating users...')
        self.create_users()
        
        self.stdout.write('Creating categories and products...')
        self.create_products()
        
        self.stdout.write('Creating services...')
        self.create_services()
        
        self.stdout.write('Creating clients and pets...')
        self.create_clients_and_pets()
        
        self.stdout.write('Creating appointments...')
        self.create_appointments()
        
        self.stdout.write('Creating sales...')
        self.create_sales()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database populated successfully!'))

    def create_users(self):
        """Create users"""
        users_data = [
            {'username': 'gerente', 'email': 'gerente@petshop.com', 'role': UserRole.MANAGER, 'first_name': 'Carlos', 'last_name': 'Silva'},
            {'username': 'atendente1', 'email': 'atendente1@petshop.com', 'role': UserRole.USER, 'first_name': 'Ana', 'last_name': 'Santos'},
            {'username': 'atendente2', 'email': 'atendente2@petshop.com', 'role': UserRole.USER, 'first_name': 'João', 'last_name': 'Oliveira'},
        ]
        
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    password='123456',
                    **user_data
                )
                self.stdout.write(f'  Created user: {user_data["username"]}')

    def create_products(self):
        """Create categories and products"""
        categories_data = [
            {'name': 'Rações', 'description': 'Rações para cães e gatos'},
            {'name': 'Medicamentos', 'description': 'Medicamentos veterinários'},
            {'name': 'Brinquedos', 'description': 'Brinquedos para pets'},
            {'name': 'Higiene', 'description': 'Produtos de higiene'},
            {'name': 'Acessórios', 'description': 'Coleiras, guias, roupas'},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
            categories.append(cat)
        
        products_data = [
            # Rações
            {'name': 'Ração Premium para Cães Adultos', 'category': categories[0], 'cost_price': 45.00, 'sale_price': 75.00, 'stock_quantity': 50, 'min_stock': 10, 'unit': 'kg', 'barcode': '7891234567891'},
            {'name': 'Ração Premium para Gatos Adultos', 'category': categories[0], 'cost_price': 42.00, 'sale_price': 70.00, 'stock_quantity': 40, 'min_stock': 10, 'unit': 'kg', 'barcode': '7891234567892'},
            {'name': 'Ração para Filhotes', 'category': categories[0], 'cost_price': 48.00, 'sale_price': 80.00, 'stock_quantity': 30, 'min_stock': 10, 'unit': 'kg', 'barcode': '7891234567893'},
            {'name': 'Ração Premium para Cães Idosos', 'category': categories[0], 'cost_price': 50.00, 'sale_price': 85.00, 'stock_quantity': 25, 'min_stock': 10, 'unit': 'kg', 'barcode': '7891234567894'},
            # Medicamentos
            {'name': 'Vermífugo para Cães', 'category': categories[1], 'cost_price': 15.00, 'sale_price': 25.00, 'stock_quantity': 100, 'min_stock': 20, 'unit': 'un', 'barcode': '7891234567895'},
            {'name': 'Vermífugo para Gatos', 'category': categories[1], 'cost_price': 14.00, 'sale_price': 24.00, 'stock_quantity': 90, 'min_stock': 20, 'unit': 'un', 'barcode': '7891234567896'},
            {'name': 'Anti-pulgas e Carrapatos', 'category': categories[1], 'cost_price': 35.00, 'sale_price': 55.00, 'stock_quantity': 60, 'min_stock': 15, 'unit': 'un', 'barcode': '7891234567897'},
            # Brinquedos
            {'name': 'Bola para Cães', 'category': categories[2], 'cost_price': 8.00, 'sale_price': 15.00, 'stock_quantity': 80, 'min_stock': 20, 'unit': 'un', 'barcode': '7891234567898'},
            {'name': 'Ratinho de Pelúcia', 'category': categories[2], 'cost_price': 12.00, 'sale_price': 22.00, 'stock_quantity': 70, 'min_stock': 20, 'unit': 'un', 'barcode': '7891234567899'},
            {'name': 'Arranhador para Gatos', 'category': categories[2], 'cost_price': 60.00, 'sale_price': 120.00, 'stock_quantity': 15, 'min_stock': 5, 'unit': 'un', 'barcode': '7891234567900'},
            # Higiene
            {'name': 'Shampoo para Cães', 'category': categories[3], 'cost_price': 18.00, 'sale_price': 30.00, 'stock_quantity': 50, 'min_stock': 15, 'unit': 'un', 'barcode': '7891234567901'},
            {'name': 'Shampoo para Gatos', 'category': categories[3], 'cost_price': 17.00, 'sale_price': 28.00, 'stock_quantity': 45, 'min_stock': 15, 'unit': 'un', 'barcode': '7891234567902'},
            {'name': 'Escova para Pelos', 'category': categories[3], 'cost_price': 10.00, 'sale_price': 18.00, 'stock_quantity': 60, 'min_stock': 15, 'unit': 'un', 'barcode': '7891234567903'},
            # Acessórios
            {'name': 'Coleira Ajustável', 'category': categories[4], 'cost_price': 12.00, 'sale_price': 22.00, 'stock_quantity': 100, 'min_stock': 20, 'unit': 'un', 'barcode': '7891234567904'},
            {'name': 'Guia Retrátil', 'category': categories[4], 'cost_price': 25.00, 'sale_price': 45.00, 'stock_quantity': 40, 'min_stock': 10, 'unit': 'un', 'barcode': '7891234567905'},
            {'name': 'Roupinha para Cães', 'category': categories[4], 'cost_price': 20.00, 'sale_price': 38.00, 'stock_quantity': 35, 'min_stock': 10, 'unit': 'un', 'barcode': '7891234567906'},
        ]
        
        for prod_data in products_data:
            Product.objects.get_or_create(
                name=prod_data['name'],
                defaults=prod_data
            )

    def create_services(self):
        """Create services"""
        services_data = [
            {'name': 'Banho e Tosa', 'description': 'Banho completo com tosa higiênica', 'price': 80.00, 'duration_minutes': 120},
            {'name': 'Banho Simples', 'description': 'Banho com secagem', 'price': 50.00, 'duration_minutes': 60},
            {'name': 'Tosa Completa', 'description': 'Tosa completa personalizada', 'price': 100.00, 'duration_minutes': 90},
            {'name': 'Tosa Higiênica', 'description': 'Tosa nas áreas íntimas e patas', 'price': 40.00, 'duration_minutes': 30},
            {'name': 'Corte de Unhas', 'description': 'Corte e lixamento de unhas', 'price': 20.00, 'duration_minutes': 15},
            {'name': 'Limpeza de Ouvidos', 'description': 'Limpeza profunda de ouvidos', 'price': 25.00, 'duration_minutes': 20},
            {'name': 'Escovação de Dentes', 'description': 'Escovação e limpeza dental', 'price': 30.00, 'duration_minutes': 25},
            {'name': 'Consulta Veterinária', 'description': 'Consulta com veterinário', 'price': 120.00, 'duration_minutes': 60},
            {'name': 'Vacinação', 'description': 'Aplicação de vacinas', 'price': 80.00, 'duration_minutes': 30},
            {'name': 'Hidratação', 'description': 'Hidratação de pelos', 'price': 45.00, 'duration_minutes': 40},
        ]
        
        for service_data in services_data:
            Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )

    def create_clients_and_pets(self):
        """Create clients and their pets"""
        clients_data = [
            {
                'name': 'Maria Silva', 'document_type': 'cpf', 'document': '12345678901',
                'phone': '11987654321', 'email': 'maria.silva@email.com',
                'street': 'Rua das Flores', 'number': '123', 'neighborhood': 'Centro',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '01000-000',
                'pets': [
                    {'name': 'Rex', 'species': 'dog', 'breed': 'Labrador', 'sex': 'male', 'birth_date': '2020-03-15', 'weight': 30.5, 'color': 'Amarelo'},
                    {'name': 'Luna', 'species': 'dog', 'breed': 'Golden Retriever', 'sex': 'female', 'birth_date': '2021-06-20', 'weight': 25.0, 'color': 'Dourado'},
                ]
            },
            {
                'name': 'João Santos', 'document_type': 'cpf', 'document': '98765432100',
                'phone': '11912345678', 'email': 'joao.santos@email.com',
                'street': 'Av. Paulista', 'number': '1000', 'neighborhood': 'Bela Vista',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '01310-100',
                'pets': [
                    {'name': 'Mimi', 'species': 'cat', 'breed': 'Persa', 'sex': 'female', 'birth_date': '2019-11-10', 'weight': 4.5, 'color': 'Branco'},
                ]
            },
            {
                'name': 'Ana Costa', 'document_type': 'cpf', 'document': '11122233344',
                'phone': '11999887766', 'email': 'ana.costa@email.com',
                'street': 'Rua do Comércio', 'number': '456', 'neighborhood': 'Jardim',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '02000-000',
                'pets': [
                    {'name': 'Thor', 'species': 'dog', 'breed': 'Husky Siberiano', 'sex': 'male', 'birth_date': '2022-01-05', 'weight': 22.0, 'color': 'Cinza e Branco'},
                    {'name': 'Nina', 'species': 'cat', 'breed': 'Siamês', 'sex': 'female', 'birth_date': '2020-08-15', 'weight': 3.8, 'color': 'Marrom e Branco'},
                ]
            },
            {
                'name': 'Carlos Oliveira', 'document_type': 'cpf', 'document': '55566677788',
                'phone': '11988776655', 'email': 'carlos.oliveira@email.com',
                'street': 'Rua das Acácias', 'number': '789', 'neighborhood': 'Vila Nova',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '03000-000',
                'pets': [
                    {'name': 'Bolinha', 'species': 'dog', 'breed': 'Poodle', 'sex': 'male', 'birth_date': '2021-04-12', 'weight': 8.5, 'color': 'Branco'},
                ]
            },
            {
                'name': 'Juliana Ferreira', 'document_type': 'cpf', 'document': '99988877766',
                'phone': '11977665544', 'email': 'juliana.ferreira@email.com',
                'street': 'Av. Brasil', 'number': '200', 'neighborhood': 'Bras',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '03000-100',
                'pets': [
                    {'name': 'Mel', 'species': 'dog', 'breed': 'Beagle', 'sex': 'female', 'birth_date': '2020-09-25', 'weight': 12.0, 'color': 'Tricolor'},
                    {'name': 'Chico', 'species': 'dog', 'breed': 'Bulldog', 'sex': 'male', 'birth_date': '2019-12-03', 'weight': 18.5, 'color': 'Bege'},
                ]
            },
            {
                'name': 'Roberto Alves', 'document_type': 'cpf', 'document': '44455566677',
                'phone': '11966554433', 'email': 'roberto.alves@email.com',
                'street': 'Rua dos Pinheiros', 'number': '321', 'neighborhood': 'Pinheiros',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '05400-000',
                'pets': [
                    {'name': 'Pipoca', 'species': 'cat', 'breed': 'Maine Coon', 'sex': 'male', 'birth_date': '2021-07-18', 'weight': 6.2, 'color': 'Marrom'},
                ]
            },
            {
                'name': 'Fernanda Lima', 'document_type': 'cpf', 'document': '33344455566',
                'phone': '11955443322', 'email': 'fernanda.lima@email.com',
                'street': 'Rua Augusta', 'number': '500', 'neighborhood': 'Consolação',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '01305-000',
                'pets': [
                    {'name': 'Lola', 'species': 'dog', 'breed': 'Yorkshire', 'sex': 'female', 'birth_date': '2022-02-14', 'weight': 3.5, 'color': 'Preto e Dourado'},
                ]
            },
            {
                'name': 'Pet Shop Premium LTDA', 'document_type': 'cnpj', 'document': '12345678000190',
                'phone': '1133445566', 'email': 'contato@petshoppremium.com',
                'street': 'Av. Faria Lima', 'number': '1500', 'neighborhood': 'Itaim Bibi',
                'city': 'São Paulo', 'state': 'SP', 'zip_code': '04538-130',
                'pets': [
                    {'name': 'Max', 'species': 'dog', 'breed': 'Rottweiler', 'sex': 'male', 'birth_date': '2020-05-30', 'weight': 35.0, 'color': 'Preto e Marrom'},
                ]
            },
        ]
        
        user = User.objects.filter(role=UserRole.USER).first()
        if not user:
            user = User.objects.first()
        
        for client_data in clients_data:
            pets_data = client_data.pop('pets', [])
            client, created = Client.objects.get_or_create(
                document=client_data['document'],
                defaults={**client_data, 'created_by': user}
            )
            
            if created:
                self.stdout.write(f'  Created client: {client.name}')
            
            for pet_data in pets_data:
                Pet.objects.get_or_create(
                    name=pet_data['name'],
                    client=client,
                    defaults={**pet_data, 'created_by': user}
                )

    def create_appointments(self):
        """Create appointments"""
        clients = list(Client.objects.filter(is_active=True)[:5])
        services = list(Service.objects.filter(is_active=True))
        users = list(User.objects.filter(role=UserRole.USER))
        
        if not clients or not services or not users:
            return
        
        # Create appointments for the next 30 days
        for i in range(20):
            client = random.choice(clients)
            pets = list(client.pets.filter(is_active=True))
            if not pets:
                continue
            
            pet = random.choice(pets)
            service = random.choice(services)
            user = random.choice(users)
            
            # Random date in next 30 days, business hours (9h to 18h)
            days_ahead = random.randint(0, 30)
            hour = random.randint(9, 17)
            minute = random.choice([0, 30])
            
            scheduled_date = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
            
            status = random.choice(['scheduled', 'scheduled', 'scheduled', 'completed', 'cancelled'])
            
            Appointment.objects.create(
                client=client,
                pet=pet,
                service=service,
                scheduled_date=scheduled_date,
                status=status,
                observations=random.choice(['', 'Primeira vez', 'Animal nervoso', 'Precisa de cuidados especiais', '']),
                created_by=user
            )

    def create_sales(self):
        """Create sales"""
        clients = list(Client.objects.filter(is_active=True)[:8])
        products = list(Product.objects.filter(is_active=True))
        services = list(Service.objects.filter(is_active=True))
        users = list(User.objects.filter(role__in=[UserRole.USER, UserRole.MANAGER]))
        
        if not clients or not products or not users:
            return
        
        payment_methods = ['cash', 'credit_card', 'debit_card', 'pix', 'pix', 'pix']
        statuses = ['paid', 'paid', 'paid', 'pending']
        
        # Create sales from last 60 days
        for i in range(50):
            client = random.choice(clients)
            user = random.choice(users)
            payment_method = random.choice(payment_methods)
            status = random.choice(statuses)
            
            days_ago = random.randint(0, 60)
            sale_date = datetime.now() - timedelta(days=days_ago)
            
            sale = Sale.objects.create(
                client=client,
                sale_date=sale_date,
                discount=random.choice([0, 0, 0, 5, 10]),
                payment_method=payment_method,
                status=status,
                created_by=user
            )
            
            # Add items to sale
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.sale_price
                discount = random.choice([0, 0, 0, 2])
                
                SaleItem.objects.create(
                    sale=sale,
                    item_type='product',
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount,
                    total=(unit_price * quantity) - discount
                )
            
            # Sometimes add a service
            if random.choice([True, False]) and services:
                service = random.choice(services)
                SaleItem.objects.create(
                    sale=sale,
                    item_type='service',
                    service=service,
                    quantity=1,
                    unit_price=service.price,
                    discount=0,
                    total=service.price
                )
            
            # Recalculate total
            sale.calculate_total()
            sale.save()
