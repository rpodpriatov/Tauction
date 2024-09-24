document.addEventListener('DOMContentLoaded', () => {
    const telegramLoginButton = document.getElementById('telegram-login-button');
    
    if (telegramLoginButton) {
        window.TelegramLoginWidget = {
            dataOnauth: (user) => {
                fetch('/auth/telegram', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(user)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect;
                    } else {
                        alert('Authentication failed. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred during authentication. Please try again.');
                });
            }
        };

        const script = document.createElement('script');
        script.src = 'https://telegram.org/js/telegram-widget.js?22';
        script.setAttribute('data-telegram-login', 'YOUR_BOT_USERNAME');
        script.setAttribute('data-size', 'large');
        script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');
        script.setAttribute('data-request-access', 'write');
        telegramLoginButton.appendChild(script);
    }
});
