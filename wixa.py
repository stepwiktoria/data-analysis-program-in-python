import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QListWidget, QTextEdit, QMenu, QAction, QListWidgetItem, QMessageBox

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

class ExcelFileLoader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.df = None
        self.selected_sheet = None
        self.selected_variable = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Excel File Loader")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.load_button = QPushButton("Load File", self)
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        self.correlation_button = QPushButton("Macierz korelacji", self)
        self.correlation_button.clicked.connect(self.correlation_matrix)
        self.layout.addWidget(self.correlation_button)

       

        self.variables_list = QListWidget(self)
        self.layout.addWidget(self.variables_list)
        self.variables_list.setContextMenuPolicy(3)  # ContextMenuPolicy.CustomContextMenu
        self.variables_list.customContextMenuRequested.connect(self.on_variable_right_click)

        self.popup_menu = QMenu(self)
        show_column_data_action = QAction("Show Column Data", self)
        show_column_data_action.triggered.connect(self.show_column_data)
        self.popup_menu.addAction(show_column_data_action)

        self.central_widget.setLayout(self.layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel files (*.xlsx)")
        if file_path:
            try:
                self.df = pd.read_excel(file_path, sheet_name=None)
                self.sheet_list.clear()
                for sheet in self.df.keys():
                    self.sheet_list.addItem(sheet)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the file: {e}")

    def on_sheet_select(self):
        try:
            index = self.sheet_list.currentRow()
            if index == -1:
                return
            self.selected_sheet = self.sheet_list.currentItem().text()
            self.variables_list.clear()
            for column in self.df[self.selected_sheet].columns:
                self.variables_list.addItem(column)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load the sheet: {e}")

    def on_variable_right_click(self, event):
        try:
            item = self.variables_list.itemAt(event.pos())
            if not item:
                return
            self.selected_variable = item.text()
            self.popup_menu.exec_(event.globalPos())
        finally:
            self.popup_menu.close()

    def show_column_data(self):
        top = QWidget(self)
        top.setWindowTitle(f"Data for {self.selected_variable}")
        data_text = QTextEdit(top)
        data_text.setGeometry(100, 100, 600, 400)
        data_text.setText(f"Names and values for '{self.selected_variable}':\n\n")
        column_data = self.df[self.selected_sheet][self.selected_variable]
        for i, value in enumerate(column_data):
            data_text.append(f"{i + 1}: {value}")
        top.show()

    def correlation_matrix(self):
        if not self.selected_sheet:
            QMessageBox.warning(self, "Warning", "Please select a sheet first.")
            return

        selection_window = QWidget(self)
        selection_window.setWindowTitle("Select Variables for Correlation Matrix")
        checkboxes = {}
        for var in self.df[self.selected_sheet].columns:
            checkboxes[var] = QCheckBox(var)
            checkboxes[var].setChecked(True)
            selection_window.layout().addWidget(checkboxes[var])

        confirm_button = QPushButton("OK", selection_window)
        confirm_button.clicked.connect(lambda: self.confirm_selection(checkboxes, selection_window))
        selection_window.layout().addWidget(confirm_button)

        selection_window.show()

    def confirm_selection(self, checkboxes, selection_window):
        selected_vars = [var for var, checkbox in checkboxes.items() if checkbox.isChecked()]
        if selected_vars:
            try:
                corr_df = self.df[self.selected_sheet][selected_vars].corr()

                # Plotting the correlation heatmap
                plt.figure(figsize=(8, 6))
                sns.heatmap(corr_df, annot=True, cmap='coolwarm', linewidths=.5)
                plt.title('Correlation Matrix Heatmap')
                plt.show()
                selection_window.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Unable to display correlation matrix: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Please select at least one variable.")

def run_regression_analysis(self):
    if not self.selected_sheet:
        QMessageBox.warning(self, "Warning", "Please select a sheet first.")
        return

    def select_independent_vars(dependent_var):
        def confirm_independent_vars():
            independent_vars = [indep_var_listitem.text() for indep_var_listitem in indep_vars_list.selectedItems()]
            if dependent_var in independent_vars:
                QMessageBox.critical(self, "Error", "Dependent variable cannot be in the independent variables list.")
                return
            if not independent_vars:
                QMessageBox.critical(self, "Error", "Please select at least one independent variable.")
                return
            perform_regression(dependent_var, independent_vars)
            indep_vars_window.close()

        indep_vars_window = QWidget(self)
        indep_vars_window.setWindowTitle("Select Independent Variables")

        indep_vars_list = QListWidget(indep_vars_window)
        indep_vars_list.setSelectionMode(QListWidget.MultiSelection)
        indep_vars_list.addItems(self.df[self.selected_sheet].columns)
        indep_vars_window.layout().addWidget(indep_vars_list)

        confirm_button = QPushButton("Confirm", indep_vars_window)
        confirm_button.clicked.connect(confirm_independent_vars)
        indep_vars_window.layout().addWidget(confirm_button)

        indep_vars_window.show()

    def confirm_dependent_var():
        if not dep_var_list.currentItem():
            QMessageBox.critical(self, "Error", "Please select a dependent variable.")
            return
        dependent_var = dep_var_list.currentItem().text()
        dep_var_window.close()
        select_independent_vars(dependent_var)

    def perform_regression(dependent_var, independent_vars):
        X = self.df[self.selected_sheet][independent_vars]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        Y = self.df[self.selected_sheet][dependent_var]
        model = sm.OLS(Y, X)
        results = model.fit()
        summary_window = QWidget(self)
        summary_window.setWindowTitle("Regression Results")

        text = QTextEdit(summary_window)
        text.setGeometry(100, 100, 600, 400)
        text.setText(results.summary().as_text())
        summary_window.show()

    # First select the dependent variable
    dep_var_window = QWidget(self)
    dep_var_window.setWindowTitle("Select Dependent Variable")

    dep_var_list = QListWidget(dep_var_window)
    dep_var_list.setSelectionMode(QListWidget.SingleSelection)
    dep_var_list.addItems(self.df[self.selected_sheet].columns)
    dep_var_window.layout().addWidget(dep_var_list)

    confirm_button = QPushButton("Confirm", dep_var_window)
    confirm_button.clicked.connect(confirm_dependent_var)
    dep_var_window.layout().addWidget(confirm_button)

    dep_var_window.show()
if __name__ == '__main__':
        app = QApplication(sys.argv)
        main_window = ExcelFileLoader()
        main_window.show()
        sys.exit(app.exec_())
