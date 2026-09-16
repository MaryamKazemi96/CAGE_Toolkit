import sys
import numpy as np
import matplotlib.pyplot as plt

import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message


BAG_PATH = sys.argv[1] if len(sys.argv) > 1 else (
    "data/Rosbags/delivery/session 5/"
    "session_2026-05-27_15-00-51/split_bag"
)

MAP_TOPIC = "/map"
POSE_TOPIC = "/amcl_pose"


reader = rosbag2_py.SequentialReader()

storage_options = rosbag2_py.StorageOptions(
    uri=BAG_PATH,
    storage_id="sqlite3"
)

converter_options = rosbag2_py.ConverterOptions(
    input_serialization_format="cdr",
    output_serialization_format="cdr"
)

reader.open(storage_options, converter_options)

topic_types = reader.get_all_topics_and_types()

type_map = {
    topic.name: topic.type
    for topic in topic_types
}

print("[INFO] Available topics:")
for topic in sorted(type_map):
    print(f"  {topic}: {type_map[topic]}")



if MAP_TOPIC not in type_map:
    raise RuntimeError(
        f"{MAP_TOPIC} not found in bag."
    )

if POSE_TOPIC not in type_map:
    raise RuntimeError(
        f"{POSE_TOPIC} not found in bag."
    )


MapMsg = get_message(type_map[MAP_TOPIC])
PoseMsg = get_message(type_map[POSE_TOPIC])


map_msg = None

trajectory_x = []
trajectory_y = []

map_count = 0
pose_count = 0

while reader.has_next():

    topic, data, timestamp = reader.read_next()

    if topic == MAP_TOPIC:

        msg = deserialize_message(data, MapMsg)

        if map_msg is None:
            map_msg = msg
            map_count += 1


    elif topic == POSE_TOPIC:

        msg = deserialize_message(data, PoseMsg)

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Ignore invalid values
        if np.isfinite(x) and np.isfinite(y):

            trajectory_x.append(x)
            trajectory_y.append(y)

            pose_count += 1



if map_msg is None:
    raise RuntimeError(
        f"No messages found on {MAP_TOPIC}"
    )

if len(trajectory_x) == 0:
    raise RuntimeError(
        f"No messages found on {POSE_TOPIC}"
    )


print()
print("[INFO] Map:")
print(f"       frame       : {map_msg.header.frame_id}")
print(f"       resolution  : {map_msg.info.resolution:.4f} m/pixel")
print(f"       width       : {map_msg.info.width}")
print(f"       height      : {map_msg.info.height}")
print(
    f"       origin      : "
    f"({map_msg.info.origin.position.x:.3f}, "
    f"{map_msg.info.origin.position.y:.3f})"
)

print()
print("[INFO] Trajectory:")
print(f"       poses       : {len(trajectory_x)}")
print(
    f"       x range    : "
    f"{min(trajectory_x):.3f} -> {max(trajectory_x):.3f}"
)
print(
    f"       y range    : "
    f"{min(trajectory_y):.3f} -> {max(trajectory_y):.3f}"
)



width = map_msg.info.width
height = map_msg.info.height
resolution = map_msg.info.resolution

origin_x = map_msg.info.origin.position.x
origin_y = map_msg.info.origin.position.y

map_data = np.asarray(
    map_msg.data,
    dtype=np.int8
).reshape((height, width))



display_map = np.where(
    map_data == -1,
    127,
    np.where(
        map_data == 0,
        255,
        0
    )
)



xmin = origin_x
xmax = origin_x + width * resolution

ymin = origin_y
ymax = origin_y + height * resolution


fig, ax = plt.subplots(
    figsize=(10, 8)
)


ax.imshow(
    display_map,
    cmap="gray",
    origin="lower",
    extent=[
        xmin,
        xmax,
        ymin,
        ymax
    ],
    interpolation="nearest"
)



ax.plot(
    trajectory_x,
    trajectory_y,
    linewidth=2.0,
    label="Robot trajectory"
)


ax.scatter(
    trajectory_x[0],
    trajectory_y[0],
    s=70,
    marker="o",
    zorder=5,
    label="Start"
)


ax.scatter(
    trajectory_x[-1],
    trajectory_y[-1],
    s=90,
    marker="X",
    zorder=5,
    label="End"
)


ax.set_xlabel("x [m]", fontsize=12)
ax.set_ylabel("y [m]", fontsize=12)

ax.set_title(
    "Robot Trajectory on Recorded Map",
    fontsize=14
)

ax.set_aspect("equal", adjustable="box")

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

ax.grid(
    True,
    alpha=0.2,
    linewidth=0.5
)

ax.legend(
    loc="best",
    frameon=True
)

plt.tight_layout()



output_path = "robot_trajectory_on_map.png"

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print()
print(f"[INFO] Figure saved to: {output_path}")

plt.show()