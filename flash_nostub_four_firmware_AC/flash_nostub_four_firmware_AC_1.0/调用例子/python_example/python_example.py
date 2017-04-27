import subprocess
import os

print "start download flash..........."

ret = os.system('.\\flashtool\\flash_downloadUI.exe \"com16\" \"Y 10000258ca 5eaefe1f-40e2-4f27-a6d0-d0f16ae8bdab d0:27:00:04:ae:e4 d0:27:00:04:ae:e5 PSF-A01-GL\"')

print ret
print type(ret)
if ret==0:
    print "download flash succeed"
else:
    print "download flash error"
print "over download flash..........."