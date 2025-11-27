"""
Setup script for Role-Based Access Control (RBAC) Users
Creates test users for each role: Admin, Supervisor, Customer
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecoshop.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import User

def create_rbac_users():
    """Create users with different roles for testing"""
    
    print("\n" + "="*60)
    print("🔐 SETTING UP RBAC USERS")
    print("="*60)
    
    # Define users for each role
    users_data = [
        # Admins
        {
            'username': 'admin',
            'email': 'admin@ecoshop.com',
            'password': 'admin123',
            'role': 'admin',
            'first_name': 'System',
            'last_name': 'Admin',
            'phone': '+1-555-0100',
            'city': 'Windsor',
            'country': 'Canada',
            'postal_code': 'N9A 1A1',
        },
        {
            'username': 'superadmin',
            'email': 'superadmin@ecoshop.com',
            'password': 'super123',
            'role': 'admin',
            'first_name': 'Super',
            'last_name': 'Admin',
            'phone': '+1-555-0101',
            'city': 'Windsor',
            'country': 'Canada',
            'postal_code': 'N9A 1A2',
        },
        
        # Supervisors
        {
            'username': 'supervisor1',
            'email': 'supervisor1@ecoshop.com',
            'password': 'super123',
            'role': 'supervisor',
            'first_name': 'John',
            'last_name': 'Manager',
            'phone': '+1-555-0200',
            'city': 'Windsor',
            'country': 'Canada',
            'postal_code': 'N9B 2B2',
        },
        {
            'username': 'supervisor2',
            'email': 'supervisor2@ecoshop.com',
            'password': 'super123',
            'role': 'supervisor',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'phone': '+1-555-0201',
            'city': 'Toronto',
            'country': 'Canada',
            'postal_code': 'M5V 1A1',
        },
        
        # Customers
        {
            'username': 'customer1',
            'email': 'customer1@example.com',
            'password': 'customer123',
            'role': 'customer',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'phone': '+1-555-0300',
            'city': 'Windsor',
            'country': 'Canada',
            'postal_code': 'N9C 3C3',
            'eco_points': 250,
        },
        {
            'username': 'customer2',
            'email': 'customer2@example.com',
            'password': 'customer123',
            'role': 'customer',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'phone': '+1-555-0301',
            'city': 'Ottawa',
            'country': 'Canada',
            'postal_code': 'K1A 0A1',
            'eco_points': 150,
        },
        {
            'username': 'customer3',
            'email': 'customer3@example.com',
            'password': 'customer123',
            'role': 'customer',
            'first_name': 'Carol',
            'last_name': 'Davis',
            'phone': '+1-555-0302',
            'city': 'Vancouver',
            'country': 'Canada',
            'postal_code': 'V6B 1A1',
            'eco_points': 500,
        },
        
        # Keep existing users but update their roles
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'role': 'customer',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1-555-1234',
            'city': 'Windsor',
            'country': 'Canada',
            'postal_code': 'N9A 1A1',
            'eco_points': 320,
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'password123',
            'role': 'customer',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+1-555-5678',
            'city': 'Windsor',
            'country': 'Canada',
            'postal_code': 'N9A 2B2',
            'eco_points': 180,
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user exists
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': user_data['email'],
                'role': user_data['role'],
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'phone': user_data.get('phone', ''),
                'city': user_data.get('city', ''),
                'country': user_data.get('country', ''),
                'postal_code': user_data.get('postal_code', ''),
                'eco_points': user_data.get('eco_points', 0),
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            created_count += 1
            role_emoji = {'admin': '👑', 'supervisor': '👔', 'customer': '👤'}.get(user_data['role'], '❓')
            print(f"  ✅ Created: {role_emoji} {username} ({user_data['role']})")
        else:
            # Update existing user's role if needed
            if user.role != user_data['role']:
                old_role = user.role
                user.role = user_data['role']
                user.save()
                updated_count += 1
                print(f"  🔄 Updated: {username} ({old_role} → {user_data['role']})")
            else:
                print(f"  ⏭️  Skipped: {username} (already exists)")
    
    print("\n" + "-"*60)
    print(f"📊 SUMMARY:")
    print(f"   • Created: {created_count} users")
    print(f"   • Updated: {updated_count} users")
    print(f"   • Total in DB: {User.objects.count()} users")
    print("-"*60)
    
    # Print role distribution
    print("\n📈 ROLE DISTRIBUTION:")
    for role_value, role_label in User.ROLE_CHOICES:
        count = User.objects.filter(role=role_value).count()
        emoji = {'admin': '👑', 'supervisor': '👔', 'customer': '👤'}.get(role_value, '❓')
        print(f"   {emoji} {role_label}: {count} users")
    
    # Print login credentials
    print("\n" + "="*60)
    print("🔑 LOGIN CREDENTIALS")
    print("="*60)
    
    print("\n👑 ADMIN ACCOUNTS (Full Access):")
    print("   ┌────────────────┬───────────────────────────┬────────────┐")
    print("   │ Username       │ Email                     │ Password   │")
    print("   ├────────────────┼───────────────────────────┼────────────┤")
    print("   │ admin          │ admin@ecoshop.com         │ admin123   │")
    print("   │ superadmin     │ superadmin@ecoshop.com    │ super123   │")
    print("   └────────────────┴───────────────────────────┴────────────┘")
    
    print("\n👔 SUPERVISOR ACCOUNTS (Limited Access):")
    print("   ┌────────────────┬───────────────────────────┬────────────┐")
    print("   │ Username       │ Email                     │ Password   │")
    print("   ├────────────────┼───────────────────────────┼────────────┤")
    print("   │ supervisor1    │ supervisor1@ecoshop.com   │ super123   │")
    print("   │ supervisor2    │ supervisor2@ecoshop.com   │ super123   │")
    print("   └────────────────┴───────────────────────────┴────────────┘")
    
    print("\n👤 CUSTOMER ACCOUNTS (Shopping Only):")
    print("   ┌────────────────┬───────────────────────────┬─────────────┐")
    print("   │ Username       │ Email                     │ Password    │")
    print("   ├────────────────┼───────────────────────────┼─────────────┤")
    print("   │ customer1      │ customer1@example.com     │ customer123 │")
    print("   │ customer2      │ customer2@example.com     │ customer123 │")
    print("   │ customer3      │ customer3@example.com     │ customer123 │")
    print("   │ john_doe       │ john@example.com          │ password123 │")
    print("   │ jane_smith     │ jane@example.com          │ password123 │")
    print("   └────────────────┴───────────────────────────┴─────────────┘")
    
    print("\n" + "="*60)
    print("✅ RBAC SETUP COMPLETE!")
    print("="*60)
    print("\n📌 ACCESS URLS:")
    print("   • Website:          http://127.0.0.1:8000/")
    print("   • Management:       http://127.0.0.1:8000/accounts/management/")
    print("   • Django Admin:     http://127.0.0.1:8000/admin/")
    print("   • Login:            http://127.0.0.1:8000/accounts/login/")
    print()

if __name__ == '__main__':
    create_rbac_users()
