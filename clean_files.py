import os

if __name__ == '__main__':
    try:
        os.remove('docker_volume/app.log')
    except FileNotFoundError:
        pass

    try:
        os.remove('docker_volume/redis_tasks.log')
    except FileNotFoundError:
        pass