from setuptools import setup

version = '0.0.3'
name = 'gnsstime'
short_description = 'Extended datetime for the gnss analysis.'
long_description = """\
`gnsstime` is a extended datetime for the gnss analysis.

Requirements
------------
* Python 3.3 or later (not support 2.x)

History
-------
0.0.3 (2014-12-04)
~~~~~~~~~~~~~~~~~~
* first release

Example
-------
::

    >>> import gnsstime as gt
    >>> gt1 = gt.gnsstime(2011, 1, 1)
    >>> print('')
    >>> print('gpscal()                        -> ', gt1.gpscal())
    >>> print('gpscal(2013,12,31)              -> ', gt1.gpscal(2013, 12, 31))
    >>> print('gpscal(ymd='2013/12/31')        -> ', gt1.gpscal(ymd='2013/12/31'))
    >>> print('gpscal(dt.datetime(2013,12,31)) -> ', gt1.gpscal(dt.datetime(2013, 12, 31)))
    gpscal()                        ->  (1, 1616, 6)
    gpscal(2013,12,31)              ->  (365, 1773, 2)
    gpscal(ymd='2013/12/31')        ->  (365, 1773, 2)
    gpscal(dt.datetime(2013,12,31)) ->  (365, 1773, 2)

    >>> print('date    :', gt1.isoformat())
    >>> print('doy     :', gt1.doy)
    >>> print('gpsw    :', gt1.gpsw)
    >>> print('gpswd   :', gt1.gpswd)
    >>> print('gpst    :', gt1.gpst.isoformat())
    >>> print('leapsec :', gt1.leapsec)
    date    : 2011-01-01T00:00:00
    doy     : 1
    gpsw    : 1616
    gpswd   : 6
    gpst    : 2010-12-31T23:59:45
    leapsec : -15

    >>> import datetime as dt
    >>> print('gt1 + dt.timedelta(days=2) :', (gt1 + dt.timedelta(days=2)).isoformat())
    >>> print('gt1 - dt.timedelta(days=2) :', (gt1 - dt.timedelta(days=2)).isoformat())
    gt1 + dt.timedelta(days=2) : 2011-01-03T00:00:00
    gt1 - dt.timedelta(days=2) : 2010-12-30T00:00:00

"""

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: Python Software Foundation License",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['gps', 'gnss', 'datetime'],
    author='Satoshi Kawamoto',
    author_email='satoshi.pes@gmail.com',
    url='None',
    license='PSL',
    #scripts = ['gnsstime.py']
    py_modules=['gnsstime']
)
