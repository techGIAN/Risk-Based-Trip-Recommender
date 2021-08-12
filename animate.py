import matplotlib.pyplot as plt
import numpy as np
import itertools

import pandas as pd
import ast
import matplotlib.animation as animation

writer = animation.FFMpegWriter(fps=2, extra_args=['-vcodec', 'libx264'])

x_ticks = [i * 2 for i in range(17)]

SIZE = 168
INDEX = 0


# ============================================================
# One plot that captures 3 distributions
# ============================================================


def mutual_change():
    global INDEX, x_ticks, x_axis, x_title, title

    plt.xticks(x_ticks)
    plt.title(title + str(INDEX))
    plt.ylabel("POI Risk - probability of infection")
    plt.xlabel(x_title)
    plt.legend(loc="upper right")
    plt.axis([-0.01, 33, -0.01, 1.01])


# Animate a scatter plot with 3 distributions
def animate_scatter(frameno):
    global INDEX, normal, skewed, uniform

    plt.clf()

    plt.scatter(x_axis, normal[INDEX], s=4, c='r', alpha=0.4,
                label='normal')
    plt.scatter(x_axis, skewed[INDEX], s=4, color='b', alpha=0.4,
                label='skewed')
    plt.scatter(x_axis, uniform[INDEX], s=4, color='g', alpha=0.4,
                label='uniform')

    mutual_change()

    INDEX += 1
    return plt


# Animate a bar plot with 3 distributions
def animate_bar(frameno):
    global INDEX, normal, skewed, uniform

    plt.clf()

    plt.bar(x_axis, normal[INDEX], color='r', alpha=0.4,
            label='normal')
    plt.bar(x_axis, skewed[INDEX], color='b', alpha=0.4,
            label='skewed')
    plt.bar(x_axis, uniform[INDEX], color='g', alpha=0.4,
            label='uniform')

    mutual_change()

    INDEX += 1
    return plt


# Animate a line plot with 3 distributions
def animate_plot(frameno):
    global INDEX, normal, skewed, uniform

    plt.clf()

    plt.plot(x_axis, normal[INDEX], color='r', alpha=0.4, lw=1,
             label='normal')
    plt.plot(x_axis, skewed[INDEX], color='b', alpha=0.4, lw=1,
             label='skewed')
    plt.plot(x_axis, uniform[INDEX], color='g', alpha=0.4, lw=1,
             label='uniform')

    mutual_change()

    INDEX += 1
    return plt


# ============================================================
# 3 plots in 1 row, each relates to a different distribution
# ============================================================


def mutual_change_2_cla():
    global axs

    axs[0].cla()
    axs[1].cla()
    axs[2].cla()


def mutual_change_2():
    global title, INDEX, x_title, x_ticks, axs, fig

    plt.suptitle(title + str(INDEX))

    fig.text(0.04, 0.5, "POI Risk - probability of infection", va='center', rotation='vertical')
    fig.text(0.5, 0.04, x_title, ha='center')

    axs[0].set_xticks(x_ticks)
    axs[1].set_xticks(x_ticks)
    axs[2].set_xticks(x_ticks)

    axs[0].set_xlim([-0.01, 35])
    axs[0].set_ylim([-0.01, 1.01])
    axs[1].set_xlim([-0.01, 35])
    axs[1].set_ylim([-0.01, 1.01])
    axs[2].set_xlim([-0.01, 35])
    axs[2].set_ylim([-0.01, 1.01])
    axs[2].set_xlim([-0.01, 35])

    axs[0].legend(loc="upper right")
    axs[1].legend(loc="upper right")
    axs[2].legend(loc="upper right")


# Animate a scatter plot with 3 distributions - each in a seperate plot
def animate_scatter_2(frameno):
    global INDEX, normal, skewed, uniform, x_axis, axs

    mutual_change_2_cla()

    axs[0].scatter(x_axis, normal[INDEX], s=4, c='r', alpha=0.4,
                   label='normal')
    axs[1].scatter(x_axis, skewed[INDEX], s=4, color='b', alpha=0.4,
                   label='skewed')
    axs[2].scatter(x_axis, uniform[INDEX], s=4, color='g', alpha=0.4,
                   label='uniform')

    mutual_change_2()

    INDEX += 1
    return axs


