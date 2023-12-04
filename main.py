import io
from chessdotcom import get_player_games_by_month, Client
import chess.pgn
import pandas as pd
import streamlit as st
import datetime as dt
from dateutil.rrule import rrule, MONTHLY
import csv

period = [2023, 4, 12]
player = "macspacs"
openingsurl = "https://www.chess.com/openings/"

game_headers = ['Event', 'Site', 'Date', 'Round', 'White',
                'Black', 'Result', 'CurrentPosition', 'Timezone',
                'ECO', 'ECOUrl', 'UTCDate', 'UTCTime', 'WhiteElo',
                'BlackElo', 'TimeControl', 'Termination', 'StartTime',
                'EndDate', 'EndTime', 'Link']

df = pd.DataFrame(columns=game_headers)

eco_dict = {}


def parseChessdotcom(start_date, end_date):
    # Generating a monthly date range
    date_range = rrule(MONTHLY, dtstart=start_date, until=end_date)

    # Iterating over the date range
    parse_date_range = []
    for d in date_range:
        parse_date_range.append([d.strftime('%Y'), d.strftime('%m')])

    Client.request_config["headers"]["User-Agent"] = (
        "My Python Application. "
        "Contact me at email@example.com"
    )

    # Month iteration
    for year, month in parse_date_range:
        games = get_player_games_by_month(player, year, month).json['games']
        for i in range(0, (len(games) - 1)):
            row = []
            pgn = io.StringIO(games[i]['pgn'])
            curr_game = chess.pgn.read_game(pgn)
            for y in game_headers:
                try:
                    row.append(curr_game.headers[y])
                except:
                    row.append("ND")
            df.loc[len(df)] = row


def createStatDF():
    # Define color played by user
    df["User played"] = ""

    # Explicit user ELO
    df["User ELO"] = ""

    # User result
    df["User result"] = ""

    df["Chessdotcom Opening Desc"] = ""

    df["Opening"] = ""

    for i in range(len(df)):
        # White
        if df.loc[i, "White"] == player:
            df.loc[i, "User played"] = "White"
            df.loc[i, "User ELO"] = df.loc[i, "WhiteElo"]

            if df.loc[i, "Result"] == "1-0":
                df.loc[i, "User result"] = "Won"
            if df.loc[i, "Result"] == "0-1":
                df.loc[i, "User result"] = "Lost"
            if df.loc[i, "Result"] == "1/2-1/2":
                df.loc[i, "User result"] = "Draw"

        # Black
        if df.loc[i, "Black"] == player:
            df.loc[i, "User played"] = "Black"
            df.loc[i, "User ELO"] = df.loc[i, "BlackElo"]

            if df.loc[i, "Result"] == "0-1":
                df.loc[i, "User result"] = "Won"
            if df.loc[i, "Result"] == "1-0":
                df.loc[i, "User result"] = "Lost"
            if df.loc[i, "Result"] == "1/2-1/2":
                df.loc[i, "User result"] = "Draw"

        if openingsurl in df.loc[i, "ECOUrl"]:
            df.loc[i, "Chessdotcom Opening Desc"] = df.loc[i, "ECOUrl"].replace(openingsurl, "")
            df.loc[i, "Chessdotcom Opening Desc"] = df.loc[i, "Chessdotcom Opening Desc"].replace("-", " ")

        if df.loc[i, "ECO"] != "":
            df.loc[i, "Opening"] = eco_dict[df.loc[i, "ECO"]]

    df[['User ELO']] = df[['User ELO']].apply(pd.to_numeric)


def writeXSLX():
    df.to_excel('output.xlsx', index=False)


def eco_csv():
    global eco_dict

    # read csv file
    with open('ECO.csv', 'r') as file:
        csv_reader = csv.reader(file, delimiter=";")
        for row in csv_reader:
            eco_dict[row[0]] = row[1]


def main():
    eco_csv()

    # createStatDF()
    # writeXSLX()

    with st.sidebar:
        st.image('chessdotcomlogo.png', caption='Chess.com')

        start_date = st.date_input(
            "From",
            dt.date.today() - dt.timedelta(days=31),
            key="key_from",
            format="DD.MM.YYYY"
        )

        end_date = st.date_input(
            "To",
            "today",
            key="key_to",
            format="DD.MM.YYYY"
        )

        if st.button("Parse Chess.com"):
            parseChessdotcom(start_date, end_date)
            createStatDF()

        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            global df
            df = pd.read_excel(uploaded_file, index_col=None)
            createStatDF()

    st.write("### Chess stats")
    st.dataframe(df)


if __name__ == "__main__":
    main()
