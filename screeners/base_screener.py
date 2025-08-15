from dotenv import load_dotenv
import os
import logging
from sqlalchemy import create_engine
from pinpylib.data.market_data.us.reader import USDBReader
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from alerts.email_sender import EmailSender

class BaseScreener:
    def __init__(self):
        load_dotenv()
        db_url = (
            "postgresql://{user}:{pw}@{host}/{db}".format(
                user=os.getenv("DB_USERNAME"),
                pw=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                db=os.getenv("DB_DATABASE")
            )
        )
        engine = create_engine(db_url)
        self.reader = USDBReader(engine)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='screener.log',
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)
        self.email_sender = EmailSender()