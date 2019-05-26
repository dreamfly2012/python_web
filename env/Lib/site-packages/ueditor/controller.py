# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import *
import os, codecs
import json
import random
import re
from urllib import parse, request as url_request
import shortuuid
from qiniu import Auth, put_file

config_path = os.path.join(os.path.dirname(__file__), "ueconfig.json")
base_dir = settings.BASE_DIR  # 项目的根目录


# 本地上传图片时构造json返回值
class JsonResult(object):
    def __init__(self, state="未知错误", url="", title="", original="", error="null"):
        super(JsonResult, self).__init__()
        self.state = state
        self.url = url
        self.title = title
        self.original = original
        self.error = error


# 构造返回json
def buildJsonResult(result):
    jsondata = {"state": result.state, "url": result.url, "title": result.title, "original": result.original,
                "error": result.error}
    return json.dumps(jsondata)


def buildFileName(pathformat, filename):
    """
        PathFormat处理
    """

    dt = datetime.now()
    name, ext = os.path.splitext(filename)

    # 创建替换字典
    keys = ['{filename}', '{time}', '{yyyy}', '{yy}', '{mm}', '{dd}', '{hh}', '{ii}', '{ss}', ]
    values = [name, '%H%M%S', '%Y', '%y', '%m', '%d', '%H', '%M', '%S', ]
    texts = dict(zip(keys, values))

    # 遍历对应替换
    format_text = pathformat
    for key, value in texts.items():
        format_text = format_text.replace(key, value)

    # 处理随机数
    regstr = r'{rand:(\d+?)}'
    ms = re.search(regstr, format_text)
    group = ms.group()
    if group:
        rand_length = int(ms.groups()[0])  # 获取随机数字的长度
        rand_number = random.randint(1, 10 ** rand_length - 1)  # 生成随机数
        rand_number = str(rand_number).zfill(rand_length)  # 不足位数补0
        format_text = format_text.replace(group, rand_number)

    return dt.strftime(format_text) + ext


# 读取json文件
def getConfigContent():
    jsonfile = open(config_path)
    content = json.load(jsonfile)
    return content


# 上传配置类
class UploadConfig(object):
    def __init__(self, PathFormat, UploadFieldName, SizeLimit, AllowExtensions, SavePath, Base64, Base64Filename):
        super(UploadConfig, self).__init__()
        self.PathFormat = PathFormat
        self.UploadFieldName = UploadFieldName
        self.SizeLimit = SizeLimit
        self.AllowExtensions = AllowExtensions
        self.SavePath = SavePath
        self.Base64 = Base64
        self.Base64Filename = Base64Filename


# 获取json配置中的某属性值
def GetConfigValue(key):
    config = getConfigContent()
    return config[key]


# 检查文件扩展名是否在允许的扩展名内
def CheckFileType(filename, AllowExtensions):
    exts = list(AllowExtensions)
    name, ext = os.path.splitext(filename)
    return ext in exts


def CheckFileSize(filesize, SizeLimit):
    return filesize < SizeLimit


# 处理上传图片、文件、视频文件
@csrf_exempt
def uploadFile(request, config):
    result = JsonResult()
    if config.Base64:
        pass
    else:
        buf = request.FILES.get(config.UploadFieldName)
        filename = buf.name
        if not CheckFileType(filename, config.AllowExtensions):
            result.error = u"不允许的文件格式"
            return HttpResponse(buildJsonResult(result))

        if not CheckFileSize(buf.size, config.SizeLimit):
            result.error = u"文件大小超出服务器限制"
            return HttpResponse(buildJsonResult(result))

        try:
            truelyName = buildFileName(config.PathFormat, filename)
            webUrl = config.SavePath + truelyName
            savePath = base_dir + webUrl

            # 判断文件夹是否存在，不存在则创建
            folder, filename = os.path.split(savePath)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            print(base_dir, savePath)

            f = codecs.open(savePath, "wb")
            for chunk in buf.chunks():
                f.write(chunk)
            f.flush()
            f.close()

            add_watermark(savePath)  # 加水印

            result.state = "SUCCESS"
            result.url = truelyName
            result.title = truelyName
            result.original = truelyName
            response = HttpResponse(buildJsonResult(result))
            response["Content-Type"] = "text/plain"
            return response
        except Exception as e:
            result.error = u"网络错误"
            return HttpResponse(buildJsonResult(result))


