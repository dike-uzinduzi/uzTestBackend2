from django.http import HttpResponse

def home(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Welcome to Uzinduzi Africa API</title>
        <style>
            body {
                background-color: #f7fafc;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2d3748;
            }
            p {
                color: #4a5568;
                margin-bottom: 20px;
            }
            a {
                display: inline-block;
                padding: 10px 20px;
                background-color: #2b6cb0;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s ease;
            }
            a:hover {
                background-color: #2c5282;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Uzinduzi Africa API</h1>
            <p>This is for Adminstration Purpose, No unauthorized user.</p>
            <a href="/admin/">Proceed to Admin Panel</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
