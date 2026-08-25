🤖 ROS 2 UR5e Gazebo Simulation

A ROS 2 project for simulating a Universal Robots UR5e robotic arm in Gazebo Classic 11.

The project includes:

- 🤖 UR5e robot simulation
- 🌎 Custom Gazebo environment
- 🎮 ROS 2 Control
- ⚙️ Gazebo ROS 2 integration
- 🧩 Custom "ur_lab" ROS 2 package
- 🚀 Custom robot-control nodes
- 🏗️ Universal Robots Gazebo simulation package

---

📌 Tested Environment

This project is intended for the following environment:

Component| Version
Operating System| Ubuntu 22.04 LTS
ROS| ROS 2 Humble
Gazebo| Gazebo Classic 11
Python| 3.10+
Architecture| amd64 / x86_64
Shell| Bash or Zsh

«⚠️ Important: This project uses Gazebo Classic 11 with ROS 2 Humble.

Do not install Gazebo Harmonic or another modern Gazebo release for this project unless you know how to adapt the project to the newer Gazebo stack.»

---

📁 Project Structure

After cloning, the workspace should look like:

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

"build/", "install/", and "log/" are generated automatically and should not normally be committed to Git.

---

🆕 Fresh Installation

If ROS 2 and Gazebo are not installed yet, follow this entire section.

