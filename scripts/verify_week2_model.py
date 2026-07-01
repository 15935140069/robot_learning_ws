#!/usr/bin/env python3
"""Week 2：完整机器人模型静态验收脚本。"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def fail(message):
    print(f'FAIL: {message}')
    return False


def passed(message):
    print(f'PASS: {message}')
    return True


def get_joint_map(root):
    result = {}

    for joint in root.findall('joint'):
        name = joint.get('name')
        parent = joint.find('parent')
        child = joint.find('child')

        result[name] = {
            'element': joint,
            'parent': parent.get('link') if parent is not None else None,
            'child': child.get('link') if child is not None else None,
        }

    return result


def has_visual_collision_inertial(link):
    return all(
        link.find(tag) is not None
        for tag in ('visual', 'collision', 'inertial')
    )


def main():
    if len(sys.argv) != 2:
        print('用法：python3 scripts/verify_week2_model.py <完整URDF路径>')
        return 2

    urdf_path = Path(sys.argv[1])

    if not urdf_path.is_file():
        print(f'FAIL: 找不到 URDF 文件：{urdf_path}')
        return 2

    text = urdf_path.read_text(encoding='utf-8')

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        print(f'FAIL: URDF XML 解析失败：{exc}')
        return 2

    all_passed = True

    print('===== Week 2 模型静态验收 =====')

    if root.get('name') == 'learning_ur5e':
        passed('机器人名称为 learning_ur5e')
    else:
        all_passed &= fail(
            f'机器人名称异常：{root.get("name")}'
        )

    if 'ur_description' not in text:
        passed('未残留 ur_description 旧包路径')
    else:
        all_passed &= fail('仍存在 ur_description 旧包路径')

    mesh_refs = sorted({
        mesh.get('filename')
        for mesh in root.findall('.//mesh')
        if mesh.get('filename')
    })

    own_mesh_refs = [
        item for item in mesh_refs
        if item.startswith(
            'package://learning_robot_description/meshes/ur5e/'
        )
    ]

    if len(own_mesh_refs) == 14:
        passed('UR5e 自维护 mesh 引用数量为 14')
    else:
        all_passed &= fail(
            f'UR5e 自维护 mesh 数量应为 14，实际为 '
            f'{len(own_mesh_refs)}'
        )

    links = {
        link.get('name'): link
        for link in root.findall('link')
    }

    physical_links = [
        'base_link_inertia',
        'shoulder_link',
        'upper_arm_link',
        'forearm_link',
        'wrist_1_link',
        'wrist_2_link',
        'wrist_3_link',
        'gripper_base_link',
        'left_finger_link',
        'right_finger_link',
        'camera_link',
    ]

    missing_physical_links = [
        name for name in physical_links
        if name not in links
        or not has_visual_collision_inertial(links[name])
    ]

    if not missing_physical_links:
        passed('机械臂、夹爪、相机均包含 visual/collision/inertial')
    else:
        all_passed &= fail(
            '以下 link 缺少 visual、collision 或 inertial：'
            + ', '.join(missing_physical_links)
        )

    joints = get_joint_map(root)

    revolute_names = [
        'shoulder_pan_joint',
        'shoulder_lift_joint',
        'elbow_joint',
        'wrist_1_joint',
        'wrist_2_joint',
        'wrist_3_joint',
    ]

    revolute_ok = True

    for name in revolute_names:
        info = joints.get(name)

        if info is None:
            print(f'FAIL: 缺少转动关节 {name}')
            revolute_ok = False
            continue

        element = info['element']
        limit = element.find('limit')
        axis = element.find('axis')

        if element.get('type') != 'revolute':
            print(f'FAIL: {name} 不是 revolute 关节')
            revolute_ok = False
            continue

        if limit is None or axis is None:
            print(f'FAIL: {name} 缺少 limit 或 axis')
            revolute_ok = False
            continue

        required_limit_attrs = ('lower', 'upper', 'effort', 'velocity')

        if any(limit.get(attr) is None for attr in required_limit_attrs):
            print(f'FAIL: {name} 的关节限位参数不完整')
            revolute_ok = False

        if axis.get('xyz') is None:
            print(f'FAIL: {name} 缺少 axis xyz')
            revolute_ok = False

    if revolute_ok:
        passed('6 个 UR5e 转动关节均包含 axis 与 limit')
    else:
        all_passed = False

    prismatic_names = [
        'left_finger_joint',
        'right_finger_joint',
    ]

    prismatic_ok = True

    for name in prismatic_names:
        info = joints.get(name)

        if info is None:
            print(f'FAIL: 缺少直线关节 {name}')
            prismatic_ok = False
            continue

        element = info['element']
        limit = element.find('limit')
        axis = element.find('axis')

        if element.get('type') != 'prismatic':
            print(f'FAIL: {name} 不是 prismatic 关节')
            prismatic_ok = False
            continue

        if limit is None or axis is None:
            print(f'FAIL: {name} 缺少 limit 或 axis')
            prismatic_ok = False
            continue

        lower = float(limit.get('lower', 'nan'))
        upper = float(limit.get('upper', 'nan'))

        if lower != 0.0 or upper != 0.03:
            print(
                f'FAIL: {name} 行程应为 0~0.03 m，'
                f'实际为 {lower}~{upper} m'
            )
            prismatic_ok = False

    if prismatic_ok:
        passed('两个夹爪直线关节行程均为 0~0.03 m')
    else:
        all_passed = False

    expected_connections = {
        'tool0_to_gripper_base': (
            'tool0',
            'gripper_base_link',
        ),
        'gripper_base_to_tcp': (
            'gripper_base_link',
            'tcp',
        ),
        'camera_mount_joint': (
            'base_link',
            'camera_link',
        ),
        'camera_link_to_optical': (
            'camera_link',
            'camera_optical_frame',
        ),
    }

    connection_ok = True

    for joint_name, expected in expected_connections.items():
        info = joints.get(joint_name)

        if info is None:
            print(f'FAIL: 缺少固定关节 {joint_name}')
            connection_ok = False
            continue

        actual = (info['parent'], info['child'])

        if actual != expected:
            print(
                f'FAIL: {joint_name} 父子关系异常，'
                f'实际={actual}，期望={expected}'
            )
            connection_ok = False

    if connection_ok:
        passed('TCP 与相机 TF 父子关系正确')
    else:
        all_passed = False

    if all_passed:
        print('===== 结论：静态模型验收通过 =====')
        return 0

    print('===== 结论：静态模型验收未通过 =====')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
