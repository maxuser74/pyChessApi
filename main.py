import io
from chessdotcom import get_player_games_by_month, Client
import chess.pgn
import pandas as pd
import csv

period = [2023,4,12]
player="macspacs"

info = ["UTCDate", "UTCTime", "Event", "White", "WhiteElo", "Black",
        "BlackElo", "Result","Termination","ECO", "TimeControl", "CurrentPosition"]

def genXSLX():
    eco = {}
    with open('ECO.csv', 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        for row in csv_reader:
            eco[str(row[0])] = [str(row[1]),str(row[2])]

    Client.request_config["headers"]["User-Agent"] = (
        "My Python Application. "
        "Contact me at email@example.com"
    )
    # Month iteration
    df = pd.DataFrame(columns=info)
    df["Opening"] = ""
    df["Moves"] = ""
    df["User played"] = ""
    df["User ELO"] = ""
    df["User result"] = ""

    for month in range(period[1],period[2]+1):
        games = get_player_games_by_month(player,period[0],month).json['games']
        for i in range(0,(len(games)-1)):
            row = []
            pgn = io.StringIO(games[i]['pgn'])
            curr_game = chess.pgn.read_game(pgn)

            for y in info:
                try:
                    row.append(curr_game.headers[y])
                except:
                    row.append("ND")
            try:
                eco_desc = eco[curr_game.headers["ECO"]]
                row.append(eco_desc[0])
                row.append(eco_desc[1])
            except:
                row.append("ND")
                row.append("ND")

            if(row[3]==player):
                row.append("White")
                row.append(row[4]) #User ELO
                if(row[7]=="1-0"):
                    row.append("Won")  # User won
                if(row[7]=="0-1"):
                    row.append("Lost")  # User won
                if(row[7]=="1/2-1/2"):
                    row.append("Draw")  # User won

            else:
                row.append("Black")
                row.append(row[6]) #User ELO
                if(row[7]=="1-0"):
                    row.append("Lost")  # User won
                if(row[7]=="0-1"):
                    row.append("Won")  # User won
                if(row[7]=="1/2-1/2"):
                    row.append("Draw")  # User won


            df.loc[len(df)] = row


    print(df)
    df[['User ELO']] = df[['User ELO']].apply(pd.to_numeric)
    df.to_excel('output.xlsx', index=False)

def main():
    #genXSLX()
    pass

if __name__ == "__main__":
    main()