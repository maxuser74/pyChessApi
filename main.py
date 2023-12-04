import io
from chessdotcom import get_player_games_by_month, Client
import chess.pgn
import pandas as pd
from tabulate import tabulate
import streamlit as st

period = [2023,4,12]
player="macspacs"
openingsurl = "https://www.chess.com/openings/"

game_headers = ['Event', 'Site', 'Date', 'Round', 'White',
                'Black', 'Result', 'CurrentPosition', 'Timezone',
                'ECO', 'ECOUrl', 'UTCDate', 'UTCTime', 'WhiteElo',
                'BlackElo', 'TimeControl', 'Termination', 'StartTime',
                'EndDate', 'EndTime', 'Link']

df = pd.DataFrame(columns=game_headers)

def parseChessdotcom():
    Client.request_config["headers"]["User-Agent"] = (
        "My Python Application. "
        "Contact me at email@example.com"
    )

    # Month iteration
    for month in range(period[1],period[2]+1):
        games = get_player_games_by_month(player,period[0],month).json['games']
        for i in range(0,(len(games)-1)):
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

    # Excplicit user ELO
    df["User ELO"] = ""

    # User result
    df["User result"] = ""

    df["Chessdotcom Opening Desc"] = ""

    for i in range(len(df)):
        # White
        if(df.loc[i, "White"]==player):
            df.loc[i, "User played"] = "White"
            df.loc[i, "User ELO"] = df.loc[i, "WhiteElo"]

            if(df.loc[i, "Result"]=="1-0"):
                df.loc[i, "User result"] = "Won"
            if (df.loc[i, "Result"] == "0-1"):
                df.loc[i, "User result"] = "Lost"
            if (df.loc[i, "Result"] == "1/2-1/2"):
                df.loc[i, "User result"] = "Draw"

        # Black
        if(df.loc[i, "Black"]==player):
            df.loc[i, "User played"] = "Black"
            df.loc[i, "User ELO"] = df.loc[i, "BlackElo"]

            if (df.loc[i, "Result"] == "0-1"):
                df.loc[i, "User result"] = "Won"
            if (df.loc[i, "Result"] == "1-0"):
                df.loc[i, "User result"] = "Lost"
            if (df.loc[i, "Result"] == "1/2-1/2"):
                df.loc[i, "User result"] = "Draw"

        if openingsurl in df.loc[i, "ECOUrl"]:
            df.loc[i, "Chessdotcom Opening Desc"] = df.loc[i, "ECOUrl"].replace(openingsurl,"")
            df.loc[i, "Chessdotcom Opening Desc"] = df.loc[i, "Chessdotcom Opening Desc"].replace("-", " ")


    df[['User ELO']] = df[['User ELO']].apply(pd.to_numeric)

def writeXSLX():
    df.to_excel('output.xlsx', index=False)

def main():
    df = None

    #parseChessdotcom()
    #createStatDF()
    #writeXSLX()

    with st.sidebar:
        st.write("This code will be printed to the sidebar.")
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file, index_col=None)

    if df is not None:
        st.write("### Chess stats", df.head().sort_index())
        st.write("### Chess stats", df.tail().sort_index())


if __name__ == "__main__":
    main()