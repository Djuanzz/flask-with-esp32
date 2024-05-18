from flask import Flask, request, redirect, url_for, Response, render_template, jsonify
from queue import PriorityQueue
import random
import socket


app = Flask(__name__) 

# --- MENGKONEKSIKAN KE ESP32 DENGAN IP DAN PORT YANG SESUAI
IP_ESP32 = "192.168.1.8"  
PORT = 80  

class InitMap:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fx = 0
        self.gx = 0
        self.hx = 0
        self.obstacle = False
        self.neighbors = []

    def __lt__(self, other):
        return self.fx < other.fx
    
    # --- MENENTUKAN OBSTACLE SECARA RANDOM
    def randomObs(self):
        if random.random() < 0.25:
            self.obstacle = True

    # --- MENAMBAHKAN NEIGHBORS PADA SETIAP GRID
    def addNeighbors(self, grids):
        x = self.x
        y = self.y
        if y < box_size - 1:
            self.neighbors.append((grids[x][y + 1], "kanan"))
        if x < box_size - 1:
            self.neighbors.append((grids[x + 1][y], "bawah"))
        if y > 0:
            self.neighbors.append((grids[x][y - 1], "kiri"))
        if x > 0:
            self.neighbors.append((grids[x - 1][y], "atas"))

# --- MENGHITUNG NILAI HEURISTIC
def calcHeuristic(curr, goal):
    heuristic = abs(curr.x - goal.x) + abs(curr.y - goal.y)
    return heuristic

# --- MENJALANKAN ALGORITMA A*
def aStarAlgo(curr, goal, path, visited):
    pq = PriorityQueue()

    startNode = curr
    startNode.gx = 0
    startNode.hx = calcHeuristic(startNode, goal)
    startNode.fx = startNode.gx + startNode.hx
    # --- MEMASUKKAN START NODE KE DALAM PRIORITY QUEUE (FX, START NODE)
    pq.put((0, startNode))
    parent = {}

    while not pq.empty():
        cur_cost, cur_node = pq.get()

        if cur_node == goal:
            while cur_node in parent:
                path.append(cur_node)
                cur_node = parent[cur_node]
            path.append(startNode)
            path.reverse()

            break

        if cur_node in visited:
            continue

        visited.add(cur_node)

        for neighbor, _ in cur_node.neighbors:
            neighbor_node = neighbor
            if neighbor_node not in visited and not neighbor_node.obstacle:
                new_gx = cur_node.gx + 1
                if new_gx < neighbor_node.gx or neighbor_node not in pq.queue:
                    neighbor_node.gx = new_gx
                    neighbor_node.hx = calcHeuristic(neighbor_node, goal)
                    neighbor_node.fx = neighbor_node.gx + neighbor_node.hx
                    # --- MEMASUKKAN NEIGHBOR NODE KE DALAM PRIORITY QUEUE (FX, NEIGHBOR NODE)
                    pq.put((neighbor_node.fx, neighbor_node))
                    # --- MENYIMPAN PARENT DARI NEIGHBOR NODE
                    parent[neighbor_node] = cur_node

# --- MERENDER HALAMAN INDEX.HTML
@app.route("/")
def index():    
    return render_template("index.html")

# --- MENERIMA DATA DARI JAVASCRIPT UNTUK MENGSETUP DATA PADA PYTHON
@app.route('/setup_data', methods=['POST'])
def setup_data():
    # --- INISIASI VARIABEL GLOBAL BOX_SIZE DAN GRID SUPAYA DAPAT DIGUNAKAN PADA FUNGSI LAINNYA
    global box_size 
    global grid 
    data = request.get_json()
    # --- MENDAPATKAN NILAI BOX_SIZE
    box_size = data['box_size']
    # --- MENDAPATKAN DATA GRID
    grid = data['grid'] 

    # --- SETELAH DATA BOX_SIZE DAN GRID DITERIMA, MAKA DATA TERSEBUT AKAN DISETUP PADA PYTHON
    # --- SETUP DILAKUKAN DENGAN CARA MEMBUAT ARRAY 2D DENGAN UKURAN SESUAI DENGAN BOX_SIZE
    grid = [[0 for _ in range(box_size)] for _ in range(box_size)]
    for i in range(box_size):
        for j in range(box_size):
            grid[i][j] = InitMap(i, j)
    print(box_size)

    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA
    return 'Data berhasil diterima'

# --- MERESET DISPLAY GRID, MEMBERSIHAKAN NILAI-NILAI YANG ADA PADA GRID
def clearDisplay():
    for i in range(box_size):
        for j in range(box_size):
            grid[i][j].fx = 0;
            grid[i][j].gx = 0;
            grid[i][j].hx = 0;
            grid[i][j].neighbors = [];
            grid[i][j].obstacle = False;

# --- MENERIMA PERINTAH DARI JAVASCRIPT UNTUK MEMBUAT RANDOM OBSTACLE
@app.route('/random_obs', methods=['POST'])
def random_obs():
    clearDisplay()
    randomnya = []
    for i in range(box_size):
        for j in range(box_size):
            # --- MEMANGGIL FUNGSI RANDOM OBS PADA CLASS InitMap
            grid[i][j].randomObs()
            randomnya.append({"x":i, "y": j, "obs": grid[i][j].obstacle})
    
    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA
    # --- PADA RESPON INI AKAN MENGIRIMKAN DATA RANDOM OBSTACLE DAN NANTINYA GRID YANG TERDAPAT OBSTACLE AKAN DIWARNAI HITAM
    return jsonify({"randomnya": randomnya})

