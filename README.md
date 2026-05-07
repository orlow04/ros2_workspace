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
# Terminal 1 — publish robot description
DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 ros2 run robot_state_publisher robot_state_publisher \
  --ros-args -p robot_description:="$(xacro /workspaces/build-your-own-simulated-race-track-cobras-da-robotica/install/real_test_robot/share/real_test_robot/urdf/real_test_robot.urdf.xacro)"

# Terminal 2 — open RViz
DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 ros2 run rviz2 rviz2
```


# Simulação no Gazebo com o mundo personalizado:
```bash
colcon build --packages-select real_test_robot
source install/setup.bash
DISPLAY=:1 LIBGL_ALWAYS_SOFTWARE=1 ros2 launch real_test_robot launch_sim.launch.py
```
O modelo de mundo criado para a atividade segue a estrutura de um arquivo SDF, onde são definidos os elementos do ambiente, como luz, chão, linha preta e paredes. Cada elemento é representado por um modelo com suas propriedades específicas, como posição, tamanho e material. O arquivo SDF é utilizado para configurar o ambiente de simulação no Gazebo, permitindo a criação de cenários personalizados para testes e desenvolvimento de robôs.

O chão é uma caixa larga e fina (6 x 6 x 0.02), as paredes também são caixas (6 x 0.1 x 1) posicionadas ao redor do chão para criar um ambiente fechado. Já a linha preta é uma caixa ainda mais fina (0 0 0.021 0 0 0) colocada um pouco acima do chão. A escolha do 0.021 para a linha é justificada pela altura da caixa do chão (0.02) mais uma pequena margem para evitar que a linha fique embutida no chão, o que poderia causar problemas de detecção pelos sensores do robô. Em um primeiro teste testamos apenas uma linha reta, para testar a detecção da linha e o controle do robô, uma vez bem sucedido progredimos para uma linha retangular, buscando testar se o robô consegue "completar a caixa" seguindo a linha.