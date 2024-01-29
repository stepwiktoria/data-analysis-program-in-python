import tkinter as tk
from tkinter import filedialog, Listbox, messagebox, Menu, Toplevel, simpledialog, ttk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

global df, selected_sheet
df = None
selected_sheet = None


def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        try:
            global df
            df = pd.read_excel(file_path, sheet_name=None)
            sheet_list.delete(0, tk.END)
            for sheet in df.keys():
                sheet_list.insert(tk.END, sheet)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the file: {e}")


def on_sheet_select(event):
    try:
        w = event.widget
        if not w.curselection():
            return
        index = int(w.curselection()[0])
        global selected_sheet
        selected_sheet = w.get(index)
        variables_list.delete(0, tk.END)
        for column in df[selected_sheet].columns:
            variables_list.insert(tk.END, column)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load the sheet: {e}")


def on_variable_right_click(event):
    try:
        w = event.widget
        index = w.nearest(event.y)
        if index < 0:
            return
        global selected_variable
        selected_variable = w.get(index)
        popup_menu.tk_popup(event.x_root, event.y_root)
    finally:
        popup_menu.grab_release()


def show_plot():
    try:
        data = df[selected_sheet][selected_variable]
        plt.figure()
        data.plot(kind='line' if data.dtype.kind in 'biufc' else 'bar')
        plt.title(selected_variable)
        plt.show()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create the plot: {e}")


def show_column_data():
    top = Toplevel(root)
    top.title(f"Data for {selected_variable}")
    data_text = tk.Text(top)
    data_text.pack()

    column_data = df[selected_sheet][selected_variable]
    data_text.insert(tk.END, f"Names and values for '{selected_variable}':\n\n")
    for i, value in enumerate(column_data):
        data_text.insert(tk.END, f"{i + 1}: {value}\n")


def correlation_matrix():
    def confirm_selection():
        selected_vars = [var for var, var_state in checkboxes.items() if var_state.get() == True]
        if selected_vars:
            try:
                corr_df = df[selected_sheet][selected_vars].corr()

                # Plotting the correlation heatmap
                plt.figure(figsize=(8, 6))
                sns.heatmap(corr_df, annot=True, cmap='coolwarm', linewidths=.5)
                plt.title('Correlation Matrix Heatmap')
                plt.show()
                selection_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Unable to display correlation matrix: {e}")

    if not selected_sheet:
        messagebox.showwarning("Warning", "Please select a sheet first.")
        return

    selection_window = Toplevel(root)
    selection_window.title("Select Variables for Correlation Matrix")
    checkboxes = {}
    for var in df[selected_sheet].columns:
        var_state = tk.BooleanVar()
        checkboxes[var] = var_state
        tk.Checkbutton(selection_window, text=var, variable=var_state).pack(anchor='w')

    confirm_button = tk.Button(selection_window, text="OK", command=confirm_selection)
    confirm_button.pack()


def run_regression_analysis():
    if not selected_sheet:
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

        indep_vars_window = Toplevel(root)
        indep_vars_window.title("Select Independent Variables")

        indep_var_listbox = Listbox(indep_vars_window, selectmode=tk.MULTIPLE)
        indep_var_listbox.pack(expand=True, fill='both')

        for var in df[selected_sheet].columns:
            indep_var_listbox.insert(tk.END, var)

        confirm_button = tk.Button(indep_vars_window, text="Confirm", command=confirm_independent_vars)
        confirm_button.pack()

    def confirm_dependent_var():
        if not dep_var_listbox.curselection():
            messagebox.showerror("Error", "Please select a dependent variable.")
            return
        dependent_var = dep_var_listbox.get(dep_var_listbox.curselection()[0])
        dep_var_window.destroy()
        select_independent_vars(dependent_var)

    def perform_regression(dependent_var, independent_vars):
        X = df[selected_sheet][independent_vars]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        Y = df[selected_sheet][dependent_var]
        model = sm.OLS(Y, X)
        results = model.fit()
        summary_window = Toplevel(root)
        summary_window.title("Regression Results")
        text = tk.Text(summary_window)
        text.pack()
        text.insert(tk.END, results.summary().as_text())

    # First select the dependent variable
    dep_var_window = Toplevel(root)
    dep_var_window.title("Select Dependent Variable")

    dep_var_listbox = Listbox(dep_var_window, selectmode=tk.SINGLE)
    dep_var_listbox.pack(expand=True, fill='both')

    for var in df[selected_sheet].columns:
        dep_var_listbox.insert(tk.END, var)

    confirm_button = tk.Button(dep_var_window, text="Confirm", command=confirm_dependent_var)
    confirm_button.pack()


