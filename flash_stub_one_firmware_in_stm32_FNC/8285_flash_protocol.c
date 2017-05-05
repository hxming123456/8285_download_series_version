#include "8285_flash_protocol"

void Data_formatt_write(uint8_t *packet,int packet_len,uint8_t packet_type)
{
	uint8_t buf[512] = {0xc0};
	int i = 0;
	int j = 1;
	
	if(packet_type == HA_HEAD_HA_TAIL)
	{
		for(i=0;i<packet_len;i++)
		{
			if(packet[i] == 0xc0)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdc;
			}
			else if(packet[i] == 0xdb)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdd;
			}
			else
			{
				buf[j++] = packet[i];
			}
		}
		buf[j] = 0xc0;
	}
	else if(packet_type == NO_HEAD_HA_TAIL)
	{
		buf[0] = 0x00;
		j = 0;
		for(i=0;i<packet_len;i++)
		{
			if(packet[i] == 0xc0)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdc;
			}
			else if(packet[i] == 0xdb)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdd;
			}
			else
			{
				buf[j++] = packet[i];
			}
		}
		buf[j] = 0xc0;
	}
	else if(packet_type == HA_HEAD_NO_TAIL)
	{
		for(i=0;i<packet_len;i++)
		{
			if(packet[i] == 0xc0)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdc;
			}
			else if(packet[i] == 0xdb)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdd;
			}
			else
			{
				buf[j++] = packet[i];
			}
		}
	}
	else if(packet_type == NO_HEAD_NO_TAIL)
	{
		buf[0] = 0x00;
		j = 0;
		for(i=0;i<packet_len;i++)
		{
			if(packet[i] == 0xc0)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdc;
			}
			else if(packet[i] == 0xdb)
			{
				buf[j++] = 0xdb;
				buf[j++] = 0xdd;
			}
			else
			{
				buf[j++] = packet[i];
			}
		}
	}

	usart_write();
}

int Data_formatt_read(uint8_t *packet,int len)
{
	uint8_t buf[512] = {};
	int i = 0;
	int j = 0;
	
	usart_read(buf,512);
	if(str_len(buf) < len)
	{
		len = str_len(buf);
	}
	for(i=0;i<len;i++)
	{
		if(buf[i] == 0xdb)
		{
			if(buf[i+1] == 0xdc)
			{
				packet[j++] = 0xc0;
				i++;
			}
			else if(buf[i+1] == 0xdd)
			{
				packet[j++] = 0xdb;
				i++
			}
		}
		else
		{
			packet[j++] = buf[i];
		}
	}
	
	return str_len(buf);
}

int 

