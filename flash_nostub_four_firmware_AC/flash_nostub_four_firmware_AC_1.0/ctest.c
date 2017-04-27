#include <stdio.h>
#include <stdlib.h>

int call_exe(void)
{
	int ret;
	uint8_t buf[1024] = {0};
  
	sprintf(buf,"%s %s %s",".\dist\Flash_downloadUI(1).exe","\"com5\"","\"Y 10000258ca 5eaefe1f-40e2-4f27-a6d0-d0f16ae8bdab d0:27:00:04:ae:e4 d0:27:00:04:ae:e5 PSF-A01-GL\"");
	ret = system(buf);
	printf("ret is %d\n",ret);
	return ret;
}

int main(void)
{
	call_exe();
	return 0
}