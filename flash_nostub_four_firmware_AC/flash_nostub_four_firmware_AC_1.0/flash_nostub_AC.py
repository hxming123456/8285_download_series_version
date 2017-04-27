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


        self.dl_list = [[u'D:\\itead_8285_download\\flashtool\\bin_file\\blank.bin', 0x7e000],
                        [u'D:\\itead_8285_download\\flashtool\\bin_file\\boot_v1.6.bin_rep', 0],
                        [u'D:\\itead_8285_download\\flashtool\\bin_file\\esp_init_data_default.bin_rep', 0xfc000],
                        [u'D:\\itead_8285_download\\flashtool\\bin_file\\user1.1024.new.2.bin', 0x01000],
                        [u'data csv', 0x78000],
                        [u'Sign a sector', 0x7A000]]
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
        self.f_note = open('D:\\itead_8285_download\\log\\'+self.now_time+sys.argv[2][2:12]+'.txt','a')
        self.file_name = 'D:\\itead_8285_download\\log\\'+self.now_time+sys.argv[2][2:12]

        self.sync_flag = 0

        self.rece_data = ''
        self.rece_last = ''
        self.send_data = ''
        self.download_again_flag = 0

        self.flash_manufacturer_id = -1
        self.flash_device_id = -1

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
                self.COM_panel_1.baudrate = 576000
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

    '''
    def COMOpen(self, port_com,com,baud,event):
            #COM_panel = serial.Serial()
            if not isOpened_panel_1.isSet():
                try:
                    port_com.port = com
                    print self.port_com.port
                    port_com.parity = 'None'[0]
                    port_com.baudrate = baud
                    print port_com.baudrate
                    port_com.bytesize = 8
                    port_com.stopbits = 1
                    port_com.open()
                    print "COM_panel_1 open succeed"
                    return True
                except Exception:
                    port_com.close()
                    print sys.exc_info()[0], sys.exc_info()[1]
                    print "COM Open Error!"
                    return False
            else:
                isOpened_panel_1.clear()
                port_com.close()
                print "COM_panel_1 close"
                return False
                # cnv3.itemconfig("led",fill="black")
    '''
    def write(self,packet):
        buf = '\xc0'
        for b in packet:
            if b == '\xc0':
                buf += '\xdb\xdc'
            elif b == '\xdb':
                buf += '\xdb\xdd'
            else:
                buf += b
        buf += '\xc0'
        self.send_data = buf
        self.COM_panel_1.write(buf)

    def read(self,length=1):
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

    def read_reg(self, addr):
        res = self.command(0x0a, struct.pack('<I', addr))
        if res[1] != "\0\0":
            raise Exception('Failed to read target memory')
        return res[0]

    def command(self,op=None,data=None,chk=0):
        self.rece_data = '0'
        self.rece_last = ''
        if op:
            pkt = struct.pack('<BBHI', 0x00, op, len(data), chk) + data
            self.write(pkt)

        self.rece_data = self.COM_panel_1.read(1)

        if  self.rece_data != '\xc0' and self.rece_data == '':
            #self.sync_flag = 2
            #raise Exception('Invalid head of packet')
            print 'waiting sync.........'
            raise Exception('waiting sync.........')

        hdr = self.read(8)
        self.rece_data += hdr
        (resp,op_ret,len_ret,val) = struct.unpack('<BBHI', hdr)
        if resp != 0x01 or (op and op_ret != op):
            #self.sync_flag = 3
            raise Exception('Invalid response')

        body = self.read(len_ret)
        self.rece_data += body

        self.rece_last = self.COM_panel_1.read(1)
        self.rece_data += self.rece_last
        if self.rece_last != chr(0xc0):
            raise Exception('Invalid end of packet')

        return val, body

    def sync_command(self,op=None,data=None,chk=0):
        self.rece_data = '0'
        self.rece_last = ''
        if op:
            pkt = struct.pack('<BBHI', 0x00, op, len(data), chk) + data
            self.write(pkt)

        self.rece_data = self.COM_panel_1.read(1)

        if  self.rece_data != '\xc0' and self.rece_data == '':
            self.sync_flag = 2
            #raise Exception('Invalid head of packet')
            print 'waiting sync.........'
            raise Exception('waiting sync.........')

        hdr = self.read(8)
        self.rece_data += hdr
        (resp,op_ret,len_ret,val) = struct.unpack('<BBHI', hdr)
        if resp != 0x01 or (op and op_ret != op):
            self.sync_flag = 3
            raise Exception('Invalid response')

        body = self.read(len_ret)
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

    def connect(self):
        #print >> self.f_note, "device_sync Connecting..."
        self.COM_panel_1.timeout = 0.2
        for i in xrange(10):
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
            self.connect()
            #print >> self.f_note, "chip sync ok!"
            return True
        except:
            #print >> self.f_note, "chip sync error."
            return False


    def flash_begin(self,_size,offset):
        old_tmo = self.COM_panel_1.timeout
        self.COM_panel_1.timeout = 90

        area_len = _size
        sector_no = offset / 4096;
        sector_num_per_block = 16;

        if 0 == (area_len % 4096):
            total_sector_num = area_len / 4096
        else:
            total_sector_num = 1 + (area_len / 4096)

        head_sector_num = sector_num_per_block - (sector_no % sector_num_per_block);
        if head_sector_num >= total_sector_num:
            head_sector_num = total_sector_num
        else:
            head_sector_num = head_sector_num

        if (total_sector_num - 2 * head_sector_num) > 0:
            size = (total_sector_num - head_sector_num) * 4096
            #print >> self.f_note, "head: ", head_sector_num, ";total:", total_sector_num
            #print >> self.f_note, "erase size : ", size
        else:
            size = int(math.ceil(total_sector_num / 2.0) * 4096)
            #print >> self.f_note, "head:", head_sector_num, ";total:", total_sector_num
            #print >> self.f_note, "erase size :", size
        if self.command(0x02,struct.pack('<IIII', size, 0x200, 0x400, offset))[1] != "\0\0":
            raise Exception('Failed to enter Flash download mode')
        self.COM_panel_1.timeout = old_tmo

    def checksum(self,data, state = 0xef):
        for b in data:
            state ^= ord(b)
        return state

    def flash_block(self,data,seq):
        if self.command(0x03,struct.pack('<IIII', len(data), seq, 0, 0) + data, self.checksum(data))[1] != "\0\0":
            raise Exception('Failed to write to target Flash')
        #print "Download Send:%s" % binascii.b2a_hex(self.send_data)
        #print "Download Rece:" + binascii.b2a_hex(self.rece_data)

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

    def flash_download(self,filename='',address=0,reboot=False):
        image = []
        #prosent = 0
        old_prosent = 1
        if filename == '':
            return True
        elif filename.find("csv") != -1:
            self.load_data_flag = 1
            #print "write address:0x%08x... (%d)" % (address)
            image = self.create_csv_packet(filename,sys.argv[2])#sys.argv[2]
        elif filename.find("Sign") != -1:
            if self.load_data_flag == 1:
                self.load_data_flag = 0
                #print "write address:0x%08x... (%d %%)" % (address)
                image = self.get_sign_sector_data()
            else:
                return True
        elif filename != '':
            #image=file(filename, 'rb').read()
            file = open(filename, 'rb')
            image = file.read()
            file.close()
            #print "write address:0x%08x... (%d %%)" % (address)
            #print >> self.f_note,"data_len:"
            #print >> self.f_note, len(image)
        #print image
        #print image
            #print >> self.f_note, 'Erasing flash...'
        try:
            self.flash_begin(len(image),address)
            #print "Erasing Send:%s"%binascii.b2a_hex(self.send_data)
            #print "Erasing Rece:" + binascii.b2a_hex(self.rece_data)
            #print >> self.f_note, "erase flash succeed"
        except:
            #print >> self.f_note, "erase flash error"
            return False

        seq = 0
        blocks = math.floor(len(image)/0x400 +1 )
        try:
            print_flg = True
            while len(image) > 0:
                if print_flg:
                    print_flg = True
                    # print >>self.f_note, "come to Write at ..."
                    #print >>self.f_note, '\rcome to Writing at 0x%08x... (%d %%)' % (address + seq * 0x400, 100 * self.process_num / self.total_len),  # 100*seq/blocks),
                    #print >>self.f_note, '\rcome to Writing at 0x%08x... (%d %%)' % (address + seq * 0x400, 100 * self.process_num / self.total_len)  # 100*seq/blocks),
                    #
                    #if (prosent%10):
                        #old_prosent = prosent
                    prosent = 100 * self.process_num / self.total_len
                    #print prosent
                    if (int(prosent)%10) == 0 and (int(old_prosent)!=int(prosent)):
                        old_prosent = prosent
                        print '\rcome to Writing at 0x%08x... (%d %%)' % (address + seq * 0x400, 100 * self.process_num / self.total_len)

                    #print >>self.f_note, int()
                    #self.Download_Panel_1_gauge.SetValue(prosent[1])
                    self.process_num += 1
                    sys.stdout.flush()
                    # print >>self.f_note, "test img_len: ",len(image), " seq: ",seq
                block = image[0:0x400]
                    # Pad the last block
                block = block + '\xff' * (0x400 - len(block))
                self.flash_block(block, seq)
                image = image[0x400:]
                seq += 1
                #print >>self.f_note, '\nLeaving...'
            return True
        except:
            #print >>self.f_note,"error when download firmware"
            #print >>self.f_note, sys.exc_info()[0], sys.exc_info()[1]
            return False

    def get_flash_id(self):
        try:
            self.flash_begin(0,0)
            self.write_reg(0x60000240, 0 , 0 , 0 )
            time.sleep(0.01)
            self.write_reg(0x60000200 , (0x1<<28) , (0x1<<28), 0 )
            time.sleep(0.01)
            flash_id = self.read_reg(0x60000240)
            print "get flash id : 0x%08x"%flash_id
            #self.flash_manufacturer_id = flash_id&0xff
            #self.flash_device_id = ((flash_id>>16)&0xff | (flash_id &( 0xff<<8)))
            #print " manufacturer_id: 0x%x\r\n"%self.flash_manufacturer_id
            #print " device_id: 0x%x\r\n"%self.flash_device_id
            return True
        except:
            print "get flash id error"
            return False

    def start_download_panel_1(self,event):
        try:
            ret = True

            '''self.dl_list[0] = [self.bin_path_1.GetValue(),0x7e000]
            self.dl_list[1] = [self.bin_path_2.GetValue(),0x00000]
            self.dl_list[2] = [self.bin_path_3.GetValue(),0xfc000]
            self.dl_list[3] = [self.bin_path_4.GetValue(),0x01000]
            self.dl_list[4] = [self.data_path_1.GetValue(),0x78000]
            self.dl_list[5] = ["Sign a sector",0x7A000]


            self.dl_list[0] = [self.bin_path_1.GetValue(), int(self.bin_path_1_addr.GetValue(),16)]
            self.dl_list[1] = [self.bin_path_2.GetValue(), int(self.bin_path_2_addr.GetValue(),16)]
            self.dl_list[2] = [self.bin_path_3.GetValue(), int(self.bin_path_3_addr.GetValue(),16)]
            self.dl_list[3] = [self.bin_path_4.GetValue(), int(self.bin_path_4_addr.GetValue(),16)]
            self.dl_list[4] = [self.data_path_1.GetValue(), int(self.data_path_1_addr.GetValue(),16)]
            self.dl_list[5] = ['Sign a sector', 0x7A000]
            '''
            #print >>self.f_note,self.dl_list

            ret = self.COMOpen(self)
            #ret = self.COMOpen(self,self.COM_panel_1,"COM12",576000)
            if ret:
                print "uart OK"
                print >> self.f_note, "uart OK"
                ret = self.device_sync()

            print >> self.f_note, "SYNC True:c001080200070712200000c0"
            print >> self.f_note,"SYNC Rece:"+binascii.b2a_hex(self.rece_data)
            print "SYNC Send:%s"%binascii.b2a_hex(self.send_data)
            print "SYNC True:c001080200070712200000c0"
            print "SYNC Rece:" + binascii.b2a_hex(self.rece_data)

            if ret:
                ret = self.get_flash_id()

            if ret:
                self.sync_flag = 0
                image_list = []
                for idx in range(len(self.dl_list)):
                    filename,offset = self.dl_list[idx]
                    #print >>self.f_note, 'filename:%s',filename
                    #print >>self.f_note, 'offset : %s',offset
                    if filename.find('csv')!=-1:
                        #image = file(filename, 'rb').read()
                        #file = open(filename, 'rb')
                        #image = file.read()
                        #file.close()
                        blocks = math.floor(4095/0x400 +1 )
                        self.total_len += blocks
                    elif filename.find('Sign')!=-1:
                        blocks = math.floor(4095 /0x400 + 1)
                        self.total_len += blocks
                    elif filename != '':
                        #image = file(filename, 'rb').read()
                        file = open(filename, 'rb')
                        image = file.read()
                        file.close()
                        blocks = math.floor(len(image) / 0x400 + 1)
                        self.total_len += blocks
                    #print >>self.f_note, "total len !!!=============",self.total_len
                        image_list.append(image)

                for filename,offset in self.dl_list:
                    #print >>self.f_note, "dl_list:"
                    #print >>self.f_note, self.dl_list
                    ret = self.flash_download(filename, offset,False)
                    if not ret:
                        break
                if ret:
                    #print >>self.f_note, "come to Writing at 0x000fc000... (100 %) "
                    self.Download_Panel_1_gauge.SetValue(100)
                    self.COM_panel_1.close()
                    #print >>self.f_note, 'Writeing all over 100%'
                    print 'Writeing all over 100%'
                    #print >>self.f_note, "COM_panel_1 close"
                    self.total_len = 0
                    self.process_num = 1
                    return True
                else:
                    return False
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
                    self.f_note.close()
                    sys.exit(2)
                if ret == 1:
                    print "download flash success"
                    print "exit 0"
                    print >> self.f_note, "download flash success"
                    print >> self.f_note, "exit 0"
                    self.f_note.close()
                    os.rename(self.file_name + '.txt', self.file_name + '_Y.txt')
                    sys.exit(0)
                else:
                    print "download flash failed"
                    print "exit 1"
                    print >> self.f_note, "download flash failed"
                    print >> self.f_note, "exit 1"
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
                self.f_note.close()
                sys.exit(2)

            if ret == 1:
                print "download flash success"
                print "exit 0"
                print >> self.f_note,"download flash success"
                print >> self.f_note,"exit 0"
                self.f_note.close()
                os.rename(self.file_name+'.txt',self.file_name+'_Y.txt')
                sys.exit(0)
            else:
                print "download flash failed"
                print "exit 1"
                print >> self.f_note,"download flash failed"
                print >> self.f_note,"exit 1"
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



if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "ERROR:Insufficient parameters"
        sys.exit(1)

    app = wx.App()
    frame = FlashUI(u'FlashTOOL1.0.0',(100,150),(550,550))
    frame.Show(True)
    app.MainLoop()