'''
    pygcn handlers to GRBs @ T80S
'''
import logging
import os

import ephem
import lxml
import time

import voevent2html
from VOEventLib import Vutil as VOEventTools
from astropysics_obstools import get_SFD_dust
from util.gcn_util import get_notice_types_dict
from util.send_email import send_html_email
from simple_telegram_messenger import send_telegram_message

__author__ = 'william'

dust_file = str(os.path.dirname(__file__) + '/../data/SFD_dust_1024_%s.fits')


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


def archive(payload, root, events_dir='./', www_dir=''):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""
    ivorn = root.attrib['ivorn']
    event_file = ivorn.strip('ivo://nasa.gsfc.gcn/').replace('#', '_')  # urllib.quote_plus(( ))
    filename_raw = "%s/raw/%s.xml" % (events_dir, event_file)
    filename_html = "%s/html/%s.html" % (events_dir, event_file)
    html = voevent2html.format_to_string(VOEventTools.parseString(payload))
    with open(filename_html, "w") as f:
        f.write(html)
    with open(filename_raw, "w") as f:
        f.write(payload)
    logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)

    return '%s/html/%s.html' % (www_dir, event_file), html


def T80SHandlerClass(configuration, observatory):
    class T80SHandler(object):

        def __init__(self, payload, root):
            t0 = time.time()
            # Check if it is a real GRB
            ra, dec = float(
                root.find(
                    "./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C1").text), float(
                root.find("./WhereWhen/ObsDataLocation/ObservationLocation/AstroCoords/Position2D/Value2/C2").text)
            packet_type = int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])

            grb = ephem.FixedBody()
            grb._ra, grb._dec = ra, dec
            grb.compute(observatory)
            # Conditions to pull the observation trigger
            # TODO: implement min_moon_distance
            if grb.alt >= configuration['min_grb_alt'] and packet_type in configuration['packet_types']:
                gal_coord = ephem.Galactic(grb)
                ebv = get_SFD_dust([gal_coord.long], [gal_coord.lat], dustmap=dust_file, interpolate=False)
                if ebv < configuration['max_extinction']:
                    print 'Total analysis time: %6.3f secs' % (time.time() - t0)
                    link, html = archive(payload, root, configuration['events_dir'], configuration['events_wwwdir'])
                    msg = 'GRB ALERT - %s - ra: %3.2f, dec: %3.2f, alt: %i deg, E_BV: %3.2f - %s' % (
                        get_notice_types_dict()[packet_type],
                        ra, dec, int(grb.alt * 57.2957795),
                        ebv, link)
                    for chat_id in configuration["telegram_chat_ids"]:
                        send_telegram_message(configuration['telegram_token'], chat_id, msg)
                    for to in configuration['to_emails'].split(','):
                        send_html_email(configuration['from_email'], to, 'GRB ALERT', html,
                                        configuration['smtp_server'],
                                        use_tls=configuration['smtp_usetls'] == "True",
                                        username=configuration['smtp_user'],
                                        password=configuration['smtp_password'])

    return T80SHandler


if __name__ == '__main__':
    import json

    with open("config_production.json") as fp:
        configuration = json.load(fp)

    # TODO: remove this. only for tests.
    configuration.update({
        'packet_types': range(1000), 'min_grb_alt': -100, 'max_extinction': 100.0})
    # 'packet_types': [60, 61, 62, 63, 64, 65], 'min_grb_alt': .523598776, 'max_extinction': 100.0}

    # TODO: Add extinction check
    # TODO: Add to Zenoss pygcn-list check

    # Init Observatory Ephem calculator.
    observatory = ephem.Observer()
    observatory.lon = configuration['observatory.lon']
    observatory.lat = configuration['observatory.lat']
    observatory.elevation = configuration['observatory.elevation']
    grb = ephem.FixedBody()
    grb._ra, grb._dec = 10, 10
    grb.compute(observatory)

    example_file = 'examples/SWIFT_bat_position_v2.0_example.xml'
    root = lxml.etree.parse(example_file).getroot()
    payload = payload = ''.join(open(example_file).readlines())

    h = T80SHandlerClass(configuration, observatory)
    h(payload, root)
