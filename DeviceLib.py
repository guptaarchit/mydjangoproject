from telnetlib import Telnet
import time
import datetime
import re
import logging
import csv
import traceback
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','device_monitor.settings')
import django
django.setup()
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from shutil import move, copyfile
from device.models import Device, Device_log
import mysql.connector
import time
import random

# from plot_graph import plot_stats_and_send_mail


def initialize_logger():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    debug_hdlr = logging.FileHandler("debug.log")
    debug_hdlr.setLevel(logging.DEBUG)
    info_hdlr = logging.FileHandler("info.log")
    debug_hdlr.setLevel(logging.INFO)
    stream_hdlr = logging.StreamHandler()
    info_formatter = logging.Formatter('%(asctime)s-%(message)s')
    debug_formatter = logging.Formatter('%(asctime)s-  "%(filename)s:%(funcName)20s()%(lineno)s - %(levelname)s - %(message)s')
    stream_hdlr.setLevel(logging.DEBUG)
    info_hdlr.setFormatter(info_formatter)
    debug_hdlr.setFormatter(debug_formatter)
    stream_hdlr.setFormatter(debug_formatter)
    log.addHandler(info_hdlr)
    log.addHandler(stream_hdlr)
    stdout_log = open("stdout.log", 'w+')
    sys.stdout = stdout_log

def archive_logs(file_list, log_folder):
    log.info("Archiving logs")
    # Remove log handler from file to free up logs
    if not os.path.exists(log_folder):
        log.info("Creating directory %s" %log_folder)
        os.mkdir(log_folder)
    else:
        log.info("Log folder %s already exists " % log_folder)
    for hdlr in log.handlers[:]:
        log.removeHandler(hdlr)
        print hdlr.name
        hdlr.close()


    for file_name in file_list:
        if os.path.isfile(file_name):
            try:
                move(file_name, os.path.join(log_folder, file_name))
            except:
                traceback.print_exc()
                print "Exception with move, try copying file"
                try:
                    copyfile(file_name, os.path.join(log_folder, file_name))
                except:
                    traceback.print_exc()
    initialize_logger()

def sendMail(subject, body = "", file_list=[], email_list=""):
    username = "belden.automation"
    emailfrom = "belden.automation@incedoinc.com"
    #emailto = ["saurabh.baid@incedoinc.com"] + email_list.split(';')
    emailto = ["archit.gupta@incedoinc.com"]
    msg = MIMEMultipart()
    msg['From'] = emailfrom
    msg['To'] = ",".join(emailto)
    msg['Subject'] = subject

    part1 = MIMEText(body, 'plain')
    msg.attach(part1)
    for file_name in file_list:
        log.info("Attaching file %s" % file_name)
        with open(file_name) as fp:
            record = MIMEBase('application', 'octet-stream')
            record.set_payload(fp.read())
            encoders.encode_base64(record)
            record.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_name))
            msg.attach(record)
    log.info("Sending EMAIL..... %s" %subject)
    try:
        server = smtplib.SMTP('mail.incedoinc.com')
    except Exception, e:
        log.error("Error observed while connecting to Incedo mail server")
        log.error(repr(e))
    else:
        server.ehlo()
        server.login(username, 'tech54321!')
        server.sendmail(emailfrom, emailto, msg.as_string())
        server.quit()
        log.info("Mail Sent")

log = logging.getLogger()
logging.basicConfig()

