# pytelebot (Python Telegram Bot)
# Copyright (C) 2020  Angel Perez <drlorente97@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# General Declarations
import sys
from curses import wrapper
import threading
import signalHandler
import logger
import dbEngine
import gInterface
import telegramInterface
import messageEngine
import time


# Main code
def main(screen):
	# Draw main window
	mainWindow = gInterface.intro()
	mainWindow.build()
	mainWindow.border()
	mainWindow.write('pytelebot: Telegram Bot Deployed in Python', y=1, x=1)
	mainWindow.write('By drlorente97', y=2, x=1)
	mainWindow.refresh()

	# Draw log window
	logBox = gInterface.logbox()
	logBox.build()
	logBox.scroll_on()

	# Init Log Handler
	log = logger.Log(logBox)

	# Init Signal Handler
	sig = signalHandler.signalHandler(log)

	# Init Database Engine
	db = dbEngine.dbEngine(log)

	# Init Telegram Interface
	teleInt = telegramInterface.telegramInterface(log, sig.start_shutdown)

	# Define worker
	def messageEngine_worker(teleInt, log, num):
		worker = messageEngine.messageEngine(teleInt, num)

	# Define worker threads amount
	workerAmount = 1

	# Set up Message Engine Threads
	worker_threads = []
	i = 0
	while i < workerAmount:
		worker_threads.append(threading.Thread(target=messageEngine_worker, name=str(i+1), args=(teleInt, log, str(i+1))))
		i += 1

	# Start threads
	try:
		for thread in worker_threads:
			thread.start()
			time.sleep(0.1)
		while True:
                        # Watchdog
			if sig.start_shutdown.is_set():
				break
			# Scroll log window
			log.logbox.read_key()
	except:
		log.error('Bot has been crash :(')
		sig.start_shutdown.set()
	finally:
		for thread in worker_threads:
			thread.join()
			name = thread.getName()
			log.warning(f"Message engine thread {name} is stoped")
		log.warning("Telebot stoped, have a nice day :)")
		# Exit curses environment

		gInterface.terminate()
		sys.exit(0)

if __name__ == '__main__':
	# Launch wrapper on main
	wrapper(main)
