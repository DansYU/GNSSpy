from math import fabs, modf


def deg2dms(degs):
    neg = (degs < 0)
    degs = fabs(degs)
    degs, d_int = modf(degs)
    mins, m_int = modf(60 * degs)
    secs = 60 * mins
    # print '%03d %02d %06.3f' % (d_int, m_int, secs)
    return neg, d_int, m_int, secs

(NSEW, ddd, mm, ss) = deg2dms(50.50)
print '%s %03d %02d %06.3f' % (NSEW, ddd, mm, ss)
