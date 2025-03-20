import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self):
        # Get email configuration from environment variables
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME', 'spacelogic.info@gmail.com')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'spacelogic.info@gmail.com')
        self.sender_name = os.environ.get('SENDER_NAME', 'SpaceLogic')

        # Check if we're in development mode
        self.is_development = os.environ.get('FLASK_ENV', 'development') == 'development'

    def send_email(self, to_email, subject, html_content, text_content=None):
        """
        Send an email

        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            html_content (str): HTML content of the email
            text_content (str, optional): Plain text content of the email

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # In development mode, just print the email instead of sending it
        if self.is_development and not self.smtp_password:
            print("\n" + "=" * 80)
            print("DEVELOPMENT MODE: Email would be sent with the following content:")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print("-" * 80)
            print(html_content)
            print("=" * 80 + "\n")
            return True

        # If no SMTP password is set, can't send real email
        if not self.smtp_password:
            print("Error: SMTP_PASSWORD environment variable not set")
            return False

        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = to_email

            # Add plain text content if provided, otherwise create from HTML
            if text_content is None:
                # Simple conversion from HTML to text
                text_content = html_content.replace('<br>', '\n').replace('</p><p>', '\n\n')
                # Remove HTML tags
                import re
                text_content = re.sub('<[^<]+?>', '', text_content)

            message.attach(MIMEText(text_content, 'plain'))
            message.attach(MIMEText(html_content, 'html'))

            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_invitation_email(self, invitation, base_url, custom_message=None):
        """
        Send an invitation email

        Args:
            invitation: Invitation object
            base_url (str): Base URL of the application
            custom_message (str, optional): Custom message from the inviter

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        invitation_url = f"{base_url}/invitation/accept/{invitation.token}"

        subject = f"Invitation à rejoindre {invitation.organization_name} sur SpaceLogic"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #3498db; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">SpaceLogic</h1>
                <p style="margin: 5px 0 0 0;">Plateforme de gestion de projets architecturaux</p>
            </div>

            <div style="padding: 20px; background-color: #f8f9fa; border: 1px solid #dee2e6;">
                <h2>Bonjour {invitation.first_name},</h2>

                <p>Vous avez été invité(e) à rejoindre l'organisation <strong>{invitation.organization_name}</strong> sur SpaceLogic.</p>

                {f'<p>Message de linvitant: <em>"{custom_message}"</em></p>' if custom_message else ''}

                <p>Pour accepter cette invitation, veuillez cliquer sur le bouton ci-dessous:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_url}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Accepter l'invitation
                    </a>
                </div>

                <p style="font-size: 0.8em; color: #6c757d;">
                    Si le bouton ne fonctionne pas, vous pouvez copier et coller ce lien dans votre navigateur:<br>
                    <a href="{invitation_url}">{invitation_url}</a>
                </p>

                <p>Cette invitation expirera le {invitation.expires_at.strftime('%d/%m/%Y à %H:%M')}.</p>
            </div>

            <div style="padding: 20px; text-align: center; font-size: 0.8em; color: #6c757d;">
                <p>Ceci est un email automatique, merci de ne pas y répondre.</p>
                <p>&copy; 2025 SpaceLogic. Tous droits réservés.</p>
            </div>
        </div>
        """

        return self.send_email(invitation.email, subject, html_content)


# Create a singleton instance
email_sender = EmailSender()