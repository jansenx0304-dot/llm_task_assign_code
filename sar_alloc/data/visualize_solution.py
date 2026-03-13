import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np
from pathlib import Path
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ----------- 全局美化：更清爽的默认样式 -----------
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 160,
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
})

def load_data(solution_file, instance_file):
    with open(solution_file, 'r') as f:
        solution = json.load(f)
    with open(instance_file, 'r') as f:
        instance = json.load(f)
    return solution, instance

# ----------- 新增：优先级颜色映射（离散/连续都兼容）-----------
def build_priority_style(tasks_dict):
    """
    返回：
    - pr_levels: 排序后的优先级集合（float/int）
    - pr_to_color: priority -> color
    - pr_to_size: priority -> marker size（路径图用）
    """
    pr_values = []
    for t in tasks_dict.values():
        pr_values.append(float(t.get("priority", 0.0)))
    pr_levels = sorted(set(pr_values))

    # 常见是 0/1/2/3；若不是也没关系，按分位映射
    # 颜色：低 -> 冷色/灰，高 -> 暖色/红
    base_palette = {
        0.0: "#9CA3AF",  # gray
        1.0: "#3B82F6",  # blue
        2.0: "#F59E0B",  # amber
        3.0: "#EF4444",  # red
    }

    pr_to_color = {}
    if all(p in base_palette for p in pr_levels) and len(pr_levels) <= 4:
        for p in pr_levels:
            pr_to_color[p] = base_palette[p]
    else:
        # 连续/不规则优先级：用 colormap
        cmap = plt.cm.get_cmap("plasma")
        if len(pr_levels) == 1:
            pr_to_color[pr_levels[0]] = cmap(0.85)
        else:
            for i, p in enumerate(pr_levels):
                pr_to_color[p] = cmap(i / (len(pr_levels) - 1))

    # marker size：更高优先级更显眼
    pr_to_size = {}
    for p in pr_levels:
        pr_to_size[p] = 70 + 35 * (pr_levels.index(p))  # 70,105,140,...

    return pr_levels, pr_to_color, pr_to_size


def plot_routes(solution, instance, ax):
    routes = solution['routes']
    tasks = {t['id']: t for t in instance['tasks']}
    agents = {a['id']: a for a in instance['agents']}
    depot = instance['depot']

    pr_levels, pr_to_color, pr_to_size = build_priority_style(tasks)

    colors = plt.cm.tab10(np.linspace(0, 1, max(1, len(routes))))

    # depot
    ax.scatter(*depot['loc'], s=320, c='white', marker='s',
               edgecolors='black', linewidth=2.2, zorder=6)
    ax.scatter(*depot['loc'], s=220, c='#DC2626', marker='s',
               edgecolors='black', linewidth=1.8, zorder=7, label='Depot')
    ax.text(depot['loc'][0], depot['loc'][1]-55, 'Depot', ha='center',
            fontsize=10, weight='bold')

    # routes
    for agent_id_str, route in routes.items():
        agent_id = int(agent_id_str)
        color = colors[agent_id % len(colors)]

        cur_loc = depot['loc']

        for idx, task_id in enumerate(route):
            task = tasks[task_id]
            nxt = task['loc']
            pr = float(task.get("priority", 0.0))

            # 更柔和的箭头（略带弧度）
            arrow = FancyArrowPatch(
                cur_loc, nxt,
                arrowstyle='-|>', mutation_scale=16,
                color=color, linewidth=2.4, alpha=0.75,
                connectionstyle="arc3,rad=0.05",
                zorder=3
            )
            ax.add_patch(arrow)

            # 任务点：填充=priority颜色，边框=agent颜色
            ax.scatter(*nxt,
                       s=pr_to_size.get(pr, 95),
                       c=[pr_to_color.get(pr, "#9CA3AF")],
                       edgecolors=[color],
                       linewidth=2.0,
                       zorder=5)
            ax.text(nxt[0]+28, nxt[1]+28, f'T{task_id} (P{pr:g})',
                    fontsize=8.5, color='black',
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65))

            cur_loc = nxt

        # return to depot
        if route:
            arrow = FancyArrowPatch(
                cur_loc, depot['loc'],
                arrowstyle='-|>', mutation_scale=16,
                color=color, linewidth=2.2, alpha=0.55,
                linestyle='--', connectionstyle="arc3,rad=-0.05",
                zorder=2
            )
            ax.add_patch(arrow)

    # unassigned
    unassigned = solution.get('unassigned', [])
    for task_id in unassigned:
        task = tasks[task_id]
        ax.scatter(*task['loc'], s=120, c='black', marker='x',
                   linewidth=2.2, zorder=6)
        ax.text(task['loc'][0]+28, task['loc'][1]+28, f'T{task_id}(未分配)',
                fontsize=8, color='gray')

    ax.set_xlabel('X坐标')
    ax.set_ylabel('Y坐标')
    ax.set_title('任务分配路径图（点颜色=优先级，边框=Agent）')
    ax.set_aspect('equal', adjustable='box')

    # legend：agent + priority
    agent_patches = [
        mpatches.Patch(color=colors[i % len(colors)], label=f'Agent {i}')
        for i in range(len(routes))
    ]
    pr_patches = [
        mpatches.Patch(color=pr_to_color[p], label=f'Priority {p:g}')
        for p in pr_levels
    ]
    agent_patches.append(mpatches.Patch(color='gray', label='未分配任务(×)'))

    leg1 = ax.legend(handles=agent_patches, loc='upper right', fontsize=9, title="Agent", title_fontsize=10)
    ax.add_artist(leg1)
    ax.legend(handles=pr_patches, loc='lower right', fontsize=9, title="Priority", title_fontsize=10)


