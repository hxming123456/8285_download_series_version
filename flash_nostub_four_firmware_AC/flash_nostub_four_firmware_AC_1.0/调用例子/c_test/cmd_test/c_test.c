#include <stdio.h>
#include <stdlib.h>

void call_exe(void)
{
	int ret;
	char buf[1024] = {".\\flashtool\\Flash_downloadUI.exe \"com16\" \"Y 10000258ca 5eaefe1f-40e2-4f27-a6d0-d0f16ae8bdab d0:27:00:04:ae:e4 d0:27:00:04:ae:e5 PSF-A01-GL\""};

	ret = system(buf);
	printf("ret is %d\n", ret);
}

int main(int argc,char *argv[])
{
	printf("now path is %s\n",argv[0]);
	call_exe();
	system("pause");
	return 0;
}