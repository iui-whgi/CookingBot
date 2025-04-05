from omni.isaac.kit import SimulationApp
simulation_app = SimulationApp({"headless": False})

import os
import numpy as np
from isaacsim.core.api import World
from isaacsim.core.prims import Articulation
# from isaacsim.core.objects import DynamicCuboid
from isaacsim.core.api.objects import DynamicCuboid

from isaacsim.core.utils.stage import add_reference_to_stage
# from isaacsim.core.utils.prims import set_prim_transform
# from isaacsim.core.utils.prims import set_prim_transform  # ✅ 사용 가능
from isaacsim.core.api.objects import DynamicCuboid

from isaacsim.core.utils.viewports import set_camera_view
import time

# 초기화
world = World(stage_units_in_meters=1.0)
robot_usd_path = os.path.abspath("./OPENX.usd")
robot_prim_path = "/World/OPENX"
add_reference_to_stage(robot_usd_path, robot_prim_path)

# 로봇 위치 살짝 띄우기
# set_prim_transform(prim_path=robot_prim_path, translation=[0, 0, 0.1])

# 바닥 + 카메라
world.scene.add_default_ground_plane()
set_camera_view(eye=[1.5, 1.5, 1.0], target=[0.0, 0.0, 0.5])

# 로봇 articulation
robot = Articulation(prim_paths_expr=robot_prim_path)
world.scene.add(robot)

# 박스(잡을 물체)
box = DynamicCuboid(
    prim_path="/World/box",
    name="box",
    position=np.array([0.2, 0.0, 0.02]),  # 바닥 위 살짝
    size=0.04,
    color=np.array([0.8, 0.2, 0.2])
)
world.scene.add(box)

# 초기화
world.reset()

# 조인트 이름 확인
joint_names = robot.joint_names
print("🤖 Joints:", joint_names)

# joint index 매핑
jidx = {name: i for i, name in enumerate(joint_names)}

# Pick & Place 상태 순서
STEPS = [
    ("approach", [0.0, -0.3, 0.0, 0.5]),   # 박스 접근
    ("close",    [0.0, -0.3, 0.0, 0.5], 0.01),  # gripper 닫기
    ("lift",     [0.0, 0.0, 0.0, 0.2]),   # 들어올리기
    ("place",    [0.4, 0.0, 0.0, 0.2]),   # 옆으로 이동
    ("open",     [0.4, 0.0, 0.0, 0.2], -0.01), # gripper 열기
]

step_index = 0
step_time = 0.0
step_duration = 1.5  # 각 동작 간 시간 간격
start_time = None



def make_joint_values(arm, grip_val=None):
    joint_values = [0.0] * len(joint_names)
    joint_values[jidx["joint1"]] = arm[0]
    joint_values[jidx["joint2"]] = arm[1]
    joint_values[jidx["joint3"]] = arm[2]
    joint_values[jidx["joint4"]] = arm[3]
    if grip_val is not None:
        joint_values[jidx["gripper_left_joint"]] = grip_val
        joint_values[jidx["gripper_right_joint"]] = -grip_val
    return joint_values



while simulation_app.is_running():
    if world.is_playing():
        world.step(render=True)

        now = world.current_time

        if start_time is None:
            start_time = now

        if now - step_time > step_duration and step_index < len(STEPS):
            step_time = now
            action = STEPS[step_index]
            name = action[0]
            arm_pos = action[1]
            grip_val = action[2] if len(action) > 2 else None

            print(f"🔧 Step {step_index+1}/{len(STEPS)}: {name}")

            # # 전체 joint 값 초기화
            # joint_values = [0.0] * len(joint_names)
            # joint_values[jidx["joint1"]] = arm_pos[0]
            # joint_values[jidx["joint2"]] = arm_pos[1]
            # joint_values[jidx["joint3"]] = arm_pos[2]
            # joint_values[jidx["joint4"]] = arm_pos[3]
            joint_values = make_joint_values(arm_pos, grip_val)

            if grip_val is not None:
                joint_values[jidx["gripper_left_joint"]] = grip_val
                joint_values[jidx["gripper_right_joint"]] = -grip_val

            # 수정
            # robot.set_joint_positions(joint_values)             # 초기 위치 설정 (optional)
            robot.set_joint_position_targets(joint_values)      # ✅ 움직이는 제어

            step_index += 1

    elif world.is_stopped():
        break

simulation_app.close()
