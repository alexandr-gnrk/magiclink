import os

from app.main import app 

  
if __name__ == "__main__": 
    app.secret_key = os.getenv('MAGICLINK_KEY')
    app.run()