int device_sync(void)
{
	uint8_t sync_send_packet[44] = {
		0x00,0x08,0x24,0x00,0x00,0x00,0x00,0x00,0x07,0x07,0x12,0x20,0x55,0x55,0x55,
		0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,
		0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55,0x55};
	uint8_t sync_recv_packet[20] = {0};
	uint8_t sync_recv_true[10] = {0x01,0x08,0x02,0x00,0x07,0x07,0x12,0x20,0x00,0x00};
	uint8_t i;
	
	Data_formatt_write(sync_send_packet,44,HA_HEAD_HA_TAIL);	
	Data_formatt_read(sync_recv_packet,20);
	
	for(i=0;i<10;i++)
	{
		if(sync_recv_packet[i] != sync_recv_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int Change_baud_command(void)
{
	uint8_t change_command[16] = {
		0x00,0x0f,0x08,0x00,0x00,0x00,0x00,0x00,
		0xc0,0xc6,0x2d,0x00,0x00,0x00,0x00,0x00};
		
	uint8_t change_recv[20] = {0};
	uint8_t change_true[10] = {0x01,0x0f,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
	
	Data_formatt_write(change_command,16,HA_HEAD_HA_TAIL);
	Data_formatt_read(change_recv,20);	
	
	for(i=0;i<10;i++)
	{
		if(eras_recv[i] != eras_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int Erasing_data_command(int file_type)
{
	uint8_t eras_command[24] = {
		0x00,0x02,0x10,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
		0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
		
	uint8_t eras_recv[20] = {0};
	uint8_t eras_true[10] = {0x01,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
		
	switch(file_type)
	{
		case FIRMWARE_BIN:
			eras_command[10] = 0x0f;
			eras_command[13] = 0x04;
			eras_command[17] = 0x04;
			break;
		case DATA_INFO:
			eras_command[9] =  0x20;
			eras_command[12] = 0x10;
			eras_command[17] = 0x04;
			eras_command[21] = 0x80;
			eras_command[22] = 0x07;
			break;
		case SIGN_INFO:
			eras_command[9] =  0x20;
			eras_command[12] = 0x10;
			eras_command[17] = 0x04;
			eras_command[21] = 0xa0;
			eras_command[22] = 0x07;
			break;
		default:break;
	}
	
	Data_formatt_write(eras_command,24,HA_HEAD_HA_TAIL);
	Data_formatt_read(eras_recv,20);	
	
	for(i=0;i<10;i++)
	{
		if(eras_recv[i] != eras_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int stub_mem_finish(void)
{
	uint8_t mem_finish_command[16] = { 
		0x00,0x06,0x08,0x00,0x00,0x00,0x00,0x00,
		0x00,0x00,0x00,0x00,0x84,0x06,0x10,0x40
	};
	
	uint8_t men_finish_recv[20] = {0};
	uint8_t men_finish_true[10] = {0x01,0x06,0x02,0x00,0x07,0x07,0x12,0x20,0x00,0x00};
	
	Data_formatt_write(mem_finish_command,16,HA_HEAD_HA_TAIL);
	Data_formatt_read(men_finish_recv,20);	
	
	for(i=0;i<10;i++)
	{
		if(men_finish_recv[i] != men_finish_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int stub_mem_begin(uint8_t type)
{
	uint8_t mem_begin_command[24] = {
		0x00,0x05,0x10,0x00,0x00,0x00,0x00,0x00,0xe0,0x1d,0x00,0x00,
		0x02,0x00,0x00,0x00,0x00,0x18,0x00,0x00,0x00,0x00,0x10,0x40
	};
	
	uint8_t mem_begin_recv[20] = {0};
	uint8_t mem_begin_true[10] = {0x01,0x05,0x02,0x00,0x07,0x07,0x12,0x20,0x00,0x00};
	
	switch(type)
	{
		case MEM_BEGIN_TEXT:
			break;
		case MEM_BEGIN_DATA:
			mem_begin_command[8] =  0x00;
			mem_begin_command[9] =  0x03;
			mem_begin_command[12] = 0x01;
			mem_begin_command[20] = 0x9c;
			mem_begin_command[21] = 0xab;
			mem_begin_command[22] = 0xff;
			mem_begin_command[23] = 0x3f;
			break;
		default:break;
	}
	
	Data_formatt_write(mem_begin_command,24,HA_HEAD_HA_TAIL);
	Data_formatt_read(mem_begin_recv,20);	
	
	for(i=0;i<10;i++)
	{
		if(mem_begin_recv[i] != mem_begin_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int stub_mem_block(uint8_t type)
{
	uint8_t mem_block_recv[20] = {0};
	uint8_t mem_block_true[10] = {0x01,0x07,0x02,0x00,0x07,0x07,0x12,0x20,0x00,0x00};
	
	switch(type)
	{
		case STUB_TEXT_UP:
			Data_formatt_write(stub_text_up,STUB_TEXT_UP_LEN,HA_HEAD_HA_TAIL);
			break;
		case STUB_TEXT_DOWN:
			Data_formatt_write(stub_text_down,STUB_TEXT_DOWN_LEN,HA_HEAD_HA_TAIL);
			break;
		case STUB_DATA:
			Data_formatt_write(stub_data,STUB_DATA_LEN,HA_HEAD_HA_TAIL);
			break;
		default:break;
	}
	
	Data_formatt_read(mem_block_recv,20);	
	
	for(i=0;i<10;i++)
	{
		if(mem_block_recv[i] != mem_block_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int run_stub(void)
{
	stub_mem_begin(MEM_BEGIN_TEXT);
	
	stub_mem_block(STUB_TEXT_UP);
	stub_mem_block(STUB_TEXT_DOWN);
	
	stub_mem_begin(MEM_BEGIN_DATA);
	stub_mem_block(STUB_DATA);
	
	stub_mem_finish();
}

uint8_t checksum(uint8_t *data,int data_len)
{
	int i = 0;
	uint8_t state = 0xef;
	
	for(i=0;i<data_len;i++)
	{
		state ^= data[i];
	}
	
	return state
}

int send_data_command(uint8_t *packet,int data_len,uint8_t seq)
{
	int i = 0;
	uint8_t send_data[16408] = {
		0x00,0x03,0x10,0x40,0x00,0x00,0x00,0x00,0x00,0x40,0x00,0x00,
		0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00
	};
	uint8_t flash_block_recv[20] = {0};
	uint8_t flash_block_true[10] = {0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
	
	
	
	if((data_len < 0x4000) && (data_len > 0x400))
	{
		send_data[3] = 0x30;
		send_data[9] = 0x30;
		send_data[12] = 0x3f;
	}
	else if(data_len < 0x400)
	{
		send_data[2] = 0x0f;
		send_data[3] = 0x10;
		send_data[8] = 0xff;
		send_data[9] = 0x0f;
	}
	send_data[12] = seq;
	send_data[4] = chexksum(packet,data_len);
	
	for(i=0;i<data_len;i++)
	{
		send_data[24+i] = packet[i];
	}
	
	Data_formatt_write(send_data,data_len+24,HA_HEAD_HA_TAIL);
	Data_formatt_read(flash_block_recv,20);	
	
	
	for(i=0;i<10;i++)
	{
		if(flash_block_recv[i] != flash_block_true[i])
		{
			return 0;
		}
	}
	
	return 1;
}

int download_start(void)
{
	uint8_t i = 0;
	uint8_t ret = 1;
	
	ret = device_sync();
	
	if(ret)
	{
		ret = run_stub();
	}
	
	if(ret)
	{
		ret = Change_baud_command();
	}
	
	if(ret)
	{
		for(i=0;i<3;i++)
		{
			
		}
	}
}


