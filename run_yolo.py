

import requests

from tqdm import tqdm
import subprocess
from zipfile import ZipFile 

import wget
import os
import shutil
from argparse import ArgumentParser

def edit_cfg(path,no_classes):
    req_filters = int(int(no_classes) + 5) *3

    file = open(path , 'r')
    lines = file.readlines()
    # print(len(lines))
    for x in range(len(lines)):

        # print(lines[x])
        if lines[x] == 'classes=80\n':
            lines[x] = 'classes='+str(no_classes)+'\n'
            print(lines[x])
        elif lines[x] == 'filters=255\n':
            lines[x] = 'filters='+str(req_filters)+'\n'
            print(lines[x])
        elif lines[x] == 'batch=64\n':
            lines[x] = 'batch='+str(opt.batch)+'\n'

        elif lines[x] == 'subdivisions=8\n':
            lines[x] = 'subdivisions='+str(opt.subdivisions)+'\n'

        elif lines[x].find('max_batches') == 0:
            lines[x] = 'max_batches='+str(opt.max_batches)+'\n'

        elif opt.width != 'default':

            if lines[x].find('width=') == 0:
                lines[x] = 'width='+str(opt.width)+'\n'

        elif opt.height != 'default':

            if lines[x].find('height=') == 0:
                lines[x] = 'height='+str(opt.height)+'\n'



        elif opt.width == 'default':
            if lines[x].find('width=') == 0:
                lines[x] = 'width='+str(416)+'\n'

        if opt.height == 'default':
            if lines[x].find('height=') == 0:
                lines[x] = 'height='+str(416)+'\n'


    file = open(path,'w')
    file.writelines(lines)
    file.close()
    # classes = lines.find('classes=80')
    # print(classes)

def un_zip(source,destination):
        file_name = source
      
        # opening the zip file in READ mode 
        with ZipFile(file_name, 'r') as zip: 
        # printing all the contents of the zip file 
            zip.printdir() 
          
            # extracting all the files 
            print('Extracting all the files now...') 

            # ######## ADD DESTINATION LOCATION HERE
            zip.extractall(destination) 
            print('Done!') 

def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            with tqdm(unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        bar.update(CHUNK_SIZE)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination) 


def find_data_folder(source_path):
    sub_folders = os.listdir(source_path)
    for x in sub_folders:
        full_path = os.path.join(source_path,x)
        check_folde = os.path.isdir(full_path)
        if check_folde is True:
            # data fodler
            check_desired_folder = os.listdir(full_path)
            if len(check_desired_folder) >= 2:
                data_folder = full_path

                # print(data_folder)
    return data_folder
def generate_txt(path):
    # find which is bigger folder
    # Read images from it and create txt in project_folder
    desired_folder = []
    sub_folder = os.listdir(path)
    for x in sub_folder:
        full_path = os.path.join(path,x)
        is_dir = os.path.isdir(full_path)
        if is_dir is True:
            desired_folder.append(full_path)
            lenth = os.listdir(full_path)
            desired_folder.append(len(lenth))

    if int(desired_folder[1]>desired_folder[3]):
        train_dir = desired_folder[0]
        test_dir = desired_folder[2]
        # print(train_dir)
    else:
        train_dir = desired_folder[2]
        test_dir = desired_folder[0]
    # print('train directory',train_dir)
    # print(test_dir)

    sub_train = os.listdir(train_dir)
    sub_test = os.listdir(test_dir)

    ext = extention_img.split(',')

    for x_train in sub_train:
        a = x_train.split('.')
        if a[-1] in ext:

            img_path = os.path.join(train_dir,x_train)
            file1 = open(str(project_fodler)+"/train.txt", "a")  # append mode 
            file1.write(str(img_path)+"\n") 
            file1.close()



    for x_test in sub_test:
        a = x_test.split('.')
        if a[-1] in ext:
            img_path = os.path.join(test_dir,x_test)
            file1 = open(str(project_fodler)+"/test.txt", "a")  # append mode 
            file1.write(str(img_path)+"\n") 
            file1.close()


def obj_names(path):
    # We are getting names from custom data download

    test = os.listdir(path)
    if 'names.txt' in test:
        source_name = os.path.join(path,'names.txt')
        destination_txt = os.path.join(project_fodler,'obj.names')
        shutil.copy(source_name,destination_txt)

    elif 'name.txt' in test:
        source_name = os.path.join(path,'name.txt')
        destination_txt = os.path.join(project_fodler,'obj.names')
        shutil.copy(source_name,destination_txt)


    file2 = open(str(os.path.join(project_fodler,'obj.names')),'r')
    lines = file2.readlines()

    return(len(lines))

def obj_data(path,no_classes):
    # project_folder is path
    obj_data_content = []
    obj_path = os.path.join(path,'obj.data')
    classes = 'classes='+str(no_classes)+'\n'
    train = 'train='+str(os.path.join(path,'train.txt'))+'\n'
    valid = 'valid='+str(os.path.join(path,'test.txt'))+'\n'
    names = 'names='+str(os.path.join(path,'obj.names'))+'\n'
    backup = 'backup='+str(os.path.join(path,'backup'))+'\n'
    back_mkdir = os.path.join(path,'backup')
    check_back_mkdir = os.path.isdir(back_mkdir)
    if check_back_mkdir is False:
        os.mkdir(os.path.join(path,'backup'))
    if check_back_mkdir is True:
        print('FOLDER ALREADY EXISTS')
    obj_data_content.append(classes)
    obj_data_content.append(train)
    obj_data_content.append(valid)
    obj_data_content.append(names)
    obj_data_content.append(backup)

    file3 = open(obj_path,'w')

    file3.writelines(obj_data_content)
    file3.close()

    sub_folder = os.listdir(path)

    for x in sub_folder:
        if x == 'obj.data':
            x1 = os.path.join(path,x)
        if x == 'yolo.cfg':
            x2 = os.path.join(path,x)
        if x == 'yolov4.conv.137':
            x3 = os.path.join(path,x)

    run = './darknet detector train '+x1+' '+x2+' '+x3

    print(run)

    return run


    # ./darknet detector train mask/obj.data mask/yolo.cfg mask/yolov4.conv.137


