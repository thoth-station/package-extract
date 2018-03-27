"""Functionality copied from Koji.

Even though copying code is not nice at all, this is better to have copied. Koji requires a bunch of dependencies
to be present including things like gcc. We actually do not need these just for these two functions. Assuming naming
is mature and stable enough, it should be safe to have them there.
"""


class KojiError(Exception):
    """An exception that would be raised by Koji."""


def parse_NVR(nvr):
    """split N-V-R into dictionary of data"""
    ret = {}
    p2 = nvr.rfind("-", 0)
    if p2 == -1 or p2 == len(nvr) - 1:
        raise KojiError("invalid format: %s" % nvr)
    p1 = nvr.rfind("-", 0, p2)
    if p1 == -1 or p1 == p2 - 1:
        raise KojiError("invalid format: %s" % nvr)
    ret['release'] = nvr[p2+1:]
    ret['version'] = nvr[p1+1:p2]
    ret['name'] = nvr[:p1]
    epochIndex = ret['name'].find(':')
    if epochIndex == -1:
        ret['epoch'] = ''
    else:
        ret['epoch'] = ret['name'][:epochIndex]
        ret['name'] = ret['name'][epochIndex + 1:]
    return ret


def parse_NVRA(nvra: str) -> dict:
    """split N-V-R.A.rpm into dictionary of data

    also splits off @location suffix"""
    parts = nvra.split('@', 1)
    location = None
    if len(parts) > 1:
        nvra, location = parts
    if nvra.endswith(".rpm"):
        nvra = nvra[:-4]
    p3 = nvra.rfind(".")
    if p3 == -1 or p3 == len(nvra) - 1:
        raise KojiError("invalid format: %s" % nvra)
    arch = nvra[p3+1:]
    ret = parse_NVR(nvra[:p3])
    ret['arch'] = arch
    if arch == 'src':
        ret['src'] = True
    else:
        ret['src'] = False
    if location:
        ret['location'] = location
    return ret
