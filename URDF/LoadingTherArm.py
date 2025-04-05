from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

import os
import numpy as np

from isaacsim.core.api import World
from isaacsim.core.prims import Articulation
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.utils.viewports import set_camera_view

# 월드 초기화
world = World(stage_units_in_meters=1.0)

# USD 경로
robot_usd_path = os.path.abspath("./OPENX.usd")
robot_prim_path = "/World/OPENX"

# Stage에 로봇 추가
add_reference_to_stage(robot_usd_path, robot_prim_path)

# 바닥 추가
world.scene.add_default_ground_plane()

# ✅ Articulation 객체를 prim_paths_expr로 초기화
robot = Articulation(prim_paths_expr=robot_prim_path)
world.scene.add(robot)

# 카메라 시점 설정
set_camera_view(eye=[1.5, 1.5, 1.0], target=[0.0, 0.0, 0.5])

# 월드 초기화
world.reset()

# 메인 루프
set_once = False
while simulation_app.is_running():
    if world.is_playing():
        world.step(render=True)

        if not set_once:
            print("✅ Joint Names:", robot.joint_names)

            if robot.joint_names:
                robot.set_joint_positions([0.5] + [0.0] * (len(robot.joint_names) - 1))
            else:
                print("⚠️  joint_names 비어 있음. OPENX.usd 안에 articulation 있는지 확인 필요!")

            set_once = True

    elif world.is_stopped():
        break

simulation_app.close()
