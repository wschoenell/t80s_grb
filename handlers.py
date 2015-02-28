
'''
    pygcn handlers to GRBs @ T80S
'''
import logging
import urllib
import ephem
import lxml
import time
from VOEventLib import Vutil as VOEventTools
import voevent2html
from xoxota import send_telegram

__author__ = 'william'

configuration = {'events_dir': '/var/www/html/events/', 'telegram_ip': '127.0.0.1', 'telegram_peer': 'alerts',
                 'events_webdir': 'http://192.168.20.105/events/',
                 'observatory.lon': '-70:48:20.48', 'observatory.lat': '-30:10:04.31', 'observatory.elevation': 2187,
                 # 'packet_types': range(1000), 'min_grb_alt': -100} #.523598776, }
                 'packet_types': [60, 61, 62, 63, 64, 65], 'min_grb_alt': .523598776, }

# Init Observatory Ephem calculator.
observatory = ephem.Observer()
observatory.lon = configuration['observatory.lon']
observatory.lat = configuration['observatory.lat']
observatory.elevation = configuration['observatory.elevation']
grb = ephem.FixedBody()
grb._ra, grb._dec = 10, 10
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


def t80s_handler(payload, root):
    # Check if it is a real GRB
    ra, dec = float(
        root.find("./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C1").text), float(
        root.find("./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C2").text)
    description = root.find("./Why/Inference/Concept").text
    packet_type = int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])
    grb._ra, grb._dec = ra, dec
    grb.compute(observatory)
    # Conditions to pull the observation trigger
    if grb.alt >= configuration['min_grb_alt'] and packet_type in configuration['packet_types']:
        link = archive(payload, root)
        msg = 'GRB ALERT - %s - ra: %3.2f, dec: %3.2f, alt: %i deg - %s' % (description, ra, dec,
                                                                               int(grb.alt * 57.2957795), link)
        send_telegram(configuration['telegram_peer'], msg)


def archive(payload, root):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""
    ivorn = root.attrib['ivorn']
    event_file = ivorn.strip('ivo://nasa.gsfc.gcn/').replace('#', '_') #urllib.quote_plus(( ))
    filename_raw = "%s/raw/%s.xml" % (configuration['events_dir'], event_file)
    filename_html = "%s/html/%s.html" % (configuration['events_dir'], event_file)
    html = voevent2html.format_to_string(VOEventTools.parseString(payload))
    with open(filename_html, "w") as f:
       f.write(html)
    with open(filename_raw, "w") as f:
       f.write(payload)
    logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)

    return '%s/html/%s.html' % (configuration['events_webdir'], event_file)

if __name__ == '__main__':

    configuration['events_dir'] = './events/'

    example_file = 'examples/SWIFT_bat_position_v2.0_example.xml'
    root = lxml.etree.parse(example_file).getroot()
    payload = payload = ''.join(open(example_file).readlines())

    t80s_handler(payload, root)