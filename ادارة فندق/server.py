import socket
import threading
import os
import re
import subprocess
import configparser

try:
    import pandas as pd
except ImportError:
    pd = None

config = configparser.ConfigParser()
config.read('config.ini')

try:
    SERVER_IP = config['Server']['host']
    # نستخدم نفس المنفذ الذي في العميل
    PORT = 5003 
    ROOMS_FILE = config['Paths']['rooms_file']
    GUESTS_EXCEL = config['Paths']['guests_excel']
    REPORTS_DIR = config['Paths']['reports_dir']
except:
    SERVER_IP = "127.0.0.1"
    PORT = 5003
    ROOMS_FILE = "data/rooms.csv"
    GUESTS_EXCEL = "data/guests.xlsx"
    REPORTS_DIR = "reports/"

os.makedirs(os.path.dirname(ROOMS_FILE), exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

if not os.path.exists(ROOMS_FILE):
    with open(ROOMS_FILE, 'w') as f:
        f.write("room_number,type,price,status\n")
        f.write("101,Single,100,Available\n")
        f.write("102,Single,100,Available\n")


def view_all_rooms():
    try:
        with open(ROOMS_FILE, 'r') as f:
            lines = f.readlines()[1:]
            result = ""
            for line in lines:
                data = line.strip().split(',')
                result += f"Room: {data[0]} | Type: {data[1]} | Price: {data[2]} | Status: {data[3]}\n"
            return result.strip() if result else "No rooms available."
    except Exception as e:
        return f"Error: {e}"

def search_room(room_id):
    try:
        with open(ROOMS_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                data = line.strip().split(',')
                if data[0] == room_id:
                    return f"Room: {data[0]} | Type: {data[1]} | Price: {data[2]} | Status: {data[3]}"
        return "Room not found"
    except Exception as e:
        return f"Error: {e}"


def book_room(room_id, name, email, phone):
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return "Error: Invalid Email format"
    if not re.match(r'^\d{9}$', phone):
        return "Error: Phone must be 9 digits"
        
    try:
        with open(ROOMS_FILE, 'r') as f:
            lines = f.readlines()
            
        found = False
        new_lines = [lines[0]]
        
        for line in lines[1:]:
            data = line.strip().split(',')
            if data[0] == room_id:
                if data[3] == "Booked":
                    return "Alert: This room is already booked! Please choose another room."
                data[3] = "Booked"
                found = True
            new_lines.append(",".join(data) + "\n")
            
        if not found:
            return "Error: Room not found"
            
        with open(ROOMS_FILE, 'w') as f:
            f.writelines(new_lines)
            
        # إضافة تفاصيل الحجز إلى ملف الحجوزات الجديد
        bookings_file = os.path.join(os.path.dirname(ROOMS_FILE), "bookings.txt")
        with open(bookings_file, 'a', encoding='utf-8') as bf:
            bf.write(f"Room: {room_id} | Name: {name} | Email: {email} | Phone: {phone}\n")
            
        return f"Success: Room {room_id} booked for {name} ({email})"
    except Exception as e:
        return f"Error: {e}"


def checkout_room(room_id):
    try:
        with open(ROOMS_FILE, 'r') as f:
            lines = f.readlines()
            
        found = False
        new_lines = [lines[0]]
        
        for line in lines[1:]:
            data = line.strip().split(',')
            if data[0] == room_id:
                if data[3] == "Available":
                    return "Alert: This room is already available."
                data[3] = "Available"
                found = True
            new_lines.append(",".join(data) + "\n")
            
        if not found:
            return "Error: Room not found"
            
        with open(ROOMS_FILE, 'w') as f:
            f.writelines(new_lines)
            
        return f"Success: Room {room_id} is now Available."
    except Exception as e:
        return f"Error: {e}"


def generate_report():
    if not pd:
        return "Error: pandas is not installed"
    try:
        df = pd.read_excel(GUESTS_EXCEL)
        total = len(df)
        revenue = df['Total_Spent'].sum()
        
        report_text = f"Total Guests: {total} | Total Revenue: {revenue}"
        with open(os.path.join(REPORTS_DIR, "summary.txt"), 'w') as f:
            f.write(report_text)
            
        return report_text
    except Exception as e:
        return f"Error: {e}"


def get_system():
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        return "\n".join(result.stdout.split('\n')[:5])
    except Exception as e:
        return f"Error: {e}"


# handle
def handle_client(conn, addr):
    
    while True:
        try:
            data = conn.recv(4096).decode()
            
            if not data or data == "EXIT":
                break
                
            parts = data.split("|")
            command = parts[0]
            
            # VIEW ALL
            if command == "VIEW":
                
                result = view_all_rooms()
            
            # SEARCH
            elif command == "SEARCH":
                
                room_id = parts[1]
                role = parts[2]
                
                result = search_room(room_id)
                
                
            # BOOK
            elif command == "BOOK":
                
                room_id = parts[1]
                name = parts[2]
                email = parts[3]
                phone = parts[4]
                role = parts[5]
                
                if role in ["Admin", "Employee"]:
                    result = book_room(room_id, name, email, phone)
                else:
                    result = "Access Denied: You cannot book rooms."
                    
            # CHECKOUT
            elif command == "CHECKOUT":
                
                room_id = parts[1]
                role = parts[2]
                
                if role in ["Admin", "Employee"]:
                    result = checkout_room(room_id)
                else:
                    result = "Access Denied: You cannot checkout rooms."
                    
                    
            # REPORT
            elif command == "REPORT":
                
                role = parts[1]
                
                if role == "Admin":
                    result = generate_report()
                else:
                    result = "Access Denied: Admin only."
                    
                    
            # SYS
            elif command == "SYS":
                
                role = parts[1]
                
                if role == "Admin":
                    result = get_system()
                else:
                    result = "Access Denied: Admin only."
                    
                    
            else:
                result = "Invalid command"
                
                
            # send result
            conn.send(result.encode())
            
        except Exception as e:
            print("Error:", e)
            break
            
    conn.close()


# start
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, PORT))
    server.listen()
    print(f"Server listening on {SERVER_IP}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()
