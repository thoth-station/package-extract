"""Functionality copied from kobo.

Even though copying code is not nice at all, this is better to have copied. Assuming naming
is mature and stable enough, it should be safe to have them there.

The original code can be found at:
  https://github.com/release-engineering/kobo/blob/master/kobo/rpmlib.py

Note we used code from Koji before, but that looks to be broken in some cases.
"""


def parse_nvra(nvra):
    """Split N-V-R.A[.rpm] into a dictionary.

    @param nvra: N-V-R:E.A[.rpm], E:N-V-R.A[.rpm], N-V-R.A[.rpm]:E or N-E:V-R.A[.rpm] string
    @type nvra: str
    @return: {name, version, release, epoch, arch}
    @rtype: dict
    """
    if "/" in nvra:
        nvra = nvra.split("/")[-1]

    epoch = ""
    for i in range(2):
        # run this twice to parse N-V-R.A.rpm:E and N-V-R.A:E.rpm
        if nvra.endswith(".rpm"):
            # strip .rpm suffix
            nvra = nvra[:-4]
        else:
            # split epoch (if exists)
            nvra, epoch = split_nvr_epoch(nvra)

    nvra_parts = nvra.rsplit(".", 1)
    if len(nvra_parts) != 2:
        raise ValueError("Invalid NVRA: %s" % nvra)

    nvr, arch = nvra_parts
    if "-" in arch:
        raise ValueError("Invalid arch '%s' in '%s'" % (arch, nvra))

    result = parse_nvr(nvr)
    result["arch"] = arch
    result["src"] = arch == "src"
    if epoch != "":
        result["epoch"] = epoch
    return result


def parse_nvr(nvre):
    """Split N-V-R into a dictionary.

    @param nvre: N-V-R:E, E:N-V-R or N-E:V-R string
    @type nvre: str
    @return: {name, version, release, epoch}
    @rtype: dict
    """
    if "/" in nvre:
        nvre = nvre.split("/")[-1]

    nvr, epoch = split_nvr_epoch(nvre)

    nvr_parts = nvr.rsplit("-", 2)
    if len(nvr_parts) != 3:
        raise ValueError("Invalid NVR: %s" % nvr)

    # parse E:V
    if epoch == "" and ":" in nvr_parts[1]:
        epoch, nvr_parts[1] = nvr_parts[1].split(":", 1)

    # check if epoch is empty or numeric
    if epoch != "":
        try:
            int(epoch)
        except ValueError:
            raise ValueError("Invalid epoch '%s' in '%s'" % (epoch, nvr))

    result = dict(zip(["name", "version", "release"], nvr_parts))
    result["epoch"] = epoch
    return result


def split_nvr_epoch(nvre):
    """Split nvre to N-V-R and E.

    @param nvre: E:N-V-R or N-V-R:E string
    @type nvre: str
    @return: (N-V-R, E)
    @rtype: (str, str)
    """
    if ":" in nvre:
        if nvre.count(":") != 1:
            raise ValueError("Invalid NVRE: %s" % nvre)

        nvr, epoch = nvre.rsplit(":", 1)
        if "-" in epoch:
            if "-" not in nvr:
                # switch nvr with epoch
                nvr, epoch = epoch, nvr
            else:
                # it's probably N-E:V-R format, handle it after the split
                nvr, epoch = nvre, ""
    else:
        nvr, epoch = nvre, ""

    return (nvr, epoch)
