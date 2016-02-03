#!/usr/bin/env python

import matplotlib.pyplot as plt

fig, ax1 = plt.subplots()

ax1 = fig.add_subplot(111)

ax1.plot(range(5), range(5))

ax1.grid(True)

ax2 = ax1.twiny()
ax1Xs = ax1.get_xticks()

ax2Xs = []
for X in ax1Xs:
    ax2Xs.append(X * 2)

ax2.set_xticks(ax1Xs)
ax2.set_xbound(ax1.get_xbound())
ax2.set_xticklabels(ax2Xs)

title = ax1.set_title("Upper x-axis ticks are lower x-axis ticks doubled!")
title.set_y(1.1)
fig.subplots_adjust(top=0.85)
plt.show()

fig.savefig("1.png")
