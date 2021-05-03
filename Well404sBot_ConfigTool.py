from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from threading import Thread
import os,shutil,random,zipfile


class main:
    def __init__(self):
        self.ui = QUiLoader().load('resources/main.ui')
        self.ui.CreatBot.clicked.connect(self.creat_bot_check)
        self.ui.refresh.clicked.connect(self.refresh_bot)
        self.ui.comboBox.currentIndexChanged.connect(self.currentIndexChanged)
        self.disable_button(True)
        self.refresh_bot(True)
        self.ui.StartBot.clicked.connect(self.start_bot_check)
        self.ui.CloseBot.clicked.connect(self.close_bot_check)
        self.ui.ResetSuperuser.clicked.connect(self.ResetSuperuser_check)
        self.ui.AddPlugins.clicked.connect(self.add_plugins)
        
    def creat_bot_check(self):
        superuserlst = []
        #获取信息
        qqnum = self.ui.QQnum.text()
        superusers = self.ui.Superuser.text()
        portnum = self.ui.Port.text()
        #判断信息是否正确
        #机器人qq号
        if qqnum.isdigit():
            pass
        else:
            self.ui.Info.appendPlainText("Error:请正确填写机器人的qq号！")
            QMessageBox.critical(
            self.ui,
            '错误',
            '请正确填写机器人的qq号！')
            return
        #管理员qq号
        try:
            for superuser in superusers.split(' '):
                superuserlst.append(superuser)
        except:
            self.ui.Info.appendPlainText("Error:请正确填写管理员的qq号！")
            QMessageBox.critical(
            self.ui,
            '错误',
            '请正确填写管理员的qq号！')
            return
        #端口号
        portnum,portnum_o = check_portnum(portnum),portnum
        if portnum_o == portnum:
            pass
        else:
            self.ui.Info.appendPlainText(f"Warning:无效的端口号，已使用随机生成的{portnum}作为端口号")
        #开始执行
        self.ui.Info.appendPlainText(creat_bot(qqnum,superuserlst,portnum))
        #安装依赖库
        os.system('pip uninstall nonebot')
        libs = ['nb-cli','nonebot-adapter-cqhttp']
        pip(libs)
    
    def refresh_bot(self,disable_warning = False):
        bot_list = read_bot()
        if bool(len(bot_list)):
            self.ui.comboBox.clear()
            self.ui.comboBox.addItems(bot_list)
            self.disable_button(True)
            if not disable_warning:
                self.ui.Info.appendPlainText("Info:已刷新机器人列表！")
        else:
            if not disable_warning:
                self.ui.Info.appendPlainText("Error:无法找到机器人，请先创建机器人！")
                QMessageBox.critical(
                self.ui,
                '错误',
                '无法找到机器人，请先创建机器人！')
                
    def disable_button(self,disable = False):
        if not disable:
            self.ui.StartBot.setEnabled(True)
            self.ui.AddPlugins.setEnabled(True)
            self.ui.RemovePlugins.setEnabled(True)
            self.ui.ResetSuperuser.setEnabled(True)
        else:
            self.ui.StartBot.setEnabled(False)
            self.ui.AddPlugins.setEnabled(False)
            self.ui.RemovePlugins.setEnabled(False)
            self.ui.ResetSuperuser.setEnabled(False)
    
    def currentIndexChanged(self):
        bot_name = self.ui.comboBox.currentText()
        if bool(bot_name):
            self.disable_button(disable = False)
    
    def start_bot_check(self):
        bot_name = self.ui.comboBox.currentText()
        os.system(f'cd {bot_name}/gocq/ & cmd/C start start.bat ')
        os.system(f'cd {bot_name}/nb2/ & cmd/C start python bot.py ')
        self.ui.Info.appendPlainText("Info:您已一键开启机器人")
        self.ui.Info.appendPlainText("Info:请注意cmd中的信息！！！")
        self.ui.CloseBot.setEnabled(True)
        self.disable_button(True)

    def close_bot_check(self):
        QMessageBox.critical(
                self.ui,
                '关闭机器人',
                '请将cmd窗口与本窗口一起关闭即可关闭机器人')

    def ResetSuperuser_check(self):
        superusers, okPressed = QInputDialog.getText(
                self.ui, 
                "输入新的超级用户",
                "请输入新的超级用户，多个超级用户可用空格分隔，本操作将删除原有超级用户数据:",
                QLineEdit.Normal,
                "")
        if okPressed:
            superuserlst = []
            for superuser in superusers.split(' '):
                superuserlst.append(superuser)
            file = f'{self.ui.comboBox.currentText()}/nb2/.env'
            with open(file, "r", encoding="utf-8") as f1,open("%s.bak" % file, "w", encoding="utf-8") as f2:
                for line in f1:
                    if 'SUPERUSERS' in line:
                        sustr = '","'.join(superuserlst)
                        line = f'SUPERUSERS=["{sustr}"]\n'
                    f2.write(line)
            os.remove(file)
            os.rename("%s.bak" % file, file)
            self.ui.Info.appendPlainText("Info:您已修改超级用户")

    def add_plugins(self):
        bot_name = self.ui.comboBox.currentText()
        filePath, filetype  = QFileDialog.getOpenFileName(
            self.ui,             # 父窗口对象
            "选择你要添加的插件", # 标题
            r"C:\\",        # 起始目录
            "压缩文件类型 (*.zip)" # 选择类型过滤项，过滤内容在括号中
            )
        if filetype:
            file_requirements = f"{bot_name}/nb2/requirements.txt"
            #移除旧的requirements.txt
            try:
                os.remove(file_requirements)
            except:
                pass
            #解压文件
            with zipfile.ZipFile(filePath,mode="a") as f:
                f.extractall(f"{bot_name}/nb2/")
            #安装依赖
            try:
                libs=[]
                with open(file_requirements,'r') as f:
                    for lib in f:
                        libs.append(lib)
                pip(libs)
                os.remove(file_requirements)
            except:
                pass
            self.ui.Info.appendPlainText('Info:成功导入插件包')
        
        