# --- MENERIMA PERINTAH DARI JAVASCRIPT UNTUK MERESET DISPLAY GRID
@app.route('/reset', methods=['POST'])
def reset():
    clearDisplay()

    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA
    return jsonify({"message": "berhasil di reset"})

# --- MENERIMA PERINTAH DARI JAVASCRIPT UNTUK MENENTUKAN PERGERAKAN ROBOT APAKAH MAJU, ROTATE KANAN, ATAU ROTATE KIRI
@app.route('/moveRobot', methods=['POST'])
def move():
    data = request.get_json()
    path = data['path']

    wadahPath = []
    robotPath = []

    # ----- PERINTAH ROBOT
    # 1 -> MAJU
    # 2 -> ROTATE KANAN
    # 3 -> ROTATE KIRI

    # ----- PERINTAH ROTASI ROBOT
    # ----- KANAN - BAWAH ARTINYA JIKA PATH SEBELUMNYA ADALAH KANAN DAN PATH SEKARANG ADALAH BAWAH MAKA PERINTAH ROTASI ADALAH ROTATE KANAN (2)
    rotationMap = {
        "kanan-bawah": 2,
        "kanan-atas": 3,
        "bawah-kanan": 3,
        "bawah-kiri": 2,
        "kiri-bawah": 3,
        "kiri-atas": 2,
        "atas-kiri": 3,
        "atas-kanan": 2,
    }

    # --- MENGUBAH PATH YANG BERUPA KOORDINAT MENJADI PERINTAH ROBOT
    # --- PATH BERISI KOORDINAT GRID
    for i in range(len(path) - 1):
        curDirection = wadahPath[-1] if len(wadahPath) > 0 else None

        if path[i + 1][0] > path[i][0] and path[i + 1][1] == path[i][1]:
            wadahPath.append("bawah")
        elif path[i + 1][0] < path[i][0] and path[i + 1][1] == path[i][1]:
            wadahPath.append("atas")
        elif path[i + 1][0] == path[i][0] and path[i + 1][1] > path[i][1]:
            wadahPath.append("kanan")
        elif path[i + 1][0] == path[i][0] and path[i + 1][1] < path[i][1]:
            wadahPath.append("kiri")

        if curDirection and curDirection != wadahPath[-1]:
            rotationKey = f"{curDirection}-{wadahPath[-1]}"
            rotationCommand = rotationMap.get(rotationKey, None)
            if rotationCommand:
                # --- MENGIRIMKAN PERINTAH ROTASI SESUAI DENGAN ROTATION MAP YANG TELAH DITENTUKAN
                robotPath.append(rotationCommand)

        # --- MENGIRIMKAN PERINTAH MAJU 
        robotPath.append(1)

    print(robotPath)
    print(path)

    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA
    # --- PADA RESPON INI AKAN MENGIRIMKAN DATA PATH ROBOT
    return jsonify({"message": "berhasil di dikirim", "robotPath": robotPath})

# --- MENERIMA PERINTAH DARI JAVASCRIPT UNTUK MENGIRIMKAN PATH ROBOT KE ESP32
@app.route('/send_path', methods=['POST'])
def send_data():
    data = request.get_json()
    dataRobotPath = str(data['dataRobotPath'])

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP_ESP32, PORT))
    client_socket.send(dataRobotPath.encode())

    # --- MENERIMA RESPON DARI ESP32
    response = client_socket.recv(1024).decode()
    # print(dataRobotPath)
    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA
    return jsonify({"message": "berhasil di dikirim", "response": response})

# --- MENERIMA PERINTAH DARI JAVASCRIPT UNTUK MENGHITUNG PATH DENGAN ALGORITMA A*
@app.route('/calculate_path', methods=['POST'])
def calculate_path():
    visited = set()
    path = []

    # --- START NODE DAN GOAL NODE
    start_node = grid[0][0]
    goal_node = grid[box_size - 1][box_size - 1]

    for i in range(box_size):
        for j in range(box_size):
            # --- MENAMBAHKAN NEIGHBORS PADA SETIAP GRID
            grid[i][j].addNeighbors(grid)
            # --- MENGHITUNG NILAI HEURISTIC PADA SETIAP GRID TERHADAP GOAL NODE
            grid[i][j].hx = calcHeuristic(grid[i][j], goal_node)

    # --- MENJALANKAN ALGORITMA A*
    aStarAlgo(start_node, goal_node, path, visited)

    visited = sorted(visited, key=lambda node: node.gx)

    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA 
    # --- PADA RESPON INI AKAN MENGIRIMKAN DATA PATH DAN VISITED
    return jsonify({"size": box_size, "path": [(node.x, node.y) for node in path], "visited": [(node.x, node.y) for node in visited]})


@app.route('/reset-server', methods=['GET'])
def reset_server_route():
    reset_server()
    # --- MEMBERIKAN RESPON KEPADA JAVASCRIPT BAHWA PERINTAH BERHASIL DITERIMA
    return 'Server reset successful!'

def reset_server():
    print("Mereset server...")

# --- MENJALANKAN APLIKASI FLASK PADA HOST DAN PORT YANG TELAH DITENTUKAN
if __name__ == "__main__": 
	app.run(host="127.0.0.1", port=5000, debug=True)
