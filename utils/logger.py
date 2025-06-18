import datetime

def log(content, category):
    if category == 'error':
        suffix = " [-] ERROR - "
    elif category == 'warning':
        suffix = " [!] WARNING - "
    else: 
        suffix = " [+] - "
        pass
    current = str(datetime.datetime.now())
    print(current + suffix + content)