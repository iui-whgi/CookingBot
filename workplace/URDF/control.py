# import omni
# from omni.isaac.kit import SimulationApp

# # headless=False 로 하면 GUI 켜짐
# simulation_app = SimulationApp({"headless": False})

# import omni.isaac.core.utils.prims as prim_utils
# from omni.isaac.core import World
# from omni.isaac.core.objects import FixedCuboid
# from omni.isaac.core.articulations import Articulation
# from omni.isaac.core.utils.nucleus import get_assets_root_path
#! 하트,별,세모 다 그릴수 있음. 별은 완벽하지는않다.

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

# Python 경로에 현재 디렉토리 추가
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from isaacsim.core.api import World
from isaacsim.core.api.scenes.scene import Scene
from isaacsim.core.utils.rotations import euler_angles_to_quat
from isaacsim.core.utils.string import find_unique_string_name
from isaacsim.core.utils.prims import is_prim_path_valid, get_prim_at_path
from isaacsim.core.utils.viewports import set_camera_view
from isaacsim.core.utils.stage import add_reference_to_stage, get_current_stage
from omni.isaac.nucleus import get_assets_root_path
from isaacsim.core.utils.extensions import enable_extension
from isaacsim.core.articulations import Articulation
from pxr import UsdGeom
import json

import carb

# 월드 세팅
world = World(stage_units_in_meters=1.0)

# 로봇 USD 경로 (수정 가능)
robot_path = "./OPENX.usd"

# 월드에 USD 로딩
robot_prim = world.scene.add(
    Articulation(
        prim_path="/World/open_manipulator",
        name="open_manipulator",
        usd_path=robot_path,
    )
)

world.reset()

# 시뮬레이션 루프
while simulation_app.is_running():
    if world.is_playing():
        world.step(render=True)

        # 최초 1회 실행: 관절 제어
        if world.current_time_step_index == 1:
            print("🔧 Setting joint positions...")

            # 조인트 이름 확인 (첫 프레임에 출력)
            joint_names = robot_prim.get_joint_names()
            print("✅ Joint Names:", joint_names)

            # 예시: 첫 번째 조인트를 0.5 라디안으로 설정
            robot_prim.set_joint_positions([0.5] + [0.0] * (len(joint_names) - 1))

    elif world.is_stopped():
        break

simulation_app.close()
