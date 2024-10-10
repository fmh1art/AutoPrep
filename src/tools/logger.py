import logging
from logging.handlers import RotatingFileHandler
import os
from global_values import debug, cut_log

class Logger:
    def __init__(self, name, level=logging.DEBUG, log_file="app.log", root='./'):
        """Initialize the logger with a specific name and level."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.log_file = log_file
        self.formatter = logging.Formatter('---------------------------- %(asctime)s - %(name)s - %(levelname)s ---------------------------- \n%(message)s')
        self.root = root
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.FIRST_N_LINES = 2
        self.LAST_N_LINES = 10
        self.MAX_LINES = self.FIRST_N_LINES + self.LAST_N_LINES
        self.log_silent = False

        os.makedirs(self.root, exist_ok=True)

        # Check if handlers are already configured
        if not self.logger.handlers:  # Only add handlers if they are not already configured
            # Create file handler for rotating logs
            file_handler = RotatingFileHandler(os.path.join(self.root, self.log_file), maxBytes=1024*1024*5, backupCount=5, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(self.formatter)

            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(self.formatter)

            # Add both handlers to the logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """Return the configured logger."""
        return self.logger
    
    def cut_last_tbl(self, msg):
        
        lines = msg.split('\n')
        last_beg, last_end = -1, -1
        for i, line in enumerate(lines):
            if line.strip() == '/*':
                last_beg = i
            if line.strip() == '*/':
                last_end = i
        
        if last_beg >= last_end:
            return msg
        
        # cut the table, only keep the first 1 lines and last 1 lines
        new_prompt = '\n'.join(lines[:last_beg+4] + ['......'] + lines[last_end-1:])

        return new_prompt
    
    def log_message(self, level='debug', msg='', line_limit=cut_log):
        if not debug or self.log_silent:
            return
        lines = str(msg).split('\n')    
        if line_limit and self.MAX_LINES>0 and len(lines) > self.MAX_LINES:
            msg = self.cut_last_tbl(msg = str(msg))
            lines = msg.split('\n')    
            lines = lines[:self.FIRST_N_LINES] + ['......'] + lines[-self.LAST_N_LINES:]
            msg = '\n'.join(lines)
        
        if level == 'debug':
            self.logger.debug(msg=msg)
        elif level == 'info':
            self.logger.info(msg)
        elif level == 'warning':
            self.logger.warning(msg)
        elif level == 'error':
            self.logger.error(msg=msg)
        elif level == 'critical':
            self.logger.critical(msg)
