# A simple smtp server to send birthday reminders to users
# pylint: disable=missing-docstring, invalid-name, redefined-outer-name

from datetime import datetime
import socket
import base64
import json
import os

HOST = "localhost"
PORT = 1025
BUFFER = 1024

C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_BLUE = "\033[94m"
C_ORANGE = "\033[93m"
C_RESET = "\033[0m"

# The timeframe to check for birthdays in
TIMEFRAME = 16 #days

# Email data
SENDER = "bdayreminder@localhost"
RECIPIENT = "forgetful@localhost"
SUBJECT = "Birthday Reminder 🎉 " + datetime.now().strftime("%d/%m/%Y")

# Optional authentication
USERNAME = base64.b64encode(SENDER.encode()).decode()
PASSWORD = base64.b64encode("YourPassw0rd1H3re".encode()).decode()
USERNAME = ""
PASSWORD = ""

def readDates():
    res = []
    if not os.path.exists("dates.txt"):
        print(f"{C_RED}dates.txt not found{C_RESET}")

    with open("dates.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            date = line.split()[0]
            name = " ".join(line.split()[1:])
            date = date.split("/")
            res.append({
                "d": int(date[0]),
                "m": int(date[1]),
                "e": name
            })

    return res

def withinTime(day1, day2, timeframe):
    try:
        d1 = datetime.strptime(day1, '%d/%m/%Y')
        d2 = datetime.strptime(day2, '%d/%m/%Y')
        diff = (d1 - d2).days
        return abs(diff) <= timeframe and diff >= 0

    except: # pylint: disable=bare-except
        return False

def constructBody(dates):
    body = f"Hi there,\n\nHere are the birthdays coming up in the next {TIMEFRAME} days:\n\n"

    for date in dates:
        body += f"{date['d']}/{date['m']} - {date['e']}\n"

    body += "\nHave a great day!"

    return body

def sendEmail(dates):
    body = constructBody(dates)

    msg = f"From: {SENDER}\r\nTo: {RECIPIENT}\r\nSubject: {SUBJECT}\r\n\r\n{body}\r\n."

    endmsg = "\r\n.\r\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))

        print(client.recv(1024).decode(), end="")

        convo = [ "HELO BDay Reminder\r\n" ]

        # Optional authentication
        if USERNAME != "" and PASSWORD != "":
            convo += [
                "AUTH LOGIN\r\n",
                (USERNAME + "\r\n"),
                (PASSWORD + "\r\n")
            ]

        convo += [
            f"MAIL FROM:<{SENDER}>\r\n",
            f"RCPT TO:<{RECIPIENT}>\r\n",
            "DATA\r\n",
            (msg + endmsg),
            "QUIT\r\n"
        ]

        # Manifest conversation
        for x in convo:
            client.send(x.encode())
            print(client.recv(1024).decode(), end="")

if __name__ == "__main__":
    dates = readDates()

    # Check for birthdays within TIMEFRAME
    dates = list(filter(
        lambda x: withinTime(
            f"{x['d']}/{x['m']}/{datetime.now().year}",
            datetime.now().strftime("%d/%m/%Y"),
            TIMEFRAME
        ),
        dates
    ))

    print("Today is", C_BLUE, datetime.now().strftime("%d/%m/%Y"), C_RESET)

    if len(dates) == 0:
        print(f"{C_GREEN}No birthdays found{C_RESET}")
    else:
        print(f"Found birthdays in {TIMEFRAME} days:", C_GREEN)
        print("\n".join([f"{d['d']}/{d['m']}\t- {d['e']}" for d in dates]))
        print(C_RESET)

        print(f"{C_BLUE}Sending email...{C_RESET}")

        sendEmail(dates)

        print(C_ORANGE, "="*50, C_RED)
        print(" "*20, "All done!")
        print(C_ORANGE, "="*50, C_RESET)
