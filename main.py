from PIL import Image, ImageDraw
from aip import AipOcr
import os

quesSplit = 0
config = {
    'appId': '18593767',
    'apiKey': 'XOLbgmM4rVOrItuq6w9odqZb',
    'secretKey': 'eGklNu6hVw7iDvQ29aALj7hN5VwHvLqh'
}
client = AipOcr(**config)


def solveImage(im):
    w, h = im.size
    cropped = im.crop((int(w / 6.75), int(h / 3.4), int(w / 1.14), int(h / 1.47)))
    w1, h1 = ((int(w / 1.14) - int(w / 6.75)), (int(h / 1.47) - int(h / 3.4)))
    imReturn = Image.new(mode="RGB", size=(w1, h1), color='white')
    draw = ImageDraw.Draw(imReturn)
    imHei = cropped.convert("L")
    for i in range(w1):
        for j in range(h1):
            gray = imHei.getpixel((i, j))
            if gray >= 230:
                draw.point((i, j), fill=(0, 0, 0))
    return imReturn


def cropImage(im):
    global quesSplit
    imHei = im.convert("L")
    w, h = im.size
    imsReturn = []
    lineHS = []
    lineHE = []
    lineWS = []
    lineWE = []
    j = 0
    flagH = 0
    while j < h:
        flagWS = 0
        flagWE = 0
        i = 0
        while i < w:
            if imHei.getpixel((i, j)) == 0 and flagWS == 0:
                lineWS.append(i)
                flagWS = 1
            if imHei.getpixel((w - 1 - i, j)) == 0 and flagWE == 0:
                lineWE.append(w - 1 - i)
                flagWE = 1
            if flagWS == 1 and flagWE == 1:
                break
            i += 1
        if flagH == 0 and flagWS == 1:
            lineHS.append(j)
            flagH = 1
        if flagH == 1 and flagWE == 0 and flagWS == 0:
            lineHE.append(j)
            flagH = 0
        j += 1
    lineWSRec = []
    lineWERec = []
    for i in range(len(lineHS)):
        if i == 0:
            lineWERec.append(max(lineWE[0:(lineHE[i] - lineHS[i])]))
            lineWSRec.append(min(lineWS[0:(lineHE[i] - lineHS[i])]))
        else:
            lineWERec.append(max(
                lineWE[(lineHE[i - 1] - lineHS[i - 1]):((lineHE[i - 1] - lineHS[i - 1]) + (lineHE[i] - lineHS[i]))]))
            lineWSRec.append(min(
                lineWS[(lineHE[i - 1] - lineHS[i - 1]):((lineHE[i - 1] - lineHS[i - 1]) + (lineHE[i] - lineHS[i]))]))
    for i in range(len(lineHS)):
        imsReturn.append(im.crop((lineWSRec[i], lineHS[i], lineWERec[i], lineHE[i])))
    lineHeight = lineHE[0] - lineHS[0]
    for splitI in range(len(lineHS) - 1):
        if lineHS[splitI + 1] - lineHE[splitI] >= lineHeight:
            quesSplit = splitI
            break
    return imsReturn


def get_file_content(file):
    with open(file, 'rb') as fp:
        return fp.read()


def img_to_str(image_path):
    image = get_file_content(image_path)
    result = client.basicGeneral(image)
    resultStr = ''
    try:
        for i in range(result['words_result_num']):
            resultStr += result['words_result'][i]['words']
        print(result)
    except:
        return ''
    return resultStr


solveList = []
quesAns = []
quesAnsFileStr = ''
with open('num.dat', 'r+') as file:
    k = int(file.read())
    while True:
        if input("是否截图：Yes(Enter) Quit(Q)") == '':
            k += 1
            solveList.append(k)
            os.system("mkdir " + str(k))
            os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
            os.system("adb pull /sdcard/screenshot.png ./" + str(k) + '/')
        else:
            for m in solveList:
                print('正在切割识别第' + str(m) + '张图像...')
                screen = Image.open("./" + str(m) + '/' + 'screenshot.png')
                imText = solveImage(screen)
                imCropped = cropImage(imText)
                os.makedirs('./' + str(m) + '/ques')
                os.makedirs('./' + str(m) + '/ans')
                flag = 0
                for i in range(len(imCropped)):
                    if i > quesSplit:
                        imCropped[i].save("./" + str(m) + '/ans/' + str(i) + '.jpg', 'jpeg')
                    else:
                        imCropped[i].save("./" + str(m) + '/ques/' + str(i) + '.jpg', 'jpeg')

                for i in range(len(imCropped)):
                    if i > quesSplit:
                        quesAns.append('Ans: ' + img_to_str("./" + str(m) + '/ans/' + str(i) + '.jpg'))
                    else:
                        if flag == 0:
                            quesAns.append(str(m) + '. ' + img_to_str("./" + str(m) + '/ques/' + str(i) + '.jpg'))
                            flag = 1
                        else:
                            quesAns[-1] += img_to_str("./" + str(m) + '/ques/' + str(i) + '.jpg')
            break
    for quesAnsStr in quesAns:
        quesAnsFileStr += quesAnsStr + '\n'
    open('tiku.txt', 'a').write(quesAnsFileStr)
    file.seek(0)
    file.truncate()
    file.write(str(k))
    file.close()
    exit()
