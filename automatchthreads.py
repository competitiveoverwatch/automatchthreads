from modules.thread_manager import ThreadManager
from modules.interface import Interface

thread_manager = ThreadManager()
thread_manager.start()

interface = Interface()
interface.start()

thread_manager.join()
interface.join()