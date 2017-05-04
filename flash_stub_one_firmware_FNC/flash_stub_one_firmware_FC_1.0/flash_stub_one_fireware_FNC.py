# -*- coding: utf-8 -*-
import wx
import sys
reload(sys)
sys.setdefaultencoding('gbk')
code_type = sys.getfilesystemencoding()
import time
import threading
import serial
import struct
import shutil
import os
import math
import binascii
import optparse
from datetime import datetime
import base64
import zlib
import hashlib


isOpened_panel_1 = threading.Event()


class FlashUI(wx.Frame):
    def __init__(self,title,pos,size):
        wx.Frame.__init__(self,None,-1,title,pos,size,style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU |wx.CAPTION | wx.CLIP_CHILDREN | wx.CLOSE_BOX )
        self.icon = wx.Icon('itead.ico',wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.Center()
        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour("white")
        self.panel.SetForegroundColour("brown")

        self.COM_panel_1 = serial.Serial()
        self.COM_panel_2 = serial.Serial()
        self.COM_panel_3 = serial.Serial()
        self.COM_panel_4 = serial.Serial()

        self.dl_list = [[''],[''],[''],[''],[''],['']]

        self.dl_list = [[sys.argv[2], 0]]
        #self.dl_list = [[u'C:\\Users\\Administrator\\Desktop\\05.01.03.0002\\[05.01.03.0002]FWSW-0185-SWITCH-8285-1.6.1\\FWSW-0185-1.6.1-noflashcipher.bin',0],[u'.\\flashtool\\bin_tmp\\downloadPanel1\\8285.csv', 0x78000],[u'Sign a sector', 0x7A000]]

        self.load_file_baud = ['9600', '23040', '46080', '57600', '115200', '230400', '345600',
         '460800', '576000','1500000']

        self.load_file_com = ["COM1", "COM2", "COM3", "COM4",
              "COM5", "COM6", "COM7", "COM8", "COM9","COM10","COM11","COM12","COM13",
              "COM14","COM15","COM16","COM17","COM18","COM19","COM20","COM21"]

        self.total_len = 0
        self.process_num = 1
        self.load_data_flag = 0

        self.now_time = datetime.now().strftime('%Y_%m_%d_%H%M%S_')
        self.f_note = open('D:\\flash_stub_one_firmware_FNC_tool\\log\\'+self.now_time+'.txt','a')
        self.file_name = 'D:\\flash_stub_one_firmware_FNC_tool\\log\\'+self.now_time

        self.sync_flag = 0

        self.rece_data = ''
        self.rece_last = ''
        self.send_formatt_data = ''
        self.send_noformatt_data = ''
        self.download_again_flag = 0

        self.flash_manufacturer_id = -1
        self.flash_device_id = -1

        #.....................................................
        self._slip_reader = slip_reader(self.COM_panel_1)

        temp = base64.b64decode(b"""
        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\
        """)
        print len(temp)
        self.STUB_CODE = eval(zlib.decompress(temp))
        print len(binascii.b2a_hex(str(self.STUB_CODE["text"])))
        print len(binascii.b2a_hex(str(self.STUB_CODE["entry"])))
        print len(binascii.b2a_hex(str(self.STUB_CODE["data"])))
        print len(binascii.b2a_hex(str(self.STUB_CODE["text_start"])))
        print len(binascii.b2a_hex(str(self.STUB_CODE["data_start"])))

        '''
        self.STUB_CODE = eval(zlib.decompress(base64.b64decode(b"""
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\
""")))
        '''
        self.binfile_path = self.binfile_Path()
        self.download_panel =self.download_config()
        self.start_download_pannel_1_threading(self)

    def COMOpen(self,event):
        if self.download_again_flag == 1:
            return True
        if not isOpened_panel_1.isSet():
            try:
                #self.COM_panel_1.timeout = 0
                #self.COM_panel_1.xonxoff = 0
                #self.COM_panel_1.port = "COM5"
                self.COM_panel_1.port = sys.argv[1]#sys.argv[1]
                #print >> self.f_note, self.COM_panel_1.port
                self.COM_panel_1.parity = 'None'[0]
                self.COM_panel_1.baudrate = 115200
                #print self.COM_panel_1.baudrate
                self.COM_panel_1.bytesize = 8
                self.COM_panel_1.stopbits = 1
                self.COM_panel_1.open()
                #print >> self.f_note, "COM_panel_1 open succeed"
                return True
            except Exception:
                self.COM_panel_1.close()
                #print >> self.f_note, sys.exc_info()[0], sys.exc_info()[1]
                #print >> self.f_note, "COM Open Error!"
                return False
        else:
            isOpened_panel_1.clear()
            self.COM_panel_1.close()
            #print >> self.f_note, "COM_panel_1 close"
            return False
            # cnv3.itemconfig("led",fill="black")

    def read(self):
        r = self._slip_reader.next()
        return r

    """ Write bytes to the serial port while performing SLIP escaping """
    def write(self, packet):
        self.send_noformatt_data = packet
        buf = '\xc0' \
              + (packet.replace('\xdb','\xdb\xdd').replace('\xc0','\xdb\xdc')) \
              + '\xc0'
        self.send_formatt_data = buf
        self.COM_panel_1.write(buf)

    def sync_write(self,packet):
        self.send_noformatt_data = ''
        buf = '\xc0'
        for b in packet:
            if b == '\xc0':
                buf += '\xdb\xdc'
            elif b == '\xdb':
                buf += '\xdb\xdd'
            else:
                buf += b
        buf += '\xc0'
        self.send_formatt_data = buf
        self.COM_panel_1.write(buf)

    def sync_read(self,length=1):
        b = ''
        while len(b) < length:
            c = self.COM_panel_1.read(1)
            if c == '\xdb':
                c = self.COM_panel_1.read(1)
                if c == '\xdc':
                    b = b + '\xc0'
                elif c == '\xdd':
                    b = b + '\xdb'
                else:
                    raise Exception('Invalid SLIP escape')
            else:
                b = b + c
        return b

    def write_reg(self, addr, value, mask, delay_us = 0):
        if self.command(0x09,
                struct.pack('<IIII', addr, value, mask, delay_us))[1] != "\0\0":
            raise Exception('Failed to write target memory')


    def command(self,op=None,data=None,chk=0):
        if op is not None:
            pkt = struct.pack('<BBHI', 0x00, op, len(data), chk) + data
            self.write(pkt)

        # tries to get a response until that response has the
        # same operation as the request or a retries limit has
        # exceeded. This is needed for some esp8266s that
        # reply with more sync responses than expected.
        for retry in xrange(100):
            p = self.read()
            if len(p) < 8:
                continue
            (resp, op_ret, len_ret, val) = struct.unpack('<BBHI', p[:8])
            if resp != 1:
                continue
            data = p[8:]
            self.rece_data = p
            if op is None or op_ret == op:
                return val, data

        raise FatalError("Response doesn't match request")

    def sync_command(self,op=None,data=None,chk=0):
        self.rece_data = '0'
        self.rece_last = ''
        if op:
            pkt = struct.pack('<BBHI', 0x00, op, len(data), chk) + data
            self.sync_write(pkt)

        self.rece_data = self.COM_panel_1.read(1)

        if  self.rece_data != '\xc0' and self.rece_data == '':
            print "rece_head:%s"%self.rece_data
            self.sync_flag = 2
            #raise Exception('Invalid head of packet')
            print 'waiting sync.........'
            raise Exception('waiting sync.........')

        hdr = self.sync_read(8)
        self.rece_data += hdr
        (resp,op_ret,len_ret,val) = struct.unpack('<BBHI', hdr)
        if resp != 0x01 or (op and op_ret != op):
            self.sync_flag = 3
            raise Exception('Invalid response')

        body = self.sync_read(len_ret)
        self.rece_data += body

        self.rece_last = self.COM_panel_1.read(1)
        self.rece_data += self.rece_last
        if self.rece_last != chr(0xc0):
            raise Exception('Invalid end of packet')

        #if self.sync_flag == 3:

        return val, body

    def sync(self):
        self.sync_command(0x08, '\x07\x07\x12\x20' + 32 * '\x55')
        for i in xrange(7):
            self.sync_command()


    def flush_input(self):
        self.COM_panel_1.flushInput()
        self._slip_reader = slip_reader(self.COM_panel_1)

    def sync_connect(self):
        #print >> self.f_note, "device_sync Connecting..."
        self.COM_panel_1.timeout = 0.2
        for i in xrange(7):
            try:
                self.COM_panel_1.flushInput()
                self.COM_panel_1.flushOutput()
                self.sync()
                self.COM_panel_1.timeout = 1
                return 0
            except:
                time.sleep(0.05)

        #return false
        raise Exception('')

    def device_sync(self):
        try:
            self.sync_connect()
            #if self.sync_flag != 0:
                #print "no come"
                #return False
            return True
        except:
            return False

    def check_command(self, op_description, op=None, data="", chk=0):
        """
        Execute a command with 'command', check the result code and throw an appropriate
        FatalError if it fails.

        Returns the "result" of a successful command.
        """
        val, data = self.command(op, data, chk)

        # things are a bit weird here, bear with us

        # the status bytes are the last 2/4 bytes in the data (depending on chip)
        if len(data) < 2:
            raise FatalError("Failed to %s. Only got %d byte status response." % (op_description, len(data)))
        status_bytes = data[-2:]
        # we only care if the first one is non-zero. If it is, the second byte is a reason.
        if status_bytes[0] != '\0':
            raise FatalError.WithResult('Failed to %s' % op_description, status_bytes)

        # if we had more data than just the status bytes, return it as the result
        # (this is used by the md5sum command, maybe other commands?)
        if len(data) > 2:
            return data[:-2]
        else:  # otherwise, just return the 'val' field which comes from the reply header (this is used by read_reg)
            return val

    def mem_block(self, data, seq):
        return self.check_command("write to target RAM", 0x07,
                                  struct.pack('<IIII', len(data), seq, 0, 0) + data,
                                  self.checksum(data))

    def mem_begin(self, size, blocks, blocksize, offset):
        return self.check_command("enter RAM download mode", 0x05,
                                  struct.pack('<IIII', size, blocks, blocksize, offset))

    def mem_finish(self, entrypoint=0):
        return self.check_command("leave RAM download mode", 0x06,
                                  struct.pack('<II', int(entrypoint == 0), entrypoint))

    def _upload_ram(self, offs, data):
        length = len(data)
        blocks = (length + 0x1800 - 1) / 0x1800
        self.mem_begin(length, blocks, 0x1800, offs)
        for seq in range(blocks):
            from_offs = seq * 0x1800
            to_offs = from_offs + 0x1800
            self.mem_block(data[from_offs:to_offs], seq)

    def run_stub(self, stub=None):
        try:
            stub = self.STUB_CODE

            # Upload
            print "Uploading stub..."
            for field in ['text', 'data']:
                if field in stub:
                    self._upload_ram(stub[field + "_start"], stub[field])
            print "Running stub..."
            self.mem_finish(stub['entry'])

            p = self.read()
            if p != 'OHAI':
                raise FatalError("Failed to start stub. Unexpected response: %s" % p)
            print "Stub running..."

            return True
        except:
            return False


    def checksum(self,data, state = 0xef):
        for b in data:
            state ^= ord(b)
        return state

    def create_csv_packet(self,filename,data):
        tmp = data.find('\n')

        #ita = data[81:91]
        #id = data[1:11]
        #key = data[11:47]
        #H_6 = (data[47:49] + data[50:52] + data[53:55] + data[56:58] + data[59:61] + data[62:64]).decode('hex')
        #L_6 = (data[64:66] + data[67:69] + data[70:72] + data[73:75] + data[76:78] + data[79:81]).decode('hex')
        ita = data[86:96]
        id = data[2:12]
        key = data[13:49]
        H_6 = (data[50:52]+data[53:55]+data[56:58]+data[59:61]+data[62:64]+data[65:67]).decode('hex')
        L_6 = (data[68:70]+data[71:73]+data[74:76]+data[77:79]+data[80:82]+data[83:85]).decode('hex')
        #print >> self.f_note, data
        #print >> self.f_note, len(data)
        #print >> self.f_note, ita
        #print >> self.f_note, id
        #print >> self.f_note, key
       # print >> self.f_note, H_6
        #print >> self.f_note, L_6

        image = ['8DB0839D'+24*'\x00'+'\
094FAFE8'+63*'\x00'+\
ita+11*'\x00'+\
id+1*'\x00'+\
key+1*'\x00'+\
H_6+\
L_6+'\
\x0A\x0A\x07\x01\xFF\xFF\xFF'+1*'\x00'+'\
\x0A\x0A\x07\x01\x49\x54\x45\x41\x44\x2D'+\
id+16*'\x00'+'\
12345678'+56*'\x00'+'\
\x10\x07'+2*'\x00'+'\
\x04'+4*'\x00'+'\
\x04'+3*'\x00'+'\
\xD0\xEA\x17'+64*'\x00'+\
3723*'\xFF']

        #print >> self.f_note, "data_len:"
        #print >> self.f_note, len(image[0])
        #file = open('test.bin','a+')
        #file.truncate()
        #file.write(image[0])
        #file.close()

        return image[0]

    def get_sign_sector_data(self):
        image = ['\x00'+4094*'\xFF']

        #print >> self.f_note, "data_len:"
        #print >> self.f_note, len(image[0])
        return image[0]

    def change_baud(self, baud):
        try:
            print "Changing baud rate to %d" % baud
            self.command(0x0F, struct.pack('<II', baud, 0))
            print "Changed."
            self.COM_panel_1.baudrate = baud
            time.sleep(0.05)  # get rid of crap sent during baud rate change
            self.flush_input()
            return True
        except:
            return False

    def get_erase_size(self, offset, size):
        """ Calculate an erase size given a specific size in bytes.

        Provides a workaround for the bootloader erase bug."""

        sectors_per_block = 16
        sector_size = 0x1000
        num_sectors = (size + sector_size - 1) / sector_size
        start_sector = offset / sector_size

        head_sectors = sectors_per_block - (start_sector % sectors_per_block)
        if num_sectors < head_sectors:
            head_sectors = num_sectors

        if num_sectors < 2 * head_sectors:
            return (num_sectors + 1) / 2 * sector_size
        else:
            return (num_sectors - head_sectors) * sector_size

    def flash_begin(self, size, offset):
        old_tmo = self.COM_panel_1.timeout
        num_blocks = (size + 0x400 - 1) / 0x400
        erase_size = self.get_erase_size(offset, size)

        self.COM_panel_1.timeout = 20
        t = time.time()
        self.check_command("enter Flash download mode", 0x02,
                           struct.pack('<IIII', erase_size, num_blocks, 0x400, offset))
        if size != 0:
            print "Took %.2fs to erase flash block" % (time.time() - t)
        self.COM_panel_1.timeout = old_tmo

    def flash_block(self, data, seq):
        self.check_command("write to target Flash after seq %d" % seq,
                           0x03,
                           struct.pack('<IIII', len(data), seq, 0, 0) + data,
                           self.checksum(data))

    def div_roundup(self,a, b):
        """ Return a/b rounded up to nearest integer,
        equivalent result to int(math.ceil(float(int(a)) / float(int(b))), only
        without possible floating point accuracy errors.
        """
        return (int(a) + int(b) - 1) / int(b)

    def flash_defl_block(self, data, seq):
        self.check_command("write compressed data to flash after seq %d" % seq,
                           0x11, struct.pack('<IIII', len(data), seq, 0, 0) + data, self.checksum(data))

    def hexify(self,s):
        return ''.join('%02X' % ord(c) for c in s)

    def unhexify(self,hs):
        s = ''
        for i in range(0, len(hs) - 1, 2):
            s += chr(int(hs[i] + hs[i + 1], 16))
        return s

    def flash_md5sum(self, addr, size):
        # the MD5 command returns additional bytes in the standard
        # command reply slot
        res = self.check_command('calculate md5sum', 0x13, struct.pack('<IIII', addr, size, 0, 0))

        if len(res) == 32:
            return res  # already hex formatted
        elif len(res) == 16:
            return self.hexify(res).lower()
        else:
            raise FatalError("MD5Sum command returned unexpected result: %r" % res)

    def start_download_panel_1(self,event):
        print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
        print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
        try:
            ret = True

            ret = self.COMOpen(self)

            if ret:
                print "uart OK"
                print >> self.f_note, "uart OK"
                ret = self.device_sync()

            print >> self.f_note, "SYNC True:c001080200070712200000c0"
            print >> self.f_note,"SYNC Rece:"+binascii.b2a_hex(self.rece_data)
            print "SYNC Send:%s"%binascii.b2a_hex(self.send_formatt_data)
            print "SYNC True:c001080200070712200000c0"
            print "SYNC Rece:" + binascii.b2a_hex(self.rece_data)

            if ret:
                self.sync_flag = 0
                ret = self.run_stub()

            if ret:
                ret = self.change_baud(3000000)

            print ret
            if ret:
                for filename, offset in self.dl_list:
                    if filename.find("csv") != -1:
                        self.load_data_flag = 1
                        image = self.create_csv_packet(filename,sys.argv[2])
                    elif filename.find("Sign") != -1:
                        if self.load_data_flag == 1:
                            self.load_data_flag = 0
                            image = self.get_sign_sector_data()
                    else:
                        print "come"
                        file = open(filename, 'rb')
                        image = file.read()
                        file.close()
                    calcmd5 = hashlib.md5(image).hexdigest()
                    uncsize = len(image)
                    blocks = self.div_roundup(len(image), 0x4000)
                    self.flash_begin(blocks * 0x4000, offset)

                    seq = 0
                    written = 0
                    t = time.time()
                    header_block = None
                    while len(image) > 0:
                        print '\rWriting at 0x%08x... (%d %%)' % (offset + seq * 0x4000, 100 * (seq + 1) / blocks),
                        sys.stdout.flush()
                        block = image[0:0x4000]
                        self.flash_block(block, seq)
                        image = image[0x4000:]
                        seq += 1
                        written += len(block)
                    t = time.time() - t
                    speed_msg = ""
                    if t > 0.0:
                        speed_msg = " (%.1f kbit/s)" % (written / t * 8 / 1000)
                    print '\rWrote %d bytes at 0x%08x in %.1f seconds%s...' % (written, offset, t, speed_msg)
                    res = self.flash_md5sum(offset, uncsize)
                    if res != calcmd5:
                        print 'File  md5: %s' % calcmd5
                        print 'Flash md5: %s' % res
                        raise FatalError("MD5 of file does not match data in flash!")
                    else:
                        print 'Hash of data verified.'
                    print '\nLeaving...'
            else:
                return False
            return True
        except:
            return False


    def Load_bin_path_1(self,event):
        file_path = ''

        dialog = wx.FileDialog(None, 'Itead bin path', style=wx.OPEN, wildcard="*.bin*")
        choice = dialog.ShowModal()
        if choice == wx.ID_OK:
            file_path = dialog.GetPath()
            self.bin_path_1.SetValue(file_path)
        elif choice == wx.ID_CANCEL:
            ret = wx.MessageBox(u"你没有选择文件！", 'Confirm', wx.OK)
            if ret == wx.OK:
                dialog.Destroy()

    def Load_bin_path_2(self,event):
        file_path = ''

        dialog = wx.FileDialog(None, 'Itead bin path', style=wx.OPEN, wildcard="*.bin*")
        choice = dialog.ShowModal()
        if choice == wx.ID_OK:
            file_path = dialog.GetPath()
            self.bin_path_2.SetValue(file_path)
        elif choice == wx.ID_CANCEL:
            ret = wx.MessageBox(u"你没有选择文件！", 'Confirm', wx.OK)
            if ret == wx.OK:
                dialog.Destroy()

    def Load_bin_path_3(self,event):
        file_path = ''

        dialog = wx.FileDialog(None, 'Itead bin path', style=wx.OPEN, wildcard="*.bin*")
        choice = dialog.ShowModal()
        if choice == wx.ID_OK:
            file_path = dialog.GetPath()
            self.bin_path_3.SetValue(file_path)
        elif choice == wx.ID_CANCEL:
            ret = wx.MessageBox(u"你没有选择文件！", 'Confirm', wx.OK)
            if ret == wx.OK:
                dialog.Destroy()

    def Load_bin_path_4(self,event):
        file_path = ''

        dialog = wx.FileDialog(None, 'Itead bin path', style=wx.OPEN, wildcard="*.bin*")
        choice = dialog.ShowModal()
        if choice == wx.ID_OK:
            file_path = dialog.GetPath()
            self.bin_path_4.SetValue(file_path)
        elif choice == wx.ID_CANCEL:
            ret = wx.MessageBox(u"你没有选择文件！", 'Confirm', wx.OK)
            if ret == wx.OK:
                dialog.Destroy()

    def Load_data_path_1(self,event):
        file_path = ''

        dialog = wx.FileDialog(None, 'Itead bin path', style=wx.OPEN, wildcard="*.csv*")
        choice = dialog.ShowModal()
        if choice == wx.ID_OK:
            file_path = dialog.GetPath()
            self.data_path_1.SetValue(file_path)
        elif choice == wx.ID_CANCEL:
            ret = wx.MessageBox(u"你没有选择文件！", 'Confirm', wx.OK)
            if ret == wx.OK:
                dialog.Destroy()

    def Load_data_path_2(self,event):
        file_path = ''

        dialog = wx.FileDialog(None, 'Itead bin path', style=wx.OPEN, wildcard="*.csv*")
        choice = dialog.ShowModal()
        if choice == wx.ID_OK:
            file_path = dialog.GetPath()
            self.data_path_2.SetValue(file_path)
        elif choice == wx.ID_CANCEL:
            ret = wx.MessageBox(u"你没有选择文件！", 'Confirm', wx.OK)
            if ret == wx.OK:
                dialog.Destroy()

    def download_again(self):
        self.download_again_flag = 1
        for i in xrange(3):
            print "sync again%s" % str(i + 1)
            print >> self.f_note, "sync again%s" % str(i + 1)
            ret = self.start_download_panel_1(self)
            self.total_len = 0
            self.process_num = 1
            if self.sync_flag != 3:
                if self.sync_flag == 2:
                    print "sync device no return data"
                    print "download flash failed"
                    print "exit 2"
                    print >> self.f_note, "sync device no return data"
                    print >> self.f_note, "exit 2"
                    print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                    print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                    self.f_note.close()
                    sys.exit(2)
                if ret == 1:
                    print "download flash success"
                    print "exit 0"
                    print >> self.f_note, "download flash success"
                    print >> self.f_note, "exit 0"
                    print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                    print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                    self.f_note.close()
                    os.rename(self.file_name + '.txt', self.file_name + '_Y.txt')
                    sys.exit(0)
                else:
                    print "download flash failed"
                    print "exit 1"
                    print >> self.f_note, "download flash failed"
                    print >> self.f_note, "exit 1"
                    print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                    print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                    self.f_note.close()
                    sys.exit(1)
            else:
                print


        print "sync three times over"
        print "exit 3"
        print >> self.f_note, "sync three times over"
        print >> self.f_note, "exit 3"
        self.f_note.close()
        sys.exit(3)

    def start_download_pannel_1_threading(self,event):
            ret = self.start_download_panel_1(self)
            if self.sync_flag == 3:
                self.download_again()
            elif self.sync_flag == 2:
                print "sync device no return data"
                print "download flash failed"
                print "exit 2"
                print >> self.f_note,"sync device no return data"
                print >> self.f_note,"exit 2"
                print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                self.f_note.close()
                sys.exit(2)

            if ret == 1:
                print "download flash success"
                print "exit 0"
                print >> self.f_note,"download flash success"
                print >> self.f_note,"exit 0"
                print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                self.f_note.close()
                os.rename(self.file_name+'.txt',self.file_name+'_Y.txt')
                sys.exit(0)
            else:
                print "download flash failed"
                print "exit 1"
                print >> self.f_note,"download flash failed"
                print >> self.f_note,"exit 1"
                print datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                print >> self.f_note, datetime.now().strftime('%Y_%m_%d_%H%M%S_') + str(datetime.now().microsecond)[0:2]
                self.f_note.close()
                sys.exit(1)



    def download_config(self):
        font = wx.Font(13,wx.SWISS, wx.NORMAL, wx.BOLD)

        self.bin_path_config = wx.StaticBox(self.panel, label=u'Download Panel Config', pos=wx.Point(0, 220), size=wx.Size(542, 280))
        self.bin_path_config.SetFont(font)

        ################################################panel 1
        self.Download_Panel_1 = wx.StaticText(self.panel, -1, u'Panel 1', pos=wx.Point(10, 245))
        self.bin_path_1_button = wx.Button(self.panel,label=u'START',pos=wx.Point(10,263),size=wx.Size(80,28),style=0)
        #self.Bind(wx.EVT_BUTTON, self.start_download_panel_1, self.bin_path_1_button)
        self.Bind(wx.EVT_BUTTON, self.start_download_pannel_1_threading, self.bin_path_1_button)
        self.bin_path_1_button = wx.Button(self.panel, label=u'STOP', pos=wx.Point(10, 293), size=wx.Size(80, 28),style=0)

        self.Download_Panel_1_port = wx.StaticText(self.panel, -1, u'PORT:', pos=wx.Point(95, 268))
        self.Download_Panel_1_port_com = wx.Choice(self.panel,choices=self.load_file_com,pos=wx.Point(135,264),size=wx.Size(85,87),style=0)
        self.Download_Panel_1_port_com.SetSelection(4)
        self.Download_Panel_1_baud = wx.StaticText(self.panel, -1, u'BAUD:', pos=wx.Point(95, 298))
        self.Download_Panel_1_port_baud = wx.Choice(self.panel, choices=self.load_file_baud,pos=wx.Point(135, 294), size=wx.Size(85, 87), style=0)
        self.Download_Panel_1_port_baud.SetSelection(6)
        self.Download_Panel_1_gauge = wx.Gauge(self.panel,-1,size=wx.Size(230,23),pos=wx.Point(10,325),style=0)

        ################################################panel 2
        self.Download_Panel_2 = wx.StaticText(self.panel, -1, u'Panel 2', pos=wx.Point(320, 245))
        self.bin_path_2_button = wx.Button(self.panel, label=u'START', pos=wx.Point(320, 263), size=wx.Size(80, 28),style=0)
        self.bin_path_2_button = wx.Button(self.panel, label=u'STOP', pos=wx.Point(320, 293), size=wx.Size(80, 28),style=0)
        self.Download_Panel_2_port = wx.StaticText(self.panel, -1, u'PORT:', pos=wx.Point(405, 268))
        self.Download_Panel_2_port_com = wx.Choice(self.panel, choices=self.load_file_com,pos=wx.Point(445, 264), size=wx.Size(85, 87), style=0)
        self.Download_Panel_2_port_com.SetSelection(0)
        self.Download_Panel_2_baud = wx.StaticText(self.panel, -1, u'BAUD:', pos=wx.Point(405, 298))
        self.Download_Panel_2_port_baud = wx.Choice(self.panel,choices=self.load_file_baud, pos=wx.Point(445, 294),size=wx.Size(85, 87), style=0)
        self.Download_Panel_2_port_baud.SetSelection(6)
        self.Download_Panel_2_gauge = wx.Gauge(self.panel,-1,size=wx.Size(230,23),pos=wx.Point(300,325),style=0)
        ################################################panel 3
        self.Download_Panel_3 = wx.StaticText(self.panel, -1, u'Panel 3', pos=wx.Point(10, 352))

        self.bin_path_3_button = wx.Button(self.panel,label=u'START',pos=wx.Point(10,263+107),size=wx.Size(80,28),style=0)
        self.bin_path_3_button = wx.Button(self.panel, label=u'STOP', pos=wx.Point(10, 293+107), size=wx.Size(80, 28),style=0)
        self.Download_Panel_3_port = wx.StaticText(self.panel, -1, u'PORT:', pos=wx.Point(95, 268+107))
        self.Download_Panel_3_port_com = wx.Choice(self.panel,choices=self.load_file_com,pos=wx.Point(135,264+107),size=wx.Size(85,87),style=0)
        self.Download_Panel_3_port_com.SetSelection(0)
        self.Download_Panel_3_baud = wx.StaticText(self.panel, -1, u'BAUD:', pos=wx.Point(95, 298+107))
        self.Download_Panel_3_port_baud = wx.Choice(self.panel, choices=self.load_file_baud,pos=wx.Point(135, 294+107), size=wx.Size(85, 87), style=0)
        self.Download_Panel_3_port_baud.SetSelection(6)
        self.Download_Panel_3_gauge = wx.Gauge(self.panel,-1,size=wx.Size(230,23),pos=wx.Point(10,433),style=0)

        ################################################panel 4
        self.Download_Panel_4 = wx.StaticText(self.panel, -1, u'Panel 4', pos=wx.Point(10+310, 352))

        self.bin_path_4_button = wx.Button(self.panel,label=u'START',pos=wx.Point(10+310,263+107),size=wx.Size(80,28),style=0)
        self.bin_path_4_button = wx.Button(self.panel, label=u'STOP', pos=wx.Point(10+310, 293+107), size=wx.Size(80, 28),style=0)
        self.Download_Panel_4_port = wx.StaticText(self.panel, -1, u'PORT:', pos=wx.Point(95, 268+107))
        self.Download_Panel_4_port_com = wx.Choice(self.panel,choices=self.load_file_com,pos=wx.Point(135+310,264+107),size=wx.Size(85,87),style=0)
        self.Download_Panel_4_port_com.SetSelection(0)
        self.Download_Panel_4_baud = wx.StaticText(self.panel, -1, u'BAUD:', pos=wx.Point(95+310, 298+107))
        self.Download_Panel_4_port_baud = wx.Choice(self.panel, choices=self.load_file_baud,pos=wx.Point(135+310, 294+107), size=wx.Size(85, 87), style=0)
        self.Download_Panel_4_port_baud.SetSelection(6)
        self.Download_Panel_4_gauge = wx.Gauge(self.panel, -1, size=wx.Size(230, 23), pos=wx.Point(300, 433), style=0)
        #self.Download_Panel_4_gauge.SetBackgroundColour('GREEN')
        #self.Download_Panel_4_gauge.SetValue(50)

        ################################################all panel
        self.All_Download_Panel_startbutton = wx.Button(self.panel,label=u'ALL START',pos=wx.Point(10,465),size=wx.Size(110,30),style=0)
        self.All_Download_Panel_stopbutton = wx.Button(self.panel, label=u'ALL STOP', pos=wx.Point(130, 465), size=wx.Size(110, 30),style=0)


    def binfile_Path(self):
        font = wx.Font(13,wx.SWISS, wx.NORMAL, wx.BOLD)

        self.bin_path_config = wx.StaticBox(self.panel,label=u'',pos=wx.Point(0,0),size=wx.Size(542,215))
        self.bin_path_config.SetFont(font)

        self.bin_file = wx.StaticText(self.panel,-1,u'BIN_PATH：',pos=wx.Point(8,10))

        self.bin_CheckBox_1 = wx.CheckBox(self.panel,label='',pos=wx.Point(10,37),size=wx.Size(16,13),style=0)
        self.bin_CheckBox_2 = wx.CheckBox(self.panel, label='', pos=wx.Point(10, 62), size=wx.Size(16, 13), style=0)
        self.bin_CheckBox_3 = wx.CheckBox(self.panel, label='', pos=wx.Point(10, 87), size=wx.Size(16, 13), style=0)
        self.bin_CheckBox_4 = wx.CheckBox(self.panel, label='', pos=wx.Point(10, 112), size=wx.Size(16, 13), style=0)
        self.bin_CheckBox_1.SetValue(True)
        self.bin_CheckBox_2.SetValue(True)
        self.bin_CheckBox_3.SetValue(True)
        self.bin_CheckBox_4.SetValue(True)


        self.bin_path_1 = wx.TextCtrl(self.panel,pos=wx.Point(32,33),style=0,value=u'.\\bin_tmp\\downloadPanel1\\blank.bin',size=wx.Size(350,21))
        self.bin_path_2 = wx.TextCtrl(self.panel, pos=wx.Point(32, 58), style=0, value=u'.\\bin_tmp\\downloadPanel1\\boot_v1.6.bin_rep_rep', size=wx.Size(350, 21))
        self.bin_path_3 = wx.TextCtrl(self.panel, pos=wx.Point(32, 83), style=0, value=u'.\\bin_tmp\\downloadPanel1\\esp_init_data_default.bin_rep', size=wx.Size(350, 21))
        self.bin_path_4 = wx.TextCtrl(self.panel, pos=wx.Point(32, 108), style=0, value=u'.\\bin_tmp\\downloadPanel1\\user1.1024.new.2.bin', size=wx.Size(350, 21))

        self.bin_path_1_button = wx.Button(self.panel,label=u'...',pos=wx.Point(382,32),size=wx.Size(30,23),style=0)
        self.Bind(wx.EVT_BUTTON,self.Load_bin_path_1,self.bin_path_1_button)
        self.bin_path_2_button = wx.Button(self.panel, label=u'...', pos=wx.Point(382, 57), size=wx.Size(30, 23),style=0)
        self.Bind(wx.EVT_BUTTON, self.Load_bin_path_2, self.bin_path_2_button)
        self.bin_path_3_button = wx.Button(self.panel, label=u'...', pos=wx.Point(382, 82), size=wx.Size(30, 23),style=0)
        self.Bind(wx.EVT_BUTTON, self.Load_bin_path_3, self.bin_path_3_button)
        self.bin_path_4_button = wx.Button(self.panel, label=u'...', pos=wx.Point(382, 107), size=wx.Size(30, 23),style=0)
        self.Bind(wx.EVT_BUTTON, self.Load_bin_path_4, self.bin_path_4_button)

        self.bin_path_1_ad = wx.StaticText(self.panel, -1, u'ADDR:', pos=wx.Point(420, 35))
        self.bin_path_2_ad = wx.StaticText(self.panel, -1, u'ADDR:', pos=wx.Point(420, 60))
        self.bin_path_3_ad = wx.StaticText(self.panel, -1, u'ADDR:', pos=wx.Point(420, 85))
        self.bin_path_4_ad = wx.StaticText(self.panel, -1, u'ADDR:', pos=wx.Point(420, 110))

        self.bin_path_1_addr = wx.TextCtrl(self.panel,pos=wx.Point(460,33),style=0,value=u'0x7e000',size=wx.Size(80,21))
        self.bin_path_2_addr = wx.TextCtrl(self.panel, pos=wx.Point(460, 58), style=0, value=u'0x00000', size=wx.Size(80, 21))
        self.bin_path_3_addr = wx.TextCtrl(self.panel, pos=wx.Point(460, 83), style=0, value=u'0xfc000', size=wx.Size(80, 21))
        self.bin_path_4_addr = wx.TextCtrl(self.panel, pos=wx.Point(460, 108), style=0, value=u'0x01000', size=wx.Size(80, 21))

        self.data_file = wx.StaticText(self.panel, -1, u'DATA_PATH：', pos=wx.Point(8, 135))

        self.data_CheckBox_1 = wx.CheckBox(self.panel,label='',pos=wx.Point(10,160),size=wx.Size(16,13),style=0)
        self.data_CheckBox_2 = wx.CheckBox(self.panel, label='', pos=wx.Point(10, 185), size=wx.Size(16, 13), style=0)
        self.data_CheckBox_1.SetValue(True)
        self.data_CheckBox_2.SetValue(True)

        self.data_path_1 = wx.TextCtrl(self.panel,pos=wx.Point(32,157),style=0,value=u'',size=wx.Size(350,21))
        self.data_path_2 = wx.TextCtrl(self.panel, pos=wx.Point(32, 183), style=0, value=u'', size=wx.Size(350, 21))
        self.data_path_1_button = wx.Button(self.panel, label=u'...', pos=wx.Point(382, 156), size=wx.Size(30, 23),style=0)
        self.Bind(wx.EVT_BUTTON, self.Load_data_path_1, self.data_path_1_button)
        self.data_path_2_button = wx.Button(self.panel, label=u'...', pos=wx.Point(382, 182), size=wx.Size(30, 23),style=0)
        self.Bind(wx.EVT_BUTTON, self.Load_data_path_2, self.data_path_2_button)

        self.data_path_3_ad = wx.StaticText(self.panel, -1, u'ADDR:', pos=wx.Point(420, 157))
        self.data_path_4_ad = wx.StaticText(self.panel, -1, u'ADDR:', pos=wx.Point(420, 185))

        self.data_path_1_addr = wx.TextCtrl(self.panel,pos=wx.Point(460,157),style=0,value=u'0x78000',size=wx.Size(80,21))

        self.data_path_2_addr = wx.TextCtrl(self.panel, pos=wx.Point(460, 185), style=0, value=u'', size=wx.Size(80, 21))

class FatalError(RuntimeError):
    """
    Wrapper class for runtime errors that aren't caused by internal bugs, but by
    ESP8266 responses or input content.
    """
    def __init__(self, message):
        RuntimeError.__init__(self, message)

    @staticmethod
    def WithResult(message, result):
        """
        Return a fatal error object that appends the hex values of
        'result' as a string formatted argument.
        """
        message += " (result was %s)" % ", ".join(hex(ord(x)) for x in result)
        return FatalError(message)

def slip_reader(port):
    """Generator to read SLIP packets from a serial port.
    Yields one full SLIP packet at a time, raises exception on timeout or invalid data.

    Designed to avoid too many calls to serial.read(1), which can bog
    down on slow systems.
    """
    partial_packet = None
    in_escape = False
    while True:
        waiting = port.inWaiting()
        read_bytes = port.read(1 if waiting == 0 else waiting)
        if read_bytes == '':
            raise FatalError("Timed out waiting for packet %s" % ("header" if partial_packet is None else "content"))
        for b in read_bytes:
            if partial_packet is None:  # waiting for packet header
                if b == '\xc0':
                    partial_packet = ""
                else:
                    raise FatalError('Invalid head of packet (%r)' % b)
            elif in_escape:  # part-way through escape sequence
                in_escape = False
                if b == '\xdc':
                    partial_packet += '\xc0'
                elif b == '\xdd':
                    partial_packet += '\xdb'
                else:
                    raise FatalError('Invalid SLIP escape (%r%r)' % ('\xdb', b))
            elif b == '\xdb':  # start of escape sequence
                in_escape = True
            elif b == '\xc0':  # end of packet
                yield partial_packet
                partial_packet = None
            else:  # normal byte in packet
                partial_packet += b


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "ERROR:Insufficient parameters"
        sys.exit(1)

    app = wx.App()
    frame = FlashUI(u'Flash_stub_one_firmware1.0.0',(100,150),(550,550))
    frame.Show(True)
    app.MainLoop()