class device(object):
    def __init__(self, ip, user_name, password):
        self.ip = ip
        self.user_name = user_name
        self.password = password
        self.cli = Telnet()
        self.prompt = '#\s+$'
        self.first_iteration = True
        self.sys_up_time = 0
        self.reboot_flag = False
        self.last_crash_record = 0
        self.crash = False

    def info_collect(self):
        pass

    def send_command(self, command, timeout=30):
        self.clear_buffer()
        self.cli.write(command + "\n")
        try:
            output = self.cli.expect([self.prompt], 30)
        except:
            log.info(self.cli.read_very_eager())
            raise AssertionError
        time.sleep(.1)
        return output[1].string

    def set_prompt(self):
        pass

    def set_pagination_off(self):
        pass

    def connect(self):
        self.cli.open(self.ip, timeout=10)
        self.cli.set_debuglevel(1)
        self.cli.expect(["Login:"], 10)
        self.cli.write(self.user_name + "\n")
        self.cli.expect(["Password:"], 10)
        self.cli.write(self.password + "\n")
        self.clear_buffer()
        self.set_prompt()
        self.set_pagination_off()
        self.clear_buffer()

    def disconnect(self):
        self.cli.close()

    def clear_buffer(self):
        log.info(self.cli.read_very_eager())

    def enable_event_logs(self):
        log.info("Enabling Event Logs")
        output = self.send_command("event show")
        for event_id in ["5-1", "5-2", "5-3", "5-4", "5-5", "5-6", "5-7"]:
            m = re.search("%s\s+\S+\s+Debug" % event_id, output)
            if not m:
                self.send_command("event set %s severity 7 local-mode persistent" % event_id)
                self.send_command("save")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            log(exc_type, exc_value, traceback)
            # return False # uncomment to pass exception through
        self.disconnect()

    def get_cpu_utilization(self):
        pass

    def get_memory_utilization(self):
        pass

