import sys
import logging
import subprocess
import os
import sys
import re
from gvm.connections import UnixSocketConnection
from gvm.errors import GvmError
from gvm.protocols.latest import Gmp
from gvm.transforms import EtreeTransform
from gvm.xml import pretty_print
from pathlib import Path
from base64 import b64decode

#xpath reference: https://www.w3schools.com/xml/xml_xpath.asptry:


def run():
    logging.basicConfig(filename='openvas-error.log', level=logging.ERROR)
    logging.basicConfig(filename='openvas-debug.log', level=logging.DEBUG)
    path = '/usr/local/var/run/gvmd.sock'
    connection = UnixSocketConnection(path=path)
    transform = EtreeTransform()
    gmp = Gmp(connection=connection, transform=transform)
    config_id = ''
    target_id = ''
    task_id = ''
    scanner_id = ''
    username = 'admin'
    password = 'admin'
    ID = int(sys.argv[1])
    with gmp:
        response = gmp.get_version()
        #pretty_print(response)

    try:
        tasks = []
        with gmp:
            gmp.authenticate(username, password)
            tasks_xml_response = gmp.get_tasks()
            #pretty_print(tasks_xml_response)
        for task_xml in tasks_xml_response.xpath('task'):
            #pretty_print(task_xml)
            config_id_list = task_xml.xpath('config/@id')
            scanner_id_list = task_xml.xpath('scanner/@id')
            target_id_list = task_xml.xpath('target/@id')
            target_name_list = task_xml.xpath('target/name/text()')
            task_id_list = task_xml.xpath('@id')
            config_id = config_id_list[0]
            scanner_id = scanner_id_list[0]
            target_id = target_id_list[0]
            task_id = task_id_list[0]
            print('task_id: ' + task_id)
            #print('config_id: ' + config_id_list[0])
            #print('scanner_id: ' + scanner_id_list[0])
            #print('target_id: ' + target_id_list[0])
            #print('target_name :' + target_name_list[0])
    except GvmError as e:
        print(e)

    try:
        with gmp:
            gmp.authenticate(username, password)
            #create_target_response = gmp.create_target('test2',hosts='192.123.34.12')
            #pretty_print(create_target_response)
    except GvmError as e:
        print(e)
    try:
        with gmp:
            gmp.authenticate(username, password)
            #response = gmp.create_task('task4',config_id,'2cab66ce-7840-46f6-928c-35f1bab5e12f',scanner_id)
            #pretty_print(response)
    except GvmError as e:
        print(e)
    try:
        with gmp:
            gmp.authenticate(username, password)
            #response = gmp.start_task('4f86d690-2ca3-420c-8380-26a2e782e620')
            #pretty_print(response)
    except GvmError as e:
        print(e)
    try:
        with gmp:
            gmp.authenticate(username, password)
            report_id = ['93333b46-7813-4ea9-bbe8-868029fda036',
                         '36a9a452-9979-4239-a533-4de23e1e236d', 
                         'd41261ad-f9a2-4af0-b439-9d289398d3cc', 
                         'ac0b7916-1a38-438d-8826-edded98dca59',
                         'b656f9b4-7f77-4cb5-b61a-73eeca77377a',
                         '94108f28-dea5-4446-bf25-32ef3768f70b',
                         '40d166b5-7f5b-49d0-8ed1-12d090ff585a',
                         'b3e3523f-ea01-46fd-9a71-a9eda9fd36f7',
                         '19b9e683-1f9d-4c51-9004-3f9f93aa2799']
            pdf_format_id = 'c402cc3e-b531-11e1-9163-406186ea4fc5'
            response = gmp.get_report(
                report_id[ID], report_format_id=pdf_format_id)
            report_element = response[0]
            # get the full content of the report element
        content = "".join(report_element.itertext())
        split_content = content.split('PDF', 1)
        print(len(split_content))
        pdf_content = split_content[1]
        print(len(pdf_content))
        non_pdf_content = split_content[0]
        print(len(non_pdf_content))
        with open('OpenvasReports/output' + str(ID), 'w+') as output:
            output.write(content)
        with open('OpenvasReports/outputpdf' + str(ID), 'w+') as output:
            output.write(pdf_content)
        with open('OpenvasReports/outputnonpdf' + str(ID), 'w+') as output:
            output.write(non_pdf_content)
        #print(content[15:])
        # convert content to 8-bit ASCII bytes
        binary_base64_encoded_pdf = pdf_content.encode('ascii')
        binary_pdf = b64decode(binary_base64_encoded_pdf)
        print('==============================================================================================')
        pdf_path = Path('OpenvasReports/test' + str(ID) + '.pdf').expanduser()
        pdf_path.write_bytes(binary_pdf)

            #report_id = '635bfc51-8d8a-4cc5-8c82-764b9
        #os.system('ls')
        #pretty_print(response)
        #print(content[75:])
        #75
        #reports_xml = gmp.get_report('484cb912-13dc-4646-8d85-0994dc41e735')
        #for report_xml in reports_xml.xpath('report'):
        #owner = report_xml.xpath('owner/name/text()')
        #pretty_print(report_xml)
        #print('==========================================================================================================')
        #print("Owner: " + owner[0])
        #for result_xml in report_xml.xpath('report/result'):
        #tags = result_xml.xpath('nvt/tags/text()')
        #print(tags[0])
        #pretty_print(response)
    except GvmError as e:
        print(e)
    try:
        with gmp:
            gmp.authenticate(username, password)
            #response = gmp.get_report_formats()
            #pretty_print(response)
    except GvmError as e:
        print(e)

#ignore missing padding causing by missing bytes
#https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
def b64decodeNew(data, altchars=b'+/'):
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    return b64decode(data, altchars)

def test()
    print('1')

if __name__ == "__main__":
    run()
