# ROS2 Robot Simulation — Complete Setup Guide
> **Platform:** Linux (Ubuntu 22.04/24.04, x86_64)  
> **ROS2 Distro:** Jazzy  
> **Simulation:** Gazebo Harmonic  
> **Stack:** SLAM Toolbox + Nav2 + MPPI Controller

---

## Prerequisites

### 1. Install Docker + VS Code
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install VS Code
sudo snap install code --classic

# Install Dev Containers extension
code --install-extension ms-vscode-remote.remote-containers
```

### 2. Clone the Repository
```bash
git clone https://github.com/PAR-2026/build-your-own-simulated-race-track-cobras-da-robotica.git
cd build-your-own-simulated-race-track-cobras-da-robotica
git checkout gabriel
```

### 3. Open in Dev Container
```bash
code .
```
When VS Code opens, click **"Reopen in Container"** in the bottom-left corner or via `Ctrl+Shift+P` → **"Dev Containers: Reopen in Container"**.

The container will build automatically — this takes **10-20 minutes** on first run as it pulls the ROS2 Jazzy + Gazebo image.

---

## First Time Setup (inside the container)

Open a terminal inside VS Code (`Ctrl+` `` ` ``).

### 1. Import dependencies
```bash
cd /workspaces/build-your-own-simulated-race-track-cobras-da-robotica
vcs import src < src/ros2.repos
```

### 2. Install ROS dependencies
```bash
rosdep update
rosdep install --from-paths src --ignore-src -y
```

### 3. Install simulation packages
```bash
sudo apt-get update && sudo apt-get install -y \
  ros-jazzy-slam-toolbox \
  ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-msgs \
  ros-jazzy-twist-mux \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-teleop-twist-keyboard
```

### 4. Build the workspace
```bash
colcon build --symlink-install
source install/setup.bash
```

Add to bashrc so you don't have to source every time:
```bash
echo "source /workspaces/build-your-own-simulated-race-track-cobras-da-robotica/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## Running the Simulation

### Option A — Basic Simulation (Gazebo + RViz only)
Use this to verify the robot loads correctly.

```bash
ros2 launch real_test_robot launch_sim.launch.py world:=arena.sdf
```

You should see:
- Gazebo opens with the arena (walls + obstacles)
- Robot spawns at the origin (purple box with black wheels and red lidar)
- RViz opens showing the robot model

**Test the robot moves:**
```bash
# In a new terminal
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.5}, angular: {z: 0.3}}' --once
```

---

## Phase 1 — Build the Map with SLAM

Run this phase first to generate a map of the arena.

### Terminal 1 — Launch SLAM
```bash
ros2 launch real_test_robot slam.launch.py world:=arena.sdf
```

### Terminal 2 — Drive the robot to explore the arena
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keyboard controls:
```
u  i  o
j  k  l
m  ,  .

i = forward
, = backward
j = rotate left
l = rotate right
k = stop
```

Drive the robot around the entire arena making sure to pass near all walls and obstacles so the lidar can scan everything. Watch the map build in RViz in real time.

### Terminal 3 — Save the map when done
```bash
ros2 run nav2_map_server map_saver_cli -f src/real_test_robot/maps/arena_map
```

This creates two files:
- `arena_map.pgm` — the map image (white=free, black=walls, grey=unknown)
- `arena_map.yaml` — map metadata (resolution, origin)

**Rebuild after saving the map** so it gets installed:
```bash
colcon build --symlink-install
```

---

## Phase 2 — Autonomous Navigation with AMCL + Nav2

Use this phase after you have a saved map from Phase 1.

### Terminal 1 — Launch Navigation
```bash
ros2 launch real_test_robot navigation.launch.py world:=arena.sdf
```

### In RViz — Set Initial Pose
1. Click **"2D Pose Estimate"** button in RViz toolbar
2. Click on the map where the robot actually is and drag to set its heading
3. AMCL will localize — the particle cloud (green arrows) should converge around the robot

### In RViz — Send Navigation Goal
1. Click **"Nav2 Goal"** button in RViz toolbar  
2. Click anywhere on the free space in the map
3. Watch the robot plan a path and drive autonomously to the goal

### Alternatively — Send goal from terminal
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "pose: {header: {frame_id: map}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}"
```

---

## Verifying Everything Works

### Check all topics are active
```bash
ros2 topic list
```

Expected topics:
```
/scan           ← lidar data
/odom           ← wheel odometry
/tf             ← transforms
/cmd_vel        ← velocity commands
/map            ← SLAM/Nav2 map
/joint_states   ← wheel joint states
/clock          ← simulation time
```