def show_descriptive_stats():
    def display_stats():
        selected_vars = [stats_var_listbox.get(idx) for idx in stats_var_listbox.curselection()]
        if not selected_vars:
            messagebox.showerror("Error", "Please select at least one variable.")
            return
        stats = df[selected_sheet][selected_vars].describe()

        # Calculate coefficient of variation (CV) and skewness
        coefficient_of_variation = df[selected_sheet][selected_vars].std() / df[selected_sheet][selected_vars].mean()
        skewness = df[selected_sheet][selected_vars].skew()

        # Append CV and skewness to the stats DataFrame
        stats.loc['coef_of_var'] = coefficient_of_variation
        stats.loc['skewness'] = skewness

        stats_window = Toplevel(root)
        stats_window.title("Descriptive Statistics")
        text = tk.Text(stats_window)
        text.pack()
        text.insert(tk.END, stats.to_string())

    if not selected_sheet:
        messagebox.showwarning("Warning", "Please select a sheet first.")
        return

    stats_window = Toplevel(root)
    stats_window.title("Select Variables for Descriptive Statistics")

    stats_var_listbox = Listbox(stats_window, selectmode=tk.MULTIPLE)
    stats_var_listbox.pack(expand=True, fill='both')

    for var in df[selected_sheet].columns:
        stats_var_listbox.insert(tk.END, var)

    confirm_button = tk.Button(stats_window, text="Show Statistics", command=display_stats)
    confirm_button.pack()


def check_variables_variation():
    if not selected_sheet:
        messagebox.showwarning("Warning", "Please select a sheet first.")
        return

    low_variation_vars = []
    for column in df[selected_sheet].columns:
        mean = df[selected_sheet][column].mean()
        std_dev = df[selected_sheet][column].std()
        cv = (std_dev / mean) * 100 if mean != 0 else float('inf')
        if cv < 10:
            low_variation_vars.append(column)

    results_window = Toplevel(root)
    results_window.title("Low Variation Variables")
    text = tk.Text(results_window)
    text.pack()
    if low_variation_vars:
        text.insert(tk.END, "Variables with CV < 10%:\n" + "\n".join(low_variation_vars))
    else:
        text.insert(tk.END, "All variables have CV >= 10%.")


root = tk.Tk()
root.geometry("1920x1080")
root.title("Gretl 2.0 App")
root.tk.call("source", "azure.tcl")
root.tk.call("set_theme", "dark")

style = ttk.Style()

frame = ttk.LabelFrame(root, style='TFrame')  # Use ttk.Frame
frame.pack()

# Przycisk "Load File" w prawym górnym rogu z zachowanym marginesem
load_button = ttk.Button(frame, text="Load File", command=load_file, style='Accent.TButton')
load_button.grid(row=0, column=1, padx=10, pady=10)

# Okno, w którym pojawia się zmienna, szerokie i poziome
variable_frame = ttk.Frame(root)
variable_frame.pack(pady=10)

correlation_button = ttk.Button(frame, text="Macierz korelacji", command=correlation_matrix, style='TButton')
correlation_button.grid(row=14, column=1, padx=10, pady=10)

# Przycisk "Check Variables Variation" pod przyciskiem "Macierz korelacji"
check_var_button = ttk.Button(frame, text="Check Variables Variation", command=check_variables_variation,style='TButton')
check_var_button.grid(row=10, column=1, pady=10)

# Pozostałe przyciski poniżej
regression_button = ttk.Button(frame, text="Run Regression Analysis", command=run_regression_analysis, style='TButton')
regression_button.grid(row=12, column=1, padx=10, pady=10)

stats_button = ttk.Button(frame, text="Statystyki opisowe", command=show_descriptive_stats,style='TButton')
stats_button.grid(row=13, column=1, padx=10, pady=10)

# Reszta przycisków poniżej
sheet_list = Listbox(root)
sheet_list.pack()
sheet_list.bind('<<ListboxSelect>>', on_sheet_select)

variables_list = Listbox(root)
variables_list.pack()

variables_list.bind('<Button-3>', on_variable_right_click)

popup_menu = Menu(root, tearoff=0)
popup_menu.add_command(label="Show Column Data", command=show_column_data)
popup_menu.add_command(label="Show Plot", command=show_plot)

root.mainloop()