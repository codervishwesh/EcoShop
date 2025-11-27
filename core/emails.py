from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.conf import settings
import threading


def send_email_async(subject, plain_message, from_email, recipient_list, html_message):
    """Send email in background thread"""
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email error: {e}")


def send_welcome_email(user):
    """Send welcome email to new users"""
    subject = '🌿 Welcome to EcoShop - Start Your Eco Journey!'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; }}
            .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            .eco-tip {{ background: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌿 Welcome to EcoShop!</h1>
            </div>
            <div class="content">
                <h2>Hi {user.first_name or user.username}! 👋</h2>
                <p>Thank you for joining EcoShop - your trusted marketplace for sustainable and eco-friendly products!</p>
                
                <p>Here's what you can do now:</p>
                <ul>
                    <li>🛍️ Browse our eco-friendly products</li>
                    <li>🌱 Earn Eco Points with every purchase</li>
                    <li>❤️ Save favorites to your Wishlist</li>
                    <li>📦 Track your orders easily</li>
                </ul>
                
                <div class="eco-tip">
                    <strong>🌱 Eco Tip:</strong> Every purchase you make earns Eco Points! The higher the EcoScore of a product, the more points you earn.
                </div>
                
                <center>
                    <a href="#" class="button">Start Shopping 🛒</a>
                </center>
                
                <p>If you have any questions, our support team is always here to help!</p>
                
                <p>Happy Eco Shopping! 🌍</p>
                <p><strong>The EcoShop Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EcoShop. All rights reserved.</p>
                <p>Making the world greener, one purchase at a time. 🌿</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_content)
    
    # Send email in background thread (non-blocking)
    email_thread = threading.Thread(
        target=send_email_async,
        args=(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_content
        )
    )
    email_thread.start()
    
    return True


def send_order_confirmation_email(order):
    """Send order confirmation email"""
    subject = f'🎉 Order Confirmed - {order.order_number}'
    
    # Build order items HTML
    items_html = ""
    for item in order.items.all():
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{item.product_name}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center;">{item.quantity}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${item.product_price}</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right;">${item.subtotal}</td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; }}
            .order-box {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f3f4f6; padding: 10px; text-align: left; }}
            .total-row {{ font-weight: bold; font-size: 18px; }}
            .eco-box {{ background: #d1fae5; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Order Confirmed!</h1>
                <p>Thank you for your purchase</p>
            </div>
            <div class="content">
                <h2>Hi {order.user.first_name or order.user.username}!</h2>
                <p>Great news! Your order has been confirmed and is being processed.</p>
                
                <div class="order-box">
                    <h3>📦 Order Details</h3>
                    <p><strong>Order Number:</strong> {order.order_number}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
                    <p><strong>Status:</strong> {order.get_status_display()}</p>
                </div>
                
                <div class="order-box">
                    <h3>🛒 Order Items</h3>
                    <table>
                        <tr>
                            <th>Product</th>
                            <th style="text-align: center;">Qty</th>
                            <th style="text-align: right;">Price</th>
                            <th style="text-align: right;">Subtotal</th>
                        </tr>
                        {items_html}
                    </table>
                    <hr style="margin: 15px 0;">
                    <table>
                        <tr>
                            <td colspan="3" style="text-align: right; padding: 5px;">Subtotal:</td>
                            <td style="text-align: right; padding: 5px;">${order.subtotal}</td>
                        </tr>
                        <tr>
                            <td colspan="3" style="text-align: right; padding: 5px;">Tax:</td>
                            <td style="text-align: right; padding: 5px;">${order.tax}</td>
                        </tr>
                        <tr>
                            <td colspan="3" style="text-align: right; padding: 5px;">Shipping:</td>
                            <td style="text-align: right; padding: 5px;">{"FREE" if order.shipping_cost == 0 else f"${order.shipping_cost}"}</td>
                        </tr>
                        <tr class="total-row">
                            <td colspan="3" style="text-align: right; padding: 10px; color: #10b981;">Total:</td>
                            <td style="text-align: right; padding: 10px; color: #10b981;">${order.total}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="order-box">
                    <h3>🚚 Shipping Address</h3>
                    <p>{order.shipping_name}<br>
                    {order.shipping_address}<br>
                    {order.shipping_city}, {order.shipping_country} {order.shipping_postal_code}<br>
                    📧 {order.shipping_email}<br>
                    📱 {order.shipping_phone}</p>
                </div>
                
                <div class="eco-box">
                    <h3>🌱 Your Eco Impact</h3>
                    <p><strong>+{order.eco_points_earned} Eco Points Earned!</strong></p>
                    <p>CO₂ Saved: {order.co2_saved}kg</p>
                </div>
                
                <p>We'll send you another email when your order ships!</p>
                
                <p>Thank you for shopping sustainably! 🌍</p>
                <p><strong>The EcoShop Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EcoShop. All rights reserved.</p>
                <p>Questions? Contact us at support@ecoshop.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_content)
    
    # Send email in background thread (non-blocking)
    email_thread = threading.Thread(
        target=send_email_async,
        args=(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            html_content
        )
    )
    email_thread.start()
    
    return True


def send_order_shipped_email(order):
    """Send email when order is shipped"""
    subject = f'🚚 Your Order is On Its Way! - {order.order_number}'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; }}
            .tracking-box {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚚 Your Order Has Shipped!</h1>
            </div>
            <div class="content">
                <h2>Hi {order.user.first_name or order.user.username}!</h2>
                <p>Great news! Your order <strong>{order.order_number}</strong> is on its way to you!</p>
                
                <div class="tracking-box">
                    <h3>📦 Shipping To:</h3>
                    <p>{order.shipping_name}<br>
                    {order.shipping_address}<br>
                    {order.shipping_city}, {order.shipping_country} {order.shipping_postal_code}</p>
                </div>
                
                <p>You can track your order status in your account dashboard.</p>
                
                <p>Thank you for shopping with EcoShop! 🌿</p>
                <p><strong>The EcoShop Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EcoShop. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_content)
    
    # Send email in background thread (non-blocking)
    email_thread = threading.Thread(
        target=send_email_async,
        args=(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            html_content
        )
    )
    email_thread.start()
    
    return True


def send_order_delivered_email(order):
    """Send email when order is delivered"""
    subject = f'✅ Order Delivered - {order.order_number}'
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; }}
            .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Order Delivered!</h1>
            </div>
            <div class="content">
                <h2>Hi {order.user.first_name or order.user.username}!</h2>
                <p>Your order <strong>{order.order_number}</strong> has been delivered!</p>
                
                <p>We hope you love your eco-friendly products! 🌿</p>
                
                <p>If you have a moment, we'd love to hear your feedback. Please leave a review for the products you purchased!</p>
                
                <center>
                    <a href="#" class="button">Leave a Review ⭐</a>
                </center>
                
                <p>Thank you for making a sustainable choice!</p>
                <p><strong>The EcoShop Team</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EcoShop. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_content)
    
    # Send email in background thread (non-blocking)
    email_thread = threading.Thread(
        target=send_email_async,
        args=(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            html_content
        )
    )
    email_thread.start()
    
    return True