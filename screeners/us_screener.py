from base_screener import BaseScreener
import datetime as dt

class USScreener(BaseScreener):
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

    def extract_tickers(self, df):
        cols = df.columns
        if hasattr(cols, 'levels') and len(cols.levels) > 1:
            # Assuming stock ticker is the second level
            return set(cols.get_level_values(1))
        else:
            return set(cols)

    def get_intersection(self, df1, df2):
        tickers_1 = self.extract_tickers(df1)
        tickers_2 = self.extract_tickers(df2)
        return tickers_1.intersection(tickers_2)

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
        self.email_sender.send_email(subject, body)

if __name__ == "__main__":
    screener = USScreener()
    screener.run()