@csrf_exempt
def catcher_remote_image(request):
    """远程抓图，当catchRemoteImageEnable:true时，
        如果前端插入图片地址与当前web不在同一个域，则由本函数从远程下载图片到本地
    """
    return False
    if not request.method == "POST":
        return HttpResponse(json.dumps("{'state:'ERROR'}"), content_type="application/javascript")

    state = "SUCCESS"

    allow_type = list(request.GET.get("catcherAllowFiles", GetConfigValue("imageAllowFiles")))
    max_size = int(request.GET.get("catcherMaxSize", GetConfigValue("imageMaxSize")))

    remote_urls = request.POST.getlist("source[]", [])
    catcher_infos = []
    path_format_var = get_path_format_vars()

    for remote_url in remote_urls:
        # 取得上传的文件的原始名称
        url_obj = parse.urlparse(remote_url)
        remote_file_name = os.path.basename(url_obj.path)
        remote_original_name, remote_original_ext = os.path.splitext(remote_file_name)
        # 文件类型检验
        if remote_original_ext in allow_type:
            path_format_var.update({
                "basename": remote_original_name,
                "extname": remote_original_ext[1:],
                "filename": remote_original_name
            })
            # 计算保存的文件名
            dir_name = 'article/' + datetime.now().strftime('%Y%m%d') + '/'
            full_dir = os.path.join(settings.MEDIA_ROOT, dir_name)
            if not os.path.exists(full_dir):
                os.makedirs(full_dir)
            file_name = shortuuid.uuid() + remote_original_ext
            file_path = os.path.join(full_dir, file_name)
            # 读取远程图片文件
            try:
                url_request.urlretrieve(remote_url,file_path)
                ret, info = upload_qiniu(file_path, file_name)
                image_url = settings.QINIU_URL + ret['key']
            except Exception as e:
                state = "抓取图片错误: %s" % str(e)

            catcher_infos.append({
                "state": state,
                "url": image_url,
                "size": os.path.getsize(file_path),
                "title": os.path.basename(file_path),
                "original": remote_file_name,
                "source": remote_url
            })

    return_info = {
        "state": "SUCCESS" if len(catcher_infos) > 0 else "ERROR",
        "list": catcher_infos
    }

    return HttpResponse(json.dumps(return_info, ensure_ascii=False), content_type="application/javascript")


def get_path_format_vars():
    return {
        "year": datetime.now().strftime("%Y"),
        "month": datetime.now().strftime("%m"),
        "day": datetime.now().strftime("%d"),
        "date": datetime.now().strftime("%Y%m%d"),
        "time": datetime.now().strftime("%H%M%S"),
        "datetime": datetime.now().strftime("%Y%m%d%H%M%S"),
        "rnd": random.randrange(100, 999)
    }


def upload_qiniu(local_url, file_name, bucket_name=settings.QINIU_BUCKET):
    qiniu = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    upload_folder = os.path.join(settings.QINIU_FOLDER, datetime.now().strftime('%Y%m%d')+'/')
    upload_name = upload_folder + file_name
    token = qiniu.upload_token(bucket_name, upload_name, 3600)
    ret, info = put_file(token, upload_name, local_url)
    return ret, info


# 加水印
def add_watermark(savePath):
    try:
        # 判断是否是图片文件
        if not os.path.splitext(savePath)[-1].lower() in ['.jpg', '.jpge', '.png', '.bmp']:
            return

        # 获取配置
        config = getConfigContent()
        is_mark = config.get('openWaterMark', False)  # 是否开启加水印功能
        watermark = config.get('waterMarkText', '')  # 水印内容
        font = config.get('waterMarkFont', 'msyhbd.ttf')  # 字体
        size = config.get('waterMarkSize', 15)  # 字体大小
        bottom = config.get('waterMarkBottom', 45)  # 下边距
        right = config.get('waterMarkRight', 155)  # 右边距

        # 判断是否开启了加水印功能
        if not is_mark:
            return

        # python2.7 pillow
        from PIL import Image, ImageDraw, ImageFont

        # 打开图片
        im = Image.open(savePath).convert('RGBA')

        # 透明的图层，用于写文本
        text_layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)

        # 加载字体，设置大小
        font_path = os.path.join(os.path.dirname(__file__), font)
        fnt = ImageFont.truetype(font_path, size)  # 要加中文字体才能识别中文

        point = (text_layer.size[0] - right, text_layer.size[1] - bottom)  # 位置
        draw.text(point, watermark, font=fnt, fill=(255, 255, 255, 255))
        # out=Image.alpha_composite(im, text_layer)
        out = Image.composite(text_layer, im, text_layer)
        out.save(savePath)
        out.close()
    except Exception as e:
        print('[error]', e.message)


