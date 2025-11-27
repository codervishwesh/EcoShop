import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoshop.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Category, Product, Review, Wishlist
from orders.models import Order, OrderItem
from decimal import Decimal
import random

User = get_user_model()

def create_database():
    print("🗄️ Setting up EcoShop Database...")
    print("=" * 50)
    
    # 1. CREATE SUPERUSER
    print("\n1️⃣ Creating Admin User...")
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@ecoshop.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("   ✅ Admin created (username: admin, password: admin123)")
    else:
        admin = User.objects.get(username='admin')
        print("   ✅ Admin already exists")
    
    # 2. CREATE REGULAR USERS
    print("\n2️⃣ Creating Regular Users...")
    users_data = [
        {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'is_seller': False},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'is_seller': False},
        {'username': 'eco_seller', 'email': 'seller@ecoshop.com', 'first_name': 'Eco', 'last_name': 'Seller', 'is_seller': True},
        {'username': 'green_vendor', 'email': 'vendor@ecoshop.com', 'first_name': 'Green', 'last_name': 'Vendor', 'is_seller': True},
    ]
    
    users = []
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='password123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_seller=user_data['is_seller'],
                phone='+1-555-' + str(random.randint(1000, 9999)),
                address='123 Green Street',
                city='Windsor',
                country='Canada',
                postal_code='N9A 1A1',
                eco_points=random.randint(50, 500)
            )
            users.append(user)
            print(f"   ✅ Created user: {user.username}")
        else:
            users.append(User.objects.get(username=user_data['username']))
            print(f"   ✅ User exists: {user_data['username']}")
    
    # 3. CREATE CATEGORIES
    print("\n3️⃣ Creating Categories...")
    categories_data = [
        {'name': 'Personal Care', 'icon': '💆', 'description': 'Eco-friendly personal care and beauty products'},
        {'name': 'Home & Living', 'icon': '🏠', 'description': 'Sustainable home and living essentials'},
        {'name': 'Fashion', 'icon': '👗', 'description': 'Organic and sustainable fashion'},
        {'name': 'Kitchen', 'icon': '🍳', 'description': 'Eco-friendly kitchen and dining essentials'},
        {'name': 'Electronics', 'icon': '📱', 'description': 'Sustainable electronics and gadgets'},
        {'name': 'Garden', 'icon': '🌱', 'description': 'Organic gardening and outdoor supplies'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'icon': cat_data['icon'],
                'description': cat_data['description']
            }
        )
        categories.append(category)
        status = "Created" if created else "Exists"
        print(f"   ✅ {status}: {category.name}")
    
    # 4. CREATE PRODUCTS
    print("\n4️⃣ Creating Products...")
    
    sellers = [u for u in users if u.is_seller]
    if not sellers:
        sellers = [admin]
    
    products_data = [
        # Personal Care
        {'name': 'Bamboo Toothbrush Set', 'category': 0, 'price': 12.99, 'stock': 150, 'eco_score': 95, 
         'description': 'Set of 4 biodegradable bamboo toothbrushes. BPA-free, vegan-friendly bristles.',
         'eco_certifications': 'Organic, Biodegradable', 'carbon_footprint': 0.05, 'recyclable': True, 'biodegradable': True, 'is_featured': True},
        
        {'name': 'Organic Shampoo Bar', 'category': 0, 'price': 15.99, 'stock': 200, 'eco_score': 92,
         'description': 'All-natural, zero-waste shampoo bar. Lasts 2-3 months.',
         'eco_certifications': 'Organic, Cruelty-Free', 'carbon_footprint': 0.08, 'recyclable': False, 'biodegradable': True, 'is_featured': True},
        
        {'name': 'Reusable Cotton Rounds', 'category': 0, 'price': 18.50, 'stock': 100, 'eco_score': 90,
         'description': 'Set of 16 reusable makeup remover pads made from organic cotton.',
         'eco_certifications': 'Organic Cotton, Fair Trade', 'carbon_footprint': 0.12, 'recyclable': True, 'biodegradable': True, 'is_featured': False},
        
        # Home & Living
        {'name': 'Beeswax Food Wraps', 'category': 1, 'price': 24.99, 'stock': 80, 'eco_score': 94,
         'description': 'Set of 5 reusable beeswax wraps. Replace plastic wrap naturally.',
         'eco_certifications': 'Organic, Biodegradable', 'carbon_footprint': 0.15, 'recyclable': False, 'biodegradable': True, 'is_featured': True},
        
        {'name': 'Bamboo Bed Sheets Set', 'category': 1, 'price': 89.99, 'stock': 45, 'eco_score': 88,
         'description': 'Luxury bamboo bed sheet set. Hypoallergenic and moisture-wicking.',
         'eco_certifications': 'Organic Bamboo', 'carbon_footprint': 2.50, 'recyclable': True, 'biodegradable': True, 'is_featured': False},
        
        {'name': 'LED Smart Bulbs 4-Pack', 'category': 1, 'price': 34.99, 'stock': 120, 'eco_score': 85,
         'description': 'Energy-efficient LED smart bulbs. 75% less energy than traditional bulbs.',
         'eco_certifications': 'Energy Star', 'carbon_footprint': 1.20, 'recyclable': True, 'biodegradable': False, 'is_featured': False},
        
        # Fashion
        {'name': 'Organic Cotton T-Shirt', 'category': 2, 'price': 29.99, 'stock': 200, 'eco_score': 87,
         'description': 'Premium organic cotton t-shirt. Fair trade certified.',
         'eco_certifications': 'Organic Cotton, Fair Trade', 'carbon_footprint': 1.80, 'recyclable': True, 'biodegradable': True, 'is_featured': True},
        
        {'name': 'Recycled Polyester Backpack', 'category': 2, 'price': 54.99, 'stock': 75, 'eco_score': 82,
         'description': 'Backpack made from 100% recycled plastic bottles. Water-resistant.',
         'eco_certifications': 'Recycled Materials', 'carbon_footprint': 3.50, 'recyclable': True, 'biodegradable': False, 'is_featured': False},
        
        {'name': 'Hemp Yoga Pants', 'category': 2, 'price': 45.99, 'stock': 90, 'eco_score': 89,
         'description': 'Comfortable yoga pants made from organic hemp blend.',
         'eco_certifications': 'Organic Hemp', 'carbon_footprint': 2.20, 'recyclable': True, 'biodegradable': True, 'is_featured': False},
        
        # Kitchen
        {'name': 'Stainless Steel Water Bottle', 'category': 3, 'price': 24.99, 'stock': 180, 'eco_score': 93,
         'description': '32oz insulated water bottle. Keeps drinks cold 24hrs, hot 12hrs.',
         'eco_certifications': 'BPA-Free', 'carbon_footprint': 1.50, 'recyclable': True, 'biodegradable': False, 'is_featured': True},
        
        {'name': 'Bamboo Utensil Set', 'category': 3, 'price': 16.99, 'stock': 150, 'eco_score': 91,
         'description': 'Portable bamboo cutlery set with carrying case.',
         'eco_certifications': 'Organic Bamboo', 'carbon_footprint': 0.30, 'recyclable': False, 'biodegradable': True, 'is_featured': False},
        
        {'name': 'Silicone Food Storage Bags', 'category': 3, 'price': 19.99, 'stock': 110, 'eco_score': 86,
         'description': 'Set of 4 reusable silicone bags. Dishwasher safe.',
         'eco_certifications': 'BPA-Free', 'carbon_footprint': 0.80, 'recyclable': True, 'biodegradable': False, 'is_featured': False},
        
        # Electronics
        {'name': 'Solar Phone Charger', 'category': 4, 'price': 45.00, 'stock': 65, 'eco_score': 90,
         'description': '20000mAh solar power bank. Waterproof and shockproof.',
         'eco_certifications': 'Energy Efficient', 'carbon_footprint': 4.50, 'recyclable': True, 'biodegradable': False, 'is_featured': True},
        
        {'name': 'Eco Wireless Mouse', 'category': 4, 'price': 28.99, 'stock': 95, 'eco_score': 83,
         'description': 'Wireless mouse made from 85% recycled plastic.',
         'eco_certifications': 'Recycled Materials', 'carbon_footprint': 1.80, 'recyclable': True, 'biodegradable': False, 'is_featured': False},
        
        {'name': 'Bamboo Keyboard', 'category': 4, 'price': 79.99, 'stock': 40, 'eco_score': 81,
         'description': 'Wireless keyboard with natural bamboo housing.',
         'eco_certifications': 'Sustainable Materials', 'carbon_footprint': 3.20, 'recyclable': True, 'biodegradable': False, 'is_featured': False},
        
        # Garden
        {'name': 'Compost Bin Starter Kit', 'category': 5, 'price': 64.99, 'stock': 55, 'eco_score': 96,
         'description': 'Complete composting system. Turn waste into nutrient-rich soil.',
         'eco_certifications': 'Organic', 'carbon_footprint': 8.50, 'recyclable': True, 'biodegradable': False, 'is_featured': True},
        
        {'name': 'Organic Seed Collection', 'category': 5, 'price': 22.99, 'stock': 130, 'eco_score': 98,
         'description': '20 organic, non-GMO vegetable and herb seeds with guide.',
         'eco_certifications': 'Organic, Non-GMO', 'carbon_footprint': 0.05, 'recyclable': True, 'biodegradable': True, 'is_featured': False},
        
        {'name': 'Recycled Plastic Planter Set', 'category': 5, 'price': 34.99, 'stock': 70, 'eco_score': 84,
         'description': 'Set of 5 planters from recycled ocean plastic. Self-watering.',
         'eco_certifications': 'Recycled Ocean Plastic', 'carbon_footprint': 2.80, 'recyclable': True, 'biodegradable': False, 'is_featured': False},
    ]
    
    products = []
    for i, prod_data in enumerate(products_data):
        seller = sellers[i % len(sellers)]
        
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'category': categories[prod_data['category']],
                'seller': seller,
                'price': Decimal(str(prod_data['price'])),
                'stock': prod_data['stock'],
                'eco_score': prod_data['eco_score'],
                'description': prod_data['description'],
                'eco_certifications': prod_data['eco_certifications'],
                'carbon_footprint': Decimal(str(prod_data['carbon_footprint'])),
                'recyclable': prod_data['recyclable'],
                'biodegradable': prod_data['biodegradable'],
                'is_featured': prod_data['is_featured'],
                'is_active': True
            }
        )
        products.append(product)
        status = "Created" if created else "Exists"
        print(f"   ✅ {status}: {product.name}")
    
    # 5. CREATE REVIEWS
    print("\n5️⃣ Creating Product Reviews...")
    
    review_comments = [
        "Excellent product! Highly recommend.",
        "Great quality and eco-friendly. Love it!",
        "Good product, worth the price.",
        "Exactly what I was looking for. Very satisfied.",
        "Amazing! Will buy again.",
    ]
    
    review_count = 0
    for product in products[:10]:
        for user in users[:2]:
            if not Review.objects.filter(product=product, user=user).exists():
                Review.objects.create(
                    product=product,
                    user=user,
                    rating=random.randint(4, 5),
                    title=f"Great {product.name.split()[0]}!",
                    comment=random.choice(review_comments),
                    is_verified_purchase=True
                )
                review_count += 1
    
    print(f"   ✅ Created {review_count} reviews")
    
    # 6. CREATE SAMPLE ORDERS
    print("\n6️⃣ Creating Sample Orders...")
    
    order_count = 0
    for user in users[:2]:
        order = Order.objects.create(
            user=user,
            order_number=f'ECO-{random.randint(10000000, 99999999):08X}',
            status='delivered',
            shipping_name=user.get_full_name(),
            shipping_email=user.email,
            shipping_phone=user.phone or '+1-555-1234',
            shipping_address='123 Green Street',
            shipping_city='Windsor',
            shipping_country='Canada',
            shipping_postal_code='N9A 1A1',
            subtotal=Decimal('89.97'),
            tax=Decimal('11.70'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('101.67'),
            eco_points_earned=270,
            co2_saved=Decimal('0.45')
        )
        
        OrderItem.objects.create(
            order=order,
            product=products[0],
            product_name=products[0].name,
            product_price=products[0].price,
            quantity=2,
            eco_score=products[0].eco_score
        )
        
        user.total_orders += 1
        user.eco_points += order.eco_points_earned
        user.co2_saved = Decimal(str(float(user.co2_saved) + float(order.co2_saved)))
        user.save()
        
        order_count += 1
    
    print(f"   ✅ Created {order_count} sample orders")
    
    # 7. CREATE WISHLISTS
    print("\n7️⃣ Creating Wishlists...")
    
    wishlist_count = 0
    for user in users[:2]:
        for product in products[5:10]:
            if not Wishlist.objects.filter(user=user, product=product).exists():
                Wishlist.objects.create(user=user, product=product)
                wishlist_count += 1
    
    print(f"   ✅ Created {wishlist_count} wishlist items")
    
    # SUMMARY
    print("\n" + "=" * 50)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 50)
    print(f"\n📊 Summary:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Categories: {Category.objects.count()}")
    print(f"   Products: {Product.objects.count()}")
    print(f"   Reviews: {Review.objects.count()}")
    print(f"   Orders: {Order.objects.count()}")
    print(f"   Wishlist Items: {Wishlist.objects.count()}")
    
    print("\n🔐 Login Credentials:")
    print("   Admin:")
    print("     Username: admin")
    print("     Password: admin123")
    print("\n   Test Users:")
    print("     Username: john_doe")
    print("     Password: password123")
    
    print("\n🌐 Access:")
    print("   Website: http://127.0.0.1:8000/")
    print("   Admin: http://127.0.0.1:8000/admin/")
    
    print("\n🎉 Database Ready to Use!")

if __name__ == '__main__':
    create_database()
