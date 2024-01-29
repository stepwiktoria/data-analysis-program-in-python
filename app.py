import tkinter as tk
from tkinter import filedialog, Listbox, messagebox, Menu, Toplevel, simpledialog, ttk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

class GretlApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry("1024x786")
        self.master.title("Gretl 2.0 App")
        self.master.tk.call("source", "azure.tcl")
        self.master.tk.call("set_theme", "dark")

        self.style = ttk.Style()

        # Data attributes
        self.df = None
        self.selected_sheet = None
        self.selected_variable = None

        # UI components
        self.load_frame = ttk.LabelFrame(self.master, text="", style='TFrame')
        self.load_frame.pack(side="top", fill="x", padx=10, pady=10)

        self.load_button = ttk.Button(self.load_frame, text="Load File", command=self.load_file, style='Accent.TButton')
        self.load_button.pack()

        self.frame = ttk.LabelFrame(self.master, style='TFrame')
        self.frame.pack()

        self.variable_frame = ttk.Frame(self.master)
        self.variable_frame.pack(pady=10)

        self.correlation_button = ttk.Button(self.frame, text="Correlation Matrix", command=self.correlation_matrix, style='TButton')
        self.correlation_button.grid(row=14, column=1, padx=10, pady=10)

        self.check_var_button = ttk.Button(self.frame, text="Check Variables Variation", command=self.check_variables_variation, style='TButton')
        self.check_var_button.grid(row=10, column=1, pady=10)

        self.regression_button = ttk.Button(self.frame, text="Run Regression Analysis", command=self.run_regression_analysis, style='TButton')
        self.regression_button.grid(row=12, column=1, padx=10, pady=10)

        self.stats_button = ttk.Button(self.frame, text="Descriptive Statistics", command=self.show_descriptive_stats, style='TButton')
        self.stats_button.grid(row=13, column=1, padx=10, pady=10)

        self.sheet_frame = tk.Frame(self.master, borderwidth=6, relief="solid", background="blue")
        self.sheet_frame.pack(pady=10)

        self.sheet_list = tk.Listbox(self.sheet_frame, width=75)
        self.sheet_list.pack(expand=True, fill="both")
        self.sheet_list.bind('<<ListboxSelect>>', self.on_sheet_select)

        self.variables_frame = tk.Frame(self.master, borderwidth=6, relief="solid", background='blue')
        self.variables_frame.pack(pady=10)

        self.variables_list = Listbox(self.variables_frame, width=75)
        self.variables_list.pack(expand=True, fill="both")
        self.variables_list.bind('<Button-3>', self.on_variable_right_click)

        self.popup_menu = Menu(self.master, tearoff=0)
        self.popup_menu.add_command(label="Show Column Data", command=self.show_column_data)
        self.popup_menu.add_command(label="Show Plot", command=self.show_plot)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                self.df = pd.read_excel(file_path, sheet_name=None)
                self.sheet_list.delete(0, tk.END)
                for sheet in self.df.keys():
                    self.sheet_list.insert(tk.END, sheet)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the file: {e}")






    def on_sheet_select(self, event):
        try:
            w = event.widget
            if not w.curselection():
                return
            index = int(w.curselection()[0])
            self.selected_sheet = w.get(index)
            self.variables_list.delete(0, tk.END)
            for column in self.df[self.selected_sheet].columns:
                self.variables_list.insert(tk.END, column)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the sheet: {e}")

    def on_variable_right_click(self, event):
        try:
            w = event.widget
            index = w.nearest(event.y)
            if index < 0:
                return
            self.selected_variable = w.get(index)
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def show_plot(self):
        try:
            data = self.df[self.selected_sheet][self.selected_variable]
            plt.figure()
            data.plot(kind='line' if data.dtype.kind in 'biufc' else 'bar')
            plt.title(self.selected_variable)
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create the plot: {e}")

    def show_column_data(self):
        top = Toplevel(self.master)
        top.title(f"Data for {self.selected_variable}")
        data_text = tk.Text(top)
        data_text.pack()

        column_data = self.df[self.selected_sheet][self.selected_variable]
        data_text.insert(tk.END, f"Names and values for '{self.selected_variable}':\n\n")
        for i, value in enumerate(column_data):
            data_text.insert(tk.END, f"{i + 1}: {value}\n")

    def correlation_matrix(self):
        def confirm_selection():
            selected_vars = [var for var, var_state in checkboxes.items() if var_state.get() == True]
            if selected_vars:
                try:
                    corr_df = self.df[self.selected_sheet][selected_vars].corr()

                    # Plotting the correlation heatmap
                    plt.figure(figsize=(8, 6))
                    sns.heatmap(corr_df, annot=True, cmap='coolwarm', linewidths=.5)
                    plt.title('Correlation Matrix Heatmap')
                    plt.show()
                    selection_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Unable to display correlation matrix: {e}")

        if not self.selected_sheet:
            messagebox.showwarning("Warning", "Please select a sheet first.")
            return

        selection_window = Toplevel(self.master)
        selection_window.title("Select Variables for Correlation Matrix")
        selection_window.geometry("400x600")
        checkboxes = {}
        for var in self.df[self.selected_sheet].columns:
            var_state = tk.BooleanVar()
            checkboxes[var] = var_state
            ttk.Checkbutton(selection_window, text=var, variable=var_state).pack(anchor='w')

        confirm_button = ttk.Button(selection_window, text="OK", command=confirm_selection)
        confirm_button.pack()

    def run_regression_analysis(self):
        if not self.selected_sheet:
            messagebox.showwarning("Warning", "Please select a sheet first.")
            return

        def select_independent_vars(dependent_var):
            def confirm_independent_vars():
                independent_vars = [indep_var_listbox.get(idx) for idx in indep_var_listbox.curselection()]
                if dependent_var in independent_vars:
                    messagebox.showerror("Error", "Dependent variable cannot be in the independent variables list.")
                    return
                if not independent_vars:
                    messagebox.showerror("Error", "Please select at least one independent variable.")
                    return
                perform_regression(dependent_var, independent_vars)
                indep_vars_window.destroy()

            indep_vars_window = Toplevel(self.master)
            indep_vars_window.title("Select Independent Variables")
            indep_vars_window.geometry("500x300")

            indep_var_listbox = Listbox(indep_vars_window, selectmode=tk.MULTIPLE)
            indep_var_listbox.pack(expand=True, fill='both')

            for var in self.df[self.selected_sheet].columns:
                indep_var_listbox.insert(tk.END, var)

            confirm_button = ttk.Button(indep_vars_window, text="Confirm", command=confirm_independent_vars)
            confirm_button.pack()

        def confirm_dependent_var():
            if not dep_var_listbox.curselection():
                messagebox.showerror("Error", "Please select a dependent variable.")
                return
            dependent_var = dep_var_listbox.get(dep_var_listbox.curselection()[0])
            dep_var_window.destroy()
            select_independent_vars(dependent_var)

        def perform_regression(dependent_var, independent_vars):
            X = self.df[self.selected_sheet][independent_vars]
            X = sm.add_constant(X)  # Adds a constant term to the predictor
            Y = self.df[self.selected_sheet][dependent_var]
            model = sm.OLS(Y, X)
            results = model.fit()
            summary_window = Toplevel(self.master)
            summary_window.title("Regression Results")
            text = tk.Text(summary_window)
            text.pack()
            text.insert(tk.END, results.summary().as_text())

        # First select the dependent variable
        dep_var_window = Toplevel(self.master)
        dep_var_window.title("Select Dependent Variable")
        dep_var_window.geometry("500x300")

        dep_var_listbox = Listbox(dep_var_window, selectmode=tk.SINGLE)
        dep_var_listbox.pack(expand=True, fill='both')

        for var in self.df[self.selected_sheet].columns:
            dep_var_listbox.insert(tk.END, var)

        confirm_button = ttk.Button(dep_var_window, text="Confirm", command=confirm_dependent_var)
        confirm_button.pack()

    def show_descriptive_stats(self):
        def display_stats():
            selected_vars = [stats_var_listbox.get(idx) for idx in stats_var_listbox.curselection()]
            if not selected_vars:
                messagebox.showerror("Error", "Please select at least one variable.")
                return
            stats = self.df[self.selected_sheet][selected_vars].describe()

            # Calculate coefficient of variation (CV) and skewness
            coefficient_of_variation = self.df[self.selected_sheet][selected_vars].std() / self.df[self.selected_sheet][selected_vars].mean()
            skewness = self.df[self.selected_sheet][selected_vars].skew()

            # Append CV and skewness to the stats DataFrame
            stats.loc['coef_of_var'] = coefficient_of_variation
            stats.loc['skewness'] = skewness

            stats_window = Toplevel(self.master)
            stats_window.title("Descriptive Statistics")
            text = tk.Text(stats_window)
            text.pack()
            text.insert(tk.END, stats.to_string())

        if not self.selected_sheet:
            messagebox.showwarning("Warning", "Please select a sheet first.")
            return

        stats_window = Toplevel(self.master)
        stats_window.title("Select Variables for Descriptive Statistics")

        stats_var_listbox = Listbox(stats_window, selectmode=tk.MULTIPLE)
        stats_var_listbox.pack(expand=True, fill='both')

        for var in self.df[self.selected_sheet].columns:
            stats_var_listbox.insert(tk.END, var)

        confirm_button = ttk.Button(stats_window, text="Show Statistics", command=display_stats)
        confirm_button.pack()

    def check_variables_variation(self):
        if not self.selected_sheet:
            messagebox.showwarning("Warning", "Please select a sheet first.")
            return

        low_variation_vars = []
        for column in self.df[self.selected_sheet].columns:
            mean = self.df[self.selected_sheet][column].mean()
            std_dev = self.df[self.selected_sheet][column].std()
            cv = (std_dev / mean) * 100 if mean != 0 else float('inf')
            if cv < 10:
                low_variation_vars.append(column)

        results_window = Toplevel(self.master)
        results_window.title("Low Variation Variables")
        text = tk.Text(results_window)
        text.pack()
        if low_variation_vars:
            text.insert(tk.END, "Variables with CV < 10%:\n" + "\n".join(low_variation_vars))
        else:
            text.insert(tk.END, "All variables have CV >= 10%.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GretlApp(root)
    root.mainloop()