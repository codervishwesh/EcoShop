import re
from products.models import Product, Category
from orders.models import Order

class EcoShopChatbot:
    """Simple AI Chatbot for EcoShop"""
    
    def __init__(self, user=None):
        self.user = user
    
    def get_response(self, message):
        message = message.lower().strip()
        
        # Greetings
        if any(word in message for word in ['hello', 'hi', 'hey', 'help']):
            return self.greeting()
        
        # Product search
        if any(word in message for word in ['find', 'search', 'looking for', 'show me', 'products']):
            return self.search_products(message)
        
        # Categories
        if 'categor' in message:
            return self.list_categories()
        
        # Order status
        if any(word in message for word in ['order', 'tracking', 'status', 'my order']):
            return self.check_orders()
        
        # Eco score info
        if any(word in message for word in ['eco score', 'ecoscore', 'sustainable', 'eco-friendly']):
            return self.eco_info()
        
        # Shipping
        if any(word in message for word in ['shipping', 'delivery', 'ship']):
            return self.shipping_info()
        
        # Returns
        if any(word in message for word in ['return', 'refund', 'exchange']):
            return self.return_policy()
        
        # Payment
        if any(word in message for word in ['payment', 'pay', 'card', 'cod']):
            return self.payment_info()
        
        # Contact
        if any(word in message for word in ['contact', 'support', 'email', 'phone']):
            return self.contact_info()
        
        # Default response
        return self.default_response()
    
    def greeting(self):
        name = self.user.first_name if self.user and self.user.first_name else "there"
        return f"""👋 Hello {name}! Welcome to EcoShop!

I'm your eco-friendly shopping assistant. I can help you with:

🛍️ **Find Products** - "Show me eco-friendly bags"
📦 **Order Status** - "Check my orders"
🌿 **Eco Scores** - "What is eco score?"
🚚 **Shipping Info** - "Shipping options"
💳 **Payments** - "Payment methods"
📞 **Contact** - "How to contact support"

What would you like to know?"""

    def search_products(self, message):
        # Extract search terms
        words = message.replace('find', '').replace('search', '').replace('show me', '').replace('looking for', '').strip()
        
        products = Product.objects.filter(
            is_active=True,
            name__icontains=words
        )[:5]
        
        if products:
            response = f"🔍 Found {products.count()} products:\n\n"
            for p in products:
                response += f"• **{p.name}** - ${p.price} (EcoScore: {p.eco_score})\n"
            response += "\n👉 Visit our Products page to see more!"
            return response
        else:
            return f"😕 Sorry, I couldn't find products matching '{words}'. Try browsing our categories or visit the Products page!"

    def list_categories(self):
        categories = Category.objects.all()
        response = "📂 **Our Categories:**\n\n"
        for cat in categories:
            response += f"• {cat.icon} **{cat.name}** - {cat.products.count()} products\n"
        return response

    def check_orders(self):
        if not self.user or not self.user.is_authenticated:
            return "🔐 Please log in to check your order status!"
        
        orders = Order.objects.filter(user=self.user).order_by('-created_at')[:3]
        
        if orders:
            response = "📦 **Your Recent Orders:**\n\n"
            for order in orders:
                status_emoji = {
                    'pending': '⏳',
                    'processing': '🔄',
                    'shipped': '🚚',
                    'delivered': '✅',
                    'cancelled': '❌'
                }.get(order.status, '📦')
                response += f"• **{order.order_number}** - {status_emoji} {order.get_status_display()} - ${order.total}\n"
            return response
        else:
            return "📦 You don't have any orders yet. Start shopping!"

    def eco_info(self):
        return """🌿 **About EcoScore**

EcoScore rates products from 0-100 based on:

- ♻️ **Materials** - Recycled/sustainable materials
- 🏭 **Production** - Eco-friendly manufacturing
- 📦 **Packaging** - Minimal/biodegradable packaging
- 🚚 **Transport** - Carbon footprint

**Score Guide:**
- 🟢 90-100: Excellent - Top eco choice!
- 🟢 80-89: Very Good
- 🟡 70-79: Good
- 🟠 60-69: Fair
- 🔴 Below 60: Needs improvement

Shop high EcoScore products to earn more Eco Points! 🌱"""

    def shipping_info(self):
        return """🚚 **Shipping Information**

- **Free Shipping**: Orders over $50
- **Standard Shipping**: $5.00 (3-5 business days)
- **Express Shipping**: $12.00 (1-2 business days)

📍 We ship to all locations in Canada and USA!

🌱 We use eco-friendly packaging materials."""

    def return_policy(self):
        return """↩️ **Return Policy**

- **30-day returns** on all products
- Items must be unused and in original packaging
- Free returns on defective items

**How to Return:**
1. Go to Order History
2. Select the order
3. Click "Request Return"
4. Print the return label

Need help? Contact our support team!"""

    def payment_info(self):
        return """💳 **Payment Methods**

We accept:
- 💳 Credit/Debit Cards (Visa, Mastercard, Amex)
- 💵 Cash on Delivery (COD)
- 🏦 Bank Transfer

🔒 All payments are secure and encrypted!"""

    def contact_info(self):
        return """📞 **Contact Us**

- 📧 Email: support@ecoshop.com
- 📱 Phone: +1-555-ECO-SHOP
- 💬 Live Chat: Available 9 AM - 6 PM EST

📍 Address:
EcoShop Headquarters
123 Green Street
Windsor, ON N9A 1A1
Canada

We typically respond within 24 hours! 🌿"""

    def default_response(self):
        return """🤔 I'm not sure I understand. Here's what I can help with:

- 🛍️ "Find products" - Search for items
- 📂 "Show categories" - Browse categories  
- 📦 "My orders" - Check order status
- 🌿 "What is eco score?" - Learn about EcoScore
- 🚚 "Shipping info" - Delivery options
- 💳 "Payment methods" - How to pay
- 📞 "Contact support" - Get in touch

Try asking one of these! 😊"""