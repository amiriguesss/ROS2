<div align="center">

# 🤖 ROS 2 UR5e Gazebo Simulation

**A ROS 2 project for simulating a Universal Robots UR5e robotic arm in Gazebo Classic 11**

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-33254b?logo=ros&logoColor=white)](https://docs.ros.org/en/humble/)
[![Gazebo](https://img.shields.io/badge/Gazebo-Classic%2011-f58113?logo=gazebo&logoColor=white)](https://classic.gazebosim.org/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20LTS-E95420?logo=ubuntu&logoColor=white)](https://releases.ubuntu.com/22.04/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/arch-amd64%20%2F%20x86__64-blue)]()

</div>

---

## ✨ The project includes

| | |
|---|---|
| 🤖 | **UR5e robot simulation** |
| 🌎 | **Custom Gazebo environment** |
| 🎮 | **ROS 2 Control** |
| ⚙️ | **Gazebo ROS 2 integration** |
| 🧩 | **Custom `ur_lab` ROS 2 package** |
| 🚀 | **Custom robot-control nodes** |
| 🏗️ | **Universal Robots Gazebo simulation package** |

---

## 📌 Tested Environment

This project is intended for the following environment:

| Component | Version |
| :--- | :--- |
| **Operating System** | Ubuntu 22.04 LTS |
| **ROS** | ROS 2 Humble |
| **Gazebo** | Gazebo Classic 11 |
| **Python** | 3.10+ |
| **Architecture** | amd64 / x86_64 |
| **Shell** | Bash or Zsh |

> ⚠️ **Important** — This project uses **Gazebo Classic 11** with **ROS 2 Humble**.
> Do not install Gazebo Harmonic or another modern Gazebo release for this project unless you know how to adapt the project to the newer Gazebo stack.

---

## 📑 Table of Contents

- [🚀 How to Simulate the Project](#-how-to-simulate-the-project)
- [📁 Project Structure](#-project-structure)
- [🆕 Fresh Installation](#-fresh-installation)
- [📥 Clone the Project](#-clone-the-project)
- [🔧 Install Project Dependencies](#-install-project-dependencies)
- [🏗️ Build the Workspace](#️-build-the-workspace)
- [🔍 Verify the Build](#-verify-the-build)
- [🧪 Test Gazebo](#-test-gazebo)
- [🤖 Test the Universal Robots Simulation](#-test-the-universal-robots-simulation)
- [🌎 Run the Complete Project](#-run-the-complete-project)
- [🖥️ Recommended Terminal Workflow](#️-recommended-terminal-workflow)
- [🐚 Zsh Configuration](#-zsh-configuration)
- [🧹 Completely Clean and Rebuild](#-completely-clean-and-rebuild)
- [🐛 Troubleshooting](#-troubleshooting)
- [🔄 Updating the Project](#-updating-the-project)
- [⚡ Quick Start](#-quick-start)
- [🧭 Complete Fresh-Install Command Sequence](#-complete-fresh-install-command-sequence)
- [🔗 References](#-references)
- [👨‍💻 Author](#-author)

---

## 🚀 How to Simulate the Project

There are **two ways** to run the simulation, depending on whether you have just downloaded the project or you have already built it before.

### ▶️ Way 1 — First Time (Just Downloaded / Cloned the Project)

If you have just downloaded the project, you **must build the workspace first**.

**1.** Open a terminal, go to the workspace and build it:

```bash
cd ~/Downloads/ros2_ws
colcon build --symlink-install
source /opt/ros/humble/setup.zsh
source install/setup.zsh
```

**2.** Launch the simulation (terminal 1 — keep it running):

```bash
ros2 launch ur_lab sim.launch.py    # terminal 1
```

> ⚠️ **Important** — Wait until Gazebo and all controllers are fully up (about **15 – 20 seconds**) before running the next commands.

**3.** Open a second terminal to watch what the gripper camera sees:

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 run rqt_image_view rqt_image_view /wrist_camera/image_raw    # terminal 2
```

**4.** Open a third terminal and run the scan and pick node:

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 run ur_lab scan_pick
```

The node spawns three cubes (red, blue and yellow — colours are shuffled on every run) in a line on the table, sweeps the arm across the line while the wrist camera classifies the colour of the cube under the gripper, and as soon as it detects the **RED** cube it stops, descends, grasps it and lifts it.

### 🔁 Way 2 — Already Built the Project Before

If you have already built the workspace, you do **NOT** need to run `colcon build` again. You only need to source the environments in every new terminal, then run the same commands.

**Terminal 1** — launch the simulation:

```bash
cd ~/Downloads/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 launch ur_lab sim.launch.py
```

**Terminal 2** — camera view (optional):

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 run rqt_image_view rqt_image_view /wrist_camera/image_raw
```

**Terminal 3** — scan and pick:

```bash
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 run ur_lab scan_pick
```

---

## 💡 Extra Notes

> ❗ The simulation **must already be running** before you start any node that interacts with the robot (`scan_pick`, `pick_cube`, `move_robot`).

> ❗ You **must source both environments** (ROS and the workspace) in **EVERY** new terminal you open.

- If you use **Bash** instead of **Zsh**, replace `setup.zsh` with `setup.bash` in every command.
- Other available demo nodes:

```bash
ros2 run ur_lab move_robot    # moves the arm along a fixed trajectory
ros2 run ur_lab pick_cube     # spawns one cube, grasps and lifts it
```

---
## 📁 Project Structure

After cloning, the workspace should look like:

```text
ros2_ws/
│
├── src/
│   │
│   ├── ur_lab/
│   │   ├── launch/
│   │   │   └── sim.launch.py
│   │   │
│   │   ├── worlds/
│   │   │   └── lab.world
│   │   │
│   │   ├── ur_lab/
│   │   │   ├── add_scene.py
│   │   │   └── move_robot.py
│   │   │
│   │   ├── resource/
│   │   ├── test/
│   │   ├── package.xml
│   │   └── setup.py
│   │
│   └── Universal_Robots_ROS2_Gazebo_Simulation/
│       └── ur_simulation_gazebo/
│           ├── config/
│           ├── launch/
│           ├── test/
│           ├── CMakeLists.txt
│           └── package.xml
│
├── build/
├── install/
└── log/
```

> ℹ️ `build/`, `install/`, and `log/` are generated automatically and should not normally be committed to Git.

---

## 🆕 Fresh Installation

If ROS 2 and Gazebo are **not installed yet**, follow this entire section.

If you already have a working ROS 2 Humble + Gazebo Classic 11 installation, skip to [Clone the Project](#-clone-the-project).

### 1️⃣ Install Ubuntu 22.04

This project is designed for **Ubuntu 22.04 LTS**.

Check your Ubuntu version:

```bash
lsb_release -a
```

Expected output:

```text
Ubuntu 22.04
```

### 2️⃣ Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

### 3️⃣ Install Basic Development Tools

```bash
sudo apt install -y \
    curl \
    git \
    gnupg \
    lsb-release \
    software-properties-common \
    build-essential \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep
```

### 4️⃣ Install ROS 2 Humble

**Add the ROS 2 repository:**

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

Update the package list:

```bash
sudo apt update
```

### 5️⃣ Install ROS 2 Humble Desktop

```bash
sudo apt install -y ros-humble-desktop
```

### 6️⃣ Install ROS Development Tools

```bash
sudo apt install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-argcomplete
```

### 7️⃣ Initialize rosdep

Run:

```bash
sudo rosdep init
```

Then:

```bash
rosdep update
```

If you receive:

```text
ERROR: rosdep sources list file already exists
```

you can safely skip `sudo rosdep init` and simply run `rosdep update`.

### 8️⃣ Configure ROS 2 for Your Shell

**Bash** — if you use Bash:

```bash
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

**Zsh** — if you use Zsh:

```bash
echo 'source /opt/ros/humble/setup.zsh' >> ~/.zshrc
source ~/.zshrc
```

> ℹ️ The rest of this README shows both where necessary. If you use Zsh, use the commands marked **Zsh**.

### 9️⃣ Verify ROS 2

Check:

```bash
echo $ROS_DISTRO
```

Expected output:

```text
humble
```

Check the ROS 2 executable:

```bash
which ros2
```

Expected output:

```text
/opt/ros/humble/bin/ros2
```

Test the ROS 2 CLI:

```bash
ros2
```

You should see the ROS 2 command help.

> ⚠️ `ros2 --version` is **not** a valid ROS 2 version command.

---
### 🔟 Install Gazebo Classic 11

Install Gazebo and the ROS integration:

```bash
sudo apt install -y \
    gazebo \
    libgazebo-dev \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control
```

Verify Gazebo:

```bash
gazebo --version
```

Expected output:

```text
Gazebo multi-robot simulator, version 11.x
```

For example:

```text
Gazebo multi-robot simulator, version 11.10.2
```

### 1️⃣1️⃣ Install ROS 2 Control Packages

Install the packages required by the UR5e simulation:

```bash
sudo apt install -y \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-controller-manager \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2
```

### 1️⃣2️⃣ Optional: Install MoveIt

If you want to use MoveIt with the robot:

```bash
sudo apt install -y ros-humble-moveit
```

> ℹ️ MoveIt is **not** required just to launch the Gazebo simulation.

---

## 📥 Clone the Project

### 1️⃣3️⃣ Create the ROS 2 Workspace

It is recommended to keep the workspace inside the Linux filesystem.

Use:

```bash
mkdir -p ~/ros2_ws/src
```

Then:

```bash
cd ~/ros2_ws
```

> ⚠️ **WSL users** — Avoid placing the workspace under `/mnt/c/Users/...`.
> Prefer `/home/<username>/ros2_ws` instead of `/mnt/c/Users/<username>/ros2_ws`.
> This avoids many filesystem, symlink, and build-performance problems.

### 1️⃣4️⃣ Clone the Repository

From inside `~/ros2_ws`:

```bash
git clone https://github.com/amiriguesss/ROS2.git .
```

Check the repository:

```bash
ls
```

You should see:

```text
src
```

Check the source directory:

```bash
ls src
```

You should have:

```text
ur_lab
Universal_Robots_ROS2_Gazebo_Simulation
```

### 1️⃣5️⃣ Verify the Universal Robots Simulation Package

The project depends on the Universal Robots Gazebo simulation package.

Check:

```bash
find src -maxdepth 3 -name package.xml -print
```

You should see:

```text
src/ur_lab/package.xml
src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo/package.xml
```

The Universal Robots simulation repository should be on the `humble` branch.

Check:

```bash
cd ~/ros2_ws/src/Universal_Robots_ROS2_Gazebo_Simulation
git branch --show-current
```

Expected output:

```text
humble
```

Return to the workspace:

```bash
cd ~/ros2_ws
```

---

## 🔧 Install Project Dependencies

### 1️⃣6️⃣ Source ROS 2

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

### 1️⃣7️⃣ Install All Project Dependencies

From the workspace root:

```bash
cd ~/ros2_ws
```

Run:

```bash
rosdep update
```

Then:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

A successful installation should end with something similar to:

```text
#All required rosdeps installed successfully
```

> ℹ️ If some dependencies are already installed, that is completely fine.

---

## 🏗️ Build the Workspace

### 1️⃣8️⃣ Clean Previous Builds

If this is a fresh clone, this is **optional**.

If you previously built the project or moved the workspace, it is recommended:

```bash
cd ~/ros2_ws
rm -rf build install log
```

> ℹ️ This removes only generated build files. It does **not** remove your source code.

### 1️⃣9️⃣ Build the Project

Source ROS 2 first.

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

Then build:

```bash
cd ~/ros2_ws
colcon build --symlink-install
```

A successful build should finish with something similar to:

```text
Summary: 2 packages finished
```

> ℹ️ The exact number may change if additional packages are added later.

### 2️⃣0️⃣ Source the Workspace

After a successful build:

**Bash:**

```bash
source ~/ros2_ws/install/setup.bash
```

**Zsh:**

```bash
source ~/ros2_ws/install/setup.zsh
```

---
## 🔍 Verify the Build

### 2️⃣1️⃣ Check the ROS Packages

Check the project package:

```bash
ros2 pkg prefix ur_lab
```

Expected output:

```text
/home/<username>/ros2_ws/install/ur_lab
```

Check the Universal Robots simulation:

```bash
ros2 pkg prefix ur_simulation_gazebo
```

Expected output:

```text
/home/<username>/ros2_ws/install/ur_simulation_gazebo
```

You can also list the UR packages:

```bash
ros2 pkg list | grep ur_
```

You should see packages similar to:

```text
ur_calibration
ur_client_library
ur_controllers
ur_dashboard_msgs
ur_description
ur_lab
ur_moveit_config
ur_msgs
ur_robot_driver
ur_simulation_gazebo
```

---

## 🧪 Test Gazebo

Before launching the complete project, make sure Gazebo itself works.

Run:

```bash
gazebo
```

Gazebo Classic should open.

Close it with <kbd>Ctrl</kbd> + <kbd>C</kbd>

---

## 🤖 Test the Universal Robots Simulation

Before running the custom `ur_lab` environment, it is recommended to test the underlying UR simulation.

Make sure ROS and your workspace are sourced.

**Bash:**

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
source ~/ros2_ws/install/setup.zsh
```

Then run:

```bash
ros2 launch ur_simulation_gazebo ur_sim_control.launch.py
```

Gazebo should open with the simulated UR5e.

If this works correctly, the Universal Robots simulation is functioning.

Stop it with <kbd>Ctrl</kbd> + <kbd>C</kbd>

---

## 🌎 Run the Complete Project

Once the basic UR simulation works, launch the actual project.

From the workspace:

```bash
cd ~/ros2_ws
```

Source ROS:

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

Source the workspace:

**Bash:**

```bash
source install/setup.bash
```

**Zsh:**

```bash
source install/setup.zsh
```

Now launch the project:

```bash
ros2 launch ur_lab sim.launch.py
```

---

## 🚀 Main Launch Command

Once everything has been installed and built, the complete project can be started with:

**Bash:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ur_lab sim.launch.py
```

**Zsh:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 launch ur_lab sim.launch.py
```

> ℹ️ This is the **main command** for the project.

---

## 🎮 Running the Custom Nodes

The `ur_lab` package contains custom executable nodes.

List them:

```bash
ros2 pkg executables ur_lab
```

You should see:

```text
ur_lab add_scene
ur_lab move_robot
```

### 🧩 `add_scene`

Run:

```bash
ros2 run ur_lab add_scene
```

### 🦾 `move_robot`

Run:

```bash
ros2 run ur_lab move_robot
```

> ⚠️ The simulation should already be running before starting nodes that interact with the simulated robot.

---
## 🖥️ Recommended Terminal Workflow

A convenient workflow is to use multiple terminals.

**Terminal 1 — Gazebo / Simulation:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh

ros2 launch ur_lab sim.launch.py
```

**Terminal 2 — Robot Node:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh

ros2 run ur_lab move_robot
```

**Terminal 3 — Scene Node:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh

ros2 run ur_lab add_scene
```

> ℹ️ The same commands work with Bash by replacing `.zsh` with `.bash`.

---

## 🐚 Zsh Configuration

If you use Zsh, you can automatically source ROS 2 and the workspace every time you open a terminal.

Run:

```bash
echo 'source /opt/ros/humble/setup.zsh' >> ~/.zshrc
```

Then:

```bash
echo 'source ~/ros2_ws/install/setup.zsh' >> ~/.zshrc
```

Reload your configuration:

```bash
source ~/.zshrc
```

Now you can simply run:

```bash
cd ~/ros2_ws
ros2 launch ur_lab sim.launch.py
```

---

## ⚠️ Important: Workspace Paths

If you previously had the project somewhere else, for example `/mnt/c/Users/Amir/Downloads/ros2_ws`, and moved it to `/home/amir/ros2_ws`, your shell may still contain references to the old workspace.

Check:

```bash
echo $AMENT_PREFIX_PATH
```

and:

```bash
echo $CMAKE_PREFIX_PATH
```

If you see an old path such as `/mnt/c/Users/.../ros2_ws/install`, clean the current shell:

```bash
unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH
```

Then source ROS again:

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

Then source the current workspace:

**Bash:**

```bash
source ~/ros2_ws/install/setup.bash
```

**Zsh:**

```bash
source ~/ros2_ws/install/setup.zsh
```

---

## 🧹 Completely Clean and Rebuild

If the project gets into a broken build state, perform a clean rebuild.

```bash
cd ~/ros2_ws
```

Remove generated files:

```bash
rm -rf build install log
```

Source ROS:

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

Install dependencies again:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

Build:

```bash
colcon build --symlink-install
```

Source the new workspace:

**Bash:**

```bash
source install/setup.bash
```

**Zsh:**

```bash
source install/setup.zsh
```

Verify:

```bash
ros2 pkg prefix ur_lab
```

and:

```bash
ros2 pkg prefix ur_simulation_gazebo
```

---
## 🐛 Troubleshooting

### ❌ `ros2: command not found`

Source ROS 2:

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

Check:

```bash
which ros2
```

Expected output:

```text
/opt/ros/humble/bin/ros2
```

### ❌ `Package 'ur_lab' not found`

Build and source the workspace:

```bash
cd ~/ros2_ws
colcon build --symlink-install
```

Then:

**Bash:**

```bash
source install/setup.bash
```

**Zsh:**

```bash
source install/setup.zsh
```

Then:

```bash
ros2 pkg prefix ur_lab
```

### ❌ `Package 'ur_simulation_gazebo' not found`

First check that the source package exists:

```bash
find ~/ros2_ws/src -name package.xml | grep ur_simulation_gazebo
```

You should have:

```text
~/ros2_ws/src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo/package.xml
```

Check whether `colcon` sees it:

```bash
cd ~/ros2_ws
colcon list
```

You should see:

```text
ur_lab
ur_simulation_gazebo
```

If necessary, clean and rebuild:

```bash
rm -rf build install log
source /opt/ros/humble/setup.zsh
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.zsh
```

### ❌ `gazebo: command not found`

Install Gazebo Classic:

```bash
sudo apt update
sudo apt install -y gazebo libgazebo-dev
```

Then:

```bash
gazebo --version
```

### ❌ Gazebo opens and immediately closes

First test Gazebo without ROS:

```bash
gazebo
```

If Gazebo itself fails, the issue is with the Gazebo/GUI environment rather than this ROS project.

### ❌ Build warnings about old `/mnt/c/...` paths

If you see:

```text
The path '/mnt/c/.../ros2_ws/install/...' in AMENT_PREFIX_PATH doesn't exist
```

your shell is probably still referencing an old workspace.

Run:

```bash
unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH
```

Then:

```bash
source /opt/ros/humble/setup.zsh
```

and:

```bash
source ~/ros2_ws/install/setup.zsh
```

If the warning returns every time you open a new terminal, inspect:

```bash
grep -n "ros2_ws" ~/.zshrc
```

Remove references to the old workspace.

---

## 🔄 Updating the Project

If you already cloned the repository and want the latest version:

```bash
cd ~/ros2_ws
git pull
```

Then rebuild:

```bash
source /opt/ros/humble/setup.zsh
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.zsh
```

Then launch:

```bash
ros2 launch ur_lab sim.launch.py
```

---

## 🛑 Stopping the Simulation

To stop the ROS 2 launch:

<kbd>Ctrl</kbd> + <kbd>C</kbd>

If Gazebo becomes stuck and refuses to close:

```bash
pkill -9 gzserver
pkill -9 gzclient
pkill -9 gazebo
```

Check that no Gazebo processes remain:

```bash
ps aux | grep -E "gzserver|gzclient|gazebo"
```

---

## 📚 Useful Commands

| Command | Description |
| :--- | :--- |
| `ros2 pkg list` | List ROS packages |
| `ros2 pkg list \| grep ur_` | Find UR packages |
| `ros2 pkg executables ur_lab` | List executables |
| `ros2 launch ur_lab` | List available launch files |
| `ros2 pkg prefix ur_lab` | Check a package |
| `ros2 pkg prefix ur_simulation_gazebo` | Check the UR simulation |
| `ros2 node list` | List ROS nodes |
| `ros2 topic list` | List ROS topics |
| `ros2 topic echo <topic_name>` | Inspect a topic |

---

## ⚡ Quick Start

If ROS 2 Humble, Gazebo Classic 11, and all dependencies are already installed, the entire process is:

**Bash:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
ros2 launch ur_lab sim.launch.py
```

**Zsh:**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.zsh
ros2 launch ur_lab sim.launch.py
```

---

## 🧭 Complete Fresh-Install Command Sequence

For someone starting with a clean Ubuntu 22.04 installation, the overall process is:

```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
    curl \
    git \
    gnupg \
    lsb-release \
    software-properties-common \
    build-essential \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep
```

Add ROS:

```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

Install ROS 2:

```bash
sudo apt update
sudo apt install -y ros-humble-desktop
```

Install Gazebo:

```bash
sudo apt install -y \
    gazebo \
    libgazebo-dev \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control
```

Install ROS control dependencies:

```bash
sudo apt install -y \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-controller-manager \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2
```

Initialize rosdep:

```bash
sudo rosdep init
rosdep update
```

Create workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

Clone:

```bash
git clone https://github.com/amiriguesss/ROS2.git .
```

Source ROS:

**Bash:**

```bash
source /opt/ros/humble/setup.bash
```

**Zsh:**

```bash
source /opt/ros/humble/setup.zsh
```

Install dependencies:

```bash
rosdep install --from-paths src --ignore-src -r -y
```

Build:

```bash
colcon build --symlink-install
```

Source workspace:

**Bash:**

```bash
source install/setup.bash
```

**Zsh:**

```bash
source install/setup.zsh
```

Launch:

```bash
ros2 launch ur_lab sim.launch.py
```

---

## 🔗 References

- [ROS 2 Humble](https://docs.ros.org/en/humble/)
- [Gazebo Classic](https://classic.gazebosim.org/)
- [Universal Robots ROS 2 Gazebo Simulation](https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation)
- [Project Repository](https://github.com/amiriguesss/ROS2)

---

## 👨‍💻 Author

**Amir Rasoulzadeh**

[![GitHub](https://img.shields.io/badge/GitHub-amiriguesss-181717?logo=github&logoColor=white)](https://github.com/amiriguesss)
[![Repo](https://img.shields.io/badge/Project-ROS2-181717?logo=github&logoColor=white)](https://github.com/amiriguesss/ROS2)

---

<div align="center">

## ⭐ Support

If this project helped you, please consider giving it a ⭐ on GitHub!

**Made with 🤖 and ROS 2 Humble**

</div>
