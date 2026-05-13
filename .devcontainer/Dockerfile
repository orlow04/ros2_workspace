FROM --platform=linux/arm64 ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive

# Install ROS 2 and Gazebo packages
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl gnupg2 lsb-release sudo \
      ros-jazzy-desktop \
      ros-jazzy-ros-gz \
  && rm -rf /var/lib/apt/lists/

# Install virtual display and VNC
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN if getent passwd ubuntu > /dev/null 2>&1; then userdel -r ubuntu; fi \
  && groupadd --gid $USER_GID $USERNAME \
  && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
  && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
  && chmod 0440 /etc/sudoers.d/$USERNAME

# Dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
      bash-completion \
      build-essential \
      cmake \
      gdb \
      git \
      python3-argcomplete \
      python3-pip \
      ros-dev-tools \
      vim \
  && rosdep init || echo "rosdep already initialized" \
  && rm -rf /var/lib/apt/lists/*

# Shell setup
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/ros/.bashrc \
  && echo "if [ -f /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash ]; then \
      source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash; fi" \
      >> /home/ros/.bashrc

ENV DEBIAN_FRONTEND=
ENV AMENT_CPPCHECK_ALLOW_SLOW_VERSIONS=1

USER ros