class dx(device):
    def __init__(self, ip, user_name="manager", password="manager"):
        print "--------------TIME %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        super(dx, self).__init__(ip, user_name, password)

    def info_collect(self):
        list_of_commands = [
            'time show',
            'system show info',
            'system show status',
            'service trouble',
            'service file show',
            'service system-polling show',
            'service redirect-shell show',
            'service exception dump',
            'event show',
            'log show files',
            'log dump %s' %self.get_curernt_log_file()
        ]
        op = []
        for command in list_of_commands:
            log.info("INFO COLLECT: %s" %command)
            op.append(self.send_command(command, timeout=30))
        with open("info_collect.log", "w+") as log_file:
            log_file.writelines(op)

        log.info("INFO COLLECT: Info dumped into file")
        return "info_collect.log"

    def get_curernt_log_file(self):
        output = self.send_command('log show files')
        m = re.search("(.*\.log).*Active", output)

        if m is None:
            return ""
        else:
            log.info("Event Log file is %s" %m.group(1))
            return m.group(1)

    def set_pagination_off(self):
        self.send_command("terminal set paging n")

    def set_prompt(self):
        self.clear_buffer()
        output = self.send_command('system show info')
        try:
            self.prompt = re.search(r'Prompt\s+:\s+(.*)', output).group(1).strip() + "#"
        except:
            traceback.print_exc()
            self.prompt = self.prompt

        log.info("Prompt for %s set to %s" %(self.ip, self.prompt))

    def __enter__(self):
        self.connect()
        self.set_pagination_off()
        return self

    def get_cpu_utilization(self):
        output = self.send_command("system show status")
        m = re.search(r"System CPU Utilization\s+:\s+(-?\d+)%", output)
        log.info("CPU Utilization %s" %m.group(1))
        return m.group(1)

    def get_memory_utilization(self):
        output = self.send_command("system show status")
        m = re.search(r"System Memory Utilization\s+:\s+(-?\d+)%", output)
        log.info("Memory Utilization %s" % m.group(1))
        return m.group(1)

    def get_system_uptime(self):
        output = self.send_command("system show info")
        m = re.search(
            r"System Uptime : ((?P<days>\d+) day.?,)?\s?((?P<hours>\d+) hour.?,)?\s?((?P<minutes>\d+) minute.?)?\s?((?P<seconds>\d+) second.?)?",
            output)
        log.info("System Uptime %s" % m.group(0))
        if m.group('days') is not None and len(m.group('days')):
            days_in_sec = int(m.group('days')) * 24 * 60 * 60
        else:
            days_in_sec = 0

        if m.group('hours') is not None and len(m.group('hours')):
            hours_in_sec = int(m.group('hours')) * 60 * 60
        else:
            hours_in_sec = 0

        if m.group('minutes') is not None and len(m.group('minutes')):
            mins_in_sec = int(m.group('minutes')) * 60
        else:
            mins_in_sec = 0

        if m.group('seconds') is not None and len(m.group('seconds')):
            secs = int(m.group('seconds'))
        else:
            secs = 0
        sys_up_time_in_sec = days_in_sec + hours_in_sec + mins_in_sec + secs
        log.info("System up time converted to seconds %s" %sys_up_time_in_sec)
        return sys_up_time_in_sec

    def check_for_reboot(self):
        cur_up_time = self.get_system_uptime()
        if cur_up_time > self.sys_up_time:
            self.reboot_flag = True

    def get_last_crash_record(self):
        output = self.send_command("service exception dump")
        m = re.findall("Record #(\d+)", output)
        if not len(m):
            ret_val=0
        else:
            ret_val=int(m[-1])
        log.info("Last Crash Record ID: %s" % ret_val)
        return ret_val

    def get_crash_record_summary(self, record_no):
        output = self.send_command("service exception dump")
        m = re.search("Record #%d.*?TASK CHECK:(.*?)\n" %record_no, output, re.DOTALL)
        if m is None:
            ret_val = "No Crash Record Found"
        else:
            ret_val = m.group(1)
        log.info(ret_val)
        return ret_val


    def get_crash_record_details(self, record_no):
        output = self.send_command("service exception dump")
        m = re.search("(=+\n+.*Record #%d.*(\s|\n)+=+)\n+(\n|.)*?(={5,}|%s)" % (record_no, self.prompt), output)
        if m is None:
            ret_val = "No Crash Record Found"
        else:
            ret_val = m.group(0)
        log.info(ret_val)
        return ret_val

    def get_device_temperature(self):
        return ""
        log.debug("Connect to 49 machine")
        # Connect to Linux machine where iss console script is present
        try:
            linux_handle = Telnet()
            linux_handle.set_debuglevel(2)
            linux_handle.open("172.16.210.49")
            linux_handle.expect(["login:"], 10)
            linux_handle.write("automation" + "\n")
            linux_handle.expect(["Password:"], 10)
            linux_handle.write("automation" + "\n")
        except:
            log.info(traceback.format_exc())
            raise AssertionError, "Not able to connect to 49 machine"

        # Get last octet of device IP because issconsole uses this
        ip_last_octet = self.ip.split('.')[-1]
        iss_console_cmd = "issconsole %s " %ip_last_octet
        log.debug("iss console command %s" %iss_console_cmd)

        # Connect to issconsole
        try:
            linux_handle.write(iss_console_cmd + "\n")
            linux_handle.write("\n")
            match_idx = linux_handle.expect(["Login:", "MagnumDX#", "->"],5)[0]
            linux_handle.read_very_eager()

            # Login to DUT
            if match_idx == 0:
                linux_handle.write("manager" + "\n")
                linux_handle.expect(["Password:"],5)
                linux_handle.write("manager" + "\n")
                linux_handle.expect(["MagnumDX#"],5)
                linux_handle.read_very_eager()
        except:
            log.info(traceback.format_exc())
            raise AssertionError, "Not to do console login on Device using issconsole"

        # Start Service Shell
        try:
            if match_idx == 1 or match_idx == 0:
                linux_handle.write("service shell" + "\n")
                linux_handle.expect([".*\s+\(yes\/no\)\?"], 5)
                linux_handle.write("yes" + "\n")
                linux_handle.expect([".*\s+\(yes\/no\)\?"], 5)
                linux_handle.write("yes" + "\n")
                linux_handle.expect(["->"], 5)
                linux_handle.read_very_eager()
        except:
            log.info(traceback.format_exc())
            raise AssertionError, "Not able to start service shell"

        try:
            linux_handle.write("ds1631ZThermShow" + "\n")
            output = linux_handle.expect(["value = "], 5)
            output = output[1].string
            log.info("output:" + output)
            m = re.search(r"Temp in Celsius:\s+(\S+),", output)
            return m.group(1)
        except:
            log.info(traceback.format_exc())
            raise AssertionError, "Not able to get temperature of the system"