### Check TF tree is correct
```bash
ros2 run tf2_tools view_frames
evince frames.pdf
```

Expected TF chain:
```
map → odom → base_footprint → base_link → chassis → lidar_link
                                        → left_wheel
                                        → right_wheel
                                        → caster_wheel
```

### Check lidar is publishing
```bash
ros2 topic echo /scan --once
```

Should print laser scan data with 360 range readings.

### Check AMCL is localizing (Phase 2 only)
```bash
ros2 topic echo /amcl_pose --once
```

Should print the robot's estimated pose in the map frame.

---

## Troubleshooting

### Robot doesn't move
```bash
# Check cmd_vel is being received
ros2 topic echo /cmd_vel

# Check the bridge is running
ros2 node list | grep bridge
```

### Map not building / lidar not visible in RViz
```bash
# Check scan topic
ros2 topic hz /scan
# Should print ~10 Hz

# In RViz: Add → By Topic → /scan → LaserScan
```

### Nav2 not starting
```bash
# Check nav2 nodes are running
ros2 node list | grep nav2

# Check map is loaded
ros2 topic echo /map --once
```

### AMCL particles not converging
- Make sure you set the **2D Pose Estimate** in RViz first
- Drive the robot slightly so AMCL gets sensor updates
- Check the map matches the actual Gazebo world

### Gazebo opens but robot doesn't spawn
```bash
# Check robot description is being published
ros2 topic echo /robot_description --once

# Rebuild if empty
colcon build --symlink-install
source install/setup.bash
```

### Twist_mux not installed
```bash
sudo apt-get install -y ros-jazzy-twist-mux
```


---

## Project Structure Reference

```
src/real_test_robot/
├── urdf/
│   ├── real_test_robot.urdf.xacro   # Main robot file (includes all below)
│   ├── robot_core.xacro             # Robot body, wheels, caster
│   ├── lidar.xacro                  # Lidar sensor
│   ├── gazebo_control.xacro         # Gazebo diff drive plugin (no ros2_control)
│   ├── ros2_control.xacro           # ros2_control hardware interface (x86 only)
│   └── inertia_macros.xacro         # Inertia calculation helpers
├── launch/
│   ├── launch_sim.launch.py         # Basic simulation
│   ├── slam.launch.py               # Phase 1: SLAM mapping
│   ├── navigation.launch.py         # Phase 2: AMCL + Nav2
│   └── rsp.launch.py                # Robot state publisher
├── config/
│   ├── gz_bridge.yaml               # Gazebo↔ROS2 topic bridge
│   ├── mapper_params_online_async.yaml  # SLAM toolbox config
│   ├── nav2_params.yaml             # Nav2 + AMCL + MPPI config
│   ├── my_controllers.yaml          # ros2_control controllers (x86 only)
│   └── twist_mux.yaml               # Velocity multiplexer
├── worlds/
│   ├── arena.sdf                    # Main arena with obstacles
│   └── line_follow.sdf              # Line following world
└── maps/
    ├── arena_map.pgm                # Generated map image
    └── arena_map.yaml               # Generated map metadata
```

---

## Known Limitations on macOS / Apple Silicon (arm64)

The following packages are **not available** for arm64 and require x86 Linux or real hardware:

| Feature | Status | Workaround |
|---|---|---|
| `ros2_control` | ❌ arm64 not available | Use Gazebo diff drive plugin directly |
| `ros2_controllers` | ❌ arm64 not available | Same as above |
| `gz_ros2_control` | ❌ arm64 not available | Same as above |
| SLAM Toolbox | ✅ Check apt | May work |
| Nav2 | ✅ Check apt | May work |
| Gazebo simulation | ✅ Works via VNC | Use x11vnc + Xvfb |

macOS users must also set up a virtual display via VNC before launching any GUI:
```bash
Xvfb :1 -screen 0 1920x1080x24 &
x11vnc -display :1 -passwd ros123 -listen 0.0.0.0 -xkb -forever &
# Connect via vnc://localhost:5900
```

---

## Quick Reference — Most Used Commands

```bash
# Build
colcon build --symlink-install && source install/setup.bash

# Basic sim
ros2 launch real_test_robot launch_sim.launch.py

# SLAM mapping
ros2 launch real_test_robot slam.launch.py

# Save map
ros2 run nav2_map_server map_saver_cli -f src/real_test_robot/maps/arena_map

# Navigation
ros2 launch real_test_robot navigation.launch.py

# Manual control
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Check topics
ros2 topic list

# Check TF
ros2 run tf2_tools view_frames
```