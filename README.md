# Gráficos:
Para iniciar a interface gráfica do container, execute o script `start_vnc.sh` e depois rode o comando `vncviewer localhost:5901` para acessar a interface gráfica do container, conectando através do Finder do MacOS ou usando um cliente VNC. A senha para acessar a interface gráfica é definida pelo comando.

# Criar ROS2 package:
```bash
cd ~/<nome_do_workspace/atividade>/src
ros2 pkg create --build-type ament_cmake <nome_do_pacote> ou
ros2 pkg create --build-type ament_python <nome_do_pacote>
```

# Compilar o workspace:
```bash
cd ~/<nome_do_workspace/atividade>
colcon build --symlink-install
source install/setup.bash
```

# Visualização no RViz:
```bash
DISPLAY=:1 ros2 launch my_robot display.launch.py
```

# Simulação no Gazebo:
```bash
DISPLAY=:1 ros2 launch my_robot gazebo.launch.py
```