# Animate a bar plot with 3 distributions
def animate_bar_2(frameno):
    global INDEX, normal, skewed, uniform, x_axis, axs

    mutual_change_2_cla()

    axs[0].bar(x_axis, normal[INDEX], color='r', alpha=0.4,
               label='normal')
    axs[1].bar(x_axis, skewed[INDEX], color='b', alpha=0.4,
               label='skewed')
    axs[2].bar(x_axis, uniform[INDEX], color='g', alpha=0.4,
               label='uniform')

    mutual_change_2()

    INDEX += 1
    return axs


# Animate a line plot with 3 distributions
def animate_plot_2(frameno):
    global INDEX, normal, skewed, uniform, x_axis, axs

    mutual_change_2_cla()

    axs[0].plot(x_axis, normal[INDEX], color='r', alpha=0.4, lw=1,
                label='normal')
    axs[1].plot(x_axis, skewed[INDEX], color='b', alpha=0.4, lw=1,
                label='skewed')
    axs[2].plot(x_axis, uniform[INDEX], color='g', alpha=0.4, lw=1,
                label='uniform')

    mutual_change_2()

    INDEX += 1
    return axs


# ============================================================
# 1 plot: sisplay a 2*3 grid.
# Column 1 for  distance, column 2 for  duration
# Row 1 for normal dist, row 2 for skewed and row 3 for uniform
# ============================================================


def mutual_code_3_cla():
    global axs

    axs[0, 0].cla()
    axs[0, 1].cla()
    axs[1, 0].cla()
    axs[1, 1].cla()
    axs[2, 0].cla()
    axs[2, 1].cla()


def mutual_code_3():
    global x_ticks, axs, fig

    axs[0, 0].set_xticks([])
    axs[0, 1].set_xticks([])
    axs[1, 0].set_xticks([])
    axs[1, 1].set_xticks([])
    axs[2, 0].set_xticks(x_ticks)
    axs[2, 1].set_xticks(x_ticks)

    axs[0, 0].set_ylabel("Normal POI Risk")
    axs[1, 0].set_ylabel("Skewed POI Risk")
    axs[2, 0].set_ylabel("Uniform POI Risk")
    # fig.supylabel("POI Risk")

    axs[2, 0].set_xlabel("Trip distance (Km)")

    axs[2, 1].set_xlabel("Trip Duration (minutes)")

    axs[0, 0].set_xlim([-0.01, 35])
    axs[0, 0].set_ylim([-0.01, 1.01])
    axs[0, 1].set_xlim([-0.01, 35])
    axs[0, 1].set_ylim([-0.01, 1.01])
    axs[1, 0].set_xlim([-0.01, 35])
    axs[1, 0].set_ylim([-0.01, 1.01])
    axs[1, 1].set_xlim([-0.01, 35])
    axs[1, 1].set_ylim([-0.01, 1.01])
    axs[2, 0].set_xlim([-0.01, 35])
    axs[2, 0].set_ylim([-0.01, 1.01])
    axs[2, 1].set_xlim([-0.01, 35])
    axs[2, 1].set_ylim([-0.01, 1.01])

    fig.suptitle("Distance and Duration Versus POI Risk at hour " + str(INDEX))


def dur_and_dist_complete_animate_bar(frameno):
    global INDEX, dur_normal, dur_skewed, dur_uniform, dist_x_axis, dur_x_axis, dist_normal, dist_skewed, dist_uniform, axs

    mutual_code_3_cla()

    axs[0, 0].bar(dist_x_axis, dist_normal[INDEX], alpha=0.4, color='r', label="normal")
    axs[0, 1].bar(dur_x_axis, dur_normal[INDEX], color='b', alpha=0.4, label="normal")

    axs[1, 0].bar(dist_x_axis, dist_skewed[INDEX], alpha=0.4, color='r', label="skewed")
    axs[1, 1].bar(dur_x_axis, dur_skewed[INDEX], color='b', alpha=0.4, label="skewed")

    axs[2, 0].bar(dist_x_axis, dist_uniform[INDEX], alpha=0.4, color='r', label="uniform")
    axs[2, 1].bar(dur_x_axis, dur_uniform[INDEX], color='b', alpha=0.4, label="uniform")

    mutual_code_3()

    INDEX += 1
    return axs