# 处理在线图片与在线文件
# 返回的数据格式：{"state":"SUCCESS","list":[{"url":"upload/image/20140627/6353948647502438222009315.png"},{"url":"upload/image/20140627/6353948659383617789875352.png"},{"url":"upload/image/20140701/6353980733328090063690725.png"},{"url":"upload/image/20140701/6353980745691597223366891.png"},{"url":"upload/image/20140701/6353980747586705613811538.png"},{"url":"upload/image/20140701/6353980823509548151892908.png"}],"start":0,"size":20,"total":6}
def listFileManage(request, imageManagerListPath, imageManagerAllowFiles, listsize):
    pstart = request.GET.get("start")
    start = pstart == None and int(pstart) or 0
    psize = request.GET.get("size")
    size = psize == None and int(GetConfigValue(listsize)) or int(psize)
    localPath = base_dir + imageManagerListPath

    # 2016-10-31自动创建在线管理的文件夹
    if not os.path.isdir(localPath):
        os.makedirs(localPath)

    filelist = []
    exts = list(imageManagerAllowFiles)
    index = start
    for imagename in os.listdir(localPath):
        name, ext = os.path.splitext(imagename)
        if ext in exts:
            filelist.append(dict(url=imagename))
            index += 1
            if index - start >= size:
                break
    jsondata = {"state": "SUCCESS", "list": filelist, "start": start, "size": size, "total": index}
    return HttpResponse(json.dumps(jsondata))


# 返回配置信息
def configHandler(request):
    content = getConfigContent()
    callback = request.GET.get("callback")
    if callback:
        return HttpResponse("{0}{1}".format(callback, json.dumps(content)))
    return HttpResponse(json.dumps(content))


# 图片上传控制
@csrf_exempt
def uploadimageHandler(request):
    AllowExtensions = GetConfigValue("imageAllowFiles")
    PathFormat = GetConfigValue("imagePathFormat")
    SizeLimit = GetConfigValue("imageMaxSize")
    UploadFieldName = GetConfigValue("imageFieldName")
    SavePath = GetConfigValue("imageUrlPrefix")
    upconfig = UploadConfig(PathFormat, UploadFieldName, SizeLimit, AllowExtensions, SavePath, False, '')
    return uploadFile(request, upconfig)


def uploadvideoHandler(request):
    AllowExtensions = GetConfigValue("videoAllowFiles")
    PathFormat = GetConfigValue("videoPathFormat")
    SizeLimit = GetConfigValue("videoMaxSize")
    UploadFieldName = GetConfigValue("videoFieldName")
    SavePath = GetConfigValue("videoUrlPrefix")
    upconfig = UploadConfig(PathFormat, UploadFieldName, SizeLimit, AllowExtensions, SavePath, False, '')
    return uploadFile(request, upconfig)


def uploadfileHandler(request):
    AllowExtensions = GetConfigValue("fileAllowFiles")
    PathFormat = GetConfigValue("filePathFormat")
    SizeLimit = GetConfigValue("fileMaxSize")
    UploadFieldName = GetConfigValue("fileFieldName")
    SavePath = GetConfigValue("fileUrlPrefix")
    upconfig = UploadConfig(PathFormat, UploadFieldName, SizeLimit, AllowExtensions, SavePath, False, '')
    return uploadFile(request, upconfig)


# 在线图片
def listimageHandler(request):
    imageManagerListPath = GetConfigValue("imageManagerListPath")
    imageManagerAllowFiles = GetConfigValue("imageManagerAllowFiles")
    imagelistsize = GetConfigValue("imageManagerListSize")
    return listFileManage(request, imageManagerListPath, imageManagerAllowFiles, imagelistsize)


# 在线文件
def ListFileManagerHander(request):
    fileManagerListPath = GetConfigValue("fileManagerListPath")
    fileManagerAllowFiles = GetConfigValue("fileManagerAllowFiles")
    filelistsize = GetConfigValue("fileManagerListSize")
    return listFileManage(request, fileManagerListPath, fileManagerAllowFiles, filelistsize)


actions = {
    "config": configHandler,
    "uploadimage": uploadimageHandler,
    "uploadvideo": uploadvideoHandler,
    "uploadfile": uploadfileHandler,
    "listimage": listimageHandler,
    "listfile": ListFileManagerHander,
    "catchimage": catcher_remote_image,
}


@csrf_exempt
def handler(request):
    action = request.GET.get("action")
    return actions.get(action)(request)
