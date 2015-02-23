__author__ = 'william'

'''
    pygcn handlers to GRBs @ T80S
'''

import os


import logging
import urllib

import ephem

from xml.etree import ElementTree
from VOEventLib import Vutil as VOEventTools
import voevent2html

observatory = ephem.Observer()
observatory.lon = '-70:48:20.48'
observatory.lat = '-30:10:04.31'
observatory.elevation = 2187

grb = ephem.FixedBody()

grb._ra = 10
grb._dec = 10
grb.compute(observatory)

def t80s_decorator(*notice_types):
    """Process only VOEvents whose integer GCN packet types are in
    `notice_types`. Should be used as a decorator, as in:

        import gcn.handlers
        import gcn.notice_types as n

        @gcn.handlers.include_notice_types(n.FERMI_GBM_GND_POS, n.FERMI_GBM_FIN_POS)
        def handle(payload, root):
            print 'Got a notice of type FERMI_GBM_GND_POS or FERMI_GBM_FIN_POS'
    """
    notice_types = frozenset(notice_types)

    def decorate(handler):
        def handle(payload, root):
            if int(root.find("./What/Param[@name='Packet_Type']").attrib['value']) in notice_types:
                handler(payload, root)

        return handle

    return decorate


#@t80s_decorator(tuple(range(0, 1000)))
def archive(payload, root):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""
    ivorn = root.attrib['ivorn']
    filename_raw = "events/raw/%s.xml" % urllib.quote_plus(ivorn)
    filename_html = "events/html/%s.html" % urllib.quote_plus(ivorn)
    ra, dec = float(
        root.find("./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C1").text), float(
        root.find("./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C2").text)
    description = root.find("./Why/Inference/Concept").text
    packet_type = int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])
    grb._ra, grb._dec = ra, dec
    grb.compute(observatory)
    # if grb.alt >= .523598776:   # > 30 degrees
    # if True:
    if packet_type in range(60,65):
        telegram = 'ra %6.3f, dec %6.3f, descr: %s' % (ra, dec, description)
        telegram += 'alt = %6.3f' % grb.alt
        print telegram
        print os.system('./telegram.sh SMAPS "%s"' % telegram)
        print payload
        html = voevent2html.format_to_string(VOEventTools.parseString(payload))
        with open(filename_html, "w") as f:
           f.write(html)
        with open(filename_raw, "w") as f:
           f.write(payload)
        logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)

