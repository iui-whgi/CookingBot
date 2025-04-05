from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

import os
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.utils.viewports import set_camera_view

# 초기 설정
world = World(stage_units_in_meters=1.0)

# 로봇 경로
robot_usd_path = os.path.abspath("./OPENX.usd")
robot_prim_path = "/World/OPENX"
add_reference_to_stage(robot_usd_path, robot_prim_path)
world.scene.add_default_ground_plane()

# 로봇 articulation 생성
robot = Articulation(prim_paths_expr=robot_prim_path)
world.scene.add(robot)

# 카메라 위치
set_camera_view(eye=[1.5, 1.5, 1.0], target=[0.0, 0.0, 0.5])

# 초기화
world.reset()

# 시뮬루프
while simulation_app.is_running():
    if world.is_playing():
        world.step(render=True)

        # 시간에 따라 조인트를 sin파형으로 움직임
        t = world.current_time
        if robot.joint_names:
            joint_count = len(robot.joint_names)
            joint_angles = [0.2 * np.sin(t + i) for i in range(joint_count)]
            robot.set_joint_positions(joint_angles)

    elif world.is_stopped():
        break

simulation_app.close()