def dur_and_dist_complete_animate_scatter(frameno):
    global INDEX, dur_normal, dur_skewed, dur_uniform, dist_x_axis, dur_x_axis, dist_normal, dist_skewed, dist_uniform, axs

    mutual_code_3_cla()

    axs[0, 0].scatter(dist_x_axis, dist_normal[INDEX], s=4, c='r', alpha=0.4, label="normal")
    axs[0, 1].scatter(dur_x_axis, dur_normal[INDEX], s=4, c='r', alpha=0.4, label="normal")

    axs[1, 0].scatter(dist_x_axis, dist_skewed[INDEX], s=4, color='b', alpha=0.4, label="skewed")
    axs[1, 1].scatter(dur_x_axis, dur_skewed[INDEX], s=4, color='b', alpha=0.4, label="skewed")

    axs[2, 0].scatter(dist_x_axis, dist_uniform[INDEX], s=4, color='g', alpha=0.4, label="uniform")
    axs[2, 1].scatter(dur_x_axis, dur_uniform[INDEX], s=4, color='g', alpha=0.4, label="uniform")

    mutual_code_3()

    INDEX += 1
    return axs


def dur_and_dist_complete_animate_plot(frameno):
    global INDEX, dur_normal, dur_skewed, dur_uniform, dist_x_axis, dur_x_axis, dist_normal, dist_skewed, dist_uniform, axs

    mutual_code_3_cla()

    axs[0, 0].plot(dist_x_axis, dist_normal[INDEX], alpha=0.4, color='r', label="normal", lw=1)
    axs[0, 1].plot(dur_x_axis, dur_normal[INDEX], color='b', alpha=0.4, label="normal", lw=1)

    axs[1, 0].plot(dist_x_axis, dist_skewed[INDEX], alpha=0.4, color='r', label="skewed", lw=1)
    axs[1, 1].plot(dur_x_axis, dur_skewed[INDEX], color='b', alpha=0.4, label="skewed", lw=1)

    axs[2, 0].plot(dist_x_axis, dist_uniform[INDEX], alpha=0.4, color='r', label="uniform", lw=1)
    axs[2, 1].plot(dur_x_axis, dur_uniform[INDEX], color='b', alpha=0.4, label="uniform", lw=1)

    mutual_code_3()

    INDEX += 1
    return axs


# ============================================================
# 3 plots in 1 row, each relates to a different distribution
# ============================================================


def mutual_change_4_cla():
    global axs

    axs[0].cla()
    axs[1].cla()


def mutual_change_4():
    global title, INDEX, x_ticks, axs, fig

    plt.suptitle(title + str(INDEX))

    axs[0].set_xlabel('Distance (Km)')
    axs[1].set_xlabel('Duration (minutes)')

    axs[0].set_ylabel('Path risk')

    axs[0].set_xticks(x_ticks)
    axs[1].set_xticks(x_ticks)

    axs[0].set_xlim([-0.01, 32])
    axs[0].set_ylim([-0.01, 23])
    axs[1].set_xlim([-0.01, 32])
    axs[1].set_ylim([-0.01, 23])


# Animate a scatter plot with 3 distributions - each in a seperate plot
def dur_and_dist_complete_animate_scatter_2(frameno):
    global INDEX, dist_path_risks, dur_path_risks, risk_dist_x_axis, risk_dur_x_axis, axs

    mutual_change_4_cla()

    axs[0].scatter(risk_dist_x_axis, dist_path_risks[INDEX], s=4, c='r', alpha=0.4)
    axs[1].scatter(risk_dur_x_axis, dur_path_risks[INDEX], s=4, color='b', alpha=0.4)

    mutual_change_4()
    INDEX += 1

    return axs


# Animate a bar plot with 3 distributions
def dur_and_dist_complete_animate_bar_2(frameno):
    global INDEX, dur_path_risks, dist_path_risks, risk_dist_x_axis, risk_dur_x_axis, axs

    mutual_change_4_cla()

    axs[0].bar(risk_dist_x_axis, dist_path_risks[INDEX], color='r', alpha=0.4)
    axs[1].bar(risk_dur_x_axis, dur_path_risks[INDEX], color='b', alpha=0.4)

    mutual_change_4()
    INDEX += 1

    return axs


# Animate a line plot with 3 distributions
def dur_and_dist_complete_animate_plot_2(frameno):
    global INDEX, dur_path_risks, dist_path_risks, risk_dist_x_axis, risk_dur_x_axis, axs

    mutual_change_4_cla()

    axs[0].plot(risk_dist_x_axis, dist_path_risks[INDEX], color='r', alpha=0.4, lw=1)
    axs[1].plot(risk_dur_x_axis, dur_path_risks[INDEX], color='b', alpha=0.4, lw=1)

    mutual_change_4()

    INDEX += 1
    return axs

