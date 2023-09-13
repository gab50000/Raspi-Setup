curl -X POST -d chat_id={{ telegram_user_id }} --data-urlencode "text=$(cat)" https://api.telegram.org/bot{{ telegram_api_token }}/sendMessage