class dx940(dx):
    pass

class dx940e(dx):
    pass


if  __name__ == "__main__":
    initialize_logger()
    polling_interval_in_sec = 60
    conn = mysql.connector.connect(
        user='root',
        password='root',
        host='127.0.0.1',
        database='testdb')

    cur = conn.cursor()
    sql = """CREATE TABLE IF NOT EXISTS DEVICE (
             MODEL  CHAR(20) NOT NULL,
             IP  CHAR(20) NOT NULL,
             CPU FLOAT NOT NULL, 
              MEMORY FLOAT NOT NULL,
              UPTIME FLOAT NOT NULL,
              REBOOTED INT NOT NULL,
              CRASHED INT NOT NULL,
             INFORMATION CHAR(100) NOT NULL,
             CREATED TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP )"""

    cur.execute(sql)
    # conn.close()
    while 1:
        with open("device_list.csv") as f:
            device_list = f.readlines()

        device_obj_list = []
        for device_details in device_list:
            device_details = device_details.strip()
            device_type, ip, user_name, password = device_details.split(",")
            a = eval("%s" % device_type)
            device_obj_list.append(a(ip, user_name, password))
        base_time = time.time()
        for d in device_obj_list:
            log.info("================   Getting info for Device %s  =================" % d.ip)
            cpu = ""
            memory = ""
            comment = ""
            temp = ""
            device_crashed = False
            reboot_flag = False
            try:
                log.info("Connecting to device")
                d.connect()
                time.sleep(5)
                log.info("Getting CPU Utilization")
                temp = d.get_device_temperature()
                cpu = d.get_cpu_utilization()
                memory = d.get_memory_utilization()
                log.info("Getting system uptime")
                uptime = d.get_system_uptime()
                if uptime < d.sys_up_time:
                    reboot_flag = True
                else:
                    reboot_flag = False
                d.sys_up_time = uptime
                log.info("Fetching Last Crash Record")
                crash_record_id = d.get_last_crash_record()
                if False:
                # if d.first_iteration:
                    log.info("It was first iteration, so ignoring any CRASH DUMP already present")
                    d.last_crash_record = crash_record_id
                    d.first_iteration = False
                else:
                    if crash_record_id == d.last_crash_record:
                        log.info("No Crash detected")
                        device_crashed = False
                        if reboot_flag:
                            comment = "Device rebooted, but no crash dump"
                    elif crash_record_id < d.last_crash_record:
                        log.info("Old Crash information is deleted")
                        comment = "Old Crash information is deleted"
                        device_crashed = True
                        d.last_crash_record = crash_record_id
                    else:
                        comment = "CRASH DETECTED: " + str(d.get_crash_record_summary(crash_record_id)) + " RECORD ID=%d" %crash_record_id
                        log.info(comment)
                        device_crashed = True
                        d.last_crash_record = crash_record_id
                    if device_crashed:
                        log.info("Doing Info Collect")
                        attachment_file = d.info_collect()
                        subject = "CRASH DETECTED: %s" % d.ip
                        body = comment + "\n" + "%s" % d.get_crash_record_details(crash_record_id)
                        log.info("----------------------------------------------------------")

                        # sql = """INSERT INTO DEVICE(MODEL,IP,CPU,MEMORY,UPTIME,REBOOTED,CRASHED,INFORMATION)
                        #              VALUES ('DX940','10.20.6.193',%s,40,2000,600,1,'crashed')""" % (
                        # random.randint(0, 100))
                        #
                        # # try:
                        # # Execute the SQL command
                        #
                        # cur.execute(sql)
                        # sql = """INSERT INTO DEVICE(MODEL,IP,CPU,MEMORY,UPTIME,REBOOTED,CRASHED,INFORMATION)
                        #              VALUES ('DX940','10.20.6.190',%s,40,2000,600,1,'crashed')""" % (
                        # random.randint(0, 100))
                        # cur.execute(sql)
                        # # Commit your changes in the database
                        # conn.commit()

                        # device_logs_obj = Device_log.objects.get_or_create(MODEL=str(d.__class__.__name__), IP=d.ip, UPTIME=uptime, CRASHED=str(device_crashed), INFORMATION=comment)
                        log.info("----------------------------------------------------------")

                        # try:
                        #     sendMail(subject, body=body, file_list=[attachment_file, stats_file, "info.log", "stdout.log"], email_list=email_list)
                        # except:
                        #     log.error(traceback.format_exc())
                        #     log.error("Error while sending email")

                    log.info("Disconnect session")
                    d.disconnect()
            except:
                log.error(traceback.format_exc())
                log.error("Error while fetching device stats")
                try:
                    d.disconnect()
                except:
                    pass
                uptime = 0
                memory = 0
                cpu = 0
                comment = "Unable to connect device"
            log.info("Writing to CSV File")
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            log.info("################################################################################")
            # device_obj = Device.objects.get_or_create(MODEL=str(d.__class__.__name__), IP=d.ip, CPU=cpu, MEMORY=memory, UPTIME=uptime, REBOOTED=str(reboot_flag), CRASHED=str(device_crashed), INFORMATION=comment)
            sql = """INSERT INTO DEVICE(MODEL,IP,CPU,MEMORY,UPTIME,REBOOTED,CRASHED,INFORMATION)
                         VALUES ('%s','%s',%s,%s,%s,%s,%s,'%s')""" % (str(d.__class__.__name__), d.ip, cpu, memory, uptime, str(reboot_flag), str(device_crashed),comment)

            # try:
            # Execute the SQL command

            cur.execute(sql)
            # Commit your changes in the database
            conn.commit()
            log.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            query = ("SELECT IP,CPU, CREATED FROM DEVICE")
            # hire_start = date(1999, 1, 1)
            # hire_end = date(1999, 12, 31)
            cur.execute(query)
            print cur
            for (ip_val, cpu_val, created_val) in cur:
                str1 = "{}, {}, {}".format(ip_val, cpu_val, created_val)
                log.info(str1)
            log.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            log.info("################################################################################")
        # try:
        #     with open(stats_file, 'ab+') as s:
        #         csv.writer(s).writerow([timestamp,d.ip,cpu,memory,uptime,str(reboot_flag),str(device_crashed),comment])
        #         # conn.execute(query)
        # except:
        #     log.error(traceback.format_exc())
        #     log.error("Error while writing to CSV file")
        # log.info("Email Report is Due in %s seconds" %str( base_time + (12 * 3600) - time.time()))
        # if time.time() > base_time + (12 * 3600):
        #     log.info("Its more that 12 hours since script has been running, email device stats now")
        #
        #     subject = "Device Stats Report"
        #     body = "Device Status Report for last 12 hours"
        #     archive_folder = "log_%s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M-%S')
        #     body = body + "\n" + "Logs archived at %s" % archive_folder
        #     try:
        #         plot_stats_and_send_mail(stats_file, email_list=email_list)
        #     except:
        #         log.error(traceback.format_exc())
        #         log.error("Error while sending email")
        #     base_time = time.time()
        #     try:
        #         archive_logs([stats_file, "info.log", "debug.log", 'stdout.log'], archive_folder)
        #     except:
        #         log.error(traceback.format_exc())
        #         log.error("Error while archiving logs")
        #     try:
        #         with open(stats_file, 'wb+') as s:
        #            csv.writer(s).writerow("timestamp,ip,CPU,memory,Up Time,Rebooted,Crashed,Other Information".split(","))
        #
        #     except:
        #         log.error(traceback.format_exc())
        #         log.error("Error while creating new CSV File")
        #
        log.info("Sleeping for %d seconds before next iteration" % polling_interval_in_sec)
        time.sleep(2)
    conn.close()