# =================================================================================
# Begin Evaluation
# =================================================================================

file = pd.read_csv('static/auxiliary_files/computed_queries3.csv')

dur = []
dist = []
path_r = []
normal_poi_risks = []
skewed_poi_risks = []
uniform_poi_risks = []
by_foot = []

for index, row in file.iterrows():
    dur.extend(ast.literal_eval(row['duration']))
    dist.extend(ast.literal_eval(row['dist']))

    LEN = len(ast.literal_eval(row['duration']))

    if 'car' in row['query']:
        by_foot.append([False] * LEN)
    else:
        by_foot.append([True] * LEN)

    path_r.extend(ast.literal_eval(row['path_risks']))

    normal_poi_risks.extend([[row['normal_risks' + str(i)] for i in range(168)]] * LEN)
    skewed_poi_risks.extend([[row['skewed_risks' + str(i)] for i in range(168)]] * LEN)
    uniform_poi_risks.extend([[row['uniform_risks_' + str(i)] for i in range(168)]] * LEN)

by_foot = list(itertools.chain.from_iterable(by_foot))

print(len(dur), len(dist), len(path_r), len(normal_poi_risks), len(skewed_poi_risks), len(uniform_poi_risks),
      len(by_foot))
df = pd.DataFrame({'dist': dist, 'duration': dur,
                   'path_risks': path_r, 'normal_hourly_poi_risks': normal_poi_risks,
                   'skewed_hourly_poi_risks': skewed_poi_risks, 'uniform_hourly_poi_risks': uniform_poi_risks,
                   'by_foot': by_foot})

# ========== Sort bu distance ============
file_sorted_by_distance = df.sort_values(by=['dist'], ignore_index=True, ascending=True)

dist_normal = np.array(file_sorted_by_distance['normal_hourly_poi_risks'].tolist()).T
dist_skewed = np.array(file_sorted_by_distance['skewed_hourly_poi_risks'].tolist()).T
dist_uniform = np.array(file_sorted_by_distance['uniform_hourly_poi_risks'].tolist()).T

dist_x_axis = file_sorted_by_distance['dist'].tolist()

# ========== Sort bu Duration ============
file_sorted_by_duration = df.sort_values(by=['duration'], ignore_index=True, ascending=True)

dur_normal = np.array(file_sorted_by_duration['normal_hourly_poi_risks'].tolist()).T
dur_skewed = np.array(file_sorted_by_duration['skewed_hourly_poi_risks'].tolist()).T
dur_uniform = np.array(file_sorted_by_duration['uniform_hourly_poi_risks'].tolist()).T

dur_x_axis = file_sorted_by_duration['duration'].tolist()

# ============ Process path risks ============

dist_path_risks = np.array(file_sorted_by_distance.loc[file_sorted_by_distance['by_foot']]['path_risks'].tolist()).T
risk_dist_x_axis = file_sorted_by_distance.loc[file_sorted_by_distance['by_foot']]['dist'].tolist()

dur_path_risks = np.array(file_sorted_by_duration.loc[file_sorted_by_duration['by_foot']]['path_risks'].tolist()).T
risk_dur_x_axis = file_sorted_by_duration.loc[file_sorted_by_duration['by_foot']]['duration'].tolist()

# =================================================================================
# ============================================================
# Go through the first and second round of plots for DISTANCE
# ============================================================
# =================================================================================

normal = dist_normal
uniform = dist_uniform
skewed = dist_skewed

title = "Distance Versus Risk at hour "
x_title = "Trip distance (Km)"
x_ticks = [i*2 for i in range(17)]
x_axis = dist_x_axis

# ---------------
fig = plt.figure()
axis = plt.axes(xlim=[-0.1,32], ylim=[-0.1,1.1])

