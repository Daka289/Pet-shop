# Pet Shop -Ecommerce app
## Team Members
- **Danilo Todorovic 2023/0284**
- **Andrija Topic 2023/0486**



## I deo - Dokumentacija

### 1. Korisnički zahtev i namena aplikacije

**Pet Shop** je potpuna e-commerce aplikacija za prodaju prateće opreme za kucne ljubimce. Aplikacija omogućava kupcima da pregledaju i kupuju proizvode po kategorijama, upravljaju svojim profilima, dodaju proizvode u korpu i listu želja,ostavljaju recenzije na proizvode, kao i da prate svoje porudžbine.

**Glavne funkcionalnosti:**
- Pregled i pretraga proizvoda po kategorijama
- Detaljni prikaz proizvoda sa recenzijama
- Registracija i upravljanje korisničkim profilima
- Shopping cart funkcionalnost
- Wishlist funkcionalnost
- Sistem porudžbina sa praćenjem statusa
- Admin panel za upravljanje proizvodima i porudžbinama
- Responzivni dizajn za sve uređaje
-View profile prikazuje prethodne porudzbine

### 2. Tehnologije korišćene u aplikaciji

**Backend tehnologije:**
- **Django 4.2.7** - Python web framework za backend logiku
- **PostgreSQL 15** - Relaciona baza podataka
- **Redis 7** - In-memory cache i session storage
- **Gunicorn** - WSGI server za pokretanje Django aplikacije u produkciji

**Frontend tehnologije:**
- **Bootstrap 5** - CSS framework za responzivni dizajn
- **Font Awesome** - Ikone
- **HTML5/CSS3** - Markup i stilizovanje

**Docker i infrastruktura:**
- **Docker** - Kontejnerizacija aplikacije
- **Docker Compose** - Orkestacija više servisa
- **Nginx** - Reverse proxy i static file server
- **WhiteNoise** - Static file serving za Django

**Python biblioteke:**
- **Pillow** - Image processing
- **django-redis** - Redis integration
- **python-decouple** - Environment variables
- **crispy-forms** - Django form rendering

### 3. Korisničko uputstvo

#### Pokretanje aplikacije

1. **Kloniranje projekta:**
```bash
git clone <repository-url>
cd petshop-docker
```

2. **Pokretanje sa Docker Compose:**
```bash
# Pokretanje svih servisa
docker-compose up -d

# Kreiranje i migracija baze podataka
docker-compose exec web python manage.py migrate

# Kreiranje sample podataka
docker-compose exec web python manage.py populate_data

# Kreiranje superuser-a (optional)
docker-compose exec web python manage.py createsuperuser
```

3. **Pristup aplikaciji:**
- **Frontend**: http://localhost ili http://localhost:80
- **Admin panel**: http://localhost/admin
- **API Health check**: http://localhost/health/

#### Osnovni slučajevi korišćenja

**1. Pregled proizvoda**
- Idite na glavnu stranicu
- Kliknite na "Products" u navigaciji
- Koristite filtere za pretragu po kategorijama
- Sortiranje po ceni, imenu ili datumu

**2. Registracija novog korisnika**
- Kliknite "Register" u navigaciji
- Popunite formu sa podacima
- Potvrdite registraciju

**3. Dodavanje proizvoda u korpu**
- Otvorite detalje proizvoda
- Izaberite količinu
- Kliknite "Add to Cart"
- Idite u korpu preko navigacije

**4. Završavanje porudžbine**
- U korpi kliknite "Checkout"
- Popunite adresu za dostavu
- Potvrdite porudžbinu

**5. Upravljanje profilom**
- Nakon prijave, idite na "Profile"
- Ažurirajte lične podatke
- Dodajte profilnu sliku

### 4. Reprezentativni delovi koda

#### Django Model (shop/models.py)
```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    stock_quantity = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    @property
    def get_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price
```

#### Django View sa caching (shop/views.py)
```python
def home(request):
    # Cache featured products for better performance
    featured_products = cache.get('featured_products')
    if not featured_products:
        featured_products = Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category')[:8]
        cache.set('featured_products', featured_products, 300)
    
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
    })
```

#### Cart funkcionalnost (shop/views.py)
```python
@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return redirect('shop:cart_detail')
```

### 5. Proces kontejnerizacije/dokerizacije
**Web(Django)->DB(PostgreSQL)->Redis->Nginx**

#### Dockerfile objašnjenje

```dockerfile
# Koristimo Python 3.11 slim image kao base
FROM python:3.11-slim

# Dodajemo metadata labels (dodatna opcija)
LABEL maintainer="Pet Shop Team"
LABEL version="1.0"
LABEL description="Django Pet Shop Application"

# Environment varijable
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instaliramo sistem dependencies
RUN apt-get update && apt-get install -y postgresql-client gcc

# Kreiramo non-root user (sigurnosna praksa)
RUN groupadd -r django && useradd -r -g django django

# Kopiramo requirements i instaliramo dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Kopiramo kod aplikacije
COPY . /app/

# Menjamo vlasništvo fajlova
RUN chown -R django:django /app

# Prebacujemo se na non-root user
USER django

# Health check (dodatna opcija)
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health/

# Pokretamo aplikaciju
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "petshop.wsgi:application"]
```

#### docker-compose.yml detaljno objašnjenje

