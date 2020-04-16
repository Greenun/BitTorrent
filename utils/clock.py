import time
import logging

# for test code
class Clock(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__qualname__)

    def clock_execute(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ret_val = func(*args, **kwargs)
            end_time = time.time()

            self.logger.info(f"--- {func.__name__} elapsed time : {int((end_time - start_time) * 1000)} ms")
            return ret_val
        return wrapper
