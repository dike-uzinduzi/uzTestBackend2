from django.http import HttpResponse
from django.urls import reverse

def home(request):
    """
    This view serves as the main entry point and navigation hub for the entire API.
    It dynamically generates links to all major app sections.
    """
    # --- Define all your application links in one place ---
    app_links = [
        # Admin and Core User Management
        {"name": "Admin Panel", "url": reverse('admin:index'), "category": "Admin"},
        {"name": "User Registration & Management (Djoser)", "url": "/api/users/", "category": "Users"},
        {"name": "User Login (JWT)", "url": "/api/jwt/create/", "category": "Users"},
        {"name": "Update User Profile", "url": "/api/profile/update/", "category": "Users"},
        {"name": "Social Authentication (Google, etc.)", "url": "/api/o/google-oauth2/", "category": "Users"},
        
        # Albums App
        {"name": "All Albums", "url": "/api/albums/albums/", "category": "Albums"},
        {"name": "Latest Albums", "url": "/api/albums/latest-albums/", "category": "Albums"},
        {"name": "All Tracks", "url": "/api/albums/tracks/", "category": "Albums"},
        {"name": "My Plaques", "url": "/api/albums/my-plaques/", "category": "Albums"},

        # Payments App
        {"name": "My Payments", "url": "/api/payments/user/", "category": "Payments"},
        {"name": "Create Seamless Payment", "url": "/api/payments/seamless/", "category": "Payments"},
        {"name": "Create Cash Payment", "url": "/api/payments/cash/", "category": "Payments"},
        
        # Notifications App
        {"name": "My Notifications", "url": "/api/notifications/list/", "category": "Notifications"},
    ]

    # --- Group links by category for a more organized layout ---
    categorized_links = {}
    for link in app_links:
        category = link["category"]
        if category not in categorized_links:
            categorized_links[category] = []
        categorized_links[category].append(f'<li><a href="{link["url"]}">{link["name"]}</a></li>')

    # --- Generate the final HTML for the link sections ---
    sections_html = ""
    for category, links in categorized_links.items():
        links_html = "".join(links)
        sections_html += f"""
            <div class="category-section">
                <h2>{category}</h2>
                <ul>{links_html}</ul>
            </div>
        """

    # --- Full HTML Page Template ---
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Uzinduzi Africa API Hub</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                justify-content: center;
                align-items: flex-start; /* Align to top */
                min-height: 100vh;
                margin: 0;
                padding: 40px 20px;
                box-sizing: border-box;
            }}
            .container {{
                text-align: left;
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.08);
                width: 100%;
                max-width: 800px;
            }}
            h1 {{
                color: #1c1e21;
                text-align: center;
                margin-top: 0;
            }}
            p {{
                color: #606770;
                text-align: center;
                margin-bottom: 40px;
                font-size: 1.1em;
            }}
            .category-section {{
                margin-bottom: 30px;
            }}
            .category-section h2 {{
                color: #2b6cb0;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            li {{
                margin-bottom: 12px;
            }}
            a {{
                display: block;
                padding: 14px 20px;
                background-color: #f0f2f5;
                color: #333;
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.2s ease;
                font-weight: 500;
            }}
            a:hover {{
                background-color: #e4e6eb;
                transform: translateX(5px);
                color: #000;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Uzinduzi Africa API</h1>
            <p>This is the central hub for all available API endpoints.</p>
            {sections_html}
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)