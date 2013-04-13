import os

def resize(fullsizepath,resizepath,imagename,width):
    if os.path.isdir(resizepath):
        pass
    else:
        os.mkdir(resizepath)
    os.system("/usr/bin/convert "+fullsizepath+"/"+imagename+" -resize "+width+" "+resizepath+"/"+imagename)
    #os.system("/usr/bin/convert "+fullsizepath+"/"+imagename.split(".")[0]+".jpg -resize "+width+" "+resizepath+"/"+imagename.split(".")[0]+".jpg")
