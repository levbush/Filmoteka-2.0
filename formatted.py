[
    importlib := __import__('importlib'),
    PyQt6_QtWidgets := importlib.import_module('PyQt6.QtWidgets'),
    QWidget := PyQt6_QtWidgets.QWidget,
    QApplication := PyQt6_QtWidgets.QApplication,
    QPlainTextEdit := PyQt6_QtWidgets.QPlainTextEdit,
    QComboBox := PyQt6_QtWidgets.QComboBox,
    QPushButton := PyQt6_QtWidgets.QPushButton,
    QDialog := PyQt6_QtWidgets.QDialog,
    QVBoxLayout := PyQt6_QtWidgets.QVBoxLayout,
    QHeaderView := PyQt6_QtWidgets.QHeaderView,
    QTableWidget := PyQt6_QtWidgets.QTableWidget,
    QTableWidgetItem := PyQt6_QtWidgets.QTableWidgetItem,
    QTabWidget := PyQt6_QtWidgets.QTabWidget,
    QHBoxLayout := PyQt6_QtWidgets.QHBoxLayout,
    QMessageBox := PyQt6_QtWidgets.QMessageBox,
    sqlite3 := __import__('sqlite3'),
    sys := __import__('sys'),
    MyWidget := type(
        'MyWidget',
        (QWidget,),
        {
            '__getattr__': lambda self, name: getattr(self.filmsTab, name, None) or getattr(self.genresTab, name),
            'tab_changed': lambda self, index: self.update_films() if index == 0 else self.update_genres(),
        },
    ),
    setattr(
        MyWidget,
        '__init__',
        lambda self: [
            super(MyWidget, self).__init__(),
            self.setGeometry(300, 300, 800, 700),
            self.setLayout(QHBoxLayout()),
            self.__setattr__('tabWidget', QTabWidget(self)),
            self.layout().addWidget(self.tabWidget),
            self.tabWidget.currentChanged.connect(self.tab_changed),
            self.__setattr__('filmsTab', FilmsTab()),
            self.__setattr__('genresTab', GenresTab()),
            self.tabWidget.addTab(self.filmsTab, 'Фильмы'),
            self.tabWidget.addTab(self.genresTab, 'Жанры'),
            None,
        ][-1],
    ),
    FilmsTab := type(
        'FilmsTab',
        (QWidget,),
        {
            'add_film': lambda self: [
                setattr(self, 'add_film_widget', AddFilmWidget(self)),
                self.add_film_widget.show(),
                None,
            ][-1],
            'edit_film': lambda self: [
                (
                    None
                    if not (index := self.filmsTable.selectedIndexes())
                    else [
                        index := index[-1],
                        c := self.conn.cursor(),
                        film := c.execute(
                            'SELECT * FROM films WHERE id = ?', (self.filmsTable.item(index.row(), 0).text(),)
                        ).fetchone(),
                        setattr(
                            self,
                            'edit_film_widget',
                            AddFilmWidget(
                                self, film['id'], film['title'], str(film['year']), film['genre'], str(film['duration'])
                            ),
                        ),
                        self.edit_film_widget.show(),
                        None,
                    ][-1]
                )
            ][-1],
            'delete_film': lambda self: [
                (
                    None
                    if not (
                        indexes := [
                            int(self.filmsTable.item(i.row(), 0).text()) for i in self.filmsTable.selectedIndexes()
                        ]
                    )
                    else [
                        (
                            None
                            if (
                                QMessageBox.question(
                                    self, '', '', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                )
                            )
                            != QMessageBox.StandardButton.Yes
                            else [
                                c := self.conn.cursor(),
                                c.execute(
                                    f'DELETE FROM films WHERE id IN '
                                    f'{tuple(indexes) if len(indexes) > 1 else f"({indexes[0]})"}'
                                ),
                                self.conn.commit(),
                                self.update_films(),
                                None,
                            ][-1]
                        )
                    ][-1]
                )
            ][-1],
            'update_films': lambda self: [
                c := self.conn.cursor(),
                c.execute(
                    'SELECT films.id, films.title, year, '
                    'IFNULL(genres.title, films.genre), duration FROM films LEFT JOIN genres ON genres.id = films.genre'
                ),
                data := c.fetchall(),
                self.filmsTable.setColumnCount(5),
                self.filmsTable.setHorizontalHeaderLabels(
                    ['ИД', 'Название фильма', 'Год выпуска', 'Жанр', 'Продолжительность']
                ),
                self.filmsTable.setRowCount(len(data)),
                [
                    self.filmsTable.setItem(i, j, QTableWidgetItem(str(el)))
                    for i, line in enumerate(data)
                    for j, el in enumerate(line)
                ],
                None,
            ][-1],
        },
    ),
    setattr(
        FilmsTab,
        '__init__',
        lambda self: [
            super(FilmsTab, self).__init__(),
            setattr(self, 'add_form', None),
            setattr(self, 'conn', sqlite3.connect('films_db.sqlite')),
            setattr(self.conn, 'row_factory', sqlite3.Row),
            layout := QVBoxLayout(),
            btn_layout := QHBoxLayout(),
            layout.addLayout(btn_layout),
            setattr(self, 'addFilmButton', QPushButton('Добавить')),
            self.addFilmButton.clicked.connect(self.add_film),
            btn_layout.addWidget(self.addFilmButton),
            setattr(self, 'editFilmButton', QPushButton('Изменить')),
            self.editFilmButton.clicked.connect(self.edit_film),
            btn_layout.addWidget(self.editFilmButton),
            setattr(self, 'deleteFilmButton', QPushButton('Удалить')),
            self.deleteFilmButton.clicked.connect(self.delete_film),
            btn_layout.addWidget(self.deleteFilmButton),
            setattr(self, 'filmsTable', QTableWidget()),
            self.filmsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch),
            self.update_films(),
            layout.addWidget(self.filmsTable),
            self.setLayout(layout),
            None,
        ][-1],
    ),
    AddFilmWidget := type(
        'AddFilmWidget',
        (QDialog,),
        {
            'add': lambda self: [
                (
                    None
                    if not (title := self.title.toPlainText())
                    or not (year := self.year.toPlainText())
                    or not year.isdigit()
                    or not 2025 > (year := int(year)) > 0
                    or (
                        not (duration := self.duration.toPlainText())
                        or not duration.isdigit()
                        or not (duration := int(duration)) > 0
                    )
                    else [
                        c := self.conn.cursor(),
                        (
                            c.execute(
                                'REPLACE INTO films(id, title, year, genre, duration) VALUES (?, ?, ?, ?, ?)',
                                (self.id, title, year, self.params[self.comboBox.currentText()], duration),
                            )
                            if self.id
                            else c.execute(
                                'INSERT INTO films(title, year, genre, duration) VALUES (?, ?, ?, ?)',
                                (title, year, self.params[self.comboBox.currentText()], duration),
                            )
                        ),
                        self.conn.commit(),
                        self.parent().update_films(),
                        setattr(self, 'flag', True),
                        self.close(),
                        None,
                    ][-1]
                )
            ][-1],
            'get_adding_verdict': lambda self: self.flag,
            'get_editing_verdict': lambda self: self.flag,
        },
    ),
    setattr(
        AddFilmWidget,
        '__init__',
        lambda self, parent, id=None, title='', year='', genre=1, duration='': [
            super(AddFilmWidget, self).__init__(parent),
            setattr(self, 'id', id),
            setattr(self, 'conn', sqlite3.connect('films_db.sqlite')),
            c := self.conn.cursor(),
            setattr(self, 'params', {el[1]: el[0] for el in c.execute('SELECT * FROM genres').fetchall()}),
            layout := QVBoxLayout(),
            self.setLayout(layout),
            setattr(self, 'title', QPlainTextEdit(title)),
            self.title.setMaximumHeight(50),
            layout.addWidget(self.title),
            setattr(self, 'year', QPlainTextEdit(year)),
            layout.addWidget(self.year),
            self.year.setMaximumHeight(50),
            setattr(self, 'comboBox', QComboBox()),
            self.comboBox.addItems(list(self.params.keys())),
            self.comboBox.setCurrentIndex(genre - 1),
            self.comboBox.setMaximumHeight(50),
            layout.addWidget(self.comboBox),
            setattr(self, 'duration', QPlainTextEdit(duration)),
            self.duration.setMaximumHeight(50),
            layout.addWidget(self.duration),
            setattr(self, 'pushButton', QPushButton('Добавить')),
            self.pushButton.clicked.connect(self.add),
            layout.addWidget(self.pushButton),
            setattr(self, 'flag', False),
            None,
        ][-1],
    ),
    GenresTab := type(
        'GenresTab',
        (QWidget,),
        {
            'add_genre': lambda self: [
                setattr(self, 'add_genre_widget', AddGenreWidget(self)),
                self.add_genre_widget.show(),
                None,
            ][-1],
            'edit_genre': lambda self: [
                (
                    None
                    if not (index := self.genresTable.selectedIndexes())
                    else [
                        index := index[-1],
                        c := self.conn.cursor(),
                        genre := c.execute(
                            'SELECT * FROM genres WHERE id = ?', (self.genresTable.item(index.row(), 0).text(),)
                        ).fetchone(),
                        setattr(self, 'edit_genre_widget', AddGenreWidget(self, genre['id'], genre['title'])),
                        self.edit_genre_widget.show(),
                        None,
                    ][-1]
                )
            ][-1],
            'delete_genre': lambda self: [
                (
                    None
                    if not (
                        indexes := [
                            int(self.genresTable.item(i.row(), 0).text()) for i in self.genresTable.selectedIndexes()
                        ]
                    )
                    else [
                        (
                            None
                            if QMessageBox.question(
                                self, '', '', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                            )
                            != QMessageBox.StandardButton.Yes
                            else [
                                c := self.conn.cursor(),
                                c.execute(
                                    f'DELETE FROM genres WHERE id IN'
                                    f'{tuple(indexes) if len(indexes) > 1 else f"({indexes[0]})"}'
                                ),
                                self.conn.commit(),
                                self.update_genres(),
                                None,
                            ][-1]
                        )
                    ][-1]
                )
            ][-1],
            'update_genres': lambda self: [
                c := self.conn.cursor(),
                c.execute('SELECT * FROM genres'),
                data := c.fetchall(),
                self.genresTable.setColumnCount(2),
                self.genresTable.setHorizontalHeaderLabels(['ИД', 'Название жанра']),
                self.genresTable.setRowCount(len(data)),
                [
                    self.genresTable.setItem(i, j, QTableWidgetItem(str(el)))
                    for i, line in enumerate(data)
                    for j, el in enumerate(line)
                ],
                None,
            ][-1],
        },
    ),
    setattr(
        GenresTab,
        '__init__',
        lambda self: [
            super(GenresTab, self).__init__(),
            setattr(self, 'add_form', None),
            setattr(self, 'conn', sqlite3.connect('films_db.sqlite')),
            setattr(self.conn, 'row_factory', sqlite3.Row),
            layout := QVBoxLayout(),
            btn_layout := QHBoxLayout(),
            layout.addLayout(btn_layout),
            setattr(self, 'addGenreButton', QPushButton('Добавить')),
            self.addGenreButton.clicked.connect(self.add_genre),
            btn_layout.addWidget(self.addGenreButton),
            setattr(self, 'editGenreButton', QPushButton('Изменить')),
            self.editGenreButton.clicked.connect(self.edit_genre),
            btn_layout.addWidget(self.editGenreButton),
            setattr(self, 'deleteGenreButton', QPushButton('Удалить')),
            self.deleteGenreButton.clicked.connect(self.delete_genre),
            btn_layout.addWidget(self.deleteGenreButton),
            setattr(self, 'genresTable', QTableWidget()),
            self.genresTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch),
            self.update_genres(),
            layout.addWidget(self.genresTable),
            self.setLayout(layout),
            None,
        ][-1],
    ),
    AddGenreWidget := type(
        'AddGenreWidget',
        (QDialog,),
        {
            'add': lambda self: [
                (
                    None
                    if not (title := self.title.toPlainText())
                    else [
                        c := self.conn.cursor(),
                        (
                            c.execute('REPLACE INTO genres(id, title) VALUES (?, ?)', (self.id, title))
                            if self.id
                            else c.execute('INSERT INTO genres(title) VALUES (?)', (title,))
                        ),
                        self.conn.commit(),
                        self.parent().update_genres(),
                        setattr(self, 'flag', True),
                        self.close(),
                        None,
                    ][-1]
                )
            ][-1],
            'get_adding_verdict': lambda self: self.flag,
            'get_editing_verdict': lambda self: self.flag,
        },
    ),
    setattr(
        AddGenreWidget,
        '__init__',
        lambda self, parent, id=None, title='': [
            super(AddGenreWidget, self).__init__(parent),
            setattr(self, 'id', id),
            setattr(self, 'conn', sqlite3.connect('films_db.sqlite')),
            layout := QVBoxLayout(),
            self.setLayout(layout),
            setattr(self, 'title', QPlainTextEdit(title)),
            self.title.setMaximumHeight(50),
            layout.addWidget(self.title),
            setattr(self, 'pushButton', QPushButton('Подтвердить')),
            self.pushButton.clicked.connect(self.add),
            layout.addWidget(self.pushButton),
            setattr(self, 'flag', False),
            None,
        ][-1],
    ),
    (
        [app := QApplication(sys.argv), window := MyWidget(), window.show(), sys.exit(app.exec()), None][-1]
        if __name__ == '__main__'
        else None
    ),
]
