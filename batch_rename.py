import os
import exifread
import time

# Convert struct time into time stamp
# '2020:09:10 08:49:45' -> 1599698985
def st2ts(st):
    yyyy, mm, dd = st[:10].split(':')
    HH, MM, SS = st[10:19].split(':')       # 不能写成st[-8:]，有的st会是'2020:11:01 16:50:22下午'这种，还带汉字

    st = (int(yyyy), int(mm), int(dd), int(HH), int(MM), int(SS), 0, 0, 0)

    return time.mktime(st)      # return timestamp

# Convert time stamp into struct time
# 1599698985 -> '20200910_084945'
def ts2st(ts):
    st = time.localtime(ts)
    yyyy = st.tm_year
    mm = st.tm_mon
    dd = st.tm_mday
    HH = st.tm_hour
    MM = st.tm_min
    SS = st.tm_sec

    return '%0004d%02d%02d_%02d%02d%02d' % (yyyy, mm, dd, HH, MM, SS)

# Return the earliest time of a given photo
# 'D:/Folder/IMG_6803.JPG' -> '20200910_084945'
def foto_time(foto_path):
    io = open(foto_path, 'rb')
    tags_dict = exifread.process_file(io)
    io.close()

    times_list = []     # [1599698985, 1603014228, ..., timestamp]
    if 'Image DateTime' in tags_dict:
        st = str(tags_dict['Image DateTime'])
        times_list.append(st2ts(st))
    if 'EXIF DateTimeOriginal' in tags_dict:
        st = str(tags_dict['EXIF DateTimeOriginal'])
        times_list.append(st2ts(st))
    if 'EXIF DateTimeDigitized' in tags_dict:
        st = str(tags_dict['EXIF DateTimeDigitized'])
        times_list.append(st2ts(st))

    created_time = os.path.getctime(foto_path)
    times_list.append(created_time)

    modified_time = os.path.getmtime(foto_path)
    times_list.append(modified_time)

    # accessed_time = os.path.getatime(foto_path)       # 通常都是最晚的，不用比了
    # time_list.append(accessed_time)

    ts_earliest = min(times_list)

    return ts2st(ts_earliest)

def foto_rename(src, dst):
    # src = 'IMG_7222.JPG'  # 当前路径
    # dst = '20201021_174925.JPG'  # 绝对路径必须和src在同一磁盘内。dst文件夹必须存在，否则移不过去，会报错，不会自动建
    if not os.path.exists(src):
        print(src, 'is NOT found!')
        return
    # 但src可以是文件夹，也可以为文件夹重命名

    src = src.replace('\\', '/')
    old_name_e = src[src.rfind('/') + 1:]

    dst = dst.replace('\\', '/')
    if '/' in dst and dst[:2] != './':  # 绝对路径
        dst_path = dst[:dst.rfind('/')]
    else:  # 当前路径
        dst_path = os.getcwd()

    new_name_e = dst[dst.rfind('/') + 1:]  # 'IMG_7233.JPG' 含扩展名
    dot_bit = new_name_e.rfind('.')
    new_name = new_name_e[:dot_bit]  # 'IMG_7233' 纯名称，不含扩展名
    e_name = new_name_e[dot_bit:]  # '.JPG'    . + 扩展名

    files_list = os.listdir(dst_path)

    n_similar = 0  # 已存在同名文件的数量
    for name_e in files_list:
        name = name_e[:name_e.rfind('.')]  # 目标路径下每个文件的纯名称，不含扩展名
        if new_name in name:  # 如果已存在同名文件(IMG_7233, IMG_7233_1, IMG_7233_2,...)
            suffix = name.replace(new_name, '').strip('_')  # 已存在的同名文件的后缀数字
            if suffix == '':  # 无后缀
                n_similar = 1  # 已经有1个同名文件
            elif int(suffix) + 1 > n_similar:
                n_similar = int(suffix) + 1

    # 如果已存在同名文件，处理一下保存的文件名，加后缀编号
    if n_similar != 0:
        new_name += ('_' + str(n_similar))
        dst = dst_path + '/' + new_name + e_name

    try:
        os.rename(src, dst)  # 相当于移动。重命名完，源路径下文件会消失
    except Exception as e:
        print(e)
        print(old_name_e, '->', new_name + e_name, '\tRename Fail!')
    else:
        print(old_name_e, '->', new_name + e_name, '\tRename Success.')


def batch_rename(src):
    # src: folder or file_name
    if not os.path.exists(src):
        print(src, 'is NOT found!')
        return
    elif os.path.isfile(src):
        path = src[:src.rfind('/') + 1]            # 路径名(含最后的 /)
        new_name = foto_time(src)           # 新名称(拍摄时间，不含扩展名)
        e_name = os.path.splitext(src)[1]      # . + 扩展名
        dst = path + new_name + e_name
        foto_rename(src, dst)
    elif os.path.isdir(src):
        name_e_list = []
        path_name_e_list = []

        for (path, dir, file) in os.walk(src):
            for name_e in file:
                path_name_e_list.append(path.replace('\\', '/') + '/' + name_e)
            name_e_list.extend(name_e)

        for path_name_e in path_name_e_list:
            path = path_name_e[:path_name_e.rfind('/') + 1]     # 路径名(含最后的 /)
            new_name = foto_time(path_name_e)                       # 新名称(拍摄时间，不含扩展名)
            e_name = os.path.splitext(path_name_e)[1]              # . + 扩展名
            dst = path + new_name + e_name

            foto_rename(path_name_e, dst)

src = 'C:/Users/lenovo/Desktop/新建文件夹 (3)/'     # 亦可直接填待处理的文件名  src = 'D:/myFolder/IMG_7243.JPG'
batch_rename(src)