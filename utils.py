import datetime
import os

class Logger:
    def __init__(self, log_file='scraping.log'):
        self.log_file = log_file
        
    def log(self, message, level='normal'):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Define log level prefixes
        level_prefixes = {
            'normal': '[INFO]',
            'warning': '[WARNING]',
            'error': '[ERROR]',
            'success': '[SUCCESS]'
        }
        
        prefix = level_prefixes.get(level, '[INFO]')
        log_message = f"{timestamp} {prefix} {message}"
        
        # Print to console
        print(log_message)
        
        # Write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}")

# Create global logger instance
logger = Logger()