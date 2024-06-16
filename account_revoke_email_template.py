account_revoke_mail_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333333;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header {
                background-color: #4CAF50;
                color: white;
                text-align: center;
                padding: 10px 0;
            }
            .content {
                padding: 20px;
                text-align: center;
            }
            .button {
                display: inline-block;
                margin: 20px 0;
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            .footer {
                text-align: center;
                color: #777777;
                padding: 10px 0;
                border-top: 1px solid #eeeeee;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Account Deletion Confirmation</h1>
            </div>
            <div class="content">
                <p>Dear {{ first_name }},</p>
                <p>You have requested to delete your account. If you did not initiate this request, please click the following link to revoke the deletion: </p>
                <a href="{{ revocation_link }}" class="button">Revoke Account</a>
                <p>Thanks,<br>PathFinder</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 PathFinder. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """