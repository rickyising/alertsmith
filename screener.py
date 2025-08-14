from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from pinpylib.data.market_data.us.reader import USDBReader
import datetime as dt
import logging
import smtplib
from email.message import EmailMessage

class Screener:
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

    def extract_tickers(self, df):
        cols = df.columns
        if hasattr(cols, 'levels') and len(cols.levels) > 1:
            # Assuming stock ticker is the second level
            return set(cols.get_level_values(1))
        else:
            return set(cols)

    def screen(self, start_date, end_date):
        # TODO: Modify screening logic here

        return self.reader.get_daily_data(
            ['price_last'],
            start_date,
            end_date,
            adjustments={'capital_change':True}
        )

    def get_index_members(self, index_name, start_date, end_date):
        return self.reader.get_index_data(
            index_name,
            start_date,
            end_date
        )

    def get_intersection(self, df1, df2):
        tickers_1 = self.extract_tickers(df1)
        tickers_2 = self.extract_tickers(df2)
        return tickers_1.intersection(tickers_2)

    def send_email(self, subject, body):
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        recipient = os.getenv('EMAIL_RECIPIENT')
        sender = os.getenv('EMAIL_SENDER', smtp_user)

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    def run(self):
        start_date = dt.datetime(2022, 12, 31)
        end_date = dt.datetime(2024, 1, 31)
        screening_results = self.screen(start_date, end_date)
        index_members = self.get_index_members('SPX', start_date, end_date)
        intersection = self.get_intersection(screening_results, index_members)

        self.logger.info(f"Result: {intersection}")
        self.logger.info(f"Result count: {len(intersection)}")
        today_str = dt.date.today().isoformat()
        subject = f"Screener Results - {today_str}"
        body = f"Result count: {len(intersection)}\n\n" + "\n".join(str(ticker) for ticker in intersection)
        self.send_email(subject, body)

if __name__ == "__main__":
    screener = Screener()
    screener.run()