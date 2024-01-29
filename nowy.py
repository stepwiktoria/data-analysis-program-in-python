import tkinter as tk
from tkinter import messagebox, scrolledtext

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


class StatsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Descriptive Statistics App')
        self.geometry('400x300')

        self.df = pd.read_csv('kc_house_data.csv')  # Load the data at initialization

        # Create buttons and add them to the window
        self.create_button('Show Stats', self.show_stats)
        self.create_button('Show Boxplots', self.show_boxplots)
        self.create_button('Clean Data', self.clean_data)
        self.create_button('Heatmap', self.show_covariance_heatmap)
        self.create_button('Delete Variables', self.delete_variables)
        self.create_button('Plot Distribution', self.plot_distribution)
        self.create_button('Show Price Correlations', self.show_price_correlations)
        self.create_button('Normalize Data', self.normalize_data)
        self.create_button('Show First 20 Rows', self.show_head)
        self.create_button('Linear Regression', self.perform_linear_regression)

    def create_button(self, text, command):
        btn = tk.Button(self, text=text, command=command)
        btn.grid(padx=10, pady=10, sticky='nsew')

    def show_stats(self):
        # Load the data from a CSV file

        # Exclude the 'price' column and calculate descriptive stats, rounding to 2 decimal places
        desc_stats = self.df.drop('price', axis=1).describe().round(2)

        # Calculate skewness, rounded to 2 decimal places
        skewness = self.df.drop('price', axis=1).skew().round(2).to_frame('skewness').T

        # Calculate coefficient of variation = std/mean, rounded to 2 decimal places
        coefficient_variation = (desc_stats.loc['std'] / desc_stats.loc['mean']).round(2).to_frame('coef_variation').T

        # Combine all stats into a single DataFrame
        all_stats = pd.concat([desc_stats, skewness, coefficient_variation], ignore_index=False)

        # Convert DataFrame to a string with appropriate formatting
        stats_str = all_stats.to_string()

        # Create a new window for the statistics
        stats_window = tk.Toplevel(self)
        stats_window.title('Statistics')
        stats_text = tk.Text(stats_window, wrap='none')
        stats_text.insert(tk.END, stats_str)
        stats_text.config(state='disabled')
        stats_text.pack(expand=True, fill='both')

        # Create horizontal and vertical scrollbars
        h_scroll = tk.Scrollbar(stats_window, orient='horizontal', command=stats_text.xview)
        h_scroll.pack(side='bottom', fill='x')
        v_scroll = tk.Scrollbar(stats_window, orient='vertical', command=stats_text.yview)
        v_scroll.pack(side='right', fill='y')

        # Configure the text widget to work with scrollbars
        stats_text.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

    def show_boxplots(self):


        # Calculate the number of outliers using 1.5 * IQR rule
        Q1 = self.df.quantile(0.25)
        Q3 = self.df.quantile(0.75)
        IQR = Q3 - Q1
        outlier_condition = ((self.df < (Q1 - 1.5 * IQR)) | (self.df > (Q3 + 1.5 * IQR)))
        outliers = outlier_condition.sum().rename('Number of outliers')

        # Display the number of outliers in a text window
        outliers_window = tk.Toplevel(self)
        outliers_window.title('Number of Outliers')
        text_area = scrolledtext.ScrolledText(outliers_window, wrap=tk.WORD, height=10, width=50)
        text_area.grid(column=0, pady=10, padx=10)
        text_area.insert(tk.INSERT, outliers.to_string())
        text_area.configure(state='disabled')

        # Function to create and show the boxplot for each variable
        def create_boxplot(variable):
            fig, ax = plt.subplots()
            self.df.boxplot(column=variable, ax=ax)
            ax.set_title(variable)
            plt.show()

        # Iterate over each variable and create a boxplot
        for column in self.df.columns:
            create_boxplot(column)

    def clean_data(self):
        # Drop columns with a coefficient of variation less than 10%
        desc_stats = self.df.describe()
        coefficient_variation = (desc_stats.loc['std'] / desc_stats.loc['mean']).abs()
        cols_to_drop = coefficient_variation[coefficient_variation < 0.1].index
        self.df.drop(cols_to_drop, axis=1, inplace=True)

        # Replace outliers
        Q1 = self.df.quantile(0.25)
        Q3 = self.df.quantile(0.75)
        IQR = Q3 - Q1

        # Define a function to replace outliers with the nearest acceptable values
        def replace_outliers(ser):
            low = Q1[ser.name] - 1.5 * IQR[ser.name]
            high = Q3[ser.name] + 1.5 * IQR[ser.name]
            ser = ser.mask(ser < low, low)
            ser = ser.mask(ser > high, high)
            return ser

        self.df = self.df.apply(replace_outliers, axis=0)

        # Confirm the changes
        messagebox.showinfo('Data Cleaning', 'Columns with low variation dropped and outliers replaced.')

        # Overwrite the original dataset
        self.df.to_csv('kc_house_data.csv', index=False)
        messagebox.showinfo('Data Saved', 'The dataset has been cleaned and saved as "kc_house_data.csv".')

    def show_covariance_heatmap(self):
        # Exclude 'price' column and calculate the covariance matrix
        cov_matrix = self.df.drop('price', axis=1).corr()


        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(cov_matrix, annot=True, fmt='.2f', cmap='coolwarm', linewidths=.5)
        plt.title('Covariance Matrix Heatmap')
        plt.show()

    def delete_variables(self):
        # Create a new window for deleting variables
        delete_window = tk.Toplevel(self)
        delete_window.title('Delete Variables')

        # Listbox to display variables
        lb = tk.Listbox(delete_window, selectmode='multiple')
        lb.pack(expand=True, fill='both', padx=10, pady=10)

        # Populate the listbox with column names
        for column in self.df.columns:
            lb.insert(tk.END, column)

        # Function to handle deletion
        def handle_delete():
            selected_indices = lb.curselection()
            selected_vars = [lb.get(i) for i in selected_indices]
            for var in selected_vars:
                if var in self.df.columns:
                    self.df.drop(var, axis=1, inplace=True)
            messagebox.showinfo('Variables Deleted', f'Deleted variables: {", ".join(selected_vars)}')
            delete_window.destroy()

            self.df.to_csv('kc_house_data.csv', index=False)
            messagebox.showinfo('Data Saved', 'The dataset has been cleaned and saved as "kc_house_data.csv".')

        # Button to confirm deletion
        delete_btn = tk.Button(delete_window, text='Delete Selected', command=handle_delete)
        delete_btn.pack(pady=10)

    def plot_distribution(self):
        # Create a new window for plotting distributions
        plot_window = tk.Toplevel(self)
        plot_window.title('Plot Probability Distribution')

        # Dropdown menu to select a variable
        var = tk.StringVar(plot_window)
        choices = [col for col in self.df.columns if self.df[col].dtype in ['float64', 'int64']]
        var.set(choices[0])  # set the default option

        popupMenu = tk.OptionMenu(plot_window, var, *choices)
        tk.Label(plot_window, text="Choose a column").pack()
        popupMenu.pack()

        # Function to handle plotting
        def handle_plot():
            selected_var = var.get()
            if selected_var in self.df.columns:
                sns.displot(self.df[selected_var], kde=True)
                plt.title(f'Probability Distribution of {selected_var}')
                plt.show()

        # Button to confirm and plot
        plot_btn = tk.Button(plot_window, text='Plot', command=handle_plot)
        plot_btn.pack(pady=10)

    def show_price_correlations(self):
        # Check if 'price' column exists
        if 'price' not in self.df.columns:
            messagebox.showwarning("Warning", "'price' column not found in the dataset.")
            return

        # Calculate the correlation with 'price'
        correlations = self.df.corr()['price'].sort_values(ascending=False)

        # Create a new window to display the correlations
        corr_window = tk.Toplevel(self)
        corr_window.title('Correlations with Price')

        # Display the correlations in a text widget
        corr_text = scrolledtext.ScrolledText(corr_window, wrap='word', height=15, width=50)
        corr_text.grid(column=0, pady=10, padx=10)
        corr_text.insert(tk.INSERT, correlations.to_string())
        corr_text.configure(state='disabled')

    def normalize_data(self):
        # Create a new window for normalization options
        norm_window = tk.Toplevel(self)
        norm_window.title('Normalize Data')

        # Radio buttons for selecting normalization type
        norm_type = tk.StringVar(value='minmax')
        minmax_radio = tk.Radiobutton(norm_window, text='Min-Max Normalization', variable=norm_type, value='minmax')
        zscore_radio = tk.Radiobutton(norm_window, text='Z-Score Normalization', variable=norm_type, value='zscore')
        minmax_radio.pack(anchor='w')
        zscore_radio.pack(anchor='w')

        # Function to apply normalization
        def apply_normalization():
            if norm_type.get() == 'minmax':
                # Min-Max Normalization
                self.df = (self.df - self.df.min()) / (self.df.max() - self.df.min())
            elif norm_type.get() == 'zscore':
                # Z-Score Normalization
                self.df = (self.df - self.df.mean()) / self.df.std()
            self.df.to_csv('kc_house_data.csv', index=False)
            messagebox.showinfo('Data Saved', 'The dataset has been cleaned and saved as "kc_house_data.csv".')
            messagebox.showinfo('Normalization Complete', f'Data normalized using {norm_type.get()} method.')
            norm_window.destroy()

        # Button to confirm and apply normalization
        apply_btn = tk.Button(norm_window, text='Apply Normalization', command=apply_normalization)
        apply_btn.pack(pady=10)

    def show_head(self):
        # Create a new window to display the first 20 rows
        head_window = tk.Toplevel(self)
        head_window.title('First 20 Rows of the Dataset')

        # Create a scrolled text widget to display the rows
        head_text = scrolledtext.ScrolledText(head_window, wrap='none')
        head_text.pack(expand=True, fill='both')

        # Insert the first 20 rows into the text widget
        first_20_rows = self.df.head(20).to_string()
        head_text.insert(tk.END, first_20_rows)
        head_text.config(state='disabled')

        # Create horizontal and vertical scrollbars
        h_scroll = tk.Scrollbar(head_window, orient='horizontal', command=head_text.xview)
        h_scroll.pack(side='bottom', fill='x')
        v_scroll = tk.Scrollbar(head_window, orient='vertical', command=head_text.yview)
        v_scroll.pack(side='right', fill='y')

        # Configure the text widget to work with scrollbars
        head_text.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

    def perform_linear_regression(self):
        # Check if 'price' column exists
        if 'price' not in self.df.columns:
            messagebox.showwarning("Warning", "'price' column not found in the dataset.")
            return

        # Separate the independent and dependent variables
        X = self.df.drop('price', axis=1)
        y = self.df['price']

        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Create and train the linear regression model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Make predictions and calculate metrics
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Display the results
        results = f'Mean Squared Error: {mse}\nR^2 Score: {r2}'
        messagebox.showinfo('Linear Regression Results', results)


if __name__ == '__main__':
    app = StatsApp()
    app.mainloop()
