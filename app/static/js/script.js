let w, h;
// let path = [];
let path = [];
let box_size = 5;
let roboPath = [];
let parent = new Map();
let visited = new Set();
let grid = new Array(box_size);

const run = document.querySelector(".run");
// const edit = document.querySelector(".edit");
const save = document.querySelector(".save");
const send = document.querySelector(".send");
const reset = document.querySelector(".reset");
const random = document.querySelector(".random");

//ubah box_size
const ubah = document.querySelector(".ubah");

// const input_box = document.querySelector(".input-box");
// box_size = input_box.value;
const WHITE = "#ffffff";
const RED = "#ff4f4f";
const GREEN = "#4fff67";
const GREY = "#525252";
const BLUE = "#4f5bff";
const PINK = "#ff4fa7";
const YELLOW = "#f6ff42";

class InitMap {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.fx = 0;
    this.gx = 0;
    this.hx = 0;
    this.obstacle = false;
    this.neighbors = [];
  }

  randomObs() {
    if (Math.random(1) < 0.3) {
      this.obstacle = true;
    }
  }

  addNeighbors(grid) {
    let x = this.x;
    let y = this.y;
    if (y < box_size - 1) this.neighbors.push(grid[x][y + 1], "bawah");
    if (x < box_size - 1) this.neighbors.push(grid[x + 1][y], "kanan");
    if (y > 0) this.neighbors.push(grid[x][y - 1], "atas");
    if (x > 0) this.neighbors.push(grid[x - 1][y], "kiri");
  }
}

async function drawBoxesWithDelay(kotaks, warna) {
  for (let i of kotaks) {
    const boxnya = document.getElementById(`${i[0]}-${i[1]}`);
    // console.log(boxnya);
    boxnya.style.setProperty("background", warna);
    // console.log(boxnya);
    await new Promise((resolve) => setTimeout(resolve, 50)); // Tunggu 1 detik sebelum melanjutkan
  }
}

async function drawOneBoxWithDelay(kotak, warna) {
  const boxnya = document.getElementById(`${kotak[0]}-${kotak[1]}`);
  boxnya.style.setProperty("background", warna);
  await new Promise((resolve) => setTimeout(resolve, 50)); // Tunggu 1 detik sebelum melanjutkan
}

function mengSetup() {
  const board = document.querySelector(".board");
  board.innerHTML = "";
  board.style.setProperty("--size", box_size);

  for (let i = 0; i < box_size; i++) {
    grid[i] = new Array(box_size);
    for (let j = 0; j < box_size; j++) {
      let square = document.createElement("div");
      square.id = i.toString() + "-" + j.toString();
      square.className = "content";
      document.querySelector(".board").append(square);

      grid[i][j] = new InitMap(i, j);
    }
  }
}

function clearDisplay() {
  for (let i = 0; i < box_size; i++) {
    for (let j = 0; j < box_size; j++) {
      let boxnya = document.getElementById(`${i}-${j}`);
      boxnya.style.setProperty("background", WHITE);
    }
  }
}

reset.onclick = () => {
  fetch("/reset", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      clearDisplay();
      const msg = data.message;
      console.log("Random:", msg);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

random.onclick = () => {
  fetch("/random_obs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const randomnya = data.randomnya;
      console.log("Random:", randomnya);

      for (let i = 0; i < randomnya.length; i++) {
        let boxnya = document.getElementById(
          `${randomnya[i].x}-${randomnya[i].y}`
        );
        if (randomnya[i].obs) boxnya.style.setProperty("background", GREY);
        else boxnya.style.setProperty("background", WHITE);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

ubah.onclick = async () => {
  const inputField = document.getElementById("inputField");
  box_size = parseInt(inputField.value);
  console.log("input : " + box_size);
  console.log(box_size);
  mengSetup();
  const dataToSend = {
    box_size: box_size, // Mengirim nilai box_size
    grid: grid, // Mengirim data grid
  };
  console.log(dataToSend);
  await ngirimData(dataToSend);
};

async function ngirimData(dataToSend) {
  fetch("/setup_data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dataToSend),
  })
    .then((response) => {
      if (response.ok) {
        // Data berhasil dikirim
        console.log("Data berhasil dikirim ke Flask.");
      } else {
        // Terjadi kesalahan saat mengirim data
        console.error("Terjadi kesalahan saat mengirim data ke Flask.");
      }
    })
    .catch((error) => {
      console.error("Terjadi kesalahan:", error);
    });
}

async function handleMove(dataRobotPath) {
  try {
    const response = await fetch("/send_path", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        dataRobotPath: dataRobotPath,
      }),
    });

    if (!response.ok) {
      throw new Error("Gagal mengirim permintaan.");
    }

    const data = await response.json();
    // Mendapatkan hasil path dari Flask dan menggunakannya
    const msg = data.message;
    const kondisi = data.response;
    console.log("Received message:", msg);
    console.log("Received kondisi:", kondisi);
    return kondisi;
  } catch (error) {
    console.error("Terjadi kesalahan:", error);
  }
}

async function sendRobot(path) {
  try {
    const response = await fetch("/moveRobot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        path: path,
      }),
    });

    if (!response.ok) {
      throw new Error("Gagal mengirim permintaan.");
    }

    const data = await response.json();

    // Mendapatkan hasil path dari Flask dan menggunakannya
    const msg = data.message;
    roboPath = data.robotPath;

    console.log("Received message:", msg);
    console.log("Received path koordinat:", path);
    console.log("Received robot path:", roboPath);

    let index = 0;
    for (let i of roboPath) {
      // await drawBoxesWithDelay(i, BLUE);
      const kondisi = await handleMove(i);
      if (kondisi == 1) {
        await drawOneBoxWithDelay(path[index], GREEN);
        index++;
      }
    }
    await handleMove(0);
    await drawOneBoxWithDelay(path[path.length - 1], GREEN);
  } catch (error) {
    console.error("Terjadi kesalahan:", error);
  }
}

run.onclick = async () => {
  try {
    // Mengirim data "box_size" ke rute Flask menggunakan fetch
    const response = await fetch("/calculate_path", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        box_size: box_size,
      }),
    });

    if (!response.ok) {
      throw new Error("Gagal mengirim permintaan.");
    }

    const data = await response.json();

    // Mendapatkan hasil path dari Flask dan menggunakannya
    path = data.path;
    const size = data.size;
    const visited = data.visited;
    // const robotPath = data.robotPath;

    console.log("Received path:", path);
    console.log("Received size:", size);
    console.log("Received visited:", visited);

    // await Promise.all([]);
    await drawBoxesWithDelay(visited, RED);
    await drawBoxesWithDelay(path, YELLOW);

    sendRobot(path);

    // Disini Anda dapat melakukan apa pun yang diperlukan dengan hasil path.
  } catch (error) {
    console.error("Terjadi kesalahan:", error);
  }
};

mengSetup();
// // Mendefinisikan data yang akan dikirim
const dataToSend = {
  box_size: box_size, // Mengirim nilai box_size
  grid: grid, // Mengirim data grid
};

console.log(dataToSend);

fetch("/setup_data", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(dataToSend),
})
  .then((response) => {
    if (response.ok) {
      // Data berhasil dikirim
      console.log("Data berhasil dikirim ke Flask.");
    } else {
      // Terjadi kesalahan saat mengirim data
      console.error("Terjadi kesalahan saat mengirim data ke Flask.");
    }
  })
  .catch((error) => {
    console.error("Terjadi kesalahan:", error);
  });