def plot_schedule(solution, instance, ax):
    schedule = solution['schedule']
    tasks = {t['id']: t for t in instance['tasks']}
    agents = {a['id']: a for a in instance['agents']}
    routes = solution['routes']
    depot = instance['depot']

    pr_levels, pr_to_color, _ = build_priority_style(tasks)

    agent_tasks = {int(aid): route for aid, route in routes.items()}
    agent_colors = plt.cm.tab10(np.linspace(0, 1, max(1, len(agent_tasks))))

    def euclidean_distance(loc1, loc2):
        dx = loc1[0] - loc2[0]
        dy = loc1[1] - loc2[1]
        return (dx * dx + dy * dy) ** 0.5

    y_pos = 0
    y_labels, y_ticks = [], []

    # 行背景条纹
    def add_row_band(y):
        ax.axhspan(y - 0.45, y + 0.45, color="black", alpha=0.04, zorder=0)

    for agent_id in sorted(agent_tasks.keys()):
        add_row_band(y_pos)

        route = agent_tasks[agent_id]
        agent = agents[agent_id]
        agent_speed = agent.get('speed', 1.0)
        agent_edge = agent_colors[agent_id % len(agent_colors)]

        current_time = 0.0
        current_loc = depot['loc']

        for idx, task_id in enumerate(route):
            schedule_key = f"{agent_id}:{task_id}"
            if schedule_key not in schedule:
                continue

            task = tasks[task_id]
            pr = float(task.get("priority", 0.0))
            pr_color = pr_to_color.get(pr, "#9CA3AF")

            exec_start, exec_end = schedule[schedule_key]
            task_loc = task['loc']

            distance = euclidean_distance(current_loc, task_loc)
            travel_time = distance / agent_speed if agent_speed > 0 else 0.0

            gap_start = current_time
            gap_end = exec_start
            gap_duration = gap_end - gap_start

            # travel / waiting（更柔和）
            if gap_duration > 1e-9:
                if travel_time > 1e-9 and travel_time <= gap_duration + 1e-9:
                    ax.barh(y_pos, travel_time, left=gap_start, height=0.62,
                            color='#FB923C', alpha=0.55, edgecolor='#C2410C', linewidth=0.9, zorder=1)
                    wait_time = gap_duration - travel_time
                    if wait_time > 1e-9:
                        ax.barh(y_pos, wait_time, left=gap_start + travel_time, height=0.62,
                                color='#FDE68A', alpha=0.65, edgecolor='#B45309', linewidth=0.9, zorder=1)
                else:
                    ax.barh(y_pos, gap_duration, left=gap_start, height=0.62,
                            color='#FDE68A', alpha=0.65, edgecolor='#B45309', linewidth=0.9, zorder=1)

            # time window band
            tw_start = float(task['tw_start'])
            tw_end = float(task['tw_end'])
            ax.barh(y_pos, tw_end - tw_start, left=tw_start, height=0.86,
                    color='#60A5FA', alpha=0.12, edgecolor='#2563EB',
                    linewidth=0.9, linestyle='--', zorder=0.5)

            # task execution: facecolor=priority, edgecolor=agent
            duration = exec_end - exec_start
            ax.barh(y_pos, duration, left=exec_start, height=0.52,
                    color=pr_color, alpha=0.92,
                    edgecolor=agent_edge, linewidth=2.2, zorder=2)

            # label: task + priority
            mid_time = exec_start + duration / 2
            ax.text(mid_time, y_pos, f'T{task_id}\nP{pr:g}',
                    ha='center', va='center', fontsize=9.5, weight='bold',
                    color='white',
                    bbox=dict(boxstyle="round,pad=0.18", fc="black", ec="none", alpha=0.20))

            current_loc = task_loc
            current_time = exec_end

        y_labels.append(f'Agent{agent_id}')
        y_ticks.append(y_pos)
        y_pos += 1

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=11, weight='bold')
    ax.set_xlabel('Time')
    ax.set_title('Task Allocation Schedule（填充=Priority，边框=Agent）')
    ax.grid(True, alpha=0.25, axis='x')
    ax.set_axisbelow(True)

    # legend：time window / travel / waiting / priority
    legend_elements = [
        Rectangle((0, 0), 1, 1, fc='#60A5FA', alpha=0.12, ec='#2563EB', linewidth=0.9, linestyle='--',
                  label='Time Window'),
        Rectangle((0, 0), 1, 1, fc='#FB923C', alpha=0.55, ec='#C2410C', linewidth=0.9,
                  label='Traveling'),
        Rectangle((0, 0), 1, 1, fc='#FDE68A', alpha=0.65, ec='#B45309', linewidth=0.9,
                  label='Waiting'),
    ]
    # priority patches
    for p in pr_levels:
        legend_elements.append(
            Rectangle((0, 0), 1, 1, fc=pr_to_color[p], alpha=0.92, ec='black', linewidth=0.6,
                      label=f'Priority {p:g}')
        )

    ax.legend(handles=legend_elements, loc='upper right', fontsize=9, ncol=2)


def main():
    runs_dir = Path(__file__).parent / 'runs'
    run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()])
    if not run_dirs:
        print("Error: 未找到任何run文件夹")
        sys.exit(1)

    latest_run = run_dirs[-1]
    solution_file = latest_run / 'solution.json'
    instance_file = latest_run / 'instance.json'

    if not solution_file.exists() or not instance_file.exists():
        print(f"Error: 未找到必要的JSON文件在 {latest_run}")
        sys.exit(1)

    print(f"正在加载数据从: {latest_run}")
    solution, instance = load_data(solution_file, instance_file)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(16, 12),
        gridspec_kw={"height_ratios": [1.15, 1.0]}
    )

    plot_routes(solution, instance, ax1)
    plot_schedule(solution, instance, ax2)

    plt.tight_layout()

    output_file = latest_run / 'visualization.png'
    plt.savefig(output_file, dpi=160, bbox_inches='tight')
    print(f"[DONE] Visualization saved to: {output_file}")

    plt.show()


if __name__ == '__main__':
    main()