If you already have a working ROS 2 Humble + Gazebo Classic 11 installation, skip to "Clone the Project" (#-clone-the-project).

---

1. Install Ubuntu 22.04

This project is designed for:

Ubuntu 22.04 LTS

Check your Ubuntu version:

lsb_release -a

You should see:

Ubuntu 22.04

---

2. Update Ubuntu

sudo apt update
sudo apt upgrade -y

---

3. Install Basic Development Tools

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

---

4. Install ROS 2 Humble

Add the ROS 2 Repository

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

Update the package list:

sudo apt update

---

5. Install ROS 2 Humble Desktop

sudo apt install -y ros-humble-desktop

---

6. Install ROS Development Tools

sudo apt install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-argcomplete

---

7. Initialize rosdep

Run:

sudo rosdep init

Then:

rosdep update

If you receive:

ERROR: rosdep sources list file already exists

you can safely skip "sudo rosdep init" and simply run:

rosdep update

---

8. Configure ROS 2 for Your Shell

Bash

If you use Bash:

echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc

Zsh

If you use Zsh:

echo 'source /opt/ros/humble/setup.zsh' >> ~/.zshrc
source ~/.zshrc

«The rest of this README shows both where necessary. If you use Zsh, use the commands marked Zsh.»

---

9. Verify ROS 2

Check:

echo $ROS_DISTRO

Expected:

humble

Check the ROS 2 executable:

which ros2

Expected:

/opt/ros/humble/bin/ros2

Test the ROS 2 CLI:

ros2

You should see the ROS 2 command help.

«"ros2 --version" is not a valid ROS 2 version command.»

---

10. Install Gazebo Classic 11

Install Gazebo and the ROS integration:

sudo apt install -y \
    gazebo \
    libgazebo-dev \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control

Verify Gazebo:

gazebo --version

Expected:

Gazebo multi-robot simulator, version 11.x

For example:

Gazebo multi-robot simulator, version 11.10.2

---

11. Install ROS 2 Control Packages

Install the packages required by the UR5e simulation:

sudo apt install -y \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-controller-manager \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2

---

12. Optional: Install MoveIt

If you want to use MoveIt with the robot:

sudo apt install -y ros-humble-moveit

MoveIt is not required just to launch the Gazebo simulation.

---

📥 Clone the Project

13. Create the ROS 2 Workspace

It is recommended to keep the workspace inside the Linux filesystem.

Use:

mkdir -p ~/ros2_ws/src

Then:

cd ~/ros2_ws

«⚠️ WSL users: Avoid placing the workspace under "/mnt/c/Users/...".

Prefer:

/home/<username>/ros2_ws

instead of:

/mnt/c/Users/<username>/ros2_ws

This avoids many filesystem, symlink, and build-performance problems.»

---

14. Clone the Repository

From inside "~/ros2_ws":

git clone https://github.com/amiriguesss/ROS2.git .

Check the repository:

ls

You should see:

src

Check the source directory:

ls src

You should have:

ur_lab
Universal_Robots_ROS2_Gazebo_Simulation

---

15. Verify the Universal Robots Simulation Package

The project depends on the Universal Robots Gazebo simulation package.

Check:

find src -maxdepth 3 -name package.xml -print

You should see:

src/ur_lab/package.xml
src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo/package.xml

The Universal Robots simulation repository should be on the "humble" branch.

Check:

cd ~/ros2_ws/src/Universal_Robots_ROS2_Gazebo_Simulation
git branch --show-current

Expected:

humble

Return to the workspace:

cd ~/ros2_ws

---

🔧 Install Project Dependencies

16. Source ROS 2

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

---

17. Install All Project Dependencies

From the workspace root:

cd ~/ros2_ws

Run:

rosdep update

Then:

rosdep install --from-paths src --ignore-src -r -y

A successful installation should end with something similar to:

#All required rosdeps installed successfully

If some dependencies are already installed, that is completely fine.

---

🏗️ Build the Workspace

18. Clean Previous Builds

If this is a fresh clone, this is optional.

If you previously built the project or moved the workspace, it is recommended:

cd ~/ros2_ws
rm -rf build install log

This removes only generated build files.

It does not remove your source code.

---

19. Build the Project

Source ROS 2 first.

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

Then build:

cd ~/ros2_ws
colcon build --symlink-install

A successful build should finish with something similar to:

Summary: 2 packages finished

The exact number may change if additional packages are added later.

---

20. Source the Workspace

After a successful build:

Bash

source ~/ros2_ws/install/setup.bash

Zsh

source ~/ros2_ws/install/setup.zsh

---

🔍 Verify the Build

21. Check the ROS Packages

Check the project package:

ros2 pkg prefix ur_lab

Expected:

/home/<username>/ros2_ws/install/ur_lab

Check the Universal Robots simulation:

ros2 pkg prefix ur_simulation_gazebo

Expected:

/home/<username>/ros2_ws/install/ur_simulation_gazebo

You can also list the UR packages:

ros2 pkg list | grep ur_

You should see packages similar to:

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

---

🧪 Test Gazebo

Before launching the complete project, make sure Gazebo itself works.

Run:

gazebo

Gazebo Classic should open.

Close it with:

Ctrl+C

---

🤖 Test the Universal Robots Simulation

Before running the custom "ur_lab" environment, it is recommended to test the underlying UR simulation.

Make sure ROS and your workspace are sourced.

Bash

source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

Zsh

source /opt/ros/humble/setup.zsh
source ~/ros2_ws/install/setup.zsh

Then run:

ros2 launch ur_simulation_gazebo ur_sim_control.launch.py

Gazebo should open with the simulated UR5e.

If this works correctly, the Universal Robots simulation is functioning.

Stop it with:

Ctrl+C

---

🌎 Run the Complete Project

Once the basic UR simulation works, launch the actual project.

From the workspace:

cd ~/ros2_ws

Source ROS:

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

Source the workspace:

Bash

source install/setup.bash

Zsh

source install/setup.zsh

Now launch the project:

ros2 launch ur_lab sim.launch.py

---

🚀 Main Launch Command

Once everything has been installed and built, the complete project can be started with:

cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch ur_lab sim.launch.py

For Zsh:

cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh
ros2 launch ur_lab sim.launch.py

This is the main command for the project.

---

🎮 Running the Custom Nodes

The "ur_lab" package contains custom executable nodes.

List them:

ros2 pkg executables ur_lab

You should see:

ur_lab add_scene
ur_lab move_robot

---

"add_scene"

Run:

ros2 run ur_lab add_scene

---

"move_robot"

Run:

ros2 run ur_lab move_robot

«⚠️ The simulation should already be running before starting nodes that interact with the simulated robot.»

---

🖥️ Recommended Terminal Workflow

A convenient workflow is to use multiple terminals.

Terminal 1 — Gazebo / Simulation

Zsh

cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh

ros2 launch ur_lab sim.launch.py

---

Terminal 2 — Robot Node

Zsh

cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh

ros2 run ur_lab move_robot

---

Terminal 3 — Scene Node

Zsh

cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
source install/setup.zsh

ros2 run ur_lab add_scene

The same commands work with Bash by replacing ".zsh" with ".bash".

---

🐚 Zsh Configuration

If you use Zsh, you can automatically source ROS 2 and the workspace every time you open a terminal.

Run:

echo 'source /opt/ros/humble/setup.zsh' >> ~/.zshrc

Then:

echo 'source ~/ros2_ws/install/setup.zsh' >> ~/.zshrc

Reload your configuration:

source ~/.zshrc

Now you can simply run:

cd ~/ros2_ws
ros2 launch ur_lab sim.launch.py

---

⚠️ Important: Workspace Paths

If you previously had the project somewhere else, for example:

/mnt/c/Users/Amir/Downloads/ros2_ws

and moved it to:

/home/amir/ros2_ws

your shell may still contain references to the old workspace.

Check:

echo $AMENT_PREFIX_PATH

and:

echo $CMAKE_PREFIX_PATH

If you see an old path such as:

/mnt/c/Users/.../ros2_ws/install

clean the current shell:

unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH

Then source ROS again:

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

Then source the current workspace:

Bash

source ~/ros2_ws/install/setup.bash

Zsh

source ~/ros2_ws/install/setup.zsh

---

🧹 Completely Clean and Rebuild

If the project gets into a broken build state, perform a clean rebuild.

cd ~/ros2_ws

Remove generated files:

rm -rf build install log

Source ROS:

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

Install dependencies again:

rosdep install --from-paths src --ignore-src -r -y

Build:

colcon build --symlink-install

Source the new workspace:

Bash

source install/setup.bash

Zsh

source install/setup.zsh

Verify:

ros2 pkg prefix ur_lab

and:

ros2 pkg prefix ur_simulation_gazebo

---

🐛 Troubleshooting

"ros2: command not found"

Source ROS 2:

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

Check:

which ros2

Expected:

/opt/ros/humble/bin/ros2

---

"Package 'ur_lab' not found"

Build and source the workspace:

cd ~/ros2_ws
colcon build --symlink-install

Then:

Bash

source install/setup.bash

Zsh

source install/setup.zsh

Then:

ros2 pkg prefix ur_lab

---

"Package 'ur_simulation_gazebo' not found"

First check that the source package exists:

find ~/ros2_ws/src -name package.xml | grep ur_simulation_gazebo

You should have:

~/ros2_ws/src/Universal_Robots_ROS2_Gazebo_Simulation/ur_simulation_gazebo/package.xml

Check whether "colcon" sees it:

cd ~/ros2_ws
colcon list

You should see:

ur_lab
ur_simulation_gazebo

If necessary, clean and rebuild:

rm -rf build install log

source /opt/ros/humble/setup.zsh

rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install

Then:

source install/setup.zsh

---

"gazebo: command not found"

Install Gazebo Classic:

sudo apt update
sudo apt install -y gazebo libgazebo-dev

Then:

gazebo --version

---

Gazebo opens and immediately closes

First test Gazebo without ROS:

gazebo

If Gazebo itself fails, the issue is with the Gazebo/GUI environment rather than this ROS project.

---

Build warnings about old "/mnt/c/..." paths

If you see:

The path '/mnt/c/.../ros2_ws/install/...' in AMENT_PREFIX_PATH doesn't exist

your shell is probably still referencing an old workspace.

Run:

unset AMENT_PREFIX_PATH
unset CMAKE_PREFIX_PATH

Then:

source /opt/ros/humble/setup.zsh

and:

source ~/ros2_ws/install/setup.zsh

If the warning returns every time you open a new terminal, inspect:

grep -n "ros2_ws" ~/.zshrc

Remove references to the old workspace.

---

🔄 Updating the Project

If you already cloned the repository and want the latest version:

cd ~/ros2_ws
git pull

Then rebuild:

source /opt/ros/humble/setup.zsh
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.zsh

Then launch:

ros2 launch ur_lab sim.launch.py

---

🛑 Stopping the Simulation

To stop the ROS 2 launch:

Ctrl+C

If Gazebo becomes stuck and refuses to close:

pkill -9 gzserver
pkill -9 gzclient
pkill -9 gazebo

Check that no Gazebo processes remain:

ps aux | grep -E "gzserver|gzclient|gazebo"

---

📚 Useful Commands

List ROS packages

ros2 pkg list

Find UR packages

ros2 pkg list | grep ur_

List executables

ros2 pkg executables ur_lab

List available launch files

ros2 launch ur_lab

Check a package

ros2 pkg prefix ur_lab

Check the UR simulation

ros2 pkg prefix ur_simulation_gazebo

List ROS nodes

ros2 node list

List ROS topics

ros2 topic list

Inspect a topic

ros2 topic echo <topic_name>

---

⚡ Quick Start

If ROS 2 Humble, Gazebo Classic 11, and all dependencies are already installed, the entire process is:

cd ~/ros2_ws

source /opt/ros/humble/setup.bash

rosdep install --from-paths src --ignore-src -r -y

colcon build --symlink-install

source install/setup.bash

ros2 launch ur_lab sim.launch.py

Zsh

If you use Zsh:

cd ~/ros2_ws
source /opt/ros/humble/setup.zsh
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.zsh
ros2 launch ur_lab sim.launch.py

---

🧭 Complete Fresh-Install Command Sequence

For someone starting with a clean Ubuntu 22.04 installation, the overall process is:

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

Add ROS:

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

Install ROS 2:

sudo apt update
sudo apt install -y ros-humble-desktop

Install Gazebo:

sudo apt install -y \
    gazebo \
    libgazebo-dev \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control

Install ROS control dependencies:

sudo apt install -y \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-controller-manager \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-xacro \
    ros-humble-rviz2

Initialize rosdep:

sudo rosdep init
rosdep update

Create workspace:

mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

Clone:

git clone https://github.com/amiriguesss/ROS2.git .

Source ROS:

Bash

source /opt/ros/humble/setup.bash

Zsh

source /opt/ros/humble/setup.zsh

Install dependencies:

rosdep install --from-paths src --ignore-src -r -y

Build:

colcon build --symlink-install

Source workspace:

Bash

source install/setup.bash

Zsh

source install/setup.zsh

Launch:

ros2 launch ur_lab sim.launch.py

---

🔗 References

- ROS 2 Humble: https://docs.ros.org/en/humble/
- Gazebo Classic: https://classic.gazebosim.org/
- Universal Robots ROS 2 Gazebo Simulation: https://github.com/UniversalRobots/Universal_Robots_ROS2_Gazebo_Simulation
- Project Repository: https://github.com/amiriguesss/ROS2

---

👨‍💻 Author

Amir Rasoulzadeh

GitHub: https://github.com/amiriguesss

Project: https://github.com/amiriguesss/ROS2

---

⭐ Support

If this project helped you learn ROS 2, Gazebo, robotics simulation, or "ros2_control", consider giving the repository a ⭐.