INDEX = 0
anim = animation.FuncAnimation(fig, animate_bar,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/distance_vs_risk_bar.mp4', writer=writer)

print("Finish dist 1")
INDEX = 0
anim = animation.FuncAnimation(fig, animate_scatter,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/distance_vs_risk_scatter.mp4', writer=writer)

print("Finish dist 2")
INDEX = 0
anim = animation.FuncAnimation(fig, animate_plot,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/distance_vs_risk_plot.mp4', writer=writer)

print("Finish dist 3")
# ---------------

fig, axs = plt.subplots(1,3)
x_ticks = [i*7 for i in range(5)]

INDEX = 0
anim = animation.FuncAnimation(fig, animate_bar_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/distance_vs_risk_bar_2.mp4', writer=writer)
print("Finish dist 4")

INDEX = 0
anim = animation.FuncAnimation(fig, animate_scatter_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/distance_vs_risk_scatter_2.mp4', writer=writer)
print("Finish dist 5")

INDEX = 0
anim = animation.FuncAnimation(fig, animate_plot_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/distance_vs_risk_plot_2.mp4', writer=writer)
print("Finish dist 6")
# =================================================================================
# ============================================================
# Go through the first and second round of plots for Duration
# ============================================================
# =================================================================================

INDEX = 0
normal = dur_normal
uniform = dur_uniform
skewed = dur_skewed

title = "Duration Versus Risk at hour "
x_title = "Trip duration (Km)"
x_ticks = [i*2 for i in range(17)]
x_axis = dur_x_axis

# ---------------
fig = plt.figure()
axis = plt.axes(xlim=[-0.1,32], ylim=[-0.1,1.1])

anim = animation.FuncAnimation(fig, animate_bar,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_vs_risk_bar.mp4', writer=writer)
print("Finish dur 1")

INDEX = 0
anim = animation.FuncAnimation(fig, animate_scatter,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_vs_risk_scatter.mp4', writer=writer)
print("Finish dur 2")

INDEX = 0
anim = animation.FuncAnimation(fig, animate_plot,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_vs_risk_plot.mp4', writer=writer)
print("Finish dur 3")
# ---------------

fig, axs = plt.subplots(1,3)
x_ticks = [i*7 for i in range(5)]
INDEX = 0

anim = animation.FuncAnimation(fig, animate_bar_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_vs_risk_bar_2.mp4', writer=writer)
print("Finish dur 4")

INDEX = 0
anim = animation.FuncAnimation(fig, animate_scatter_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_vs_risk_scatter_2.mp4', writer=writer)
print("Finish dur 5")

INDEX = 0
anim = animation.FuncAnimation(fig, animate_plot_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_vs_risk_plot_2.mp4', writer=writer)
print("Finish dur 6")

# =================================================================================
# ============================================================
# Go through third round for both distance and duration
# ============================================================
# =================================================================================

plt.clf()
x_ticks = [i*7 for i in range(5)]
title = "Distance and Duration Versus POI Risk at hour "

fig, axs = plt.subplots(3,2)

INDEX = 0
anim = animation.FuncAnimation(fig, dur_and_dist_complete_animate_bar,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_and_duration_vs_risk_bar_complete.mp4', writer=writer)
print("Finish dist + dur 1")

INDEX = 0
anim = animation.FuncAnimation(fig, dur_and_dist_complete_animate_scatter,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_and_duration_vs_risk_scatter_complete.mp4', writer=writer)
print("Finish dist + dur 2")

INDEX = 0
anim = animation.FuncAnimation(fig, dur_and_dist_complete_animate_plot,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_and_duration_vs_risk_plot_complete.mp4', writer=writer)
print("Finish dist + dur 3")

# =================================================================================
# ============================================================
# Go through third round for both distance and duration for path risks
# ============================================================
# =================================================================================

plt.clf()
x_ticks = [i*7 for i in range(5)]
title = "Distance and Duration Versus Path Risk at hour "
fig, axs = plt.subplots(1,2)

INDEX = 0
anim = animation.FuncAnimation(fig, dur_and_dist_complete_animate_bar_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_and_duration_vs_risk_bar_complete_path.mp4', writer=writer)
print("Finish dist + dur 4")

INDEX = 0
anim = animation.FuncAnimation(fig, dur_and_dist_complete_animate_scatter_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_and_duration_vs_risk_scatter_complete_path.mp4', writer=writer)
print("Finish dist + dur 4")

INDEX = 0
anim = animation.FuncAnimation(fig, dur_and_dist_complete_animate_plot_2,
                               repeat=False, blit=False, frames=SIZE-1)
anim.save('vis/duration_and_duration_vs_risk_plot_complete_path.mp4', writer=writer)
print("Finish dist + dur 5")
