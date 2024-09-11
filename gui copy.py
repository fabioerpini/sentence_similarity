import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
import random
from PyQt6.QtCore import QTimer
import os 
import json
from datetime import datetime
import sys

DEBUG = False

class MainWindow(qtw.QWidget):
    def __init__(self):
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists('data/external'):
            os.mkdir('data/external')
            if not os.path.exists('data/external/subscale_file.csv'):
                with open('data/external/subscale_file.csv', 'w', encoding='utf-8') as file:
                    file.write('')
            with open('settings.json', 'w', encoding='utf-8') as file:
                file.write('{"subscale_file": "data/external/subscale_file.csv", "choice_method": "random"}')
        if not os.path.exists('data/evaluations'):
            os.mkdir('data/evaluations')
        if not os.path.exists('settings.json'):
            with open('settings.json', 'w', encoding='utf-8') as file:
                file.write('{"subscale_file": "data/external/subscale_file.csv", "choice_method": "random"}')
        if not os.path.exists('data/temp'):
            os.mkdir('data/temp')
        super().__init__()
        self.setWindowTitle('Semantic Similarity')
        self.showMaximized()

        self.setLayout(qtw.QVBoxLayout())
        self.login_page()

    def login_page(self, message = ''):
        self.clearLayout(self.layout())
        title = qtw.QLabel('Semantic Similarity')
        title.setFont(qtg.QFont('Arial', 20))
        title.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        username = qtw.QLineEdit()
        username.setPlaceholderText('Username')
        password = qtw.QLineEdit()
        password.setPlaceholderText('Password')
        password.setEchoMode(qtw.QLineEdit.EchoMode.Password)
        login_button = qtw.QPushButton('Login', clicked = lambda: self.check_login(username.text(), password.text()))

        groupbox = qtw.QGroupBox('Login')
        groupbox.setLayout(qtw.QVBoxLayout())
        groupbox.layout().addWidget(title)
        groupbox.layout().addSpacing(20)
        groupbox.layout().addWidget(username, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        groupbox.layout().addWidget(password, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        groupbox.layout().addWidget(login_button, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        if message != '':
            groupbox.layout().addWidget(qtw.QLabel(message), alignment=qtc.Qt.AlignmentFlag.AlignCenter)

        self.layout().addWidget(groupbox)
        self.layout().setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)

        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        filename = settings['subscale_file']
        if not os.path.exists(filename):
            username.setEnabled(False)
            password.setEnabled(False)
            login_button.setEnabled(False)
            groupbox.layout().addWidget(qtw.QLabel('Subscale file not found'), alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        else:
            with open(filename, 'r', encoding='utf-8') as file:
                items = file.readlines()
            if not items:
                username.setEnabled(True)
                password.setEnabled(True)
                login_button.setEnabled(True)
                groupbox.layout().addWidget(qtw.QLabel('Subscale file is empty'), alignment=qtc.Qt.AlignmentFlag.AlignCenter)
                
    def check_login(self, username, password):
        if DEBUG:
            print('Checking login')
        self.username = username
        # remove all widgets
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if username == 'admin' and password != '':
            self.admin_page(username)
        elif username != '' and password != '':
            self.user_page(username)
        else:
            self.login_page('Invalid username or password')

    def admin_page(self, username):
        self.clearLayout(self.layout())
        if DEBUG:
            print('Admin page')
        # add widgets
        self.dict = {}
        if os.path.exists('settings.json'):
            
            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            filename = settings['subscale_file']

            with open(filename, 'r', encoding='utf-8') as file:
                items = file.readlines()
            for i in range(len(items)):
                q = items[i].split(',')[0]
                n = q.split('_')[1]
                q = q.split('_')[0].replace('Q','')
                item = items[i][items[i].index(',')+1:].replace('"','').replace('\n','')
                if q not in self.dict:
                    self.dict[q] = {}
                self.dict[q][n] = item

            self.dict = {k: v for k, v in sorted(self.dict.items(), key=lambda item: int(item[0]))}
        else:
            self.dict = {}

        header = qtw.QLabel('Welcome,\n'+username)

        header.setAlignment(qtc.Qt.AlignmentFlag.AlignLeft)
        self.layout().addWidget(header)
        
        layout_admin = qtw.QHBoxLayout()
        self.layout().addLayout(layout_admin)

        logout_button = qtw.QPushButton('Logout', clicked = self.logout)
        layout_admin.addWidget(logout_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)

        tabs = qtw.QTabWidget()
        items_tab = qtw.QWidget()
        evaluations_tab = qtw.QWidget()
        tabs.addTab(items_tab, 'Items')
        tabs.addTab(evaluations_tab, 'Evaluations')
        items_tab.setLayout(qtw.QVBoxLayout())
        self.search_bar = qtw.QLineEdit()
        self.search_bar.setPlaceholderText('Search')
        self.search_bar.textChanged.connect(lambda text: self.search(text, items_layout))
        items_tab.layout().addWidget(self.search_bar, alignment=qtc.Qt.AlignmentFlag.AlignTop|qtc.Qt.AlignmentFlag.AlignRight)
        evaluations_tab.setLayout(qtw.QVBoxLayout())
        items_layout = qtw.QVBoxLayout()
        evaluations_layout = qtw.QVBoxLayout()

        self.scroll_area = qtw.QScrollArea() 
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = qtw.QWidget()
        self.scroll_widget.setLayout(items_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        items_tab.layout().addWidget(self.scroll_area)
        
        scroll_area_2 = qtw.QScrollArea()
        scroll_area_2.setWidgetResizable(True)
        scroll_widget_2 = qtw.QWidget()
        scroll_widget_2.setLayout(evaluations_layout)
        scroll_area_2.setWidget(scroll_widget_2)
        evaluations_tab.layout().addWidget(scroll_area_2)
        evaluation_files = os.listdir('data/evaluations')
        if not evaluation_files:
            message = qtw.QLabel('No evaluations')
            evaluations_layout.addWidget(message, alignment=qtc.Qt.AlignmentFlag.AlignCenter)

        for i in evaluation_files:
            if i.endswith('.jsonl'):
                
                with open('data/evaluations/'+i, 'r', encoding='utf-8') as file:
                    item = qtw.QGroupBox(i)
                    item.setLayout(qtw.QVBoxLayout())
                    evaluations_layout.addWidget(item, alignment=qtc.Qt.AlignmentFlag.AlignTop)


                    for line in file:
                        subitem = qtw.QGroupBox()
                        subitem.setStyleSheet('QGroupBox {border: 1px solid #ddd; border-radius: 5px;}')
                        subitem.setLayout(qtw.QVBoxLayout())
                        eval_data = eval(line)
                        
                        subitem.layout().addWidget(qtw.QLabel('Item 1: '+eval_data['item1']))
                        subitem.layout().addWidget(qtw.QLabel('Item 2: '+eval_data['item2']))
                        subitem.layout().addWidget(qtw.QLabel('Semantic similarity: '+eval_data['semantically']))
                        subitem.layout().addWidget(qtw.QLabel('Taxonomic similarity: '+eval_data['taxonomically']))
                        subitem.layout().addWidget(qtw.QLabel('Causal similarity: '+eval_data['causally']))
                        if 'T5' in eval_data:
                            subitem.layout().addWidget(qtw.QLabel('T5 similarity: '+str(eval_data['T5'])))
                        else:
                            T5_button = qtw.QPushButton('Run T5 evaluation')
                            T5_button.clicked.connect(lambda checked,item1=eval_data['item1'], item2=eval_data['item2'],item=subitem, button=T5_button, filename=i: self.run_T5({'item1': item1, 'item2': item2},item,button, filename))
                            subitem.layout().addWidget(T5_button)
                        item.layout().addWidget(subitem)
                        


        for subscale in self.dict:
            self.s = qtw.QGroupBox('Subscale '+subscale)
            self.s.setLayout(qtw.QVBoxLayout())
            items_layout.addWidget(self.s, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            for i in self.dict[subscale]:
                item_view = qtw.QHBoxLayout()
                item = qtw.QLineEdit()
                item.setText(self.dict[subscale][i])
                if item.text() == '':
                    item.setPlaceholderText('Item '+i)
                item.textChanged.connect(lambda text, subscale=subscale, i=i: self.dict[subscale].update({i: text}))

                item_view.addWidget(item)
                delete_button = qtw.QPushButton('Delete')
                item_view.addWidget(delete_button)
                self.s.layout().addLayout(item_view)
                delete_button.clicked.connect(lambda checked, subscale=subscale, i=i, groupbox=self.s, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))

            buttons_view = qtw.QHBoxLayout()
            add_item = qtw.QPushButton('Add item')
            add_item.clicked.connect(lambda checked, subscale=subscale, groupbox=self.s: self.add_item(subscale, groupbox))
            buttons_view.addWidget(add_item)
            delete_subscale = qtw.QPushButton('Delete subscale')
            buttons_view.addWidget(delete_subscale)
            delete_subscale.clicked.connect(lambda checked, subscale=subscale, groupbox=self.s: self.delete_subscale(subscale, groupbox))
            self.s.layout().addLayout(buttons_view)
        if not self.dict:
            self.s = qtw.QGroupBox('Subscale 1')
            self.s.setLayout(qtw.QVBoxLayout())
            items_layout.addWidget(self.s, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            item_view = qtw.QHBoxLayout()
            item = qtw.QLineEdit()
            self.dict['1'] = {}
            item.setPlaceholderText('Item 1')
            item.textChanged.connect(lambda text, subscale='1', i='1': self.dict[subscale].update({i: text}))
            item_view.addWidget(item)
            delete_button = qtw.QPushButton('Delete')
            item_view.addWidget(delete_button)
            self.s.layout().addLayout(item_view)
            delete_button.clicked.connect(lambda checked, subscale='1', i='1', groupbox=self.s, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))
            buttons_view = qtw.QHBoxLayout()
            add_item = qtw.QPushButton('Add item')
            add_item.clicked.connect(lambda checked, subscale='1', groupbox=self.s: self.add_item(subscale, groupbox))
            buttons_view.addWidget(add_item)
            delete_subscale = qtw.QPushButton('Delete subscale')
            buttons_view.addWidget(delete_subscale)
            delete_subscale.clicked.connect(lambda checked, subscale='1', groupbox=self.s: self.delete_subscale(subscale, groupbox))
            self.s.layout().addLayout(buttons_view)

        layout_admin.addWidget(tabs)
        add_subscale = qtw.QPushButton('Add subscale')
        add_subscale.clicked.connect(lambda: self.add_subscale(items_layout))
        save_button = qtw.QPushButton('Save')
        save_button.clicked.connect(self.save_subscales)
        save_button.setToolTip('Save the subscales')

        self.message_label = qtw.QLabel('Subscales saved', self)
        self.message_label.setStyleSheet("QLabel { background-color : gray; color : white; border-radius: 5px; }")
        self.message_label.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.message_label.setVisible(False)
        self.message_label.setFixedSize(150, 50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right

        buttons_view_2 = qtw.QHBoxLayout()
        buttons_view_2.addWidget(add_subscale)
        buttons_view_2.addWidget(save_button)
        items_tab.layout().addLayout(buttons_view_2)

        settings_button = qtw.QPushButton('Settings')
        settings_button.clicked.connect(lambda: self.admin_settings())
        layout_admin.addWidget(settings_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)

    

    def run_T5(self, eval_data, item, button, filename):

        self.message_label.setText('Running T5 evaluation for\n' + eval_data['item1'] + '\n' + eval_data['item2'])
        if len(eval_data['item1']) > 20 or len(eval_data['item2']) > 20:
            self.message_label.setFixedSize(max(len(eval_data['item1']), len(eval_data['item2'])) * 7, 50)
        else:
            self.message_label.setFixedSize(200, 50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)
        self.message_label.setVisible(True)
        qtc.QTimer.singleShot(5000, lambda: self.message_label.setVisible(False))

        if DEBUG:
            print('Running T5')
        button.setHidden(False)

        


        # Delay the execution of the T5 model evaluation
        qtc.QTimer.singleShot(100, lambda: self.perform_T5_eval(eval_data, item, button, filename))

    def perform_T5_eval(self, eval_data, item, button, filename):
        similarity = self.perform_T5(eval_data)
        item.layout().addWidget(qtw.QLabel('T5 similarity: ' + str(similarity)))

        
        with open('data/evaluations/'+filename, 'r', encoding='utf-8') as file:
            evaluations = file.readlines()
        for i in range(len(evaluations)):
            e = eval(evaluations[i])
            if eval_data['item1'] == e['item1'] and eval_data['item2'] == e['item2']:
                eval_data['semantically'] = e['semantically']
                eval_data['taxonomically'] = e['taxonomically']
                eval_data['causally'] = e['causally']
                eval_data['T5'] = similarity

                evaluations[i] = json.dumps(eval_data)+'\n'
        with open('data/evaluations/'+filename, 'w', encoding='utf-8') as file:
            file.writelines(evaluations)

        self.message_label.setText('T5 similarity done')
        self.message_label.setFixedSize(150, 50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)
        self.message_label.setVisible(True)
        qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))
        button.setHidden(True)
        

    def perform_T5(self, eval_data):
        from sentence_similarity import T5_model, util
        item1 = eval_data['item1']
        item2 = eval_data['item2']
        
        model = T5_model()
        
        embeddings = model.encode([item1, item2])
        return round(float(util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()), 2)



        









       

        













    


    def admin_settings(self):
        self.clearLayout(self.layout())
        settings_layout = qtw.QHBoxLayout()
        logout_button = qtw.QPushButton('Logout', clicked = self.logout)
        settings_layout.addWidget(logout_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)
        box = qtw.QVBoxLayout()

        back_button = qtw.QPushButton('Back', clicked = lambda: self.admin_page('admin'))
        back_button.setToolTip('Go back to the admin page')
        box.addWidget(back_button, alignment=qtc.Qt.AlignmentFlag.AlignLeft | qtc.Qt.AlignmentFlag.AlignTop)
        

        box.addWidget(qtw.QLabel('Subscale file'))
        self.file = qtw.QLineEdit()
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        self.file.setText(settings['subscale_file'])

        self.file.setEnabled(False)
        select_file = qtw.QPushButton('Select file')
        select_file.clicked.connect(lambda: self.file.setText(qtw.QFileDialog.getOpenFileName(self, 'Select file', '')[0]))
        select_file.clicked.connect(lambda: self.save_settings(self.file.text()))
        select_file.setToolTip('Select a file with the subscales')

        new_file = qtw.QPushButton('New file')
        new_file.clicked.connect(self.new_file)
        new_file.setToolTip('Create a new file')
        
        box.addWidget(self.file)
        buttons_layout = qtw.QHBoxLayout()
        buttons_layout.addWidget(new_file, alignment= qtc.Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(select_file, alignment= qtc.Qt.AlignmentFlag.AlignCenter)
        box.addLayout(buttons_layout)
        
        
        settings_layout.addLayout(box)


        settings_layout1 = qtw.QVBoxLayout()
        # choose between 'random choice' and 'sequential choice' with radio buttons
        choice_label = qtw.QLabel('Choice method')
        settings_layout1.addWidget(choice_label)
        self.choice_method = qtw.QGroupBox()
        self.choice_method.setLayout(qtw.QVBoxLayout())
        random_choice = qtw.QRadioButton('Random choice')
        sequential_choice = qtw.QRadioButton('Sequential choice')
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        choice_method = settings['choice_method']
        if choice_method == 'random':
            random_choice.setChecked(True)
            sequential_choice.setChecked(False)
        elif choice_method == 'sequential':
            sequential_choice.setChecked(True)
            random_choice.setChecked(False)
        self.choice_method.layout().addWidget(random_choice)
        self.choice_method.layout().addWidget(sequential_choice)
        settings_layout1.addWidget(self.choice_method)
        save_button = qtw.QPushButton('Save', clicked = lambda: self.save_choice_method(random_choice, sequential_choice))
        # tip message when cursor is over the save button
        save_button.setToolTip('Save the choice method')

        self.message_label = qtw.QLabel('Choice method saved', self)
        self.message_label.setStyleSheet("QLabel { background-color : gray; color : white; border-radius: 5px; }")
        self.message_label.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.message_label.setVisible(False)
        self.message_label.setFixedSize(150, 50)

        settings_layout1.addWidget(save_button, alignment=qtc.Qt.AlignmentFlag.AlignCenter)

        box.addLayout(settings_layout1)

        self.layout().addLayout(settings_layout)

    def save_choice_method(self, random_choice, sequential_choice):
        if random_choice.isChecked():
            choice_method = 'random'
        elif sequential_choice.isChecked():
            choice_method = 'sequential'
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        settings['choice_method'] = choice_method
        with open('settings.json', 'w', encoding='utf-8') as file:
            json.dump(settings, file)
        self.message_label.setFixedSize(150,50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
        self.message_label.setText('Choice method saved')
        self.message_label.setVisible(True)
        qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))
        
    def new_file(self):

        self.dict = {}
        with open('data/external/subscale_file.csv', 'w', encoding='utf-8') as file:
            file.write('')
        with open('settings.json', 'w', encoding='utf-8') as file:
            file.write('{"subscale_file": "data/external/subscale_file.csv", "choice_method": "random"}')
        self.message_label.setFixedSize(150,50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
        self.message_label.setText('New file created')
        self.message_label.setVisible(True)
        qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))

        self.admin_page('admin')
        
    def save_settings(self, filename):
        if DEBUG:
            print('Saving settings')
        if self.check_file(filename) and filename.endswith('.csv'):
            result = self.check_file(filename)
            cwd = os.getcwd()
            if cwd in filename:
                filename = filename.replace(os.getcwd()+'/', '')
            else:
                cwd = cwd.split('\\')[-1]
                filename = filename[filename.index(cwd)+len(cwd)+1:]
            self.file.setText(filename)
            with open('settings.json', 'w', encoding='utf-8') as file:
                json.dump({'subscale_file': filename, 'choice_method': 'random'}, file)
            # go back to the admin page
            self.admin_page('admin')

            self.message_label.setText('File: '+filename+'\nLoaded')
            # adjust the size of the message label
            if len(filename) > 20:
                self.message_label.setFixedSize(len(filename)*10, 50)
            else:
                self.message_label.setFixedSize(200, 50)
            self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
            
            self.message_label.setVisible(True)
            qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))
            
        else:
            self.file.setText('Invalid file')
            self.message_label.setFixedSize(150,50)
            self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
            self.message_label.setText('Invalid file')
            self.message_label.setVisible(True)
            qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))

    def check_file(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                items = file.readlines()
            d = {}
            for i in range(len(items)):
                try:
                    q=items[i].split(',')[0]
                    item = items[i][items[i].index(',')+1:].replace('"','').replace('\n','')
                    q=q[1:]
                    subscale = q.split('_')[0]
                    number = q.split('_')[1]
                    if subscale.isdigit() and number.isdigit():
                        if subscale not in d:
                            d[subscale] = {}
                        d[subscale][number] = item
                    return True
                except:
                    return False
        else:
            return False

    def search(self, text, layout):
        for i in reversed(range(layout.count())):
            widget_to_remove = layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        for subscale in self.dict:
            if self.dict[subscale]:
                if text.lower() in self.dict[subscale][list(self.dict[subscale].keys())[0]].lower():
                    groupbox = qtw.QGroupBox('Subscale '+subscale)
                    groupbox.setLayout(qtw.QVBoxLayout())
                    layout.addWidget(groupbox, alignment=qtc.Qt.AlignmentFlag.AlignTop)
                    for i in self.dict[subscale]:
                        if text.lower() in self.dict[subscale][i].lower():
                            item_view = qtw.QHBoxLayout()
                            item = qtw.QLineEdit()
                            item.setText(self.dict[subscale][i])
                            item.textChanged.connect(lambda text, subscale=subscale, i=i: self.dict[subscale].update({i: text}))
                            item_view.addWidget(item)
                            delete_button = qtw.QPushButton('Delete')
                            item_view.addWidget(delete_button)
                            groupbox.layout().addLayout(item_view)
                            delete_button.clicked.connect(lambda checked, subscale=subscale, i=i, groupbox=groupbox, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))
                    buttons_view = qtw.QHBoxLayout()
                    add_item = qtw.QPushButton('Add item')
                    add_item.clicked.connect(lambda checked, subscale=subscale, groupbox=groupbox: self.add_item(subscale, groupbox))
                    buttons_view.addWidget(add_item)
                    delete_subscale = qtw.QPushButton('Delete subscale')
                    buttons_view.addWidget(delete_subscale)
                    delete_subscale.clicked.connect(lambda checked, subscale=subscale, groupbox=groupbox: self.delete_subscale(subscale, groupbox))
                    groupbox.layout().addLayout(buttons_view)
        
    def delete_item(self, subscale, item_key, groupbox, item_view):
        if subscale in self.dict and item_key in self.dict[subscale]:
            del self.dict[subscale][item_key]
            if not self.dict[subscale]:  
                self.delete_subscale(subscale, groupbox)
        for i in reversed(range(item_view.count())): 
            widget_to_remove = item_view.itemAt(i).widget()
            if widget_to_remove is not None: 
                widget_to_remove.setParent(None)
        groupbox.layout().removeItem(item_view)
        item_view.deleteLater()

    def add_item(self, subscale, groupbox):
        if subscale not in self.dict:
            self.dict[subscale] = {}
        n = str(len(self.dict[subscale])+1)
        self.dict[subscale][n] = ''
        item_view = qtw.QHBoxLayout()
        item = qtw.QLineEdit()
        item.setPlaceholderText('Item '+n)
        item.textChanged.connect(lambda text, subscale=subscale, i=n: self.dict[subscale].update({i: text}))
        item_view.addWidget(item)
        delete_button = qtw.QPushButton('Delete')
        item_view.addWidget(delete_button)
        groupbox.layout().insertLayout(groupbox.layout().count()-1, item_view)
        delete_button.clicked.connect(lambda checked, subscale=subscale, i=n, groupbox=groupbox, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))

    def delete_subscale(self, subscale, groupbox):
        if subscale in self.dict:
            del self.dict[subscale]
        for i in reversed(range(groupbox.layout().count())):
            widget_to_remove = groupbox.layout().itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        groupbox.deleteLater()
        if not self.dict:
            message = qtw.QLabel('No subscales')
            self.scroll_widget.layout().addWidget(message, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        self.scroll_widget.adjustSize()

    def add_subscale(self, layout):
        if DEBUG:
            print('Adding subscale')
        if not self.dict:
            if 'No subscales' in [layout.itemAt(i).widget().text() for i in range(layout.count())]:
                layout.itemAt(0).widget().deleteLater()
            self.dict['1'] = {}
            groupbox = qtw.QGroupBox('Subscale '+str(len(self.dict)))
            groupbox.setLayout(qtw.QVBoxLayout())
            layout.addWidget(groupbox, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            item_view = qtw.QHBoxLayout()
            item = qtw.QLineEdit()

            item.setPlaceholderText('Item '+str(len(self.dict['1'])+1))
            item.textChanged.connect(lambda text, subscale='1', i='1': self.dict[subscale].update({i: text}))
            item_view.addWidget(item)
            delete_button = qtw.QPushButton('Delete')
            item_view.addWidget(delete_button)
            groupbox.layout().addLayout(item_view)
            delete_button.clicked.connect(lambda checked, subscale='1', i='1', groupbox=groupbox, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))
            buttons_view = qtw.QHBoxLayout()
            add_item = qtw.QPushButton('Add item')
            add_item.clicked.connect(lambda checked, subscale='1', groupbox=groupbox: self.add_item(subscale, groupbox))
            buttons_view.addWidget(add_item)
            delete_subscale = qtw.QPushButton('Delete subscale')
            buttons_view.addWidget(delete_subscale)
            delete_subscale.clicked.connect(lambda checked, subscale='1', groupbox=groupbox: self.delete_subscale(subscale, groupbox))
            groupbox.layout().addLayout(buttons_view)
            self.scroll_widget.adjustSize()
            self.dict['1']['1'] = ''
        else:
            last_subscale = list(self.dict.keys())[-1]
            n = str(int(last_subscale)+1)
            self.dict[n] = {}
            groupbox = qtw.QGroupBox('Subscale '+n)
            groupbox.setLayout(qtw.QVBoxLayout())
            layout.addWidget(groupbox, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            item_view = qtw.QHBoxLayout()
            item = qtw.QLineEdit()

            item.setPlaceholderText('Item 1')
            item.textChanged.connect(lambda text, subscale=n, i='1': self.dict[subscale].update({i: text}))

            item_view.addWidget(item)
            delete_button = qtw.QPushButton('Delete')
            item_view.addWidget(delete_button)
            groupbox.layout().addLayout(item_view)
            delete_button.clicked.connect(lambda checked, subscale=n, i='1', groupbox=groupbox, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))
            buttons_view = qtw.QHBoxLayout()
            add_item = qtw.QPushButton('Add item')
            add_item.clicked.connect(lambda checked, subscale=n, groupbox=groupbox: self.add_item(subscale, groupbox))
            buttons_view.addWidget(add_item)
            delete_subscale = qtw.QPushButton('Delete subscale')
            buttons_view.addWidget(delete_subscale)
            delete_subscale.clicked.connect(lambda checked, subscale=n, groupbox=groupbox: self.delete_subscale(subscale, groupbox))
            groupbox.layout().addLayout(buttons_view)
            self.scroll_widget.adjustSize()
            self.dict[n]['1'] = ''
        
        QTimer.singleShot(100, lambda: self.scroll_area.ensureVisible(0, self.scroll_area.widget().sizeHint().height()))

    def save_subscales(self):
        if DEBUG:
            print('Saving')
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            filename = settings['subscale_file']
            with open(filename, 'w', encoding='utf-8') as file:
                for i in self.dict:
                    for j in self.dict[i]:
                        file.write('Q'+i+'_'+j+','+self.dict[i][j]+'\n')
            self.message_label.setFixedSize(150,50)
            self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
            self.message_label.setText('Subscales saved')
            self.message_label.setVisible(True)
            qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))
        else:
            if DEBUG:
                print('No settings file')
            self.message_label.setFixedSize(150,50)
            self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
            self.message_label.setText('Error\nNo settings file')
            self.message_label.setVisible(True)
            qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))

    def logout(self):
        if DEBUG:
            print('Logging out')
        self.dict = {}
        self.evaluations = {}
        self.choices = {}
        self.current_index = 0

        # Properly remove all widgets from the layout
        while self.layout().count():
            item = self.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())
        # Call the login page function to return to the login screen
        self.login_page()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    self.clearLayout(item.layout())

    def user_page(self, username):
        if DEBUG:
            print('User page')
        self.clearLayout(self.layout())
        self.username = username

        with open('settings.json', 'r', encoding='utf-8') as file:
            self.settings = json.load(file)
            choice_method = self.settings['choice_method']
    
        self.evaluations = self.load_evaluations()
        self.choices= self.load_data()

        if choice_method == 'sequential':
            group_keys = list(self.choices.keys())

            # Number of groups
            n = len(group_keys)

            # Initial pairs: sum of the number of items in each group
            initial_pairs = sum(len(self.choices[key]) for key in group_keys)
            self.pairs = 0
            for i in range(initial_pairs):
                self.pairs += i

        elif choice_method == 'random':

            self.pairs = len(self.choices)

        if self.choices == {}:
            os.remove('data/temp/'+self.username+'_choices.csv')
            self.choices = self.load_data()
        
        self.current_index = 0

        header = qtw.QLabel('Welcome,\n'+username)
        header.setAlignment(qtc.Qt.AlignmentFlag.AlignLeft)
        self.layout().addWidget(header)

        self.label1 = qtw.QLabel()
        self.label2 = qtw.QLabel()
        self.label1.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.label2.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)

        self.label1.setWordWrap(True)
        self.label2.setWordWrap(True)

        self.label1.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)
        self.label2.setSizePolicy(qtw.QSizePolicy.Policy.Expanding, qtw.QSizePolicy.Policy.Expanding)

        self.btn_next = qtw.QPushButton('-->\nNext', clicked = self.next_choice)
        self.btn_back = qtw.QPushButton('<--\nBack', clicked = self.previous_choice)

        self.update_labels()
                
        self.layout_buttons = qtw.QVBoxLayout()

        logout_button = qtw.QPushButton('Logout', clicked = self.logout)
        self.layout_buttons.addWidget(logout_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)
        save_button = qtw.QPushButton('Save and exit', clicked = self.save)
        self.layout_buttons.layout().addWidget(save_button)

        self.principal_layout = qtw.QHBoxLayout()
        self.principal_layout.addLayout(self.layout_buttons)
        
        # add tabs 'Evaluate', 'Your evaluations'
        self.tabs = qtw.QTabWidget()
        evaluate_tab = qtw.QWidget()
        self.your_evaluations_tab = qtw.QWidget()
        self.tabs.addTab(evaluate_tab, 'Evaluate')
        self.tabs.addTab(self.your_evaluations_tab, 'Your evaluations')

        # add widgets to evaluate tab
        evaluate_tab.setLayout(qtw.QVBoxLayout())

        self.ev = qtw.QVBoxLayout()

        item1 = qtw.QGroupBox('Item 1')
        item1.setLayout(qtw.QVBoxLayout())
        self.ev.layout().addWidget(item1)

        item1.layout().addWidget(self.label1)

        item2 = qtw.QGroupBox('Item 2')
        item2.setLayout(qtw.QVBoxLayout())
        self.ev.layout().addWidget(item2)

        #add spacing between the two items
        self.ev.addSpacing(50)

        item2.layout().addWidget(self.label2)

        # add a box with slider for 'somiglianza semantica'
        self.ev_1 = qtw.QGroupBox('Somiglianza semantica')
        self.ev_1.setLayout(qtw.QVBoxLayout())
        self.ev.layout().addWidget(self.ev_1)

        self.slider = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.update)

        self.ev_1.layout().addWidget(self.slider)

        self.check_box = qtw.QCheckBox("Can't annotate")
        self.check_box.stateChanged.connect(self.update)
        self.ev_1.layout().addWidget(self.check_box, alignment=qtc.Qt.AlignmentFlag.AlignRight)

        # add a label for the slider
        self.slider_label = qtw.QLabel('Semantic similarity: '+str(self.slider.value()/100))
        self.slider_label.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.ev_1.layout().addWidget(self.slider_label)

        # connect slider to label
        self.slider.valueChanged.connect(lambda: self.slider_label.setText('Semantic similarity: '+str(self.slider.value()/100)))

        # if the checkbox is checked, disable the slider and disable label
        self.check_box.stateChanged.connect(lambda: self.slider.setEnabled(not self.check_box.isChecked()))
        self.check_box.stateChanged.connect(lambda: self.slider_label.setEnabled(not self.check_box.isChecked()))

        self.ev_2 = qtw.QGroupBox('Somiglianza tassonomica')
        self.ev_2.setLayout(qtw.QVBoxLayout())
        self.ev.layout().addWidget(self.ev_2)

        self.slider_2 = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        self.slider_2.setRange(0, 100)
        self.slider_2.setValue(50)
        self.slider_2.valueChanged.connect(self.update)
        self.ev_2.layout().addWidget(self.slider_2)

        self.check_box_2 = qtw.QCheckBox("Can't annotate")
        self.check_box_2.stateChanged.connect(self.update)
        self.ev_2.layout().addWidget(self.check_box_2, alignment=qtc.Qt.AlignmentFlag.AlignRight)

        # add a label for the slider
        self.slider_label_2 = qtw.QLabel('Taxonomic similarity: '+str(self.slider_2.value()/100))
        self.slider_label_2.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)

        self.ev_2.layout().addWidget(self.slider_label_2)

        # connect slider to label
        self.slider_2.valueChanged.connect(lambda: self.slider_label_2.setText('Taxonomic similarity: '+str(self.slider_2.value()/100)))

        # if the checkbox is checked, disable the slider and disable label
        self.check_box_2.stateChanged.connect(lambda: self.slider_2.setEnabled(not self.check_box_2.isChecked()))
        self.check_box_2.stateChanged.connect(lambda: self.slider_label_2.setEnabled(not self.check_box_2.isChecked()))

        self.ev_3 = qtw.QGroupBox('Somiglianza causale')
        self.ev_3.setLayout(qtw.QVBoxLayout())
        self.ev.layout().addWidget(self.ev_3)

        self.slider_3 = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        self.slider_3.setRange(0, 100)
        self.slider_3.setValue(50)
        self.slider_3.valueChanged.connect(self.update)
        self.ev_3.layout().addWidget(self.slider_3)

        self.check_box_3 = qtw.QCheckBox("Can't annotate")
        self.check_box_3.stateChanged.connect(self.update)
        self.ev_3.layout().addWidget(self.check_box_3, alignment=qtc.Qt.AlignmentFlag.AlignRight)

        # add a label for the slider
        self.slider_label_3 = qtw.QLabel('Causal similarity: '+str(self.slider_3.value()/100))
        self.slider_label_3.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.ev_3.layout().addWidget(self.slider_label_3)

        # connect slider to label
        self.slider_3.valueChanged.connect(lambda: self.slider_label_3.setText('Causal similarity: '+str(self.slider_3.value()/100)))
        
        # if the checkbox is checked, disable the slider and disable label
        self.check_box_3.stateChanged.connect(lambda: self.slider_3.setEnabled(not self.check_box_3.isChecked()))
        self.check_box_3.stateChanged.connect(lambda: self.slider_label_3.setEnabled(not self.check_box_3.isChecked()))
        self.update_values()
        # add buttons to layout

        self.button_layout = qtw.QHBoxLayout()
        
        #add progress bar
        self.progress = qtw.QProgressBar()
        self.progress.setValue(0)
        self.progress.setMaximum(100)
        self.progress.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        #self.ev.addSpacing(50)
        self.ev.addWidget(self.progress)

        self.button_layout.addWidget(self.btn_back)
        self.button_layout.addLayout(self.ev)
        self.button_layout.addWidget(self.btn_next)

        evaluate_tab.layout().addLayout(self.button_layout)
    
        # add tabs to layout
        self.principal_layout.addWidget(self.tabs)

        settings_button = qtw.QPushButton('Settings')
        self.principal_layout.addWidget(settings_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)

        self.layout().addLayout(self.principal_layout)

        # add widgets to your evaluations tab
        self.your_evaluations_tab.setLayout(qtw.QVBoxLayout())
        self.evaluations_layout = qtw.QVBoxLayout()
        scroll_area = qtw.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = qtw.QWidget()
        scroll_widget.setLayout(self.evaluations_layout)
        scroll_area.setWidget(scroll_widget)
        self.your_evaluations_tab.layout().addWidget(scroll_area)
        
        self.tabs.setCurrentIndex(0)
        self.tabs.currentChanged.connect(self.update_your_evaluations)

    def update(self):
        
        semantically = self.slider.value()/100
        taxonomically = self.slider_2.value()/100
        causally = self.slider_3.value()/100
        if self.check_box.isChecked():
            semantically = 'No annotation'
        if self.check_box_2.isChecked():
            taxonomically = 'No annotation'
        if self.check_box_3.isChecked():
            causally = 'No annotation'

        self.evaluations[self.current_index] = {'item1': self.label1.text(), 'item2': self.label2.text(), 'semantically': str(semantically), 'taxonomically': str(taxonomically), 'causally': str(causally)}

    def update_values(self):
        if self.current_index in self.evaluations:
            eval_data = self.evaluations[self.current_index]
            semantically = eval_data['semantically']
            taxonomically = eval_data['taxonomically']
            causally = eval_data['causally']

            if semantically != 'No annotation':
                self.slider.setValue(int(float(semantically) * 100))
                self.check_box.setChecked(False)
            else:
                self.slider.setValue(50)
                self.check_box.setChecked(True)

            if taxonomically != 'No annotation':
                self.slider_2.setValue(int(float(taxonomically) * 100))
                self.check_box_2.setChecked(False)
            else:
                self.slider_2.setValue(50)
                self.check_box_2.setChecked(True)

            if causally != 'No annotation':
                self.slider_3.setValue(int(float(causally) * 100))
                self.check_box_3.setChecked(False)
            else:
                self.slider_3.setValue(50)
                self.check_box_3.setChecked(True)
        else:
            # Set the default values without writing them to the evaluations dictionary
            self.slider.disconnect()
            self.slider.setValue(50)
            self.slider.valueChanged.connect(self.update)
            self.slider.valueChanged.connect(lambda: self.slider_label.setText('Semantic similarity: '+str(self.slider.value()/100)))

            self.check_box.disconnect() 
            self.check_box.setChecked(False)
            self.check_box.stateChanged.connect(self.update)
            self.slider.setEnabled(True)
            self.slider_label.setEnabled(True)
            self.check_box.stateChanged.connect(lambda: self.slider.setEnabled(not self.check_box.isChecked()))
            self.check_box.stateChanged.connect(lambda: self.slider_label.setEnabled(not self.check_box.isChecked()))

            self.slider_2.disconnect()
            self.slider_2.setValue(50)
            self.slider_2.valueChanged.connect(self.update)
            self.slider_2.valueChanged.connect(lambda: self.slider_label_2.setText('Taxonomic similarity: '+str(self.slider_2.value()/100)))

            self.check_box_2.disconnect()
            self.check_box_2.setChecked(False)
            self.slider_2.setEnabled(True)
            self.slider_label_2.setEnabled(True)
            self.check_box_2.stateChanged.connect(self.update)
            self.check_box_2.stateChanged.connect(lambda: self.slider_2.setEnabled(not self.check_box_2.isChecked()))
            self.check_box_2.stateChanged.connect(lambda: self.slider_label_2.setEnabled(not self.check_box_2.isChecked()))

            self.slider_3.disconnect()
            self.slider_3.setValue(50)
            self.slider_3.valueChanged.connect(self.update)
            self.slider_3.valueChanged.connect(lambda: self.slider_label_3.setText('Causal similarity: '+str(self.slider_3.value()/100)))
            
            self.check_box_3.disconnect()
            self.check_box_3.setChecked(False)
            self.slider_3.setEnabled(True)
            self.slider_label_3.setEnabled(True)
            self.check_box_3.stateChanged.connect(self.update)
            self.check_box_3.stateChanged.connect(lambda: self.slider_3.setEnabled(not self.check_box_3.isChecked()))
            self.check_box_3.stateChanged.connect(lambda: self.slider_label_3.setEnabled(not self.check_box_3.isChecked()))

    def update_your_evaluations(self):
        self.clearLayout(self.evaluations_layout)
        if self.tabs.currentIndex() == 1:
            if self.evaluations:
                for i in self.evaluations:
                    item = qtw.QGroupBox('Item '+str(i+1))
                    item.setLayout(qtw.QVBoxLayout())

                    item.layout().addWidget(qtw.QLabel('Item 1: '+self.evaluations[i]['item1']))
                    item.layout().addWidget(qtw.QLabel('Item 2: '+self.evaluations[i]['item2']))
                    item.layout().addWidget(qtw.QLabel('Semantic similarity: '+self.evaluations[i]['semantically']))
                    item.layout().addWidget(qtw.QLabel('Taxonomic similarity: '+self.evaluations[i]['taxonomically']))
                    item.layout().addWidget(qtw.QLabel('Causal similarity: '+self.evaluations[i]['causally']))
                    edit_button = qtw.QPushButton('Edit', clicked = lambda checked, i=i: self.edit_evaluation(i))
                    item.layout().addWidget(edit_button, alignment=qtc.Qt.AlignmentFlag.AlignRight | qtc.Qt.AlignmentFlag.AlignBottom)
                    self.evaluations_layout.addWidget(item, alignment=qtc.Qt.AlignmentFlag.AlignTop)
                submit_button = qtw.QPushButton('Submit')
                submit_button.clicked.connect(self.submit)
                self.evaluations_layout.addWidget(submit_button, alignment=qtc.Qt.AlignmentFlag.AlignCenter | qtc.Qt.AlignmentFlag.AlignBottom)
            else:
                self.evaluations_layout.addWidget(qtw.QLabel('No evaluations yet'), alignment=qtc.Qt.AlignmentFlag.AlignCenter)

    def edit_evaluation(self, index):
        self.current_index = index
        self.tabs.setCurrentIndex(0)
        self.update_labels()
        semantically = self.evaluations[self.current_index]['semantically']
        taxonomically = self.evaluations[self.current_index]['taxonomically']
        causally = self.evaluations[self.current_index]['causally']
        if semantically != 'No annotation':
            self.slider.setValue(int(float(semantically)*100))
            self.check_box.setChecked(False)
        else:
            self.slider.setValue(50)
            self.check_box.setChecked(True)
        if taxonomically != 'No annotation':
            self.slider_2.setValue(int(float(taxonomically)*100))
            self.check_box_2.setChecked(False)
        else:
            self.slider_2.setValue(50)
            self.check_box_2.setChecked(True)
        if causally != 'No annotation':
            self.slider_3.setValue(int(float(causally)*100))
            self.check_box_3.setChecked(False)
        else:
            self.slider_3.setValue(50)
            self.check_box_3.setChecked(True)
        self.progress.setValue(int(self.current_index/len(self.choices)*100))

    def submit(self):
        if os.path.exists('data/temp/'+self.username+'_choices.csv'):
            os.remove('data/temp/'+self.username+'_choices.csv')
        if os.path.exists('data/temp/'+self.username+'_evaluations.jsonl'):
            os.remove('data/temp/'+self.username+'_evaluations.jsonl')
        time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

        if not os.path.exists('data/evaluations'):
            os.mkdir('data/evaluations')
        self.save('data/evaluations/'+self.username+'_'+time+'.jsonl',True)

        
    def save(self, filename, closeFile = False):
        if filename == False:
            filename = 'data/temp/'+self.username+'_evaluations.jsonl'
        if DEBUG:
            print('Saving',filename)
        # save evaluations to file
        self.evaluations = {k: v for k, v in sorted(self.evaluations.items(), key=lambda item: int(item[0]))}
        with open(filename, 'w', encoding='utf-8') as file:
            for i in self.evaluations:
                if not closeFile:
                    self.evaluations[i]['index'] = i    
                file.write(str(self.evaluations[i])+'\n')
        self.evaluations = {}
        self.current_index = 0
        self.update_labels()
        self.progress.setValue(0)
        self.tabs.setCurrentIndex(0)
        exit()
        
    def load_data(self):
        choice_method = self.settings['choice_method']
        if choice_method == 'random':
            return self.load_random_choices()
        elif choice_method == 'sequential':
            return self.load_sequential_choices()
        else:
            return {}
        
    def load_random_choices(self):
        import itertools 
        if os.path.exists('data/temp/'+self.username+'_choices.csv'):
            if DEBUG:
                print('Loading random choices')
            with open('data/temp/'+self.username+'_choices.csv', 'r', encoding='utf-8') as file:
                items = file.readlines()
            choices = {}
            for i in range(0, len(items), 2):
                q = items[i].split(',')[0]
                item1 = items[i][items[i].index(',')+1:].replace('\n','')
                item2 = items[i+1][items[i+1].index(',')+1:].replace('\n','')
                choices[q] = [item1, item2]
            return choices
        else:
            if DEBUG:
                print('Creating random choices')
            if os.path.exists('settings.json'):
                filename = self.settings['subscale_file']
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as file:
                        items = file.readlines()
                    d = {}
                    for i in range(len(items)):
                        q=items[i].split(',')[0]
                        item = items[i][items[i].index(',')+1:].replace('"','').replace('\n','')
                        q=q[1:]
                        subscale = q.split('_')[0]
                        number = q.split('_')[1]

                        if subscale not in d:
                            d[subscale] = {}
                        d[subscale][number] = item
                    choices = {}
                    d= {k: v for k, v in sorted(d.items(), key=lambda item: int(item[0]))}

                    for i in d:
                        if i not in choices:
                            choices[i] = []
                            choices[i].append(random.choice(list(d[i].values())))
                            d[i].pop(list(d[i].keys())[list(d[i].values()).index(choices[i][0])])
                            choices[i].append(random.choice(list(d[i].values())))
                            d[i].pop(list(d[i].keys())[list(d[i].values()).index(choices[i][1])])
                    with open('data/temp/'+self.username+'_choices.csv', 'w', encoding='utf-8') as file:
                        for i in choices:
                            file.write(i+'A,'+choices[i][0]+'\n')
                            file.write(i+'B,'+choices[i][1]+'\n')
                    return choices
                else:
                    return {}
            else:
                return {}
            
    def load_sequential_choices(self):
        if DEBUG:
            print('Loading sequential choices')
        self.choices = {}
        filename = self.settings['subscale_file']
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                items = file.readlines()
            d = {}
            for i in range(len(items)):
                q=items[i].split(',')[0]

                if '"' in items[i][items[i].index(',')+1:]:
                    item = items[i][items[i].index(',')+1:].replace('"','')
                    item = item.replace('\n','')
                else:
                    item = items[i][items[i].index(',')+1:].replace('\n','')
                q=q[1:]
                subscale = q.split('_')[0]
                number = q.split('_')[1]
                if subscale not in d:
                    d[subscale] = {}
                d[subscale][number] = item
            d= {k: v for k, v in sorted(d.items(), key=lambda item: int(item[0]))}
            for i in d:
                if i not in self.choices:
                    self.choices[i] = []
                    for j in d[i]:
                        self.choices[i].append(d[i][j])
            return self.choices
        else:
            return {}
        
    def load_evaluations(self):
        if os.path.exists('data/temp/'+self.username+'_evaluations.jsonl'):
            if DEBUG:
                print('Loading evaluations')
            with open('data/temp/'+self.username+'_evaluations.jsonl', 'r', encoding='utf-8') as file:     
                evaluations = {}
                for line in file:
                    eval_data = eval(line)
                    index = eval_data['index']
                    del eval_data['index']
                    evaluations[index] = eval_data
            return evaluations
        else:
            return {}
        
    def update_labels(self):
        if self.current_index == 0:
            self.btn_back.setDisabled(True)
            self.btn_next.setDisabled(False)
            self.btn_next.setHidden(False)
            if hasattr(self, 'btn_summary'):
                self.btn_summary.setHidden(True)

        elif self.current_index == self.pairs - 1:
            self.btn_back.setDisabled(False)
            self.btn_next.setHidden(True)
            self.btn_summary = qtw.QPushButton('Summary')
            self.btn_summary.setFixedSize(self.btn_next.sizeHint())

            font = self.btn_summary.font()
            font.setPointSize(10)
            self.btn_summary.setFont(font)

            self.btn_summary.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
            self.button_layout.addWidget(self.btn_summary, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        else:
            self.btn_back.setDisabled(False)
            self.btn_next.setDisabled(False)
            self.btn_next.setHidden(False)
            if hasattr(self, 'btn_summary'):
                self.btn_summary.setHidden(True)
        choice_method = self.settings['choice_method']
        if choice_method == 'random':
            if self.current_index < len(self.choices):
                subscale = list(self.choices.keys())[self.current_index]
                self.label1.setText(self.choices[subscale][0])
                self.label2.setText(self.choices[subscale][1])
        elif choice_method == 'sequential':
            all_items = []
            for subscale in self.choices.values():
                all_items.extend(subscale)
            comparisons = []
            for i in range(len(all_items)):
                for j in range(i+1, len(all_items)):
                    comparisons.append((all_items[i], all_items[j]))
            if self.current_index < len(comparisons):
                item1, item2 = comparisons[self.current_index]
                self.label1.setText(item1)
                self.label2.setText(item2)

    def next_choice(self):
            if self.current_index < self.pairs - 1:
                self.current_index += 1
                self.update_labels()
            self.progress.setValue(int(self.current_index/self.pairs *100))
            self.update_values()

    def previous_choice(self):        
            if self.current_index > 0:
                self.current_index -= 1
                self.update_labels()
            self.progress.setValue(int(self.current_index/self.pairs *100))
            self.update_values()

app = qtw.QApplication([])
mw = MainWindow()
sys.exit(app.exec())


'''
causale
logica'''