```yaml
version: '3.8'

# Ime projekta/aplikacije
name: petshop-application

services:
  # Django Web Aplikacija
  web:
    container_name: petshop-web                    # Naziv kontejnera
    build:
      context: .                                   # Build context
      dockerfile: Dockerfile                       # Putanja do Dockerfile
      args:
        - BUILDKIT_INLINE_CACHE=1                 # Dodatna build opcija
    ports:
      - "8000:8000"                               # Port mapping
    volumes:
      - ./:/app:ro                                # Bind-mount (read-only)
      - static_volume:/app/staticfiles            # Named volume za static
      - media_volume:/app/media                   # Named volume za media
    env_file:
      - env_file                                  # Environment varijable
    depends_on:
      db:
        condition: service_healthy                # Čeka da db bude healthy
      redis:
        condition: service_healthy
    networks:
      - petshop-network                           # Custom network
    restart: unless-stopped                       # Auto restart opcija
    healthcheck:                                  # Health check
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:                                       # Resource limits
      resources:
        limits:
          memory: 512M

  # PostgreSQL Baza podataka
  db:
    container_name: petshop-db
    image: postgres:15-alpine                     # Gotov image sa DockerHub
    volumes:
      - postgres_data:/var/lib/postgresql/data    # Persistent storage
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:                                  # Environment varijable
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    networks:
      - petshop-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    container_name: petshop-redis
    image: redis:7-alpine
    volumes:
      - redis_data:/data                          # Persistent storage
    networks:
      - petshop-network
    restart: unless-stopped
    command: redis-server --appendonly yes       # Dodatne opcije

  # Nginx Reverse Proxy (dodatni servis)
  nginx:
    container_name: petshop-nginx
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/static:ro
      - media_volume:/media:ro
    depends_on:
      - web
    networks:
      - petshop-network
    restart: unless-stopped

# Definisanje mreže
networks:
  petshop-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

# Definisanje volumena
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local
```

### Dodatne Docker opcije objašnjene

#### .dockerignore
```
# Git files
.git
.gitignore

# Python cache
__pycache__
*.pyc

# Virtual environments
.env
.venv

# Development files
.vscode/
.idea/

# Database files
*.db
*.sqlite3
```

#### Environment varijable (env_file)
```
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=petshop_db
DB_USER=petshop_user
DB_PASSWORD=petshop_password
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/1
```

## II deo – Implementacija

Implementacija je realizovana koristeći Django framework sa sledećim aplikacijama:

### Struktura aplikacije:
```
petshop/
├── petshop/                 # Glavni projekat
│   ├── settings.py         # Konfiguracija
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI konfiguracija
├── shop/                   # Shop aplikacija
│   ├── models.py          # Product, Category, Cart modeli
│   ├── views.py           # Business logika
│   ├── admin.py           # Admin konfiguracija
│   └── templates/         # HTML templates
|
├──media/products          #images for web
├── accounts/               # User management
│   ├── models.py          # UserProfile model
│   ├── views.py           # Authentication views
│   └── forms.py           # User forms
├── orders/                 # Order management
│   ├── models.py          # Order, OrderItem modeli
│   └── views.py           # Order processing
└── templates/              # Shared templates
    └── base.html          # Base template
```

### Ključne funkcionalnosti:
- **Product Management**: CRUD operacije za proizvode
- **User Authentication**: Registracija, prijava, profili
- **Shopping Cart**: Session-based cart sa Redis
- **Order Processing**: Kompletna logika porudžbina
- **Admin Interface**: Django admin za upravljanje
- **Responsive Design**: Bootstrap 5 frontend

## III deo – Dokerizacija

### Kontejneri u aplikaciji:

1. **web** - Django aplikacija (port 8000)
2. **db** - PostgreSQL baza (port 5432)
3. **redis** - Redis cache (port 6379)
4. **nginx** - Reverse proxy (port 80)

### Volumeni:
- `postgres_data` - Persistent storage za bazu
- `redis_data` - Persistent storage za Redis
- `static_volume` - Django static files
- `media_volume` - User uploaded files
- Bind-mount `./:/app:ro` - Development volume

### Mreža:
- Custom bridge network `petshop-network`
- Subnet: 172.20.0.0/16
- Omogućava komunikaciju između kontejnera

### Health Checks:
- Web aplikacija: HTTP GET na `/health/`
- PostgreSQL: `pg_isready` komanda
- Redis: `redis-cli ping`
- Nginx: HTTP GET na `/`

### Postupak kontejnerizacije:

1. **Build images:**
```bash
docker-compose build
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Initialize database:**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py populate_data
```

4. **View logs:**
```bash
docker-compose logs -f
```

5. **Stop services:**
```bash
docker-compose down
```

### Ažuriranje aplikacije:
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Run migrations if needed
docker-compose exec web python manage.py migrate
```

<!-- ## Zaključak

Pet Shop aplikacija demonstrira potpunu implementaciju moderne web aplikacije sa Docker kontejnerizacijom. Aplikacija koristi najbolje prakse za:

- **Sigurnost**: Non-root Docker user, environment varijable
- **Performance**: Redis caching, optimizovani queries
- **Skalabilnost**: Microservices arhitektura sa Docker Compose
- **Maintainability**: Čist kod, jasna struktura, dokumentacija

Aplikacija je spremna za produkciju i može se lako deployovati na cloud platforme poput AWS, Azure ili Google Cloud.  -->