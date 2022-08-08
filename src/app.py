from bot import bot
from webserver import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
    bot.run()