def start_training(run):
    # run_command = str(run)

    # os.system(run_command)

    run_command = str(run)

    p = subprocess.Popen(run_command, shell=True, stdout=subprocess.PIPE)
    while True:
        out = p.stdout.readline()
        if out.decode("utf-8").find("hours")!=-1:
            print("##########################################")
            print((out.decode("utf-8")))
            print('###########################################')
            x=out.decode("utf-8").split(':')[0]
            if int(x)%100 == 0:
                if x != 0:
                    send_tele(out.decode("utf-8"),'chart.png')





if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--type", default='yolov4', help="Which yolo you want to use yolov4 or yolov3")
    parser.add_argument("--project", required=True, help="Give project name")
    parser.add_argument("--classes", default=5, help="Number of classes")
    parser.add_argument("--batch", default=32, help="Batch size")
    parser.add_argument("--img_typ", default= 'jpg,png,jpge' , help="Image extentions(split by comma)")

    parser.add_argument("--subdivisions", default=8, help="subdivisions size")
    parser.add_argument("--width", default='default', help="Width size should be default or userdefined")
    parser.add_argument("--height", default='default', help="height size should be default or userdefined")
    parser.add_argument("--max_batches", default=40000, help="Number of classes")
    parser.add_argument("--google_id", type = str, help="Give ID or 'already'  ",required = True)








  
    opt = parser.parse_args()

    yolo_name = {'yolov4':'yolov4.cfg' , 'yolov3':'yolov3.cfg'}
# Darknet directory
    current_dir = os.getcwd()
    project_name = opt.project
    type_yolo = opt.type
    google_drive_id = opt.google_id
    extention_img = opt.img_typ


    # make folder named as project 

    project_fodler = os.path.join(os.getcwd(),project_name)
    is_folder = os.path.isdir(project_fodler)
    if is_folder is False:
        os.mkdir(project_fodler)

# Copy desired cfg file to project folder

    file_yolo_name = yolo_name[type_yolo]

    dummy_cfg_dir = 'cfg/'+file_yolo_name 
    source_dir_yolo = os.path.join(current_dir,dummy_cfg_dir )
    destination_cfg = os.path.join(project_fodler, 'yolo.cfg')  
    shutil.copy(source_dir_yolo,destination_cfg)

# DOWNLOAD AND UNZIP STARTS
# DOWNLOAD AND UNZIP STARTS
# DOWNLOAD AND UNZIP STARTS
# DOWNLOAD AND UNZIP STARTS
# DOWNLOAD AND UNZIP STARTS

    is_googleid_dir = os.path.isdir(google_drive_id)
    print(is_googleid_dir)

    if is_googleid_dir is True:

        data_dir = google_drive_id

    
    elif is_googleid_dir is False:

        is_google_id_url = google_drive_id.find('https')
        print('url or not  ',is_google_id_url)
        if is_google_id_url is 0:
            print("Download from a link")
            # ENABLE THIS TO DOWNLOAD FROM LINK
            wget.download(google_drive_id,project_fodler)
            list_sub_folder = os.listdir(project_fodler)
            for x in list_sub_folder:
                check = x.find('.zip')
                if check != -1:
                    source_zip = os.path.join(project_fodler,x)
                    destination_zip = project_fodler

                    un_zip(source_zip,destination_zip)

        elif is_google_id_url == -1 and is_googleid_dir == False :

            print('Download from google drive')
            project_fodler_zip = os.path.join(project_fodler, 'custom_data.zip')
            print('assssssssssssssssssssssssssssssssssssssssss',project_fodler_zip)
            download_file_from_google_drive(google_drive_id,project_fodler_zip)
            sub_folder = os.listdir(project_fodler)
            print('FFFFFFFFFFFFFFFFFFFFFFFFf')
            print(sub_folder)

            # index = sub_folder.index('.zip')
            # zip_folder = os.path.join(project_fodler,sub_folder[index])
            
            for x in range(len(sub_folder)):
                print('RRRRRRRRRRRRRRRR')
                is_zip = sub_folder[x].find('.zip')
                if is_zip != -1:
                    zip_folder = os.path.join(project_fodler,sub_folder[x])

            un_zip(zip_folder,project_fodler)

        data_dir = find_data_folder(project_fodler)

        if type_yolo == 'yolov4':
            wget.download('https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.conv.137',project_fodler)
        if type_yolo == 'yolov3' :
            wget.download('https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.conv.137',project_fodler)
    

# DOWNLOAD AND UNZIP ENDS
# DOWNLOAD AND UNZIP ENDS
# DOWNLOAD AND UNZIP ENDS
# DOWNLOAD AND UNZIP ENDS

    generate_txt(data_dir)
    number_classes = obj_names(data_dir)
    edit_cfg(destination_cfg,number_classes)
    run = obj_data(project_fodler,number_classes)
    start_training(run)
    print(run)








# finalll  working


# https://drive.google.com/uc?id=1mUiOqQTasR_jhI6jZVTe0cFhv7A3ANgr&export=download
# 1mUiOqQTasR_jhI6jZVTe0cFhv7A3ANgr
