#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

# x = np.array([3,5,7,1,9,8,6,6])
# y = np.array([2,1,5,10,100,6])
# TOWall = np.array([9, 3, 2, 1, 4, 5, 6, 7, 8, 10])
# TOW = np.array([3, 2, 7, 4, 10, 8])
# CN0 = np.array([50.5, 51.2, 50.7, 51.2, 49.5, 52.3])

TOWall = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
TOW = np.array([2, 3, 4, 7, 8, 10])
CN0 = np.array([50.5, 51.2, 50.7, 51.2, 49.5, 52.3])

print('TOWall = %s' % TOWall)
print('TOW = %s' % TOW)
print('CN0 = %s\n' % CN0)

index = np.argsort(TOWall)
sorted_TOWall = TOWall[index]
sorted_TOW = TOW[np.argsort(TOW)]

print('sorted_TOWall = %s' % sorted_TOWall)
print('sorted_TOW = %s' % sorted_TOW)

sorted_index = np.searchsorted(sorted_TOWall, TOW)
print('sorted_index = %s' % sorted_index)

# TOWindex = np.take(index, sorted_index, mode="clip")
# print('TOWindex = %s' % TOWindex)

# mask = TOWall[TOWindex] != TOW
# print('mask = %s' % mask)

# result = np.ma.array(TOWindex, mask=mask)
# print('result = %s' % result)

CN0new = np.zeros(np.size(sorted_TOWall))
CN0new.fill(np.nan)  # = CN0new * np.nan
print('CN0new = %s' % CN0new)

for idx, val in enumerate(sorted_index):
    print idx, val
    CN0new[val] = CN0[idx]

print('CN0new = %s\n' % CN0new)

# y = np.ma.masked_values(TOWall, TOW)
# print('y.mask = %s' % y.mask)
# print('y.data = %s' % y.data)
# print('y = %s' % y)

# plt.style.use('BEGPIOS')
plt.style.use('ggplot')
plt.figure(1)

plt.plot(TOWall, CN0new, 'ro-')
plt.show()
