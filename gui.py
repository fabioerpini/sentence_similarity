import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as qtg
import PyQt6.QtCore as qtc
from PyQt6.QtCore import QTimer
import random
import os 
import json
from datetime import datetime
import sys
from numpy import mean
from sentence_similarity import T5_model, util
from sklearn.metrics import mean_absolute_error
from itertools import combinations

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
        self.slider = qtw.QSlider()
        self.check_box = qtw.QCheckBox()
        self.slider_label = qtw.QLabel()
        self.slider_2 = qtw.QSlider()
        self.check_box_2 = qtw.QCheckBox()
        self.slider_label_2 = qtw.QLabel()
        self.slider_3 = qtw.QSlider()
        self.check_box_3 = qtw.QCheckBox()
        self.slider_label_3 = qtw.QLabel()
        self.message_label = qtw.QLabel()

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
        self.message_label = qtw.QLabel()

        if DEBUG:
            print('Admin page')
        # add widgets
        self.dict = {}
        if os.path.exists('settings.json'):
            
            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            filename = settings['subscale_file']
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    items = file.readlines()
                for i in range(len(items)):
                    q = items[i].split(',')[0]
                    n = q.split('_')[1]
                    q = q.split('_')[0].replace('Q','')
                    item = items[i][items[i].index(',')+1:].replace('"','')
                    item = item.replace('\n','')
                    if q not in self.dict:
                        self.dict[q] = {}
                    self.dict[q][n] = item

                self.dict = {k: v for k, v in sorted(self.dict.items(), key=lambda item: int(item[0]))}
            except:
                pass
        else:
            self.dict = {}
        if settings['choice_method'] == 'random_in_subscale':
            if os.path.exists('data/temp/random_in_subscale_'+settings['selected_subscale']+'_choices.csv'):
                pass
            else:
                self.create_choices()
        else:
            if os.path.exists('data/temp/random_choices.csv'):
                pass
            else:
                self.create_choices()
            if os.path.exists('data/temp/sequential_choices.csv'):
                pass
            else:
                self.create_choices()

        header = qtw.QLabel('Welcome,\n'+username)

        header.setAlignment(qtc.Qt.AlignmentFlag.AlignLeft)
        self.layout().addWidget(header)
        
        layout_admin = qtw.QHBoxLayout()
        self.layout().addLayout(layout_admin)

        logout_button = qtw.QPushButton('Logout', clicked = self.logout)
        layout_admin.addWidget(logout_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)

        tabs = qtw.QTabWidget()
        items_tab = qtw.QWidget()
        self.evaluations_tab = qtw.QWidget()
        tabs.addTab(items_tab, 'Items')
        tabs.addTab(self.evaluations_tab, 'Evaluations')
        items_tab.setLayout(qtw.QVBoxLayout())
        self.search_bar = qtw.QLineEdit()
        self.search_bar.setPlaceholderText('Search')
        self.search_bar.textChanged.connect(lambda text: self.search(text, items_layout))
        items_tab.layout().addWidget(self.search_bar, alignment=qtc.Qt.AlignmentFlag.AlignTop|qtc.Qt.AlignmentFlag.AlignRight)
        self.evaluations_tab.setLayout(qtw.QVBoxLayout())
        items_layout = qtw.QVBoxLayout()
        self.evaluations_layout = qtw.QVBoxLayout()

        self.scroll_area = qtw.QScrollArea() 
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = qtw.QWidget()
        self.scroll_widget.setLayout(items_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        items_tab.layout().addWidget(self.scroll_area)
        
        scroll_area_2 = qtw.QScrollArea()
        scroll_area_2.setWidgetResizable(True)
        scroll_widget_2 = qtw.QWidget()
        scroll_widget_2.setLayout(self.evaluations_layout)
        scroll_area_2.setWidget(scroll_widget_2)
        self.evaluations_tab.layout().addWidget(scroll_area_2)
        evaluation_files = os.listdir('data/evaluations')
        if not evaluation_files:
            message = qtw.QLabel('No evaluations')
            self.evaluations_layout.addWidget(message, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        self.evaluations = {}
        for i in evaluation_files:
            if i.endswith('.jsonl'):
                choice_method = i.split('(')[1].split(')')[0]
                with open('settings.json', 'r', encoding='utf-8') as file:
                    settings = json.load(file)
                x=''
                if settings['choice_method'] == 'random_in_subscale':
                    x = 'random_in_subscale_'+settings['selected_subscale']
                if settings['choice_method'] == choice_method or choice_method == x:
                    with open('data/evaluations/'+i, 'r', encoding='utf-8') as file:
                        for line in file:
                            eval_data = eval(line)
                            items = (eval_data['item1'], eval_data['item2'])
                            if items not in self.evaluations:
                                self.evaluations[items] = {}
                                if eval_data['semantically'] != 'No annotation':
                                    self.evaluations[items]['semantically'] = [float(eval_data['semantically'])]
                                #else:
                                #    self.evaluations[items]['semantically'] = [0.5]
                                if eval_data['taxonomically'] != 'No annotation':
                                    self.evaluations[items]['taxonomically'] = [float(eval_data['taxonomically'])]
                                #else:
                                #    self.evaluations[items]['taxonomically'] = [0.5]
                                if eval_data['causally'] != 'No annotation':
                                    self.evaluations[items]['causally'] = [float(eval_data['causally'])]
                                #else:
                                #    self.evaluations[items]['causally'] = [0.5]
                            else:
                                if eval_data['semantically'] != 'No annotation':
                                    self.evaluations[items]['semantically'].append(float(eval_data['semantically']))
                                #else:
                                #    self.evaluations[items]['semantically'].append(0.5)
                                if eval_data['taxonomically'] != 'No annotation':
                                    self.evaluations[items]['taxonomically'].append(float(eval_data['taxonomically']))
                                #else:
                                #    self.evaluations[items]['taxonomically'].append(0.5)
                                if eval_data['causally'] != 'No annotation':
                                    self.evaluations[items]['causally'].append(float(eval_data['causally']))
                                #else:
                                #    self.evaluations[items]['causally'].append(0.5)

        for items in self.evaluations:
            if 'semantically' in self.evaluations[items]:
                self.evaluations[items]['semantically_average'] = round(mean(self.evaluations[items]['semantically']),2)
            else:
                self.evaluations[items]['semantically_average'] = 'No annotation'
            if 'taxonomically' in self.evaluations[items]:
                self.evaluations[items]['taxonomically_average'] = round(mean(self.evaluations[items]['taxonomically']),2)
            else:
                self.evaluations[items]['taxonomically_average'] = 'No annotation'
            if 'causally' in self.evaluations[items]:
                self.evaluations[items]['causally_average'] = round(mean(self.evaluations[items]['causally']),2)
            else:
                self.evaluations[items]['causally_average'] = 'No annotation'
            item = qtw.QGroupBox()
            item.setLayout(qtw.QVBoxLayout())
            self.evaluations_layout.addWidget(item, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            item.layout().addWidget(qtw.QLabel('Item 1: '+items[0]))
            item.layout().addWidget(qtw.QLabel('Item 2: '+items[1]))
            item.layout().addWidget(qtw.QLabel('Semantic similarity: '+str(self.evaluations[items]['semantically_average'])))
            item.layout().addWidget(qtw.QLabel('Taxonomic similarity: '+str(self.evaluations[items]['taxonomically_average'])))
            item.layout().addWidget(qtw.QLabel('Causal similarity: '+str(self.evaluations[items]['causally_average'])))
            '''
            if 'T5' in self.evaluations[items]:
                item.layout().addWidget(qtw.QLabel('T5 similarity: '+str(self.evaluations[items]['T5'])))
            else:
                T5_button = qtw.QPushButton('Run T5 evaluation')
                T5_button.clicked.connect(lambda checked,item1=items[0], item2=items[1],item=item, button=T5_button, filename=i: self.run_T5({'item1': item1, 'item2': item2},item,button, filename))
                item.layout().addWidget(T5_button)
            '''
        T5_mae_button = qtw.QPushButton('Run T5 and calculate MAE')
        T5_mae_button.clicked.connect(self.T5_mae)

        self.evaluations_tab.layout().addWidget(T5_mae_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)


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


    def T5_mae(self):
        progress_bar = qtw.QProgressBar()
        self.evaluations_tab.layout().addWidget(progress_bar)
        progress_bar.setRange(0, len(self.evaluations))

        for items in self.evaluations:
            if 'T5' not in self.evaluations[items]:

                item1 = items[0]
                item2 = items[1]

                # update progress bar
                progress_bar.setValue(progress_bar.value() + 1)

                qtw.QApplication.processEvents()
                
                # add a sleep to simulate the time it takes to run the T5 model






                model = T5_model()
                embeddings = model.encode([item1, item2], convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
                self.evaluations[items]['T5'] = round(similarity.item(),2)
        
        progress_bar.deleteLater()
                

        # update evaluation layout
        self.clearLayout(self.evaluations_layout)
        for items in self.evaluations:
            item = qtw.QGroupBox()
            item.setLayout(qtw.QVBoxLayout())
            self.evaluations_layout.addWidget(item, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            item.layout().addWidget(qtw.QLabel('Item 1: '+items[0]))
            item.layout().addWidget(qtw.QLabel('Item 2: '+items[1]))
            item.layout().addWidget(qtw.QLabel('Semantic similarity: '+str(self.evaluations[items]['semantically_average'])))
            item.layout().addWidget(qtw.QLabel('Taxonomic similarity: '+str(self.evaluations[items]['taxonomically_average'])))
            item.layout().addWidget(qtw.QLabel('Causal similarity: '+str(self.evaluations[items]['causally_average'])))
            item.layout().addWidget(qtw.QLabel('T5 similarity: '+str(self.evaluations[items]['T5'])))
        

        

        
        




        semantically = []
        taxonomically = []
        causally = []
        T5 = []
        for items in self.evaluations:
            if 'semantically' in self.evaluations[items]:
                semantically.append(self.evaluations[items]['semantically_average'])
            if 'taxonomically' in self.evaluations[items]:
                taxonomically.append(self.evaluations[items]['taxonomically_average'])
            if 'causally' in self.evaluations[items]:
                causally.append(self.evaluations[items]['causally_average'])
            if 'T5' in self.evaluations[items]:
                T5.append(self.evaluations[items]['T5'])
        if len(semantically) > 1 and len(taxonomically) > 1 and len(causally) > 1 and len(T5) > 1:
            mae_semantically = round(mean_absolute_error(semantically, T5),2)
            mae_taxonomically = round(mean_absolute_error(taxonomically, T5),2)
            mae_causally = round(mean_absolute_error(causally, T5),2)
            #pearson_semantically = pearsonr(semantically, T5).correlation
            #pearson_taxonomically = pearsonr(taxonomically, T5).correlation
            #pearson_causally = pearsonr(causally, T5).correlation
            smaller = min(mae_semantically, mae_taxonomically, mae_causally)
            label = ''
            if smaller == mae_semantically:
                label = 'Semantically'
            elif smaller == mae_taxonomically:
                label = 'Taxonomically'
            elif smaller == mae_causally:
                label = 'Causally'
            self.message_label.setText('Smallest MAE: '+label+'\n'+str(smaller))
            self.message_label.setFixedSize(200, 50)
            self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
            self.message_label.setVisible(True)
            qtc.QTimer.singleShot(10000, lambda: self.message_label.setVisible(False))
        else:
            self.message_label.setText('Not enough data for evaluation')
            self.message_label.setFixedSize(300, 50)
            self.message_label.move(self.width() - self.message_label.width() - 20, 20)
            self.message_label.setVisible(True)
            qtc.QTimer.singleShot(3000, lambda: self.message_label.setVisible(False))
            

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
        random_choice = qtw.QRadioButton('10 Random choices')
        sequential_choice = qtw.QRadioButton('All possible combinations')
        random_choice1 = qtw.QRadioButton('10 Random choices in the same subscale')
        select_subscale = qtw.QComboBox()

        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        choice_method = settings['choice_method']
        if 'selected_subscale' in settings:
            selected_subscale = settings['selected_subscale']
        if choice_method == 'random':
            random_choice.setChecked(True)
            sequential_choice.setChecked(False)
            random_choice1.setChecked(False)
            select_subscale.setEnabled(False)

        elif choice_method == 'sequential':
            sequential_choice.setChecked(True)
            random_choice.setChecked(False)
            random_choice1.setChecked(False)
            select_subscale.setEnabled(False)
        elif choice_method == 'random_in_subscale':
            random_choice1.setChecked(True)
            random_choice.setChecked(False)
            sequential_choice.setChecked(False)
            select_subscale.setEnabled(True)

        self.choice_method.layout().addWidget(random_choice)
        self.choice_method.layout().addWidget(sequential_choice)
        
        layout = qtw.QHBoxLayout()
        if 'selected_subscale' not in settings:
            select_subscale.addItem('Select subscale')
        for i in self.dict:
            select_subscale.addItem('Subscale '+i)
        if 'selected_subscale' in settings:
            select_subscale.setCurrentText('Subscale '+selected_subscale)
        select_subscale.currentIndexChanged.connect(lambda: select_subscale.currentText())
        layout.addWidget(random_choice1)
        layout.addWidget(select_subscale)
        
        self.choice_method.layout().addLayout(layout)

        random_choice1.toggled.connect(lambda: select_subscale.setEnabled(True))
        random_choice.toggled.connect(lambda: select_subscale.setEnabled(False))
        sequential_choice.toggled.connect(lambda: select_subscale.setEnabled(False))



        b_layout = qtw.QHBoxLayout()
        settings_layout1.addWidget(self.choice_method)
        save_button = qtw.QPushButton('Save', clicked = lambda: self.save_choice_method(random_choice, sequential_choice, random_choice1, select_subscale))
        # tip message when cursor is over the save button
        save_button.setToolTip('Save the choice method')
        generate_button = qtw.QPushButton('Generate choices', clicked = self.create_choices)
        generate_button.setToolTip('Generate the choices')
        b_layout.addWidget(generate_button, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        b_layout.addWidget(save_button, alignment=qtc.Qt.AlignmentFlag.AlignCenter)
        settings_layout1.addLayout(b_layout)


        self.message_label = qtw.QLabel('Choice method saved', self)
        self.message_label.setStyleSheet("QLabel { background-color : gray; color : white; border-radius: 5px; }")
        self.message_label.setAlignment(qtc.Qt.AlignmentFlag.AlignCenter)
        self.message_label.setVisible(False)
        self.message_label.setFixedSize(150, 50)

        settings_layout1.addWidget(save_button, alignment=qtc.Qt.AlignmentFlag.AlignCenter)

        box.addLayout(settings_layout1)

        self.layout().addLayout(settings_layout)

    def save_choice_method(self, random_choice, sequential_choice, random_choice1, select_subscale):
        if random_choice.isChecked():
            choice_method = 'random'
        elif sequential_choice.isChecked():
            choice_method = 'sequential'
        elif random_choice1.isChecked():
            choice_method = 'random_in_subscale'
            subscale = select_subscale.currentText().replace('Subscale ', '')
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        settings['choice_method'] = choice_method
        if choice_method == 'random_in_subscale':
            settings['selected_subscale'] = subscale
        else:
            if 'selected_subscale' in settings:
                del settings['selected_subscale']
        with open('settings.json', 'w', encoding='utf-8') as file:
            json.dump(settings, file)
        self.message_label.setFixedSize(150,50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
        self.message_label.setText('Choice method saved\n'+choice_method)
        self.message_label.setVisible(True)
        qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))
        
        if os.path.exists('data/temp/random_choices.csv'):
            pass
        else:
            self.create_choices()
        if os.path.exists('data/temp/sequential_choices.csv'):
            pass
        else:
            self.create_choices()
        if settings['choice_method'] == 'random_in_subscale':
            if os.path.exists('data/temp/random_in_subscale_'+settings['selected_subscale']+'_choices.csv'):
                pass

            else:
                if DEBUG:
                    print('Creating random choices')
                    print(settings['choice_method'])
                self.create_choices()

    def create_choices(self):
        with open('settings.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
        choice_method = settings['choice_method']
        if choice_method == 'random':
            self.choices = self.create_random_choices()
        elif choice_method == 'sequential':
            self.choices = self.create_sequential_choices()
        elif choice_method == 'random_in_subscale':
            self.choices = self.create_random_in_subscale_choices(settings['selected_subscale'])
        self.message_label.setFixedSize(150,50)
        self.message_label.move(self.width() - self.message_label.width() - 20, 20)  # Position the message label at top-right
        self.message_label.setText('Choices created')
        self.message_label.setVisible(True)
        qtc.QTimer.singleShot(2000, lambda: self.message_label.setVisible(False))
        



    def create_random_choices(self):
        if DEBUG:
            print('Creating random choices')
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            filename = settings['subscale_file']
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    items = file.readlines()
                d = {}
                for i in range(len(items)):
                    q=items[i].split(',')[0]
                    item = items[i][items[i].index(',')+1:].replace('"','')
                    item = item.replace('\n','')
                    q=q[1:]
                    subscale = q.split('_')[0]
                    number = q.split('_')[1]
                    if subscale not in d:
                        d[subscale] = {}
                    d[subscale][number] = item
                self.choices = []
                d= {k: v for k, v in sorted(d.items(), key=lambda item: int(item[0]))}
                # create all possible combinations of items with no repetitions

                
                all_items = []
                for subscale, items_dict in d.items():
                    all_items.extend(items_dict.values())
                
                self.choices = random.sample(list(combinations(all_items, 2)),k=10)
                
                with open('data/temp/random_choices.csv', 'w', encoding='utf-8') as file:
                    for i in self.choices:
                        file.write('Q'+str(self.choices.index(i))+'\n'+i[0]+'\n'+i[1]+'\n')
                


    def create_sequential_choices(self):
        if DEBUG:
            print('Loading sequential choices')
        self.choices = []
        if os.path.exists('settings.json'):

            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
        filename = settings['subscale_file']
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
            '''
            for i in d:
               if i not in self.choices:
                    self.choices[i] = []
                    for j in d[i]:
                        self.choices[i].append(d[i][j])
            '''

            self.choices = [item for subscale in d.values() for item in subscale.values()]
            self.choices = list(combinations(self.choices, 2))

            with open('data/temp/'+settings['choice_method']+'_choices.csv', 'w', encoding='utf-8') as file:
                for i in self.choices:
                    file.write('Q'+str(self.choices.index(i))+'\n'+i[0]+'\n'+i[1]+'\n')

    def create_random_in_subscale_choices(self, subscale):
        if DEBUG:
            print('Creating random choices')
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
            filename = settings['subscale_file']
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    items = file.readlines()
                d = {}
                for i in range(len(items)):
                    q=items[i].split(',')[0]
                    item = items[i][items[i].index(',')+1:].replace('"','').replace('\n','')
                    q=q[1:]
                    sub = q.split('_')[0]
                    number = q.split('_')[1]
                    if sub == subscale:
                        if sub not in d:
                            d[sub] = {}
                        d[sub][number] = item
                self.choices = []
                self.choices = [item for subscale in d.values() for item in subscale.values()]
                self.choices = list(combinations(self.choices, 2))
                self.choices = random.choices(self.choices, k=10)


                with open('data/temp/random_in_subscale_'+subscale+'_choices.csv', 'w', encoding='utf-8') as file:
                    for i in self.choices:
                        file.write('Q'+str(self.choices.index(i))+'\n'+i[0]+'\n'+i[1]+'\n')






        
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
        qtc.QTimer.singleShot(2000, lambda: self.admin_settings())

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
        if DEBUG:
            print('Searching')
        self.clearLayout(layout)
        self.message_label.setVisible(False)
        if text == '':
            self.admin_page('admin')
        else:
            for subscale in self.dict:
                matching_items = []
                for j in self.dict[subscale]:
                    if text.lower() in self.dict[subscale][j].lower():
                        matching_items.append(j)

                if matching_items:
                    groupbox_title = f'Subscale {subscale}'
                    groupbox = qtw.QGroupBox(groupbox_title)
                    groupbox.setLayout(qtw.QVBoxLayout())
                    layout.addWidget(groupbox, alignment=qtc.Qt.AlignmentFlag.AlignTop)

                    buttons_view = qtw.QHBoxLayout()
                    add_item = qtw.QPushButton('Add item')
                    add_item.clicked.connect(lambda checked, subscale=subscale, groupbox=groupbox: self.add_item(subscale, groupbox))
                    buttons_view.addWidget(add_item)
                    delete_subscale = qtw.QPushButton('Delete subscale')
                    buttons_view.addWidget(delete_subscale)
                    delete_subscale.clicked.connect(lambda checked, subscale=subscale, groupbox=groupbox: self.delete_subscale(subscale, groupbox))

                    

                    for j in matching_items:
                        item_view = qtw.QHBoxLayout()
                        item = qtw.QLineEdit()
                        item.setText(self.dict[subscale][j])
                        if item.text() == '':
                            item.setPlaceholderText(f'Item {j}')
                        item.textChanged.connect(lambda text, subscale=subscale, i=j: self.dict[subscale].update({i: text}))

                        item_view.addWidget(item)
                        delete_button = qtw.QPushButton('Delete')
                        item_view.addWidget(delete_button)
                        groupbox.layout().addLayout(item_view)
                        delete_button.clicked.connect(lambda checked, subscale=subscale, i=j, groupbox=groupbox, item_view=item_view: self.delete_item(subscale, i, groupbox, item_view))
                        # if j is the last item in the subscale, add the buttons
                        if j == matching_items[-1]:
                            groupbox.layout().addLayout(buttons_view)
                            

        if not self.dict:
            message = qtw.QLabel('No subscales')
            layout.addWidget(message, alignment=qtc.Qt.AlignmentFlag.AlignCenter)

        






                


            











                    

                    


                


        
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
                        if '\n' in self.dict[i][j]:
                            self.dict[i][j] = self.dict[i][j].replace('\n', '')
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
        self.choices = []
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
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        self.message_label.setVisible(False)

    def user_page(self, username):
        if DEBUG:
            print('User page')
        self.clearLayout(self.layout())
        self.username = username

        with open('settings.json', 'r', encoding='utf-8') as file:
            self.settings = json.load(file)
    
        self.evaluations = self.load_evaluations()
        self.choices= self.load_data()

        if self.choices == {}:
            if self.settings['choice_method'] == 'random' or self.settings['choice_method'] == 'sequential':
                if os.path.exists('data/temp/'+self.settings['choice_method']+'_choices.csv'):
                    os.remove('data/temp/'+self.settings['choice_method']+'_choices.csv')
            elif self.settings['choice_method'] == 'random_in_subscale':
                if os.path.exists('data/temp/random_in_subscale_'+self.settings['selected_subscale']+'_choices.csv'):
                    os.remove('data/temp/random_in_subscale_'+self.settings['selected_subscale']+'_choices.csv')
            self.create_choices()
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

        codebook_button = qtw.QPushButton('Codebook')
        self.principal_layout.addWidget(codebook_button, alignment=qtc.Qt.AlignmentFlag.AlignBottom)
        codebook_button.clicked.connect(self.codebook)

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
    
    def codebook(self):
        from docx import Document
        # Create a new window for the codebook
        self.codebook_window = qtw.QWidget()
        self.codebook_window.setWindowTitle('Codebook')
        self.codebook_window.setFixedSize(400, 400)
        self.codebook_window.setLayout(qtw.QVBoxLayout())
        self.codebook_window.show()

        scroll_area = qtw.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = qtw.QWidget()
        scroll_widget.setLayout(qtw.QVBoxLayout())
        scroll_area.setWidget(scroll_widget)
        self.codebook_window.layout().addWidget(scroll_area)

        try:
            document = Document('codebook.docx')
            for i in document.paragraphs:
                label = qtw.QLabel(i.text)
                label.setWordWrap(True)
                scroll_widget.layout().addWidget(label)
        except:
            label = qtw.QLabel('Codebook not found')
            scroll_widget.layout().addWidget(label)

















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
            try:
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
            except:
                pass

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
                submit_button = qtw.QPushButton('Submit and exit')
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
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
        if settings['choice_method'] == 'random' or settings['choice_method'] == 'sequential':
            self.save('data/evaluations/'+self.username+'_('+settings['choice_method']+')_'+time+'.jsonl', closeFile = True)
        else:
            self.save('data/evaluations/'+self.username+'_('+settings['choice_method']+'_'+settings['selected_subscale']+')_'+time+'.jsonl', closeFile = True)

        
    def save(self, filename, closeFile = False):
        if filename == False:
            filename = 'data/temp/'+self.username+'_evaluations.jsonl'
        if DEBUG:
            print('Saving',filename)
        # save evaluations to file
        self.evaluations = {k: v for k, v in sorted(self.evaluations.items(), key=lambda item: int(item[0]))}
        with open(filename, 'w', encoding='utf-8') as file:
            for i in self.evaluations:
                self.evaluations[i]['item1'] = self.evaluations[i]['item1'].replace('\n','')
                self.evaluations[i]['item2'] = self.evaluations[i]['item2'].replace('\n','')
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
        if self.settings['choice_method'] == 'random' or self.settings['choice_method'] == 'sequential':
            if os.path.exists('data/temp/'+self.settings['choice_method']+'_choices.csv'):
                if DEBUG:
                    print('Loading data '+self.settings['choice_method'])
                with open('data/temp/'+self.settings['choice_method']+'_choices.csv', 'r', encoding='utf-8') as file:
                    self.choices = []
                    for line in file:
                        first = line
                        item1 = next(file)
                        item2 = next(file)
                        self.choices.append((item1, item2))
                return self.choices
            else:
                return {}
        else:
            if os.path.exists('data/temp/'+self.settings['choice_method']+'_'+self.settings['selected_subscale']+'_choices.csv'):
                if DEBUG:
                    print('Loading data')
                with open('data/temp/'+self.settings['choice_method']+'_'+self.settings['selected_subscale']+'_choices.csv', 'r', encoding='utf-8') as file:
                    self.choices = []
                    for line in file:
                        first = line
                        item1 = next(file)
                        item2 = next(file)
                        self.choices.append((item1, item2))
                        
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
            self.btn_next.setText('-->\nNext')
            self.btn_next.clicked.disconnect()
            self.btn_next.clicked.connect(self.next_choice)

        elif self.current_index == len(self.choices) - 1:
            self.btn_back.setDisabled(False)
            font = self.btn_next.font()
            font.setPointSize(10)
            self.btn_next.setText('Summary')
            self.btn_next.clicked.disconnect()
            self.btn_next.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
            self.btn_next.setFixedSize(self.btn_back.sizeHint())
            self.btn_next.setFont(font)
        else:
            self.btn_back.setDisabled(False)
            self.btn_next.setDisabled(False)
            self.btn_next.setHidden(False)
            self.btn_next.setText('-->\nNext')
            self.btn_next.clicked.disconnect()
            self.btn_next.clicked.connect(self.next_choice)

        if self.choices:
            self.label1.setText(self.choices[self.current_index][0])
            self.label2.setText(self.choices[self.current_index][1])
        else:
            self.label1.setText('No choices')
            self.label2.setText('No choices')
        self.update_values()


    def next_choice(self):
        if self.current_index < len(self.choices) - 1:
            self.current_index += 1
            self.update_labels()
        self.progress.setValue(int(self.current_index/len(self.choices)*100))
        self.update_values()

    def previous_choice(self):        
            if self.current_index > 0:
                self.current_index -= 1
                self.update_labels()
            self.progress.setValue(int(self.current_index/len(self.choices)*100))
            self.update_values()

app = qtw.QApplication([])
mw = MainWindow()
sys.exit(app.exec())


'''
causale
logica'''