import shutil, errno, os, time
src='out'
dst='carryon'
timein=time.clock()
def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            shutil.rmtree(dst)
            print ' please wait while the request is processed'
            time.sleep(5)
            try:
                shutil.copytree(src, dst)
            except OSError as exc: # python >2.5
                if exc.errno == errno.ENOTDIR:
                    shutil.copy(src, dst)
                else: pass
copyanything(src,dst)
timeout=time.clock()
print timeout-timein
#os.system("domainerv2carryon_threaded.py")