#创建机器人
def creat_bot(qqnum,superuser,portnum):
    #先创建该文件夹
    dirname = f'BOT{qqnum}-{portnum}'
    os.mkdir(dirname)
    #复制资源至文件夹
    try:
        shutil.copytree('resources/gocq', f'{dirname}/gocq')
        shutil.copytree('resources/nb2', f'{dirname}/nb2')
    except:
        return 'Error:无法复制资源文件，请检查resources文件夹内的文件是否齐全，或已存在该文件夹'
    #更改配置文件
    try:
        #修改gocq的配置
        file = f'{dirname}/gocq/config.yml'
        with open(file, "r", encoding="utf-8") as f1,open("%s.bak" % file, "w", encoding="utf-8") as f2:
            for line in f1:
                if '-qqnum-' in line:
                    line = line.replace('-qqnum-', str(qqnum))
                elif '-port-' in line:
                    line = line.replace('-port-', str(portnum))
                f2.write(line)
        os.remove(file)
        os.rename("%s.bak" % file, file)
        #修改nb2配置
        file = f'{dirname}/nb2/.env'
        with open(file, "r", encoding="utf-8") as f1,open("%s.bak" % file, "w", encoding="utf-8") as f2:
            for line in f1:
                if '-SUPERUSERS-' in line:
                    line = line.replace('-SUPERUSERS-', '","'.join(superuser))
                elif '-port-' in line:
                    line = line.replace('-port-', str(portnum))
                f2.write(line)
        os.remove(file)
        os.rename("%s.bak" % file, file)
    except:
         return 'Error:无法修改配置文件，请检查resources文件夹内的文件是否齐全'
    return f'Info:已成功创建该机器人，机器人QQ号为{qqnum}，管理者的qq号为{superuser}，运行的端口号为{portnum}'

#读取已有机器人
def read_bot(mod = 'bot'):
    botlist = []
    portlist = []
    files = os.listdir()
    for f in files:
        if f.startswith('BOT'):
            botlist.append(f)
            _,port = f.split('-')
            portlist.append(int(port))
    if mod == 'port':
        return portlist
    else:
        return botlist

#检查端口号，不合规则随机生成一个
def check_portnum(portnum = ''):
    try:
        if int(portnum) > 5000:
            if not int(portnum) in read_bot(mod = 'port'):
                return int(portnum)
        return check_portnum(random.randint(10000, 65535))
    except:
        return check_portnum(random.randint(10000, 65535))
#安装依赖库
def pip(libs):
    def action(libs):
        print ("开始线程pip")
        trytime = 0
        failed_libs = []    
        while len(libs):
            trytime += 1
            #读取已安装的库的列表
            lib_str = os.popen('pip freeze').read()
            #遍历要安装的库
            for lib in libs:
                #查看该库是否已安装，是则移除，不是则安装，每个源尝试两次
                try:
                    lib_check,_ = lib.split('==')
                except:
                    lib_check = lib
                if lib_check in lib_str:
                    print(f'{lib}已安装')
                    libs.remove(lib)
                else:
                    print(f'{lib}未安装，正在进行第{trytime}次尝试')
                    try:
                        #第一轮尝试用清华镜像源
                        if trytime <= 2:
                            print('正在尝试从清华大学镜像源安装')
                            os.system("pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn " + lib)
                        #最后一轮尝试用官方源
                        elif trytime <= 8:
                            print('正在尝试从官方源安装')
                            os.system("pip install -i https://pypi.org/simple --trusted-host pypi.org " + lib)
                        elif trytime <=10:
                            print('正在尝试从官方源安装，并忽略版本')
                            os.system("pip install -i https://pypi.org/simple --trusted-host pypi.org " + lib_check)
                        #上述方法均尝试过之后，
                        elif trytime > 10:
                            failed_libs.append(lib)
                            libs.remove(lib)
                    except Exception as e:
                        print(e)
                        if trytime > 10:
                            failed_libs.append(lib)
                            libs.remove(lib)
        for i in range(10):
            if len(failed_libs):
                print(f'{failed_libs}未能成功安装，请重新安装')
            else:
                print('所需的库全部安装成功')
        print ("退出线程pip")
    thread = Thread(target = action,
                        args=(libs,))
    thread.start()
    
    
if __name__ == '__main__':   
    app = QApplication([])
    Main = main()
    Main.ui.show()
    app.exec_()