import socket
from datetime import datetime


SERVER_IP = "127.0.0.1"
PORT = 5003


#connect server
client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print("Connection failed:", e)
    exit()


#save 
def save_activity(action, result):

    with open(
        "client_activity.txt", "a") as file:

        time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        file.write(
            time + " | " +
            action + " | " +
            result.replace("\n", " ") +
            "\n"
        )


print("1. Admin")
print("2. Employee")
print("3. Guest")

role_choice = input("Choose Role: ")
roles = {"1": "Admin", "2": "Employee", "3": "Guest"}
role = roles.get(role_choice, "Guest")


# قائمة العمليات
while True:

    print("\n1. View All Rooms")
    print("2. Search Room")
    print("3. Book Room")
    print("4. Checkout Room")
    print("5. Generate Report (Admin)")
    print("6. Check System (Admin)")
    print("7. Exit")

    choice = input("Choose Option [1-7]: ")


    # VIEW ALL
    if choice == "1":

        request = "VIEW|" + role

        action = "View All Rooms"


    # SEARCH
    elif choice == "2":

        room_id = input("Room Number: ")

        request = "SEARCH|" + room_id + "|" + role

        action = "Search Room " + room_id


    # BOOK
    elif choice == "3":

        room_id = input("Room Number: ")
        
        check_req = "SEARCH|" + room_id + "|" + role
        client.send(check_req.encode())
        check_res = client.recv(4096).decode()
        
        if "Status: Booked" in check_res:
            print("\nAlert: This room is already booked! Please choose another room.")
            save_activity("Pre-check Room " + room_id, "Alert: Room already booked")
            continue
        elif "Room not found" in check_res:
            print("\nError: Room not found.")
            continue

        name = input("Guest Name: ")
        email = input("Email: ")
        phone = input("Phone: ")

        request = "BOOK|" + room_id + "|" + name + "|" + email + "|" + phone + "|" + role

        action = "Book Room " + room_id


    # CHECKOUT
    elif choice == "4":

        room_id = input("Room Number to Checkout: ")

        request = "CHECKOUT|" + room_id + "|" + role

        action = "Checkout Room " + room_id


    # REPORT
    elif choice == "5":

        request = "REPORT|" + role

        action = "Generate Report"


    # SYS
    elif choice == "6":

        request = "SYS|" + role

        action = "Check System Processes"


    # EXIT
    elif choice == "7":

        client.send("EXIT".encode())

        save_activity("Exit", "Program closed")

        break

    else:
        print("Invalid choice")
        continue


    #send 
    client.send(request.encode())

    #recc result 
    result = client.recv(4096).decode()

    print("\n" + result)

    # log 
    save_activity(action, result)


client.close()
