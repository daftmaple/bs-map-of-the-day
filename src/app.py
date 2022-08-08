import multiprocessing

def run_app():
    from webserver import app
    app.run(debug=False, host='0.0.0.0', port=5000)

def run_bot():
    from bot import bot
    bot.run()

proc1 = multiprocessing.Process(target=run_app)
proc2 = multiprocessing.Process(target=run_bot)

proc1.start()
proc2.start()

proc1.join()
proc2.join()

print("Exiting process")
