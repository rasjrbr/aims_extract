from typing import List
from  aims.mytypes import *
import datetime as dt
import re
from dateutil import tz

def dump(dutylist: List[Duty]) -> str:
    dutylist.sort()
    output: List[str] = []
    for duty in dutylist:
        start, end = [X.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
                      for X in (duty.on, duty.off)]
        output.append("-" * 70)
        output.append("{:%d/%m/%Y}\nReport: {:%H:%M}".format(start, start))
        if duty.sectors:
            for sector in duty.sectors:
                sched_off, sched_on = [
                    X.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
                    for X in (sector.sched_off, sector.sched_on)]
                output.append("\n\t{}".format(sector.flightnum))
                output.append("\t{:%H:%M} - {:%H:%M}".format(sched_off, sched_on))
                output.append("\t{} - {}".format(sector.from_, sector.to))
            output.append("")
        else:
            output.append("\n\t{}\n\t{:%H:%M}-{:%H:%M}\n".format(
                duty.text, start, end))
        output.append("Off duty: {:%H:%M}".format(end))
    return "\n".join(output)
