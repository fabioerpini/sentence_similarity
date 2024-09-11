item = qtw.QGroupBox(i)
            item.setLayout(qtw.QVBoxLayout())
            evaluations_layout.addWidget(item, alignment=qtc.Qt.AlignmentFlag.AlignTop)
            with open('data/evaluations/'+i, 'r', encoding='utf-8') as file:
                for line in file:
                    #insert evaluation data in a subitem with border red
                    subitem = qtw.QGroupBox()
                    subitem.setStyleSheet('QGroupBox {border: 1px solid #ddd; border-radius: 5px;}')
                    subitem.setLayout(qtw.QVBoxLayout())
                    eval_data = eval(line)
                    
                    subitem.layout().addWidget(qtw.QLabel('Item 1: '+eval_data['item1']))
                    subitem.layout().addWidget(qtw.QLabel('Item 2: '+eval_data['item2']))
                    subitem.layout().addWidget(qtw.QLabel('Semantic similarity: '+eval_data['semantically']))
                    subitem.layout().addWidget(qtw.QLabel('Taxonomic similarity: '+eval_data['taxonomically']))
                    subitem.layout().addWidget(qtw.QLabel('Causal similarity: '+eval_data['causally']))
                    item.layout().addWidget(subitem)
                    T5_button = qtw.QPushButton('Run T5 evaluation')
                    T5_button.clicked.connect(lambda checked, eval_data=eval_data: self.run_T5(eval_data))
                    subitem.layout().addWidget(T5_button)